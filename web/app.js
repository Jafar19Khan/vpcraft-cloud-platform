const REFRESH_MS = 10000;
const SVG_NS = 'http://www.w3.org/2000/svg';
const $ = (id) => document.getElementById(id);
const text = (id, value) => { const el = $(id); if (el) el.textContent = value; };

function duration(seconds) {
  if (seconds == null) return '--';
  const d = Math.floor(seconds / 86400), h = Math.floor(seconds % 86400 / 3600), m = Math.floor(seconds % 3600 / 60);
  if (d) return `${d}d ${h}h`;
  if (h) return `${h}h ${m}m`;
  if (m) return `${m}m ${seconds % 60}s`;
  return `${seconds}s`;
}

function setBar(id, percent) {
  const el = $(id);
  if (!el) return;
  const value = percent == null ? 0 : Math.max(0, Math.min(100, percent));
  el.style.width = `${value}%`;
  el.className = 'bar-fill' + (value >= 90 ? ' crit' : value >= 70 ? ' warn' : '');
}

function setState(id, ok, goodLabel, badLabel) {
  const el = $(id);
  el.textContent = ok ? goodLabel : badLabel;
  el.className = 'metric-value ' + (ok ? 'good-text' : 'bad-text');
}

async function getJson(url) {
  const response = await fetch(url, { cache: 'no-store' });
  return { ok: response.ok, data: await response.json().catch(() => ({})) };
}

function renderOverview(data) {
  text('region', data.region || '--');
  const NA = 'Not on AWS';
  text('az', data.instance?.availability_zone || NA);
  text('instance-type', data.instance?.type || NA);
  text('instance-id', data.instance?.id || NA);
  text('public-ip', data.instance?.public_ip || NA);
  text('version', `v${data.version}`);
  text('env-name', data.environment);
  text('env-avatar', (data.environment || '--').slice(0, 2).toUpperCase());
  const events = $('events');
  events.replaceChildren();
  data.latest_events.forEach((item) => {
    const row = document.createElement('div'); row.className = 'event';
    const mark = document.createElement('span'); mark.className = 'event-mark';
    const body = document.createElement('div');
    const title = document.createElement('strong'); title.textContent = `${item.environment} · ${item.status}`;
    const detail = document.createElement('small'); detail.textContent = `Release ${item.version}`;
    const time = document.createElement('time'); time.textContent = new Date(item.created_at).toLocaleString();
    body.append(title, detail); row.append(mark, body, time); events.append(row);
  });
}

function renderSystem(data) {
  text('app-uptime', duration(data.app_uptime_seconds));
  text('host-uptime', `Host uptime ${duration(data.host_uptime_seconds)}`);
  text('hostname', data.hostname);
  const load = data.load;
  text('cpu-text', load.percent == null ? 'n/a' : `${load.percent}%`);
  text('cpu-detail', load.one == null ? 'Load average unavailable' : `Load average ${load.one} / ${load.five} / ${load.fifteen} · ${load.cpu_count} vCPU`);
  setBar('cpu-bar', load.percent);
  const mem = data.memory;
  text('mem-text', mem ? `${mem.percent}%` : 'n/a');
  text('mem-detail', mem ? `${mem.used_mb} MB of ${mem.total_mb} MB in use` : 'Memory data unavailable');
  setBar('mem-bar', mem?.percent);
  const disk = data.disk;
  text('disk-text', disk ? `${disk.percent}%` : 'n/a');
  text('disk-detail', disk ? `${disk.used_gb} GB of ${disk.total_gb} GB used` : 'Disk data unavailable');
  setBar('disk-bar', disk?.percent);
}

function renderLatency(data) {
  text('latency-now', `${data.latency_ms.toFixed(2)} ms`);
  text('latency-avg', `Average ${data.average_latency_ms.toFixed(2)} ms · peak ${data.max_latency_ms.toFixed(2)} ms`);
  text('sample-count', `${data.sample_count} ${data.sample_count === 1 ? 'sample' : 'samples'}`);
  text('chart-note', `Each point is a stored database round-trip, sampled at most every 5 seconds.`);
  const svg = $('latency-chart');
  svg.replaceChildren();
  [35, 70, 105].forEach((y) => {
    const line = document.createElementNS(SVG_NS, 'line');
    line.setAttribute('x1', 0); line.setAttribute('x2', 600); line.setAttribute('y1', y); line.setAttribute('y2', y); line.setAttribute('class', 'grid');
    svg.append(line);
  });
  const values = data.samples.map((s) => s.latency_ms);
  if (values.length < 2) {
    text('chart-note', 'Collecting samples. The chart appears after the second sample (about 10 seconds).');
    return;
  }
  const max = Math.max(...values) * 1.15 || 1;
  const points = values.map((v, i) => [i / (values.length - 1) * 600, 130 - v / max * 120]);
  const path = points.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)} ${y.toFixed(1)}`).join(' ');
  const area = document.createElementNS(SVG_NS, 'path');
  area.setAttribute('d', `${path} L600 140 L0 140 Z`); area.setAttribute('class', 'area');
  const line = document.createElementNS(SVG_NS, 'path');
  line.setAttribute('d', path); line.setAttribute('class', 'line');
  svg.append(area, line);
}

async function refresh() {
  const [health, ready, overview, system, status] = await Promise.allSettled([
    getJson('/health'), getJson('/ready'), getJson('/api/overview'), getJson('/api/system'), getJson('/api/status'),
  ]);
  const ok = (r) => r.status === 'fulfilled' && r.value.ok;
  setState('api-status', ok(health), 'Healthy', 'Unavailable');
  setState('db-status', ok(ready), 'Ready', 'Unavailable');
  if (ok(overview)) renderOverview(overview.value.data);
  if (ok(system)) renderSystem(system.value.data);
  if (ok(status)) renderLatency(status.value.data);
  const live = ok(health) && ok(ready);
  text('live-label', live ? 'Live' : 'Degraded');
  text('last-refresh', `Last refresh ${new Date().toLocaleTimeString()}`);
}

refresh();
setInterval(refresh, REFRESH_MS);
