import asyncio
from pymodbus.client import AsyncModbusTcpClient
import logging

TARGET_IP = "localhost"
TARGET_PORT = 5020

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RECON] - %(message)s')

async def run_recon():
    client = AsyncModbusTcpClient(TARGET_IP, port=TARGET_PORT)
    await client.connect()
    
    if not client.connected:
        logging.error("Target unreachable.")
        return

    logging.info("Starting Modbus Reconnaissance...")

    # 1. Identify Device
    logging.info("Probe 1: Read Device Identification (Func 0x2B/0x0E)")
    # Note: pymodbus client helper for this is specific, we'll try reading registers to fingerprint if ID fails
    # In a real scenario we'd use ReadDeviceInformation, but let's stick to register scanning for this lab
    
    # 2. Scan Holding Registers
    logging.info("Probe 2: Scanning Holding Registers (0-20)...")
    try:
        rr = await client.read_holding_registers(0, 20, slave=1)
        if not rr.isError():
            logging.info("Dump of Registers 0-19:")
            for i, val in enumerate(rr.registers):
                if val != 0:
                    logging.info(f"  Reg {i}: {val}")
        else:
            logging.info("Read failed or protected.")
    except Exception as e:
        logging.error(f"Scan error: {e}")

    client.close()

if __name__ == "__main__":
    asyncio.run(run_recon())
