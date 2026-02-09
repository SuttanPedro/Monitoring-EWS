// Global variables
let waterHeightChart, rainfallChart, windSpeedChart, alertChart;
const maxDataPoints = 50;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadLatestData();
    loadHistoryData();
    loadSettings();
    loadStats();
    initCharts();
    
    // Auto-refresh every 5 seconds
    setInterval(loadLatestData, 5000);
    setInterval(loadHistoryData, 10000);
    setInterval(loadStats, 15000);
});

// Load latest sensor data
function loadLatestData() {
    fetch('/api/data/latest')
        .then(response => response.json())
        .then(data => {
            if (data.error) return;
            
            // Update cards
            document.getElementById('waterHeight').textContent = data.water_height.toFixed(1);
            document.getElementById('rainfall').textContent = data.rainfall.toFixed(1);
            document.getElementById('windSpeed').textContent = data.wind_speed.toFixed(1);
            
            // Format timestamp
            const timestamp = new Date(data.timestamp);
            document.getElementById('updateTime').textContent = timestamp.toLocaleTimeString('id-ID');
            
            // Update alert box
            updateAlertBox(data.alert_status);
        })
        .catch(error => console.error('Error loading latest data:', error));
}

// Load historical data
function loadHistoryData() {
    fetch('/api/data/history?limit=100')
        .then(response => response.json())
        .then(data => {
            if (!data || data.error) return;
            
            // Limit to maxDataPoints for chart performance
            const limitedData = data.slice(-maxDataPoints);
            
            // Update charts
            updateCharts(limitedData);
            
            // Update table
            updateTable(data);
        })
        .catch(error => console.error('Error loading history:', error));
}

// Load settings
function loadSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(data => {
            if (data.error) return;
            
            document.getElementById('waterThreshold').textContent = 
                `Ambang: ${data.water_height_threshold.toFixed(1)} cm`;
            document.getElementById('rainfallThreshold').textContent = 
                `Ambang: ${data.rainfall_threshold.toFixed(1)} mm`;
            document.getElementById('windThreshold').textContent = 
                `Ambang: ${data.wind_speed_threshold.toFixed(1)} km/h`;
            
            // Update input fields
            document.getElementById('waterThresholdInput').value = data.water_height_threshold;
            document.getElementById('rainfallThresholdInput').value = data.rainfall_threshold;
            document.getElementById('windThresholdInput').value = data.wind_speed_threshold;
        })
        .catch(error => console.error('Error loading settings:', error));
}

// Load statistics
function loadStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.error) return;
            
            // Water Height
            document.getElementById('statWaterAvg').textContent = 
                (data.water_height.avg || 0).toFixed(1) + ' cm';
            document.getElementById('statWaterMax').textContent = 
                (data.water_height.max || 0).toFixed(1) + ' cm';
            document.getElementById('statWaterMin').textContent = 
                (data.water_height.min || 0).toFixed(1) + ' cm';
            
            // Rainfall
            document.getElementById('statRainfallAvg').textContent = 
                (data.rainfall.avg || 0).toFixed(1) + ' mm';
            document.getElementById('statRainfallMax').textContent = 
                (data.rainfall.max || 0).toFixed(1) + ' mm';
            document.getElementById('statRainfallMin').textContent = 
                (data.rainfall.min || 0).toFixed(1) + ' mm';
            
            // Wind Speed
            document.getElementById('statWindAvg').textContent = 
                (data.wind_speed.avg || 0).toFixed(1) + ' km/h';
            document.getElementById('statWindMax').textContent = 
                (data.wind_speed.max || 0).toFixed(1) + ' km/h';
            document.getElementById('statWindMin').textContent = 
                (data.wind_speed.min || 0).toFixed(1) + ' km/h';
            
            // Alert Summary
            document.getElementById('statTotalRecords').textContent = data.total_records || 0;
            document.getElementById('statEmergency').textContent = data.emergency_count || 0;
            document.getElementById('statWarning').textContent = data.warning_count || 0;
        })
        .catch(error => console.error('Error loading stats:', error));
}

// Update alert box
function updateAlertBox(status) {
    const alertBox = document.getElementById('alertBox');
    const alertMessages = {
        'NORMAL': {
            icon: 'fa-check-circle',
            title: 'Status Normal',
            message: 'Semua parameter dalam kondisi aman'
        },
        'ALERT': {
            icon: 'fa-exclamation-circle',
            title: 'Peringatan',
            message: 'Ada indikasi kondisi mulai meningkat'
        },
        'WARNING': {
            icon: 'fa-exclamation-triangle',
            title: 'Peringatan Tinggi',
            message: 'Kondisi bahaya, bersiaplah untuk mengambil tindakan'
        },
        'EMERGENCY': {
            icon: 'fa-times-circle',
            title: 'KEADAAN DARURAT',
            message: 'BANJIR AKAN SEGERA TERJADI! SEGERA EVAKUASI!'
        }
    };
    
    const msg = alertMessages[status] || alertMessages['NORMAL'];
    
    alertBox.className = `alert-box ${status.toLowerCase()}`;
    alertBox.innerHTML = `
        <div class="alert-icon">
            <i class="fas ${msg.icon}"></i>
        </div>
        <div class="alert-content">
            <h2>${msg.title}</h2>
            <p>${msg.message}</p>
        </div>
    `;
    
    // Add sound alert for emergency
    if (status === 'EMERGENCY') {
        playAlert();
    }
}

