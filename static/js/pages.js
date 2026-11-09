import { getJSON, postJSON } from "./api.js";
import { lineChart } from "./charts.js";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

function readJSON(id) {
  const node = document.getElementById(id);
  return node ? JSON.parse(node.textContent) : {};
}

function setText(selector, value) {
  const node = $(selector);
  if (node) node.textContent = value;
}

function clear(node) {
  if (node) node.replaceChildren();
}

function badge(text, tone) {
  const node = document.createElement("span");
  node.className = `badge ${tone}`;
  node.textContent = text;
  return node;
}

function textNode(tag, value, className = "") {
  const node = document.createElement(tag);
  node.className = className;
  node.textContent = value;
  return node;
}

function resultItem(tone, title, text) {
  const wrap = document.createElement("div");
  wrap.className = `result-item ${tone}`;
  wrap.appendChild(textNode("div", title, "result-title"));
  wrap.appendChild(textNode("div", text, "result-text"));
  return wrap;
}

function meter(score) {
  const track = document.createElement("div");
  track.className = "meter";
  const fill = document.createElement("span");
  fill.style.width = `${Math.min(100, Math.round(score * 100))}%`;
  fill.className = score >= 0.7 ? "risk" : score >= 0.35 ? "warn" : "";
  track.appendChild(fill);
  return track;
}

function renderAnomalies(items) {
  const list = $("#p1-anomalies");
  clear(list);
  if (!items.length) {
    list.appendChild(textNode("li", "Выбросов не обнаружено.", "muted"));
    return;
  }
  items.forEach((item) => {
    const row = document.createElement("li");
    row.appendChild(badge(`${item.z}σ`, Math.abs(item.z) > 5 ? "risk" : "warn"));
    row.appendChild(textNode("span", `${item.label} · ${item.at} · ${item.value} · ${item.direction}`));
    list.appendChild(row);
  });
}

function drawMonitor(model) {
  lineChart($("#p1-chart"), {
    labels: model.labels,
    series: model.series,
    marks: model.anomalies.map((item) => ({ series: model.series.findIndex((line) => line.label === item.label), index: item.index })),
  });
}

async function initP1() {
  const hostSelect = $("#p1-host");
  drawMonitor(readJSON("p1-data"));
  hostSelect.addEventListener("change", async (event) => {
    const model = await getJSON(`/p1/api/overview?host=${encodeURIComponent(event.target.value)}`);
    drawMonitor(model);
    setText("#p1-summary", model.summary);
    renderAnomalies(model.anomalies);
  });
}

function renderLogs(rows) {
  const box = $("#p2-logs");
  clear(box);
  rows.forEach((row) => {
    box.appendChild(resultItem(row.level === "error" ? "risk" : row.level === "warn" ? "warn" : "", `${row.cause} · ${row.confidence}`, `${row.message}`));
  });
}

function initP2() {
  $$("[data-job]").forEach((button) => {
    button.addEventListener("click", async () => {
      const verdict = await postJSON(`/p2/api/analyze/${button.dataset.job}`);
      setText("#p2-summary", verdict.summary);
      renderLogs(verdict.logs);
    });
  });
}

function riskRow(user) {
  const row = document.createElement("tr");
  const name = textNode("td", user.full_name);
  name.appendChild(textNode("div", `${user.position} · ${user.department}`, "muted"));
  const roles = document.createElement("td");
  user.roles.forEach((role) => roles.appendChild(badge(role, "muted")));
  const score = textNode("td", user.score.toFixed(2), "num");
  score.appendChild(meter(user.score));
  const issues = document.createElement("td");
  user.issues.forEach((issue) => issues.appendChild(resultItem(issue.weight >= 0.7 ? "risk" : issue.weight >= 0.4 ? "warn" : "", issue.code, issue.text)));
  row.append(name, roles, score, issues);
  return row;
}

function initP3() {
  $("#p3-recount").addEventListener("click", async () => {
    const model = await postJSON("/p3/api/recount");
    setText("#p3-summary", model.summary);
    const body = $("#p3-rows");
    clear(body);
    model.risky.forEach((user) => body.appendChild(riskRow(user)));
  });
}

function changeRow(kind, name, tone) {
  const row = document.createElement("tr");
  row.append(textNode("td", kind), textNode("td", name, "mono"));
  const mark = document.createElement("td");
  mark.appendChild(badge(tone.text, tone.tone));
  row.appendChild(mark);
  return row;
}

