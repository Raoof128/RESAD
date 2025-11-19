# Modbus Server Settings
MODBUS_HOST = "0.0.0.0"
MODBUS_PORT = 5020

# Simulation Timing
UPDATE_INTERVAL = 1.0  # Seconds between model updates

# Register Map (Holding Registers)
# We use a simple offset-based mapping for the simulation context
REG_SOLAR_OUTPUT = 0  # kW (float32 or scaled int) - Let's use scaled int (x10) for simplicity in Modbus
REG_INVERTER_STATUS = 1  # 0=OFF, 1=ON, 2=FAULT
REG_BATTERY_SOC = 2  # % (0-100)
REG_GRID_EXPORT_LIMIT = 3  # kW
REG_GRID_FREQ = 4  # Hz (scaled x100, e.g., 5000 = 50.00Hz)
REG_GRID_VOLTAGE = 5  # Volts
REG_GRID_POWER_ACTIVE = 6  # kW (scaled x10)
REG_GRID_POWER_REACTIVE = 7  # kVAR (scaled x10)
REG_WIND_SPEED = 8  # m/s (scaled x10) - Optional environmental factor
REG_IRRADIANCE = 9  # W/m2

# Coil Map (Read/Write Booleans)
COIL_INVERTER_ENABLE = 0  # Write 1 to enable, 0 to disable
COIL_DEFENCE_MODE = 1  # Write 1 to enable auto-defence

# Simulation Constants
MAX_SOLAR_OUTPUT = 500.0  # kW
BATTERY_CAPACITY = 1000.0  # kWh
MAX_EXPORT_LIMIT = 500.0  # kW
GRID_VOLTAGE_BASE = 240.0  # V
GRID_FREQ_BASE = 50.0  # Hz
