const NUMERIC = /^[-−]?\d+([.,]\d+)?$/;

function cellValue(cell) {
  const text = cell.textContent.trim();
  const compact = text.replace(/\s|\u00a0/g, "").replace("−", "-").replace(",", ".");
  return NUMERIC.test(compact) ? Number.parseFloat(compact) : text.toLowerCase();
}

function compareRows(left, right, index, direction) {
  const first = cellValue(left.children[index]);
  const second = cellValue(right.children[index]);
  const result = typeof first === "number" && typeof second === "number" ? first - second : String(first).localeCompare(String(second), "ru");
  return direction === "asc" ? result : -result;
}

function sortTable(table, index, direction) {
  const body = table.tBodies[0];
  const rows = Array.from(body.rows).filter((row) => !row.dataset.nosort);
  rows.sort((left, right) => compareRows(left, right, index, direction));
  rows.forEach((row) => body.appendChild(row));
}

function bindHeader(table, cell, index) {
  cell.classList.add("sortable");
  cell.setAttribute("tabindex", "0");
  cell.setAttribute("role", "button");
  const toggle = () => {
    const direction = cell.dataset.dir === "asc" ? "desc" : "asc";
    Array.from(cell.parentNode.children).forEach((item) => item.removeAttribute("data-dir"));
    cell.dataset.dir = direction;
    sortTable(table, index, direction);
  };
  cell.addEventListener("click", toggle);
  cell.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggle();
    }
  });
}

export function sortableTables() {
  document.querySelectorAll("table").forEach((table) => {
    Array.from(table.querySelectorAll("thead th")).forEach((cell, index) => bindHeader(table, cell, index));
  });
}

function applyFilter(cards, filter, empty) {
  const visible = cards.filter((card) => filter === "all" || (card.dataset.tags || "").includes(filter));
  cards.forEach((card) => card.classList.toggle("is-hidden", !visible.includes(card)));
  if (empty) empty.hidden = visible.length > 0;
}

export function initProductFilter() {
  const bar = document.getElementById("product-filter");
  if (!bar) return;
  const cards = Array.from(document.querySelectorAll("#product-grid .product"));
  const empty = document.getElementById("product-empty");
  bar.addEventListener("click", (event) => {
    const chip = event.target.closest(".chip");
    if (!chip) return;
    Array.from(bar.querySelectorAll(".chip")).forEach((item) => item.classList.toggle("active", item === chip));
    applyFilter(cards, chip.dataset.filter, empty);
  });
}

export function toast(message, tone = "ok") {
  const wrap = document.getElementById("toast-wrap");
  if (!wrap) return;
  const node = document.createElement("div");
  node.className = `toast ${tone}`;
  node.textContent = message;
  wrap.appendChild(node);
  window.setTimeout(() => node.remove(), 3200);
}

export function setLoading(element, state) {
  if (element) element.classList.toggle("is-loading", state);
}
