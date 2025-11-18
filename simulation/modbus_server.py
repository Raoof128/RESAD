import asyncio
import logging
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

from . import config
from .solar_model import SolarModel, BatteryModel, InverterModel, GridModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModbusSimulation")

class SimulationEngine:
    def __init__(self, context):
        self.context = context
        self.solar = SolarModel()
        self.battery = BatteryModel()
        self.inverter = InverterModel()
        self.grid = GridModel()
        self.slave_id = 0x01

    async def run_loop(self):
        logger.info("Starting Simulation Loop...")
        while True:
            try:
                # 1. Read current state from Modbus (in case HMI/Attacker changed settings)
                # Note: In a real PLC, logic runs then updates registers.
                # Here we check for control inputs first.
                
                # Read Export Limit
                register = 3 # Holding Register
                slave_context = self.context[self.slave_id]
                
                # Get Export Limit (Reg 3)
                export_limit_raw = slave_context.getValues(3, config.REG_GRID_EXPORT_LIMIT, count=1)[0]
                self.grid.export_limit = float(export_limit_raw)

                # Get Inverter Enable Coil (Coil 0)
                inverter_enable = slave_context.getValues(1, config.COIL_INVERTER_ENABLE, count=1)[0]
                self.inverter.status = 1 if inverter_enable else 0

                # Get Defence Mode Coil (Coil 1)
                defence_mode = slave_context.getValues(1, config.COIL_DEFENCE_MODE, count=1)[0]
                
                # DEFENCE MODE LOGIC
                if defence_mode:
                    # Rule: If Export Limit is set to < 100kW (likely attack), revert to 500kW
                    if self.grid.export_limit < 100.0:
                        logger.warning("DEFENCE MODE: Detected malicious Export Limit change! Reverting...")
                        self.grid.export_limit = 500.0
                        # Write back to register to fix it immediately
                        slave_context.setValues(3, config.REG_GRID_EXPORT_LIMIT, [500])

                
                # 2. Update Physics
                solar_power = self.solar.update()
                
                # Simple logic: If solar > export limit, charge battery. If solar < load (0 for now), discharge.
                # For this simplified lab, we just export everything possible up to limit, rest to battery.
                
                potential_export = solar_power * self.inverter.efficiency
                actual_export = min(potential_export, self.grid.export_limit)
                
                # Excess energy to battery (or from battery if we wanted to support load, but let's keep it simple: solar farm export only)
                # If we are curtailed (actual < potential), the extra energy goes to battery? 
                # Or we just clip it. Let's say we clip it unless we want to show battery charging.
                # Let's make it: Battery charges if we are curtailed.
                battery_power = potential_export - actual_export
                
                # Update Battery
                soc = self.battery.update(battery_power, config.UPDATE_INTERVAL)
                
                # Update Grid Metrics
                voltage, freq = self.grid.update(actual_export)

                # 3. Write outputs back to Modbus Registers
                # We scale floats to integers for Modbus registers
                
                # Solar Output (x10)
                slave_context.setValues(3, config.REG_SOLAR_OUTPUT, [int(solar_power * 10)])
                
                # Inverter Status
                slave_context.setValues(3, config.REG_INVERTER_STATUS, [self.inverter.status])
                
                # Battery SoC
                slave_context.setValues(3, config.REG_BATTERY_SOC, [int(soc)])
                
                # Grid Freq (x100)
                slave_context.setValues(3, config.REG_GRID_FREQ, [int(freq * 100)])
                
                # Grid Voltage
                slave_context.setValues(3, config.REG_GRID_VOLTAGE, [int(voltage)])
                
                # Active Power (x10)
                slave_context.setValues(3, config.REG_GRID_POWER_ACTIVE, [int(actual_export * 10)])
                
                # Irradiance
                slave_context.setValues(3, config.REG_IRRADIANCE, [int(self.solar.irradiance)])

                logger.debug(f"Sim Update: Solar={solar_power:.2f}kW, Export={actual_export:.2f}kW, SoC={soc:.1f}%")

            except Exception as e:
                logger.error(f"Error in simulation loop: {e}")
            
            await asyncio.sleep(config.UPDATE_INTERVAL)

async def main():
    # 1. Setup Modbus Datastore
    # Initialize with some default values
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),
        co=ModbusSequentialDataBlock(0, [1]*100), # Coils, default ON
        hr=ModbusSequentialDataBlock(0, [0]*100), # Holding Registers
        ir=ModbusSequentialDataBlock(0, [0]*100)
    )
    context = ModbusServerContext(slaves=store, single=True)

    # 2. Identity
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'SolarSCADA'
    identity.ProductCode = 'SIM-001'
    identity.VendorUrl = 'http://github.com/solar-scada-lab'
    identity.ProductName = 'Solar Farm Controller'
    identity.ModelName = 'SOCI-Compliant-v1'
    identity.MajorMinorRevision = '1.0'

    # 3. Start Simulation Loop in background
    sim_engine = SimulationEngine(context)
    asyncio.create_task(sim_engine.run_loop())

    # 4. Start Modbus TCP Server
    logger.info(f"Starting Modbus TCP Server on {config.MODBUS_HOST}:{config.MODBUS_PORT}")
    await StartAsyncTcpServer(context, identity=identity, address=(config.MODBUS_HOST, config.MODBUS_PORT))

if __name__ == "__main__":
    asyncio.run(main())
