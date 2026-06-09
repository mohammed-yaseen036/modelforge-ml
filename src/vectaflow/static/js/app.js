// --- API HELPERS ---
const api = {
    async get(url) {
        const response = await fetch(url);
        return response.json();
    },
    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
};

// --- CONSOLE LOGGER ---
function appendLog(message, type = 'INFO') {
    const consoleLogs = document.getElementById('console-logs');
    if (!consoleLogs) return;

    const time = new Date().toLocaleTimeString();
    let prefix = `[${time}] [${type}] `;
    
    // Style console logs by type
    if (type === 'SUCCESS') {
        prefix = `[${time}] \u2713 `;
    } else if (type === 'ERROR') {
        prefix = `[${time}] \u26A0 [ERROR] `;
    } else if (type === 'SYSTEM') {
        prefix = `[${time}] \u2699 [SYSTEM] `;
    }

    const currentLogs = consoleLogs.innerText;
    consoleLogs.innerText = currentLogs + `\n${prefix}${message}`;
    consoleLogs.scrollTop = consoleLogs.scrollHeight;
}

// --- TOAST NOTIFICATION ---
function showToast(message) {
    const toast = document.getElementById('toast-notif');
    document.getElementById('toast-message').innerText = message;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// --- CHARTS INSTANCES ---
let revenueChart, timelineChart, demandChart, banditChart, miniPriceChart;

// --- INITIALIZE ALL CHARTS ---
function initCharts() {
    // 1. Revenue Chart
    revenueChart = new Chart(document.getElementById('revenueChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'Vectaflow TS Agent (Dynamic)', borderColor: '#06b6d4', backgroundColor: 'rgba(6, 182, 212, 0.05)', data: [], borderWidth: 3, tension: 0.15, fill: true },
                { label: 'Static Low Price ($24.99)', borderColor: '#ef4444', borderDash: [5, 5], data: [], borderWidth: 1.5, fill: false },
                { label: 'Static Mid Price ($34.99)', borderColor: '#fbbf24', borderDash: [5, 5], data: [], borderWidth: 1.5, fill: false },
                { label: 'Static High Price ($44.99)', borderColor: '#10b981', borderDash: [5, 5], data: [], borderWidth: 1.5, fill: false }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af' } },
                y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af', callback: v => '$' + v } }
            },
            plugins: { legend: { labels: { color: '#f3f4f6' } } }
        }
    });

    // 2. Timeline Chart
    timelineChart = new Chart(document.getElementById('timelineChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'Our Price', borderColor: '#6366f1', data: [], borderWidth: 2, tension: 0.2 },
                { label: 'Competitor Price', borderColor: '#a855f7', borderDash: [3, 3], data: [], borderWidth: 1.5, tension: 0.2 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af' } },
                y: { grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af', callback: v => '$' + v } }
            },
            plugins: { legend: { labels: { color: '#f3f4f6' } } }
        }
    });

    // 3. Demand Curve + Elasticity Chart
    demandChart = new Chart(document.getElementById('demandChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                { label: 'True Demand Curve', borderColor: 'rgba(255,255,255,0.25)', borderDash: [4, 4], data: [], borderWidth: 1.5, tension: 0.2 },
                { label: 'Fitted Demand (SGD)', borderColor: '#06b6d4', data: [], borderWidth: 2.5, tension: 0.2 },
                { label: 'Elasticity (\u03B5)', borderColor: '#f43f5e', data: [], borderWidth: 2, yAxisID: 'yElasticity', tension: 0.2 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { type: 'linear', position: 'bottom', title: { display: true, text: 'Price ($)', color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af' } },
                y: { position: 'left', title: { display: true, text: 'Conversion Rate', color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af' }, min: 0, max: 1 },
                yElasticity: { position: 'right', title: { display: true, text: 'Elasticity', color: '#f43f5e' }, grid: { drawOnChartArea: false }, ticks: { color: '#f43f5e' } }
            },
            plugins: { legend: { labels: { color: '#f3f4f6' } } }
        }
    });

    // 4. Bandit PDF Chart
    banditChart = new Chart(document.getElementById('banditChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { type: 'linear', position: 'bottom', title: { display: true, text: 'Conversion Probability', color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.03)' }, ticks: { color: '#9ca3af' }, min: 0, max: 1 },
                y: { display: false }
            },
            plugins: { legend: { labels: { color: '#f3f4f6' } } }
        }
    });

    // 5. Mini Widget Chart
    miniPriceChart = new Chart(document.getElementById('miniPriceChart'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{ label: 'Price History', borderColor: '#22d3ee', data: [], borderWidth: 2, tension: 0.1, fill: false, pointRadius: 1.5 }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { display: false },
                y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { font: { size: 8 }, color: '#22d3ee' } }
            },
            plugins: { legend: { display: false } }
        }
    });
}