// Play alert sound
function playAlert() {
    // Create simple beep sound using Web Audio API
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 1000;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

// Initialize charts
function initCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                labels: {
                    usePointStyle: true,
                    padding: 15
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
    
    // Water Height Chart
    const waterHeightCtx = document.getElementById('waterHeightChart').getContext('2d');
    waterHeightChart = new Chart(waterHeightCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Ketinggian Air (cm)',
                data: [],
                borderColor: '#0288d1',
                backgroundColor: 'rgba(2, 136, 209, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointBackgroundColor: '#0288d1'
            }]
        },
        options: chartOptions
    });
    
    // Rainfall Chart
    const rainfallCtx = document.getElementById('rainfallChart').getContext('2d');
    rainfallChart = new Chart(rainfallCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Curah Hujan (mm)',
                data: [],
                backgroundColor: '#388e3c',
                borderColor: '#2e7d32',
                borderWidth: 1
            }]
        },
        options: chartOptions
    });
    
    // Wind Speed Chart
    const windSpeedCtx = document.getElementById('windSpeedChart').getContext('2d');
    windSpeedChart = new Chart(windSpeedCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Kecepatan Angin (km/h)',
                data: [],
                borderColor: '#7b1fa2',
                backgroundColor: 'rgba(123, 31, 162, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointBackgroundColor: '#7b1fa2'
            }]
        },
        options: chartOptions
    });
    
    // Alert Status Chart
    const alertCtx = document.getElementById('alertChart').getContext('2d');
    alertChart = new Chart(alertCtx, {
        type: 'doughnut',
        data: {
            labels: ['Normal', 'Alert', 'Warning', 'Emergency'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#388e3c',
                    '#f57f17',
                    '#f57f17',
                    '#d32f2f'
                ],
                borderColor: 'white',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Update charts with new data
function updateCharts(data) {
    if (!data || data.length === 0) return;
    
    // Prepare labels
    const labels = data.map(d => {
        const date = new Date(d.timestamp);
        return date.toLocaleTimeString('id-ID', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
    });
    
    const waterHeights = data.map(d => d.water_height);
    const rainfalls = data.map(d => d.rainfall);
    const windSpeeds = data.map(d => d.wind_speed);
    
    // Update Water Height Chart
    waterHeightChart.data.labels = labels;
    waterHeightChart.data.datasets[0].data = waterHeights;
    waterHeightChart.update();
    
    // Update Rainfall Chart
    rainfallChart.data.labels = labels;
    rainfallChart.data.datasets[0].data = rainfalls;
    rainfallChart.update();
    
    // Update Wind Speed Chart
    windSpeedChart.data.labels = labels;
    windSpeedChart.data.datasets[0].data = windSpeeds;
    windSpeedChart.update();
    
    // Update Alert Status Chart
    const statusCounts = {
        NORMAL: 0,
        ALERT: 0,
        WARNING: 0,
        EMERGENCY: 0
    };
    
    data.forEach(d => {
        statusCounts[d.alert_status]++;
    });
    
    alertChart.data.datasets[0].data = [
        statusCounts.NORMAL,
        statusCounts.ALERT,
        statusCounts.WARNING,
        statusCounts.EMERGENCY
    ];
    alertChart.update();
}

// Update data table
function updateTable(data) {
    const tbody = document.getElementById('dataTableBody');
    
    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Tidak ada data</td></tr>';
        return;
    }
    
    let html = '';
    data.reverse().forEach((row, index) => {
        const timestamp = new Date(row.timestamp);
        const formattedTime = timestamp.toLocaleString('id-ID');
        
        let statusClass = 'status-' + row.alert_status.toLowerCase();
        
        html += `
            <tr>
                <td>${index + 1}</td>
                <td>${formattedTime}</td>
                <td>${row.water_height.toFixed(1)}</td>
                <td>${row.rainfall.toFixed(1)}</td>
                <td>${row.wind_speed.toFixed(1)}</td>
                <td><span class="${statusClass}">${translateStatus(row.alert_status)}</span></td>
            </tr>
        `;
    });
    
    tbody.innerHTML = html;
}

// Translate status
function translateStatus(status) {
    const translations = {
        'NORMAL': 'Normal',
        'ALERT': 'Peringatan',
        'WARNING': 'Peringatan Tinggi',
        'EMERGENCY': 'DARURAT'
    };
    return translations[status] || status;
}

// Update settings
function updateSettings() {
    const waterThreshold = parseFloat(document.getElementById('waterThresholdInput').value);
    const rainfallThreshold = parseFloat(document.getElementById('rainfallThresholdInput').value);
    const windThreshold = parseFloat(document.getElementById('windThresholdInput').value);
    
    if (isNaN(waterThreshold) || isNaN(rainfallThreshold) || isNaN(windThreshold)) {
        alert('Mohon isi semua nilai dengan angka yang valid');
        return;
    }
    
    fetch('/api/settings/update', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            water_height_threshold: waterThreshold,
            rainfall_threshold: rainfallThreshold,
            wind_speed_threshold: windThreshold
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Pengaturan berhasil disimpan!');
            loadSettings();
        } else {
            alert('Gagal menyimpan pengaturan');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Terjadi kesalahan saat menyimpan pengaturan');
    });
}

// Export to Excel
function exportToExcel() {
    window.location.href = '/api/export/excel';
}

// Export to PDF
function exportToPDF() {
    window.location.href = '/api/export/pdf';
}

// Manual data input for testing (optional)
function addTestData() {
    const testData = {
        water_height: Math.random() * 100,
        rainfall: Math.random() * 150,
        wind_speed: Math.random() * 50
    };
    
    fetch('/api/data/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadLatestData();
            loadHistoryData();
        }
    })
    .catch(error => console.error('Error:', error));
}
