const form = document.querySelector("#analysis-form");
const message = document.querySelector("#message");
const count = document.querySelector("#character-count");
const result = document.querySelector("#result");
const button = document.querySelector("#analyse-button");
const historyContainer = document.querySelector("#history");

message.addEventListener("input", () => {
  count.textContent = `${message.value.length.toLocaleString()} / 10,000`;
});

function scoreColour(score) {
  if (score >= 70) return "var(--danger)";
  if (score >= 40) return "var(--warning)";
  return "var(--accent)";
}

function renderResult(data) {
  const signals = data.signals.length
    ? data.signals.map((signal) => `
        <article class="signal">
          <strong>${escapeHtml(signal.label)}</strong>
          <p>${escapeHtml(signal.detail)}</p>
        </article>`).join("")
    : `<p class="muted">No explicit rule-based signals were detected.</p>`;

  result.classList.remove("empty");
  result.innerHTML = `
    <div class="score-row">
      <div><p class="eyebrow">Risk score</p><div class="score" style="color:${scoreColour(data.risk_score)}">${data.risk_score}<small>/100</small></div></div>
      <span class="verdict">${escapeHtml(data.verdict)}</span>
    </div>
    <div class="signals">${signals}</div>
    <p class="recommendation"><strong>Recommended action:</strong> ${escapeHtml(data.recommendation)}</p>`;
}

function escapeHtml(value) {
  const element = document.createElement("div");
  element.textContent = value;
  return element.innerHTML;
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history?limit=6");
    if (!response.ok) throw new Error("History could not be loaded");
    const items = await response.json();
    historyContainer.innerHTML = items.length ? items.map((item) => `
      <article class="history-card">
        <span class="verdict">${escapeHtml(item.verdict)}</span>
        <p>${escapeHtml(item.preview)}</p>
        <div class="history-meta"><strong style="color:${scoreColour(item.risk_score)}">${item.risk_score}/100</strong><span>${new Date(item.created_at + "Z").toLocaleString()}</span></div>
      </article>`).join("") : `<p class="muted">No messages analysed yet.</p>`;
  } catch (error) {
    historyContainer.innerHTML = `<p class="muted">${escapeHtml(error.message)}</p>`;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  button.disabled = true;
  button.textContent = "Analysing…";
  try {
    const response = await fetch("/api/analyse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: message.value }),
    });
    if (!response.ok) throw new Error("Analysis failed. Check the message and try again.");
    renderResult(await response.json());
    await loadHistory();
  } catch (error) {
    result.classList.add("empty");
    result.innerHTML = `<div class="empty-state"><h2>Unable to analyse</h2><p>${escapeHtml(error.message)}</p></div>`;
  } finally {
    button.disabled = false;
    button.textContent = "Analyse message";
  }
});

document.querySelector("#refresh-history").addEventListener("click", loadHistory);
loadHistory();