function renderDiff(result) {
  const body = $("#p4-changes");
  clear(body);
  [["added", "Добавлен", "ok"], ["changed", "Изменён", "warn"], ["removed", "Удалён", "risk"]].forEach(([group, title, tone]) => {
    result.changes[group].forEach((item) => body.appendChild(changeRow(item.kind, item.name, { text: title, tone })));
  });
  setText("#p4-summary", result.summary);
  setText("#p4-risk", result.risk.toFixed(2));
  const list = $("#p4-checklist");
  clear(list);
  result.checklist.forEach((step, index) => {
    const row = document.createElement("li");
    row.appendChild(badge(String(index + 1), "muted"));
    row.appendChild(textNode("span", step));
    list.appendChild(row);
  });
}

async function loadVersions() {
  const rows = await getJSON(`/p4/api/versions?config=${encodeURIComponent($("#p4-config").value)}`);
  $("#p4-old").replaceChildren(...rows.map((row) => new Option(row.version, row.version)));
  $("#p4-new").replaceChildren(...rows.map((row) => new Option(row.version, row.version)));
  $("#p4-old").selectedIndex = Math.max(0, rows.length - 2);
  $("#p4-new").selectedIndex = Math.max(0, rows.length - 1);
}

async function compareNow() {
  const query = `config=${encodeURIComponent($("#p4-config").value)}&old=${$("#p4-old").value}&new=${$("#p4-new").value}`;
  renderDiff(await getJSON(`/p4/api/diff?${query}`));
}

function initP4() {
  $("#p4-config").addEventListener("change", loadVersions);
  $("#p4-compare").addEventListener("click", compareNow);
}

function renderFindings(items) {
  const box = $("#p5-findings");
  clear(box);
  if (!items.length) {
    box.appendChild(textNode("p", "Правила не нашли проблем.", "muted"));
    return;
  }
  items.forEach((item) => box.appendChild(resultItem(item.level === "high" ? "risk" : item.level === "warn" ? "warn" : "", `${item.label} · ${item.title}`, `${item.detail} Что делать: ${item.advice}`)));
}

function initP5() {
  $("#p5-analyze").addEventListener("click", async () => {
    const result = await postJSON("/p5/api/analyze", {
      dbms: $("#p5-dbms").value,
      query: $("#p5-query").value,
      plan: $("#p5-plan").value,
      duration_ms: Number($("#p5-duration").value || 0),
    });
    setText("#p5-score", result.score);
    setText("#p5-summary", result.summary);
    setText("#p5-index", result.index.ddl || "Явных условий для индекса не найдено.");
    renderFindings(result.findings);
  });
}

function initP6() {
  $("#p6-route").addEventListener("click", async () => {
    const result = await postJSON("/p6/api/route", { subject: $("#p6-subject").value, body: $("#p6-body").value });
    setText("#p6-summary", result.summary);
    setText("#p6-draft", result.draft);
  });
}

function renderFacts(facts) {
  const body = $("#p7-facts");
  clear(body);
  Object.entries(facts).forEach(([key, value]) => {
    const row = document.createElement("tr");
    row.append(textNode("td", key, "mono"), textNode("td", value, "num"));
    body.appendChild(row);
  });
}

function initP7() {
  const button = $("#p7-validate");
  if (!button) return;
  button.addEventListener("click", async () => {
    const result = await postJSON(`/p7/api/validate/${button.dataset.report}`);
    renderFacts(result.facts);
    const box = $("#p7-issues");
    clear(box);
    result.issues.forEach((item) => box.appendChild(resultItem(item.level === "risk" ? "risk" : "warn", item.title, item.detail)));
    setText("#p7-summary", result.summary);
    setText("#p7-status", result.status);
  });
}

function documentRow(row) {
  const tr = document.createElement("tr");
  const name = textNode("td", row.file_name);
  name.appendChild(textNode("div", `тип: ${row.predicted}`, "muted"));
  tr.append(name, textNode("td", row.confidence.toFixed(2), "num"));
  tr.append(textNode("td", row.requisites.counterparty || "—"));
  tr.append(textNode("td", row.requisites.inn || "—", "mono"));
  tr.append(textNode("td", row.requisites.amount ?? "—", "num"));
  return tr;
}

function initP8() {
  $("#p8-run").addEventListener("click", async () => {
    const model = await postJSON("/p8/api/classify");
    const body = $("#p8-rows");
    clear(body);
    model.documents.forEach((row) => body.appendChild(documentRow(row)));
    setText("#p8-summary", model.summary);
  });
}

const PAGES = { p1: initP1, p2: initP2, p3: initP3, p4: initP4, p5: initP5, p6: initP6, p7: initP7, p8: initP8 };

export function initPage(name) {
  const init = PAGES[name];
  if (init) init();
}
