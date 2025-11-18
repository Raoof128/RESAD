# Blue Team Playbook

## Mission
Detect, Analyze, and Respond to cyber threats targeting the Solar Farm SCADA system.

## 1. Detection (IDS)
The lab includes a custom Intrusion Detection System (`defender/ids.py`).

**Running the IDS:**
```bash
python defender/ids.py
```
*Or via Docker:*
```bash
docker-compose logs -f ids
```

**Signatures:**
- **Sabotage**: Checks if `Export Limit == 0` while `Solar Output > 50`.
- **Grid Instability**: Checks if `Grid Frequency` deviates > 2Hz from 50Hz.
- **Physics Violation**: Checks if `Solar Output` > `Max Capacity`.

**Logs:**
Events are logged to `ids_events.json` in JSON format for SIEM ingestion.
```json
{"timestamp": "2023-11-19T10:00:00", "level": "WARNING", "message": "ALERT: Suspicious Export Limit...", "module": "IDS"}
```

## 2. Monitoring (HMI)
The HMI (`http://localhost:8000`) is your primary pane of glass.
- **Visual Indicators**: Look for the "Alerts" box turning red.
- **Trend Analysis**: Use the real-time graph to spot sudden drops (DoS) or spikes (Injection).

## 3. Response & Mitigation

### Immediate Actions
1.  **Verify**: Confirm the anomaly on the HMI.
2.  **Contain**:
    - **Enable Defence Mode**: Toggle "DEFENCE MODE" on the HMI dashboard.
    - **Effect**: The PLC will automatically revert unauthorized changes to critical setpoints (e.g., Export Limit).
3.  **Recover**:
    - Manually reset setpoints via HMI controls.
    - Restart the PLC if logic is corrupted.

### Forensics
Analyze `ids_events.json` to determine:
- **Time of Attack**: When did the value change?
- **Nature of Attack**: Was it a write command (DoS) or data injection?
