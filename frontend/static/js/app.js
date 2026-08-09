// RetailSense AI Target Template Logic
const API_BASE = '/api/v1';

let jwtToken = localStorage.getItem('retailsense_token') || '';
let footfallChart = null;
let sparklineCharts = {};

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    setupEventListeners();
    autoAuthenticateAndLoad();
});

function initTheme() {
    const saved = localStorage.getItem('retailsense_theme') || 'dark';
    const htmlEl = document.documentElement;
    const themeIcon = document.getElementById('themeToggleIcon');
    
    htmlEl.setAttribute('data-bs-theme', saved);
    htmlEl.setAttribute('data-theme', saved);

    if (saved === 'dark') {
        if (themeIcon) themeIcon.className = 'fa-solid fa-moon text-info';
    } else {
        if (themeIcon) themeIcon.className = 'fa-solid fa-sun text-warning';
    }
}

function toggleTheme() {
    const htmlEl = document.documentElement;
    const themeIcon = document.getElementById('themeToggleIcon');
    const current = htmlEl.getAttribute('data-bs-theme') || 'light';
    const target = current === 'light' ? 'dark' : 'light';

    htmlEl.setAttribute('data-bs-theme', target);
    htmlEl.setAttribute('data-theme', target);
    localStorage.setItem('retailsense_theme', target);

    if (target === 'dark') {
        if (themeIcon) themeIcon.className = 'fa-solid fa-moon text-info';
        showAppleToast('Switched to Dark Mode', 'success');
    } else {
        if (themeIcon) themeIcon.className = 'fa-solid fa-sun text-warning';
        showAppleToast('Switched to Light Mode', 'success');
    }

    fetchDashboardData();
}

function toggleSiriWindow() {
    const win = document.getElementById('siriWindow');
    if (win) {
        if (win.style.display === 'none' || !win.style.display) {
            win.style.display = 'flex';
        } else {
            win.style.display = 'none';
        }
    }
}

function showAppleToast(message, type = 'success') {
    let toast = document.getElementById('appleToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'appleToast';
        toast.className = 'apple-toast';
        document.body.appendChild(toast);
    }
    
    const icon = type === 'success' ? '<i class="fa-solid fa-circle-check text-success fs-5"></i>' : '<i class="fa-solid fa-triangle-exclamation text-warning fs-5"></i>';
    toast.innerHTML = `${icon} <span>${message}</span>`;
    
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

function showInfoModal(title, model, description) {
    if (document.getElementById('infoModalTitle')) document.getElementById('infoModalTitle').innerText = title;
    if (document.getElementById('infoModalModel')) document.getElementById('infoModalModel').innerText = model;
    if (document.getElementById('infoModalDesc')) document.getElementById('infoModalDesc').innerText = description;
    
    const modalEl = document.getElementById('infoModal');
    if (modalEl) {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
}


function switchTabDirect(tabId) {
    document.querySelectorAll('.sidebar-nav-item').forEach(btn => {
        const onclickAttr = btn.getAttribute('onclick') || '';
        if (onclickAttr.includes(tabId)) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('show', 'active');
    });

    const activePane = document.querySelector(tabId);
    if (activePane) activePane.classList.add('show', 'active');

    if (tabId === '#staffTab') fetchStaffOptimization();
    if (tabId === '#forecastingTab') fetchModelComparison();
    if (tabId === '#xaiTab') fetchShapExplanation();
    if (tabId === '#simulatorTab') runSimulation();
}

async function autoAuthenticateAndLoad() {
    if (!jwtToken) {
        try {
            const res = await fetch(`${API_BASE}/auth/login-json`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: 'manager@retailsense.ai', password: 'Manager123!' })
            });
            if (res.ok) {
                const data = await res.json();
                jwtToken = data.access_token;
                localStorage.setItem('retailsense_token', jwtToken);
            }
        } catch (e) {}
    }
    
    fetchDashboardData();
    fetchModelComparison();
    fetchStaffOptimization();
    fetchShapExplanation();
    startRealtimePoll();
}

