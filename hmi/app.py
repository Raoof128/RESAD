import asyncio
import logging
from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymodbus.client import AsyncModbusTcpClient
import json
import os
import sys

# Add parent directory to path to import simulation config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simulation import config

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="hmi/static"), name="static")
templates = Jinja2Templates(directory="hmi/templates")

# Modbus Client to poll the server
modbus_client = AsyncModbusTcpClient(config.MODBUS_HOST, port=config.MODBUS_PORT)

@app.on_event("startup")
async def startup_event():
    await modbus_client.connect()

@app.on_event("shutdown")
async def shutdown_event():
    modbus_client.close()

@app.get("/")
async def get_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if not modbus_client.connected:
                await modbus_client.connect()

            # Poll Modbus Registers
            # We read a block of registers
            rr = await modbus_client.read_holding_registers(0, 10, slave=1)
            
            if not rr.isError():
                regs = rr.registers
                data = {
                    "solar_output": regs[config.REG_SOLAR_OUTPUT] / 10.0,
                    "inverter_status": regs[config.REG_INVERTER_STATUS],
                    "battery_soc": regs[config.REG_BATTERY_SOC],
                    "export_limit": regs[config.REG_GRID_EXPORT_LIMIT],
                    "grid_freq": regs[config.REG_GRID_FREQ] / 100.0,
                    "grid_voltage": regs[config.REG_GRID_VOLTAGE],
                    "active_power": regs[config.REG_GRID_POWER_ACTIVE] / 10.0,
                    "irradiance": regs[config.REG_IRRADIANCE]
                }
                
                # Read Coils for Status
                rr_coils = await modbus_client.read_coils(0, 2, slave=1)
                if not rr_coils.isError():
                    data["defence_mode"] = rr_coils.bits[config.COIL_DEFENCE_MODE]

                await websocket.send_json(data)
            else:
                await websocket.send_json({"error": "Modbus Read Error"})

            await asyncio.sleep(1)
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.post("/api/control/inverter")
async def toggle_inverter(state: dict):
    # state: {"enable": true/false}
    val = 1 if state.get("enable") else 0
    await modbus_client.write_coil(config.COIL_INVERTER_ENABLE, val, slave=1)
    return {"status": "ok", "val": val}

@app.post("/api/control/export_limit")
async def set_export_limit(data: dict):
    # data: {"limit": 500}
    limit = int(data.get("limit", 500))
    await modbus_client.write_register(config.REG_GRID_EXPORT_LIMIT, limit, slave=1)
    return {"status": "ok", "limit": limit}

@app.post("/api/control/defence")
async def toggle_defence(state: dict):
    # state: {"enable": true/false}
    val = 1 if state.get("enable") else 0
    await modbus_client.write_coil(config.COIL_DEFENCE_MODE, val, slave=1)
    return {"status": "ok", "val": val}
