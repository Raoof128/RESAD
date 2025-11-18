import random
import math
from datetime import datetime
from . import config

class SolarModel:
    def __init__(self):
        self.irradiance = 0.0 # W/m2
        self.output_power = 0.0 # kW

    def update(self):
        # Simulate daily solar cycle based on system time (accelerated or real-time)
        # For simplicity, we'll just use a sine wave with some noise
        now = datetime.now()
        # Simple day cycle: peak at noon
        hour_float = now.hour + now.minute / 60.0
        if 6 <= hour_float <= 18:
            # Sun is up
            peak_factor = math.sin((hour_float - 6) * math.pi / 12)
            # Add cloud noise
            noise = random.uniform(0.8, 1.0)
            self.irradiance = 1000.0 * peak_factor * noise
            self.output_power = (self.irradiance / 1000.0) * config.MAX_SOLAR_OUTPUT
        else:
            self.irradiance = 0.0
            self.output_power = 0.0
        
        return self.output_power

class BatteryModel:
    def __init__(self):
        self.soc = 50.0 # State of Charge %
        self.capacity = config.BATTERY_CAPACITY # kWh

    def update(self, net_power_kw, dt_seconds):
        # net_power_kw: positive = charging, negative = discharging
        energy_delta_kwh = net_power_kw * (dt_seconds / 3600.0)
        
        # Update SoC
        new_energy = (self.soc / 100.0) * self.capacity + energy_delta_kwh
        new_energy = max(0.0, min(new_energy, self.capacity))
        
        self.soc = (new_energy / self.capacity) * 100.0
        return self.soc

class InverterModel:
    def __init__(self):
        self.status = 1 # 1=ON
        self.efficiency = 0.95

    def update(self, dc_power_in):
        if self.status == 1:
            return dc_power_in * self.efficiency
        return 0.0

class GridModel:
    def __init__(self):
        self.voltage = config.GRID_VOLTAGE_BASE
        self.frequency = config.GRID_FREQ_BASE
        self.export_limit = config.MAX_EXPORT_LIMIT

    def update(self, active_power_out):
        # Simulate grid stiffness - high export raises voltage slightly
        voltage_rise = (active_power_out / config.MAX_SOLAR_OUTPUT) * 5.0 # Max 5V rise
        self.voltage = config.GRID_VOLTAGE_BASE + voltage_rise + random.uniform(-1.0, 1.0)
        
        # Frequency noise
        self.frequency = config.GRID_FREQ_BASE + random.uniform(-0.05, 0.05)
        
        return self.voltage, self.frequency
