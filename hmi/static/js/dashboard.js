// Chart Configuration
const ctx = document.getElementById('powerChart').getContext('2d');
const powerChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Solar Output (kW)',
            borderColor: '#38bdf8',
            backgroundColor: 'rgba(56, 189, 248, 0.1)',
            data: [],
            fill: true,
            tension: 0.4
        }, {
            label: 'Grid Export (kW)',
            borderColor: '#4ade80',
            backgroundColor: 'rgba(74, 222, 128, 0.1)',
            data: [],
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { labels: { color: '#94a3b8' } }
        },
        scales: {
            y: {
                grid: { color: '#334155' },
                ticks: { color: '#94a3b8' }
            },
            x: {
                grid: { display: false },
                ticks: { display: false } // Hide time labels for cleaner look
            }
        },
        animation: false
    }
});

// WebSocket Connection
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/ws/metrics`);

const MAX_DATA_POINTS = 50;

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.error) {
        console.error(data.error);
        return;
    }

    // Update KPIs
    document.getElementById('val-solar').innerText = data.solar_output.toFixed(1);
    document.getElementById('val-active').innerText = data.active_power.toFixed(1);
    document.getElementById('val-soc').innerText = data.battery_soc;
    document.getElementById('bar-soc').style.width = `${data.battery_soc}%`;
    document.getElementById('val-freq').innerText = data.grid_freq.toFixed(2);
    document.getElementById('val-export-limit').innerText = data.export_limit;

    // Update Inverter Status
    const invStatus = document.getElementById('val-inverter-status');
    if (data.inverter_status === 1) {
        invStatus.innerText = "ONLINE";
        invStatus.className = "font-bold status-on";
    } else if (data.inverter_status === 0) {
        invStatus.innerText = "OFFLINE";
        invStatus.className = "font-bold status-off";
    } else {
        invStatus.innerText = "FAULT";
        invStatus.className = "font-bold text-yellow-500";
    }

    // Update Defence Status
    const defStatus = document.getElementById('defence-status');
    if (data.defence_mode) {
        defStatus.innerText = "ACTIVE";
        defStatus.className = "font-bold text-blue-400 cursor-pointer hover:text-blue-300";
    } else {
        defStatus.innerText = "OFF";
        defStatus.className = "font-bold text-slate-500 cursor-pointer hover:text-slate-300";
    }

    // Update Chart
    const now = new Date().toLocaleTimeString();
    powerChart.data.labels.push(now);
    powerChart.data.datasets[0].data.push(data.solar_output);
    powerChart.data.datasets[1].data.push(data.active_power);

    if (powerChart.data.labels.length > MAX_DATA_POINTS) {
        powerChart.data.labels.shift();
        powerChart.data.datasets[0].data.shift();
        powerChart.data.datasets[1].data.shift();
    }
    powerChart.update();

    // Check for anomalies (Simple frontend logic for demo)
    checkAlerts(data);
};

function checkAlerts(data) {
    const container = document.getElementById('alerts-container');
    let alerts = [];

    if (data.grid_freq > 50.5 || data.grid_freq < 49.5) {
        alerts.push("CRITICAL: Grid Frequency Instability Detected");
    }
    if (data.export_limit === 0 && data.solar_output > 10) {
        alerts.push("WARNING: Export Limit Unexpectedly Zero");
    }

    if (alerts.length > 0) {
        container.innerHTML = alerts.map(a => `<div class="mb-1">🔥 ${a}</div>`).join('');
    } else {
        container.innerHTML = "No active alerts.";
    }
}

// Control Functions
async function controlInverter(enable) {
    await fetch('/api/control/inverter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enable: enable })
    });
    logEvent(`User sent Inverter ${enable ? 'START' : 'STOP'} command`);
}

async function setExportLimit() {
    const val = document.getElementById('input-export-limit').value;
    if (!val) return;
    await fetch('/api/control/export_limit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ limit: val })
    });
    logEvent(`User set Export Limit to ${val} kW`);
}

function logEvent(msg) {
    const log = document.getElementById('event-log');
    const entry = document.createElement('div');
    entry.innerText = `[${new Date().toLocaleTimeString()}] ${msg}`;
    log.prepend(entry);
}

async function toggleDefence() {
    // We don't know current state easily without a global var, but the UI update will handle it.
    // For now, let's just assume we want to toggle. 
    // Actually, better to read the current visual state.
    const currentText = document.getElementById('defence-status').innerText;
    const newState = currentText === 'OFF'; // If OFF, we want to turn ON

    await fetch('/api/control/defence', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enable: newState })
    });
    logEvent(`User toggled Defence Mode to ${newState ? 'ON' : 'OFF'}`);
}