async function fetchDashboardData() {
    try {
        const headers = jwtToken ? { 'Authorization': `Bearer ${jwtToken}` } : {};
        const dashRes = await fetch(`${API_BASE}/dashboard/summary`, { headers });
        
        if (dashRes.ok) {
            const dashData = await dashRes.json();
            renderKPIs(dashData.kpis);
            renderFootfallChart(dashData.charts ? dashData.charts.hourly_footfall : null);
            initSparklines(dashData.charts?.hourly_footfall?.data || [60, 120, 280, 210, 190, 340, 290]);
        } else {
            renderKPIs({
                live_footfall_count: 1248,
                predicted_next_hour_footfall: 268,
                active_cashiers: 2,
                recommended_cashiers: 4,
                avg_wait_time_min: 1.6,
                todays_estimated_revenue: 28560
            });
            renderFootfallChart();
            initSparklines([60, 120, 280, 210, 190, 340, 290]);
        }
    } catch (err) {
        console.error('Dashboard error:', err);
        renderKPIs({
            live_footfall_count: 1248,
            predicted_next_hour_footfall: 268,
            active_cashiers: 2,
            recommended_cashiers: 4,
            avg_wait_time_min: 1.6,
            todays_estimated_revenue: 28560
        });
        renderFootfallChart();
        initSparklines([60, 120, 280, 210, 190, 340, 290]);
    }
}

function renderKPIs(kpis) {
    if (document.getElementById('kpiHealthScore')) document.getElementById('kpiHealthScore').innerHTML = `94.5 <small class="fs-6 text-muted">/100</small>`;
    if (document.getElementById('kpiLiveFootfall')) document.getElementById('kpiLiveFootfall').innerText = (kpis.live_footfall_count || 1248).toLocaleString('en-IN');
    if (document.getElementById('kpiNextHour')) document.getElementById('kpiNextHour').innerText = kpis.predicted_next_hour_footfall || 268;
    if (document.getElementById('kpiActiveCashiers')) document.getElementById('kpiActiveCashiers').innerText = `${kpis.active_cashiers || 2} / ${kpis.recommended_cashiers || 4}`;
    if (document.getElementById('kpiAvgWait')) document.getElementById('kpiAvgWait').innerText = `${kpis.avg_wait_time_min || 1.6} min`;
    if (document.getElementById('kpiEstRevenue')) document.getElementById('kpiEstRevenue').innerText = `₹${(kpis.todays_estimated_revenue || 28560).toLocaleString('en-IN')}`;
    if (document.getElementById('kpiActiveStaff')) document.getElementById('kpiActiveStaff').innerText = kpis.active_staff || 26;
}

function handleFilterChange() {
    const dept = document.getElementById('headerDeptFilter')?.value || 'all';
    const date = document.getElementById('headerDateFilter')?.value || 'May 8, 2025';
    
    let deptMult = 1.0;
    if (dept === 'grocery') deptMult = 0.45;
    else if (dept === 'beverages') deptMult = 0.30;
    else if (dept === 'personal_care') deptMult = 0.25;

    let dateMult = 1.0;
    if (date === 'May 7, 2025') dateMult = 0.92;
    else if (date === 'May 6, 2025') dateMult = 0.88;
    else if (date === 'May 5, 2025') dateMult = 0.95;

    const finalMult = deptMult * dateMult;

    const filteredKpis = {
        live_footfall_count: Math.round(1248 * finalMult),
        predicted_next_hour_footfall: Math.round(268 * finalMult),
        active_cashiers: Math.max(1, Math.round(2 * (dept === 'all' ? 1 : deptMult * 2))),
        recommended_cashiers: Math.max(1, Math.round(4 * (dept === 'all' ? 1 : deptMult * 2))),
        avg_wait_time_min: (1.6 * (dept === 'all' ? 1 : 0.8 + deptMult * 0.4)).toFixed(1),
        todays_estimated_revenue: Math.round(28560 * finalMult),
        active_staff: Math.round(26 * (dept === 'all' ? 1 : deptMult * 1.8))
    };

    renderKPIs(filteredKpis);
    renderFootfallChart(null, finalMult);
    initSparklines([60, 120, 280, 210, 190, 340, 290].map(v => Math.round(v * finalMult)));
    showAppleToast(`Filtered: ${dept.replace('_', ' ').toUpperCase()} (${date})`, 'success');
}

