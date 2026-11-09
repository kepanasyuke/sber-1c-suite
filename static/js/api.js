async function request(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`HTTP ${response.status}: ${url}`);
  return response.json();
}

export function getJSON(url) {
  return request(url, { headers: { Accept: "application/json" } });
}

export function postJSON(url, body) {
  return request(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body ?? {}),
  });
}

export function text(value) {
  const node = document.createElement("span");
  node.textContent = value ?? "—";
  return node;
}