// --- UPDATE DASHBOARD UI ---
async function updateDashboard(isInitial = false) {
    const config = await api.get('/api/config');
    document.getElementById('current-day-text').innerText = config.current_day;
    document.getElementById('arms-display').innerText = config.price_arms.map(p => `$${p}`).join(', ');
    
    const analytics = await api.get('/api/analytics');
    
    const history = analytics.cumulative_revenues.agent;
    const currentRevenue = history.length > 0 ? history[history.length - 1] : 0.0;
    document.getElementById('kpi-revenue').innerText = `$${currentRevenue.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    
    const medHist = analytics.cumulative_revenues.med_baseline;
    const medRevenue = medHist.length > 0 ? medHist[medHist.length - 1] : 0.0;
    if (medRevenue > 0) {
        const lift = ((currentRevenue - medRevenue) / medRevenue) * 100;
        const sign = lift >= 0 ? '+' : '';
        document.getElementById('kpi-revenue-lift').innerText = `${sign}${lift.toFixed(1)}% vs Static Mid Baseline`;
        document.getElementById('kpi-revenue-lift').className = `kpi-change ${lift >= 0 ? 'positive' : 'neutral'}`;
    } else {
        document.getElementById('kpi-revenue-lift').innerText = 'Starting baseline comparison';
        document.getElementById('kpi-revenue-lift').className = 'kpi-change neutral';
    }

    const totalVisits = analytics.agent_stats.reduce((acc, curr) => acc + curr.pulls, 0) + analytics.manual_stats.clicks;
    const totalConversions = analytics.agent_stats.reduce((acc, curr) => acc + curr.conversions, 0) + analytics.manual_stats.purchases;
    const avgConversion = totalVisits > 0 ? (totalConversions / totalVisits) * 100 : 0.0;
    document.getElementById('kpi-conversion').innerText = `${avgConversion.toFixed(1)}%`;
    document.getElementById('kpi-total-sales').innerText = `${totalConversions} sales / ${totalVisits} visits`;

    // Extract current offered price
    const currentPrice = config.current_day > 0 ? config.price_arms[analytics.agent_stats.reduce((maxIdx, current, idx, arr) => current.pulls > arr[maxIdx].pulls ? idx : maxIdx, 0)] : 29.99;
    document.getElementById('kpi-active-price').innerText = `$${currentPrice}`;
    document.getElementById('kpi-competitor-price').innerText = `Competitor: $${config.competitor_price.toFixed(2)}`;
    document.getElementById('store-price-text').innerText = `$${currentPrice}`;

    document.getElementById('kpi-inventory').innerText = config.inventory.toLocaleString();
    const invPct = (config.inventory / config.initial_inventory) * 100 || 100;
    document.getElementById('kpi-inventory-pct').innerText = `${invPct.toFixed(1)}% remaining`;

    document.getElementById('manual-clicks-text').innerText = analytics.manual_stats.clicks;
    document.getElementById('manual-buys-text').innerText = analytics.manual_stats.purchases;

    // --- RENDER DYNAMIC PRICING SUGGESTION ---
    const recommenderEl = document.getElementById('recommender-suggestion');
    const elasticityValues = analytics.elasticity_curve.values;
    
    // Check if the model has actually been fitted (SGD weights non-trivial)
    // We can infer fitting if there is transaction history (>10 logs)
    const totalHistoryLogs = totalVisits;
    if (totalHistoryLogs <= 10) {
        recommenderEl.innerHTML = `Model training in progress (${totalHistoryLogs}/11 samples). Need more simulation steps to establish price elasticity.`;
        recommenderEl.style.borderLeftColor = 'var(--text-muted)';
    } else {
        const prices = analytics.elasticity_curve.prices;
        let closestIdx = 0;
        let minDiff = Infinity;
        for (let i = 0; i < prices.length; i++) {
            const diff = Math.abs(prices[i] - currentPrice);
            if (diff < minDiff) {
                minDiff = diff;
                closestIdx = i;
            }
        }
        const currentElasticity = elasticityValues[closestIdx];
        
        if (currentElasticity < -1.0) {
            recommenderEl.innerHTML = `<strong>Elastic Demand (\u03B5 = ${currentElasticity.toFixed(2)}):</strong> At the current price of $${currentPrice.toFixed(2)}, consumers are highly price-sensitive. <strong>Action:</strong> Lowering prices is advised to stimulate volume, which will net higher total revenue yield.`;
            recommenderEl.style.borderLeftColor = 'var(--accent-cyan)';
        } else if (currentElasticity >= -1.0 && currentElasticity < 0.0) {
            recommenderEl.innerHTML = `<strong>Inelastic Demand (\u03B5 = ${currentElasticity.toFixed(2)}):</strong> At the current price of $${currentPrice.toFixed(2)}, consumers are relatively price-insensitive. <strong>Action:</strong> Raising prices is advised. Margins will expand significantly, yielding higher total revenue despite a minor dip in sales volume.`;
            recommenderEl.style.borderLeftColor = 'var(--warning)';
        } else {
            recommenderEl.innerHTML = `<strong>Unstable Elasticity Reading (\u03B5 = ${currentElasticity.toFixed(2)}):</strong> Positively correlated demand indicates sparse price exploration or consumer bias. <strong>Action:</strong> Run more simulation cycles or reset parameters to stabilize SGD model weights.`;
            recommenderEl.style.borderLeftColor = 'var(--error)';
        }
    }

    // --- RENDER CHARTS ---
    const daysLabels = Array.from({ length: history.length }, (_, i) => `Day ${i + 1}`);

    revenueChart.data.labels = daysLabels;
    revenueChart.data.datasets[0].data = analytics.cumulative_revenues.agent;
    revenueChart.data.datasets[1].data = analytics.cumulative_revenues.low_baseline;
    revenueChart.data.datasets[2].data = analytics.cumulative_revenues.med_baseline;
    revenueChart.data.datasets[3].data = analytics.cumulative_revenues.high_baseline;
    revenueChart.update();

    // Load actual prices history from simulation history logs
    const hasHistory = history.length > 0;
    
    // We can simulate fetching timeline price from server or compute active price sequence
    // To make this fully complete, we can query state from simulator records
    // Let's compute historical prices offered in each day
    // We will build a dummy list for timelineChart datasets if we don't fetch it explicitly
    // In backend step endpoint, simulator.history is updated, let's look at get_analytics
    // Actually, let's query analytics which provides expected revenues and pulls.
    // Wait, the API endpoint '/api/run_all' returns state.simulator.history.
    // Let's call another helper if necessary, or just read from local storage or cached states.
    // Wait! Let's check how the original code populated the timelineChart:
    // It did: config.current_day > 0 && i < config.current_day ? state.simulator.history[i].our_price : 0.0
    // Wait, the original code had access to `state` inside `get_dashboard()` template string because it was running on the server!
    // But since this is a decoupled static JavaScript file, `state` is NOT defined in the client!
    // Oh, that's a huge bug in the original code's Javascript! The original code tried to access `state.simulator.history` in the client script block, which would raise `ReferenceError: state is not defined`!
    // Let's verify: indeed, line 1124 in `app.py`:
    // `state.simulator.history[i].our_price`
    // Yes! `state` is a python variable in the backend, but the javascript code was trying to evaluate it!
    // That means the original client-side dashboard timeline chart was completely broken!
    // We can fix this by returning the timeline history list inside the `/api/analytics` response, or inside `/api/config` response!
    // Let's check our backend implementation of `get_analytics`:
    // In our new `app.py`, we return `cumulative_revenues` and `agent_stats`, but we don't return the full history list in `/api/analytics`.
    // Wait! Let's modify `get_analytics` or return `history` as part of `get_analytics`!
    // Yes, returning `history: state.simulator.history` in `/api/analytics` is extremely clean, and allows us to plot both the offered prices and competitor prices correctly in the client without reference errors!
    // Let's see: we should make sure we return `history` in `/api/analytics`. Let's check what we returned in `/api/analytics` in the new `app.py`:
    // We returned: `cumulative_revenues`, `agent_stats`, `manual_stats`, `true_demand_curve`, etc.
    // Let's check if we can add `"history": state.simulator.history` to `/api/analytics`.
    // Let's write down the timelineChart updating logic assuming we add `"history": history_data` to `/api/analytics`.
    // We can extract `our_price` and `competitor_price` from `analytics.history` directly!
    // That is incredibly clean and fixes the client-side `ReferenceError` bug!

    const historyData = analytics.history || [];
    timelineChart.data.labels = daysLabels;
    timelineChart.data.datasets[0].data = historyData.map(day => day.our_price);
    timelineChart.data.datasets[1].data = historyData.map(day => day.competitor_price);
    timelineChart.update();

    const prices = analytics.true_demand_curve.prices;
    demandChart.data.datasets[0].data = prices.map((p, i) => ({ x: p, y: analytics.true_demand_curve.rates[i] }));
    demandChart.data.datasets[1].data = prices.map((p, i) => ({ x: p, y: analytics.fitted_demand_curve.rates[i] }));
    demandChart.data.datasets[2].data = prices.map((p, i) => ({ x: p, y: analytics.elasticity_curve.values[i] }));
    demandChart.update();

    const colorPalettes = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e', '#10b981'];
    banditChart.data.datasets = analytics.beta_pdfs.map((pdf, idx) => {
        return {
            label: `$${pdf.price}`,
            borderColor: colorPalettes[idx % colorPalettes.length],
            data: pdf.x.map((xVal, i) => ({ x: xVal, y: pdf.y[i] })),
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.2,
            fill: false
        };
    });
    banditChart.update();

    const activePrices = historyData.map(day => day.our_price);
    if (activePrices.length === 0) activePrices.push(29.99);
    miniPriceChart.data.labels = Array.from({ length: activePrices.length }, (_, i) => i + 1);
    miniPriceChart.data.datasets[0].data = activePrices;
    miniPriceChart.update();

    const buyhatkeBox = document.getElementById('buyhatke-rec-box');
    const buyhatkeText = document.getElementById('buyhatke-signal-text');
    
    if (activePrices.length < 2) {
        buyhatkeBox.className = "buyhatke-recommendation";
        buyhatkeText.innerText = "ACCUMULATING PRICE TRENDS...";
    } else {
        const avgPrice = activePrices.reduce((a, b) => a + b, 0) / activePrices.length;
        const lastPrice = activePrices[activePrices.length - 1];
        
        if (lastPrice <= avgPrice * 0.95) {
            buyhatkeBox.className = "buyhatke-recommendation";
            buyhatkeText.innerText = "GREAT PRICE - BUY NOW!";
            buyhatkeBox.style.backgroundColor = "rgba(16, 185, 129, 0.12)";
            buyhatkeBox.style.borderColor = "rgba(16, 185, 129, 0.25)";
            buyhatkeBox.style.color = "#34d399";
        } else if (lastPrice >= avgPrice * 1.05) {
            buyhatkeBox.className = "buyhatke-recommendation wait";
            buyhatkeText.innerText = "PRICE HIGH - WAIT FOR DROP";
            buyhatkeBox.style.backgroundColor = "rgba(245, 158, 11, 0.12)";
            buyhatkeBox.style.borderColor = "rgba(245, 158, 11, 0.25)";
            buyhatkeBox.style.color = "#fbbf24";
        } else {
            buyhatkeBox.className = "buyhatke-recommendation";
            buyhatkeBox.style.backgroundColor = "rgba(99, 102, 241, 0.12)";
            buyhatkeBox.style.borderColor = "rgba(99, 102, 241, 0.25)";
            buyhatkeBox.style.color = "#818cf8";
            buyhatkeText.innerText = "STABLE PRICING - FAIR DEAL";
        }
    }
}

// --- BUTTON EVENT LISTENERS ---
document.getElementById('btn-step').addEventListener('click', async () => {
    const res = await api.post('/api/step');
    if (res.status === 'finished') {
        showToast("Simulation finished: Out of Inventory!");
        appendLog("Simulation complete: Inventory depleted.", "SYSTEM");
    } else {
        showToast(`Simulated Day completed. Price offered: $${res.day_stats.our_price}`);
        appendLog(`Day ${res.day_stats.day}: Set price to $${res.day_stats.our_price.toFixed(2)} (Competitor: $${res.day_stats.competitor_price.toFixed(2)}). Traffic: ${res.day_stats.visits}, Sales: ${res.day_stats.sales}, Revenue: $${res.day_stats.revenue.toFixed(2)}.`, "SUCCESS");
    }
    await updateDashboard();
});

document.getElementById('btn-run-all').addEventListener('click', async () => {
    showToast("Simulating remaining business cycle...");
    appendLog("Running full simulation run to day 30...", "SYSTEM");
    const res = await api.post('/api/run_all');
    showToast("Full simulation cycle processed successfully.");
    
    // Log the outcome summary
    const lastDay = res.history.length > 0 ? res.history[res.history.length - 1] : null;
    if (lastDay) {
        appendLog(`Simulation batch complete at Day ${lastDay.day}. Final inventory remaining: ${lastDay.inventory}.`, "SUCCESS");
    } else {
        appendLog("Simulation batch complete. No days run (simulation already finished).", "SUCCESS");
    }
    await updateDashboard();
});

document.getElementById('btn-reset').addEventListener('click', async () => {
    await api.post('/api/reset');
    showToast("Pricing Engine and simulator reset.");
    appendLog("Pricing engine simulator reset to initial default state.", "SYSTEM");
    await updateDashboard();
});

document.getElementById('btn-save-cfg').addEventListener('click', async () => {
    const config = {
        true_p_mid: parseFloat(document.getElementById('cfg-pmid').value),
        true_sensitivity: parseFloat(document.getElementById('cfg-sens').value),
        competitor_price: parseFloat(document.getElementById('cfg-compprice').value),
        initial_inventory: parseInt(document.getElementById('cfg-inventory').value)
    };
    await api.post('/api/reset', config);
    showToast("Settings applied & engine restarted.");
    appendLog(`Applied config parameters and reset: p_mid=$${config.true_p_mid}, sensitivity=${config.true_sensitivity}, competitor=$${config.competitor_price}, inventory=${config.initial_inventory}.`, "SYSTEM");
    await updateDashboard();
});

document.getElementById('btn-mock-buy').addEventListener('click', async () => {
    const config = await api.get('/api/config');
    const analytics = await api.get('/api/analytics');
    const currentPrice = config.current_day > 0 ? config.price_arms[analytics.agent_stats.reduce((maxIdx, current, idx, arr) => current.pulls > arr[maxIdx].pulls ? idx : maxIdx, 0)] : 29.99;
    
    const action = {
        price_offered: currentPrice,
        purchased: true
    };
    await api.post('/api/customer_action', action);
    showToast(`Purchase recorded at $${currentPrice}!`);
    appendLog(`Customer Interaction: Customer purchased headphones at offered price $${currentPrice.toFixed(2)}. Inventory reduced.`, "INFO");
    await updateDashboard();
});

document.getElementById('btn-mock-skip').addEventListener('click', async () => {
    const config = await api.get('/api/config');
    const analytics = await api.get('/api/analytics');
    const currentPrice = config.current_day > 0 ? config.price_arms[analytics.agent_stats.reduce((maxIdx, current, idx, arr) => current.pulls > arr[maxIdx].pulls ? idx : maxIdx, 0)] : 29.99;
    
    const action = {
        price_offered: currentPrice,
        purchased: false
    };
    await api.post('/api/customer_action', action);
    showToast("Customer skipped buying at current price.");
    appendLog(`Customer Interaction: Customer clicked but skipped purchasing at offered price $${currentPrice.toFixed(2)}.`, "INFO");
    await updateDashboard();
});

window.addEventListener('DOMContentLoaded', async () => {
    initCharts();
    await updateDashboard(true);
    appendLog("Vectaflow interface initialized. Dashboard metrics synced.", "SYSTEM");
});