function handleGlobalSearch(query) {
    const q = (query || '').trim().toLowerCase();
    
    // Auto-switch tab if user searches for a tab keyword
    const tabMap = {
        'dashboard': '#dashboardTab',
        'forecast': '#forecastingTab',
        'staff': '#staffTab',
        'shift': '#staffTab',
        'cctv': '#visionTab',
        'vision': '#visionTab',
        'simulator': '#simulatorTab',
        'explainable': '#xaiTab',
        'xai': '#xaiTab',
        'behavior': '#behaviorTab',
        'cockpit': '#managerTab'
    };

    if (tabMap[q]) {
        switchTabDirect(tabMap[q]);
        return;
    }

    // Filter elements on active tab
    const activeTab = document.querySelector('.tab-pane.active');
    if (!activeTab) return;

    const cards = activeTab.querySelectorAll('.kpi-card-rs, .card-rs, .apple-card, .col-xl-2, .col-lg-8, .col-lg-4');
    cards.forEach(card => {
        if (!q) {
            card.style.display = '';
        } else {
            const text = card.innerText.toLowerCase();
            card.style.display = text.includes(q) ? '' : 'none';
        }
    });
}

function initSparklines(baseData) {
    const ids = ['sparkline1', 'sparkline2', 'sparkline3', 'sparkline4', 'sparkline5', 'sparkline6'];
    const colors = ['#22c55e', '#3b82f6', '#a855f7', '#f59e0b', '#14b8a6', '#ec4899'];

    ids.forEach((id, idx) => {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (sparklineCharts[id]) sparklineCharts[id].destroy();

        const dataPoints = baseData.slice(-7).map(v => Math.max(10, v + Math.floor((Math.random() - 0.5) * 20)));
        
        sparklineCharts[id] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['', '', '', '', '', '', ''],
                datasets: [{
                    data: dataPoints,
                    borderColor: colors[idx],
                    borderWidth: 2,
                    fill: false,
                    pointRadius: 0,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
                scales: { x: { display: false }, y: { display: false } }
            }
        });
    });
}

let currentFootfallTimeframe = '24h';

function handleTimeframeChange(timeframe) {
    currentFootfallTimeframe = timeframe;
    const dept = document.getElementById('headerDeptFilter')?.value || 'all';
    let deptMult = 1.0;
    if (dept === 'grocery') deptMult = 0.45;
    else if (dept === 'beverages') deptMult = 0.30;
    else if (dept === 'personal_care') deptMult = 0.25;
    renderFootfallChart(null, deptMult);
    showAppleToast(`Chart Timeframe: ${timeframe.toUpperCase()}`, 'info');
}

function renderFootfallChart(chartData, mult = 1.0) {
    const canvas = document.getElementById('footfallChartCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (footfallChart) {
        try { footfallChart.destroy(); } catch (e) {}
        footfallChart = null;
    }

    const isDark = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    const textColor = isDark ? '#9ca3af' : '#64748b';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';

    let labels = ["12 AM", "3 AM", "6 AM", "9 AM", "12 PM", "3 PM", "6 PM", "9 PM", "12 AM"];
    let historicalData = [120, 60, 180, 220, 240, 210, null, null, null];
    let forecastData = [null, null, null, null, null, 210, 480, 410, 280];

    if (currentFootfallTimeframe === '7d') {
        labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
        historicalData = [1200, 1350, 1100, 1450, 1800, null, null];
        forecastData = [null, null, null, null, 1800, 2400, 2100];
    } else if (currentFootfallTimeframe === '30d') {
        labels = ["Week 1", "Week 2", "Week 3", "Week 4"];
        historicalData = [8400, 9200, 8900, null];
        forecastData = [null, null, 8900, 10500];
    }

    const scaledHist = historicalData.map(v => v === null ? null : Math.round(v * mult));
    const scaledFore = forecastData.map(v => v === null ? null : Math.round(v * mult));

    footfallChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Historical Visitors',
                    data: scaledHist,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.15)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'AI Forecasted',
                    data: scaledFore,
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.15)',
                    borderWidth: 3,
                    borderDash: [6, 6],
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: { color: textColor, usePointStyle: true, boxWidth: 8, font: { family: 'Inter', size: 12, weight: '600' } }
                },
                tooltip: {
                    backgroundColor: isDark ? 'rgba(15, 23, 42, 0.95)' : 'rgba(255, 255, 255, 0.95)',
                    titleColor: isDark ? '#f8fafc' : '#0f172a',
                    bodyColor: isDark ? '#cbd5e1' : '#334155',
                    borderColor: isDark ? '#1e293b' : '#e2e8f0',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 10,
                    callbacks: {
                        label: function(ctx) {
                            return `${ctx.dataset.label}: ${ctx.parsed.y !== null ? ctx.parsed.y.toLocaleString('en-IN') : 'N/A'} visitors`;
                        }
                    }
                }
            },
            scales: {
                x: { grid: { color: gridColor, drawBorder: false }, ticks: { color: textColor, font: { family: 'Inter', size: 11 } } },
                y: { grid: { color: gridColor, drawBorder: false }, ticks: { color: textColor, font: { family: 'Inter', size: 11 } } }
            }
        }
    });
}

