# Red Team Playbook

## Mission
Demonstrate the fragility of unauthenticated ICS protocols (Modbus TCP) and the impact of cyber-physical attacks on renewable energy infrastructure.

## Tools
All tools are located in the `attacker/` directory.

### 1. Reconnaissance
**Objective**: Identify the target and map its memory map (registers).
**Technique**: Modbus Function Code Scanning.
**Script**: `attacker/recon.py`
```bash
python attacker/recon.py
```
**Expected Output**: List of active Holding Registers and their current values. Look for values that change (Solar Output) vs static configuration (Export Limit).

### 2. Denial of Service (DoS) - Export Limiting
**Objective**: Cause financial loss by curtailing power generation.
**Technique**: Unauthorized Write to Setpoint (Register 3).
**Script**: `attacker/write_attack.py`
```bash
python attacker/write_attack.py
```
**Impact**:
- HMI "Export Limit" drops to 0.
- Active Power drops to 0.
- Revenue generation stops.

### 3. False Data Injection (Replay)
**Objective**: Confuse operators or automated control loops.
**Technique**: Injecting previously recorded "high noon" values during low-light conditions.
**Script**: `attacker/replay_attack.py`
```bash
python attacker/replay_attack.py
```
**Impact**:
- HMI shows high solar output despite actual conditions.
- Battery might misbehave (charging when it should discharge).

### 4. Man-in-the-Middle (MITM) Simulation
**Objective**: Mask an attack or trigger false alarms.
**Technique**: Overwriting read values to spoof sensor data.
**Script**: `attacker/mitm_sim.py`
```bash
python attacker/mitm_sim.py
```
**Impact**:
- Grid Voltage on HMI spikes erratically.
- May trigger automatic safety disconnects if logic was implemented.

## Advanced Manual Attacks
You can use standard tools like `metasploit` or `mbtget` against the lab.

**Read Registers:**
```bash
# Read 10 registers starting at 0
mbtget -r -a 0 -n 10 localhost
```

**Write Register:**
```bash
# Write value 0 to register 3
mbtget -w6 -a 3 0 localhost
```
