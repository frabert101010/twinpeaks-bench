// TwinPeaks Bench - Leaderboard JavaScript

let modelsData = [];
let currentMode = 'no-search';
let currentSort = { column: 'accuracy', ascending: false };

// Load data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    renderLeaderboard();
    renderChart();
    renderInsights();
    setupEventListeners();
});

// Load data from JSON
async function loadData() {
    try {
        const response = await fetch('data/summary.json');
        modelsData = await response.json();
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Render leaderboard table
function renderLeaderboard() {
    const tbody = document.getElementById('leaderboard-body');
    tbody.innerHTML = '';

    // Get data for current mode
    const data = getCurrentModeData();

    data.forEach((model, index) => {
        const row = document.createElement('tr');

        // Rank
        const rankCell = document.createElement('td');
        let rankEmoji = '';
        if (index === 0) rankEmoji = '🥇';
        else if (index === 1) rankEmoji = '🥈';
        else if (index === 2) rankEmoji = '🥉';
        else rankEmoji = `#${index + 1}`;

        const rankClass = index === 0 ? 'gold' : index === 1 ? 'silver' : index === 2 ? 'bronze' : '';
        rankCell.innerHTML = `<span class="rank ${rankClass}">${rankEmoji}</span>`;
        row.appendChild(rankCell);

        // Model
        const modelCell = document.createElement('td');
        modelCell.innerHTML = `<span class="model-name">${model.model}</span>`;
        row.appendChild(modelCell);

        // Accuracy
        const accuracyCell = document.createElement('td');
        const accuracyClass = getMetricClass(model.accuracy);
        accuracyCell.innerHTML = `<span class="metric ${accuracyClass}">${model.accuracy.toFixed(2)}%</span>`;
        row.appendChild(accuracyCell);

        // Pass@1
        const pass1Cell = document.createElement('td');
        const pass1Class = getMetricClass(model.pass1);
        pass1Cell.innerHTML = `<span class="metric ${pass1Class}">${model.pass1.toFixed(2)}%</span>`;
        row.appendChild(pass1Cell);

        // Pass@3
        const pass3Cell = document.createElement('td');
        const pass3Class = getMetricClass(model.pass3);
        pass3Cell.innerHTML = `<span class="metric ${pass3Class}">${model.pass3.toFixed(2)}%</span>`;
        row.appendChild(pass3Cell);

        tbody.appendChild(row);
    });
}

// Get current mode data
function getCurrentModeData() {
    const modeKey = currentMode === 'no-search' ? 'no_search' : 'with_search';

    return modelsData.map(model => ({
        model: model.model,
        accuracy: model[modeKey]?.accuracy || 0,
        pass1: model[modeKey]?.pass1 || 0,
        pass3: model[modeKey]?.pass3 || 0
    })).sort((a, b) => {
        const aVal = a[currentSort.column];
        const bVal = b[currentSort.column];

        if (currentSort.column === 'model') {
            return currentSort.ascending ?
                aVal.localeCompare(bVal) :
                bVal.localeCompare(aVal);
        }

        return currentSort.ascending ? aVal - bVal : bVal - aVal;
    });
}

// Get metric color class
function getMetricClass(value) {
    if (value >= 70) return 'high';
    if (value >= 50) return 'medium';
    return 'low';
}

// Render performance chart
function renderChart() {
    const chart = document.getElementById('performance-chart');
    chart.innerHTML = '';

    const data = getCurrentModeData();

    data.forEach(model => {
        const barDiv = document.createElement('div');
        barDiv.className = 'chart-bar';

        barDiv.innerHTML = `
            <div class="chart-label">${model.model}</div>
            <div class="chart-bar-container">
                <div class="chart-bar-fill" style="width: ${model.accuracy}%">
                    <span class="chart-value">${model.accuracy.toFixed(1)}%</span>
                </div>
            </div>
        `;

        chart.appendChild(barDiv);
    });

    // Animate bars
    setTimeout(() => {
        document.querySelectorAll('.chart-bar-fill').forEach(bar => {
            bar.style.width = bar.style.width;
        });
    }, 100);
}

// Render insights
function renderInsights() {
    const insightsDiv = document.getElementById('insights');
    insightsDiv.innerHTML = '';

    const data = getCurrentModeData();

    // Best model
    const best = data[0];
    insightsDiv.innerHTML += `
        <div class="insight-card">
            <h4>🏆 Top Performer</h4>
            <p><strong>${best.model}</strong> leads with ${best.accuracy.toFixed(2)}% accuracy${currentMode === 'with-search' ? ' (with search)' : ''}.</p>
        </div>
    `;

    // Average
    const avg = data.reduce((sum, m) => sum + m.accuracy, 0) / data.length;
    insightsDiv.innerHTML += `
        <div class="insight-card">
            <h4>📊 Average Performance</h4>
            <p>Models achieve an average accuracy of ${avg.toFixed(2)}% ${currentMode === 'no-search' ? 'without search capabilities' : 'with search enabled'}.</p>
        </div>
    `;

    // Search improvement (if with-search mode)
    if (currentMode === 'with-search') {
        const improvements = modelsData.map(model => {
            const noSearch = model.no_search?.accuracy || 0;
            const withSearch = model.with_search?.accuracy || 0;
            return withSearch - noSearch;
        });
        const avgImprovement = improvements.reduce((sum, val) => sum + val, 0) / improvements.length;

        insightsDiv.innerHTML += `
            <div class="insight-card">
                <h4>📈 Search Impact</h4>
                <p>Search capabilities improve performance by an average of ${avgImprovement.toFixed(2)} percentage points.</p>
            </div>
        `;
    }
}

// Setup event listeners
function setupEventListeners() {
    // Mode toggle
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            renderLeaderboard();
            renderChart();
            renderInsights();
        });
    });

    // Sortable columns
    document.querySelectorAll('.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const column = th.dataset.sort;

            // Toggle sort direction
            if (currentSort.column === column) {
                currentSort.ascending = !currentSort.ascending;
            } else {
                currentSort.column = column;
                currentSort.ascending = false;
            }

            // Update UI
            document.querySelectorAll('.sortable').forEach(header => {
                header.classList.remove('active', 'asc', 'desc');
                header.querySelector('.sort-icon').textContent = '';
            });

            th.classList.add('active');
            th.classList.add(currentSort.ascending ? 'asc' : 'desc');
            th.querySelector('.sort-icon').textContent = currentSort.ascending ? '▲' : '▼';

            renderLeaderboard();
        });
    });
}