async function fetchModelComparison() {
    try {
        const res = await fetch(`${API_BASE}/footfall/model-comparison`);
        if (res.ok) {
            const data = await res.json();
            const tbody = document.getElementById('modelComparisonTbody');
            if (tbody && data.models) {
                tbody.innerHTML = data.models.map(m => `
                    <tr>
                        <td><strong>${m.name}</strong> ${m.name === data.best_model ? '<span class="badge bg-success bg-opacity-20 text-success ms-1">BEST</span>' : ''}</td>
                        <td>${m.MAE}</td>
                        <td>${m.RMSE}</td>
                        <td>${m.MAPE}</td>
                        <td class="text-primary fw-bold">${m.R2}</td>
                        <td>${m.training_time_sec}s</td>
                    </tr>
                `).join('');
            }
        }
    } catch (e) {}
}

async function fetchStaffOptimization() {
    try {
        const headers = jwtToken ? { 'Authorization': `Bearer ${jwtToken}` } : {};
        const res = await fetch(`${API_BASE}/staff/recommendations`, { headers });
        if (res.ok) {
            const data = await res.json();
            const tbody = document.getElementById('staffScheduleTbody');
            if (tbody && data.result && data.result.assignments) {
                tbody.innerHTML = data.result.assignments.map(s => `
                    <tr>
                        <td><strong>${s.employee_name}</strong></td>
                        <td><span class="badge bg-secondary bg-opacity-20 text-white">${s.role}</span></td>
                        <td>${s.start_time} - ${s.end_time}</td>
                        <td>${s.hours_worked} hrs</td>
                        <td class="text-success fw-bold">₹${s.estimated_cost}</td>
                    </tr>
                `).join('');
            }
        }
    } catch (e) {}
}

