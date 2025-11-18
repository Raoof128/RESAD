import pytest
from simulation.solar_model import SolarModel, BatteryModel, InverterModel, GridModel
from simulation import config

def test_battery_charging():
    battery = BatteryModel()
    initial_soc = battery.soc
    
    # Charge for 1 hour at 100kW
    # Capacity is 1000kWh. 100kWh added = +10% SoC
    battery.update(100.0, 3600)
    
    assert battery.soc > initial_soc
    assert battery.soc == pytest.approx(initial_soc + 10.0, 0.1)

def test_battery_limits():
    battery = BatteryModel()
    battery.soc = 99.0
    
    # Charge massive amount
    battery.update(1000.0, 3600)
    
    assert battery.soc == 100.0 # Should cap at 100

def test_inverter_efficiency():
    inv = InverterModel()
    inv.status = 1
    inv.efficiency = 0.95
    
    output = inv.update(100.0)
    assert output == 95.0

def test_inverter_off():
    inv = InverterModel()
    inv.status = 0
    output = inv.update(100.0)
    assert output == 0.0
