const SVG_NS = "http://www.w3.org/2000/svg";
const PAD = { top: 18, right: 18, bottom: 28, left: 46 };
const COLORS = ["#21a038", "#2a6fdb", "#f0a30a", "#d92d20"];

function el(name, attrs = {}) {
  const node = document.createElementNS(SVG_NS, name);
  Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
  return node;
}

function bounds(series) {
  const values = series.flatMap((item) => item.points);
  return { min: Math.min(...values), max: Math.max(...values) };
}

function toPoints(points, box, limits) {
  const span = limits.max - limits.min || 1;
  const step = points.length > 1 ? box.width / (points.length - 1) : 0;
  return points.map((value, index) => ({
    x: box.x + index * step,
    y: box.y + box.height - ((value - limits.min) / span) * box.height,
  }));
}

function toPath(points) {
  return points.map((point, index) => `${index === 0 ? "M" : "L"}${point.x.toFixed(1)},${point.y.toFixed(1)}`).join(" ");
}

function drawGrid(svg, box, limits) {
  const ticks = 4;
  const rows = Array.from({ length: ticks + 1 }, (_, index) => index);
  rows.forEach((row) => {
    const y = box.y + (box.height / ticks) * row;
    const value = limits.max - ((limits.max - limits.min) / ticks) * row;
    svg.appendChild(el("line", { x1: box.x, y1: y, x2: box.x + box.width, y2: y, stroke: "#eef0f2", "stroke-width": 1 }));
    const label = el("text", { x: box.x - 8, y: y + 4, "text-anchor": "end", "font-size": 10, fill: "#8a9098" });
    label.textContent = Math.round(value);
    svg.appendChild(label);
  });
}

function drawAxis(svg, box, labels) {
  const step = labels.length > 1 ? box.width / (labels.length - 1) : 0;
  const every = Math.ceil(labels.length / 6);
  labels.filter((_, index) => index % every === 0).forEach((text, index) => {
    const node = el("text", { x: box.x + index * every * step, y: box.y + box.height + 18, "text-anchor": "middle", "font-size": 10, fill: "#8a9098" });
    node.textContent = text;
    svg.appendChild(node);
  });
}

function drawLegend(svg, series, width) {
  series.forEach((item, index) => {
    const x = width - 120;
    const y = PAD.top + index * 16;
    svg.appendChild(el("rect", { x, y: y - 8, width: 8, height: 8, rx: 2, fill: item.color || COLORS[index % COLORS.length] }));
    const label = el("text", { x: x + 14, y, "font-size": 10.5, fill: "#565b62" });
    label.textContent = item.label;
    svg.appendChild(label);
  });
}

export function lineChart(svg, config) {
  const width = svg.clientWidth || 640;
  const height = svg.clientHeight || 240;
  const box = { x: PAD.left, y: PAD.top, width: width - PAD.left - PAD.right - 130, height: height - PAD.top - PAD.bottom };
  const limits = bounds(config.series);
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.replaceChildren();
  drawGrid(svg, box, limits);
  drawAxis(svg, box, config.labels);
  config.series.forEach((item, index) => {
    const points = toPoints(item.points, box, limits);
    const stroke = item.color || COLORS[index % COLORS.length];
    svg.appendChild(el("path", { d: toPath(points), fill: "none", stroke, "stroke-width": 2, "stroke-linejoin": "round", "stroke-linecap": "round" }));
    (config.marks || []).filter((mark) => mark.series === index).forEach((mark) => {
      svg.appendChild(el("circle", { cx: points[mark.index].x, cy: points[mark.index].y, r: 4, fill: "#fff", stroke, "stroke-width": 2 }));
    });
  });
  drawLegend(svg, config.series, width);
}

export function barChart(target, items) {
  const max = Math.max(...items.map((item) => item.value), 1);
  target.replaceChildren();
  items.forEach((item) => {
    const row = document.createElement("div");
    row.style.cssText = "display:grid;grid-template-columns:120px 1fr 44px;gap:10px;align-items:center;margin-bottom:10px;font-size:13px;";
    const name = document.createElement("span");
    name.textContent = item.label;
    const track = document.createElement("div");
    track.className = "meter";
    const fill = document.createElement("span");
    fill.style.width = `${Math.round((item.value / max) * 100)}%`;
    fill.className = item.tone || "";
    track.appendChild(fill);
    const value = document.createElement("span");
    value.textContent = item.display ?? item.value;
    value.style.cssText = "text-align:right;color:#565b62;font-variant-numeric:tabular-nums;";
    row.append(name, track, value);
    target.appendChild(row);
  });
}