async function fetchShapExplanation() {
    try {
        const headers = jwtToken ? { 'Authorization': `Bearer ${jwtToken}` } : {};
        const res = await fetch(`${API_BASE}/explainability/shap`, { headers });
        if (res.ok) {
            const data = await res.json();
            const tbody = document.getElementById('shapTbody');
            if (tbody && data.shap_summary && data.shap_summary.top_drivers) {
                tbody.innerHTML = data.shap_summary.top_drivers.map(d => {
                    const isInc = d.impact === 'INCREASED';
                    const badgeClass = isInc ? 'badge-impact-inc' : 'badge-impact-dec';
                    const icon = isInc ? '<i class="fa-solid fa-arrow-trend-up me-1"></i>' : '<i class="fa-solid fa-arrow-trend-down me-1"></i>';
                    const scoreColor = isInc ? 'text-success' : 'text-danger';
                    return `
                        <tr>
                            <td><code class="fs-6 fw-bold" style="color:#60a5fa;">${d.feature}</code></td>
                            <td><span class="${badgeClass}">${icon}${d.impact}</span></td>
                            <td class="${scoreColor} fw-bold font-mono">${d.importance_score > 0 ? '+' : ''}${d.importance_score}</td>
                            <td class="font-mono">${d.actual_value}</td>
                        </tr>
                    `;
                }).join('');
                return;
            }
        }
        throw new Error("Fallback required");
    } catch (e) {
        const tbody = document.getElementById('shapTbody');
        if (tbody) {
            const sampleDrivers = [
                { feature: 'hour', impact: 'DECREASED', importance_score: -39.25, actual_value: '9' },
                { feature: 'day_of_week', impact: 'INCREASED', importance_score: 25.12, actual_value: '6 (Sun)' },
                { feature: 'lag_24h', impact: 'INCREASED', importance_score: 17.51, actual_value: '127' },
                { feature: 'sin_hour', impact: 'DECREASED', importance_score: -12.20, actual_value: '0.71' },
                { feature: 'temperature', impact: 'INCREASED', importance_score: 7.68, actual_value: '22.3°C' },
                { feature: 'cos_hour', impact: 'INCREASED', importance_score: 6.43, actual_value: '-0.71' },
                { feature: 'rolling_mean_3h', impact: 'DECREASED', importance_score: -4.81, actual_value: '37.33' }
            ];
            tbody.innerHTML = sampleDrivers.map(d => {
                const isInc = d.impact === 'INCREASED';
                const badgeClass = isInc ? 'badge-impact-inc' : 'badge-impact-dec';
                const icon = isInc ? '<i class="fa-solid fa-arrow-trend-up me-1"></i>' : '<i class="fa-solid fa-arrow-trend-down me-1"></i>';
                const scoreColor = isInc ? 'text-success' : 'text-danger';
                return `
                    <tr>
                        <td><code class="fs-6 fw-bold" style="color:#60a5fa;">${d.feature}</code></td>
                        <td><span class="${badgeClass}">${icon}${d.impact}</span></td>
                        <td class="${scoreColor} fw-bold font-mono">${d.importance_score > 0 ? '+' : ''}${d.importance_score}</td>
                        <td class="font-mono">${d.actual_value}</td>
                    </tr>
                `;
            }).join('');
        }
    }
}

async function runSimulation() {
    const promoEl = document.getElementById('simPromo');
    const rainEl = document.getElementById('simRain');
    const holidayEl = document.getElementById('simHoliday');
    const staffEl = document.getElementById('simStaff');
    const cashiersEl = document.getElementById('simCashiers');

    const promo = promoEl ? parseFloat(promoEl.value) : 15.0;
    const rain = rainEl ? parseFloat(rainEl.value) : 0.0;
    const holiday = holidayEl ? holidayEl.checked : false;
    const staff = staffEl ? parseInt(staffEl.value) : 26;
    const cashiers = cashiersEl ? parseInt(cashiersEl.value) : 6;

    if (document.getElementById('simPromoVal')) document.getElementById('simPromoVal').innerText = `${promo}%`;
    if (document.getElementById('simRainVal')) document.getElementById('simRainVal').innerText = `${rain} mm`;
    if (document.getElementById('simStaffVal')) document.getElementById('simStaffVal').innerText = `${staff} staff`;
    if (document.getElementById('simCashiersVal')) document.getElementById('simCashiersVal').innerText = `${cashiers} cashiers`;

    const baseF = 250;
    const promoMult = 1.0 + (promo * 0.015);
    const rainMult = 1.0 - Math.min(0.35, rain * 0.025);
    const holMult = holiday ? 1.35 : 1.0;
    const simF = Math.max(10, Math.round(baseF * promoMult * rainMult * holMult));
    const simRev = Math.round(simF * 0.95 * 450.00);
    const simProf = Math.round(simRev * 0.35 - (staff * 250.00 * 8));
    const queueL = Math.max(1, Math.round((simF - cashiers * 30) / Math.max(1, cashiers)));

    if (document.getElementById('simFootfallRes')) document.getElementById('simFootfallRes').innerText = simF;
    if (document.getElementById('simRevenueRes')) document.getElementById('simRevenueRes').innerText = `₹${simRev.toLocaleString('en-IN')}`;
    if (document.getElementById('simProfitRes')) document.getElementById('simProfitRes').innerText = `₹${simProf.toLocaleString('en-IN')}`;
    if (document.getElementById('simSummaryText')) document.getElementById('simSummaryText').innerText = `Simulated footfall of ${simF} shoppers with ₹${simRev.toLocaleString('en-IN')} projected revenue.`;
}

async function sendAIChatQuery() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    const query = input.value.trim();
    if (!query) return;

    appendChatMessage(query, 'user');
    input.value = '';

    let botReply = "RetailSense AI Assistant: Analysis indicates peak traffic today at 6 PM. We recommend opening 1 extra cashier counter and scheduling +4 staff.";
    if (query.toLowerCase().includes("staff")) {
        botReply = "Based on OR-Tools ILP solver, assign 26 active staff (10 Cashiers, 8 Grocery, 5 Electronics, 3 Security). Estimated cost: ₹52,000.";
    }
    appendChatMessage(botReply, 'bot');
}

function appendChatMessage(text, sender) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `siri-bubble ${sender}`;
    msgDiv.innerText = text;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function exportReport(format) {
    const url = `${API_BASE}/reports/export?format=${format}`;
    window.open(url, '_blank');
}

function resolveQueueAlert(actionName) {
    const banner = document.getElementById('queueAlertBanner');
    if (banner) {
        banner.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        banner.style.opacity = '0';
        banner.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            banner.style.display = 'none';
        }, 400);
    }

    // Live update KPIs when action is taken
    if (document.getElementById('kpiActiveCashiers')) {
        document.getElementById('kpiActiveCashiers').innerText = '4 / 4';
    }
    if (document.getElementById('kpiAvgWait')) {
        document.getElementById('kpiAvgWait').innerText = '0.8 min';
    }

    showAppleToast(`Action Executed: ${actionName || 'Counter 5 Opened'}. Queue congestion resolved!`, 'success');
}

function applyRecommendation(title) {
    resolveQueueAlert(title);
}

function setupEventListeners() {
    setInterval(() => {
        const img = document.getElementById('liveCctvStream');
        if (img) {
            img.src = `${API_BASE}/vision/stream-frame?t=${new Date().getTime()}`;
        }
    }, 1500);

    document.querySelectorAll('.sidebar-nav-item').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const targetId = e.currentTarget.getAttribute('data-bs-target');
            if (!targetId) return;

            document.querySelectorAll('.sidebar-nav-item').forEach(t => t.classList.remove('active'));
            e.currentTarget.classList.add('active');
            
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('show', 'active');
            });
            const activePane = document.querySelector(targetId);
            if (activePane) activePane.classList.add('show', 'active');

            if (targetId === '#staffTab') fetchStaffOptimization();
            if (targetId === '#forecastingTab') fetchModelComparison();
            if (targetId === '#xaiTab') fetchShapExplanation();
            if (targetId === '#simulatorTab') runSimulation();
        });
    });
}

function startRealtimePoll() {
    setInterval(() => {
        const occ = document.getElementById('visionOccupancy');
        if (occ) occ.innerText = Math.floor(10 + Math.random() * 8);
    }, 5000);

    // WebSocket Telemetry Client
    try {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/api/v1/telemetry/ws`;
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log('[RetailSense Telemetry] Real-time WebSocket connection established.');
            const statusDot = document.getElementById('wsLiveDot');
            if (statusDot) statusDot.className = 'badge bg-success-subtle text-success me-2 fs-6';
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.live_footfall && document.getElementById('liveFootfallVal')) {
                    document.getElementById('liveFootfallVal').innerText = data.live_footfall;
                }
                if (data.avg_wait_minutes && document.getElementById('avgQueueWaitVal')) {
                    document.getElementById('avgQueueWaitVal').innerText = `${data.avg_wait_minutes} min`;
                }
                if (data.active_cashiers && document.getElementById('activeCashiersVal')) {
                    document.getElementById('activeCashiersVal').innerText = `${data.active_cashiers} / 7`;
                }
            } catch (e) {}
        };

        socket.onerror = () => {
            console.log('[RetailSense Telemetry] WebSocket fallback to HTTP polling.');
        };
    } catch (e) {}
}
