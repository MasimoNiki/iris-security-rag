const form = document.querySelector("#query-form");
const questionInput = document.querySelector("#question");
const rerankInput = document.querySelector("#rerank");
const topKInput = document.querySelector("#top-k");
const askButton = document.querySelector("#ask-button");
const loadingState = document.querySelector("#loading-state");
const loadingMessage = document.querySelector("#loading-message");
const errorState = document.querySelector("#error-state");
const errorMessage = document.querySelector("#error-message");
const result = document.querySelector("#result");
const answerCard = document.querySelector("#answer-card");
const answerStatus = document.querySelector("#answer-status");
const answerElement = document.querySelector("#answer");
const resultBadges = document.querySelector("#result-badges");
const confidenceBar = document.querySelector("#confidence-bar");
const confidenceValue = document.querySelector("#confidence-value");
const latencyElement = document.querySelector("#latency");
const sourceCount = document.querySelector("#source-count");
const sourcesElement = document.querySelector("#sources");

const apiPrefix = document.body.dataset.apiPrefix || "/api/v1";
let activeController = null;
let loadingTimer = null;

const loadingMessages = [
  "Searching the knowledge base…",
  "Ranking the strongest evidence…",
  "Generating a grounded answer…",
];

function setLoading(isLoading) {
  askButton.disabled = isLoading;
  askButton.classList.toggle("loading", isLoading);
  loadingState.classList.toggle("hidden", !isLoading);

  window.clearInterval(loadingTimer);
  if (!isLoading) return;

  let index = 0;
  loadingMessage.textContent = loadingMessages[index];
  loadingTimer = window.setInterval(() => {
    index = Math.min(index + 1, loadingMessages.length - 1);
    loadingMessage.textContent = loadingMessages[index];
  }, 4500);
}

function formatMilliseconds(value) {
  if (!Number.isFinite(value)) return "—";
  if (value < 1000) return `${Math.round(value)} ms`;
  return `${(value / 1000).toFixed(value >= 10000 ? 1 : 2)} s`;
}

function formatScore(value) {
  return Number.isFinite(value) ? Number(value).toFixed(3) : null;
}

function appendBadge(label, active = false) {
  const badge = document.createElement("span");
  badge.className = `badge${active ? " active" : ""}`;
  badge.textContent = label;
  resultBadges.append(badge);
}

function renderAnswerText(answer, validCitationIds) {
  answerElement.replaceChildren();
  const parts = String(answer || "").split(/(\[\d+\])/g);

  for (const part of parts) {
    const match = /^\[(\d+)\]$/.exec(part);
    const citationId = match ? Number(match[1]) : null;

    if (citationId && validCitationIds.has(citationId)) {
      const link = document.createElement("a");
      link.className = "citation-link";
      link.href = `#source-${citationId}`;
      link.textContent = `[${citationId}]`;
      link.setAttribute("aria-label", `Jump to source ${citationId}`);
      answerElement.append(link);
    } else {
      answerElement.append(document.createTextNode(part));
    }
  }
}

function appendMetaItem(container, value) {
  if (!value) return;
  const item = document.createElement("span");
  item.textContent = value;
  container.append(item);
}

function appendScore(container, label, value) {
  const formatted = formatScore(value);
  if (formatted === null) return;

  const item = document.createElement("span");
  item.className = "score-pill";
  item.append(document.createTextNode(label));

  const strong = document.createElement("strong");
  strong.textContent = formatted;
  item.append(strong);
  container.append(item);
}

function createSourceCard(source) {
  const citationId = Number(source.citation_id);
  const card = document.createElement("article");
  card.className = "source-card";
  card.id = `source-${citationId}`;

  const topline = document.createElement("div");
  topline.className = "source-topline";

  const index = document.createElement("span");
  index.className = "source-index";
  index.textContent = `[${citationId}]`;

  const type = document.createElement("span");
  type.className = "source-type";
  type.textContent = String(source.source_type || "knowledge base").replaceAll(
    "_",
    " ",
  );
  topline.append(index, type);

  const title = document.createElement("h3");
  title.textContent = source.title || "Untitled source";

  const meta = document.createElement("div");
  meta.className = "source-meta";
  appendMetaItem(meta, source.section_title);
  appendMetaItem(meta, source.language?.toUpperCase());
  appendMetaItem(meta, `chunk ${source.chunk_id}`);

  const excerpt = document.createElement("p");
  excerpt.className = "source-excerpt";
  excerpt.textContent = source.content || "No excerpt available.";
  excerpt.title = source.content || "";

  const scores = document.createElement("div");
  scores.className = "source-scores";
  appendScore(scores, "score", source.score);
  appendScore(scores, "dense", source.dense_score);
  appendScore(scores, "lexical", source.lexical_score);
  appendScore(scores, "fusion", source.fusion_score);
  appendScore(scores, "reranker", source.reranker_score);

  card.append(topline, title, meta, excerpt, scores);
  return card;
}

function renderResult(data, clientLatencyMs) {
  const sources = Array.isArray(data.sources) ? data.sources : [];
  const metadata = data.metadata || {};
  const validCitationIds = new Set(
    sources.map((source) => Number(source.citation_id)).filter(Number.isFinite),
  );

  resultBadges.replaceChildren();
  appendBadge(metadata.retrieval_strategy || "unknown", true);
  appendBadge(
    metadata.reranker_applied ? "reranked" : "reranker not applied",
    Boolean(metadata.reranker_applied),
  );
  appendBadge(metadata.llm_provider || "unknown provider");
  if (metadata.fallback_used) appendBadge("fallback", true);

  answerStatus.classList.toggle("hidden", Boolean(data.is_answerable));
  answerStatus.textContent = data.is_answerable
    ? ""
    : "The retrieved evidence was not sufficient for a reliable answer.";
  answerCard.classList.toggle("not-answerable", !data.is_answerable);

  renderAnswerText(data.answer, validCitationIds);

  const confidence = Math.max(0, Math.min(1, Number(data.confidence) || 0));
  confidenceBar.style.width = `${Math.round(confidence * 100)}%`;
  confidenceValue.textContent = `${Math.round(confidence * 100)}%`;

  const backendLatency = Number(metadata.latency_ms);
  const latencyParts = [
    `API ${formatMilliseconds(backendLatency)}`,
    `browser ${formatMilliseconds(clientLatencyMs)}`,
  ];
  if (Number.isFinite(metadata.reranker_latency_ms)) {
    latencyParts.push(
      `reranker ${formatMilliseconds(Number(metadata.reranker_latency_ms))}`,
    );
  }
  latencyElement.textContent = latencyParts.join(" · ");

  sourcesElement.replaceChildren(...sources.map(createSourceCard));
  sourceCount.textContent = `${sources.length} source${sources.length === 1 ? "" : "s"}`;
  result.classList.remove("hidden");
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function extractErrorMessage(payload, status) {
  if (typeof payload?.detail === "string") return payload.detail;
  if (Array.isArray(payload?.detail)) {
    return payload.detail
      .map((item) => item.msg || "Invalid request")
      .join("; ");
  }
  return `The API returned HTTP ${status}. Check the FastAPI terminal for details.`;
}

async function submitQuestion() {
  const query = questionInput.value.trim();
  if (!query) {
    questionInput.focus();
    return;
  }

  activeController?.abort();
  activeController = new AbortController();
  errorState.classList.add("hidden");
  result.classList.add("hidden");
  setLoading(true);

  const requestBody = {
    query,
    top_k: Number(topKInput.value),
    strategy: form.elements.strategy.value,
    rerank: rerankInput.checked,
  };
  const startedAt = performance.now();

  try {
    const response = await fetch(`${apiPrefix}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
      signal: activeController.signal,
    });
    const payload = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(extractErrorMessage(payload, response.status));
    }

    renderResult(payload, performance.now() - startedAt);
  } catch (error) {
    if (error.name === "AbortError") return;
    errorMessage.textContent =
      error instanceof TypeError
        ? "Could not reach the API. Make sure FastAPI is running and try again."
        : error.message;
    errorState.classList.remove("hidden");
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  submitQuestion();
});

questionInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
    event.preventDefault();
    submitQuestion();
  }
});

document.querySelectorAll("[data-question]").forEach((button) => {
  button.addEventListener("click", () => {
    questionInput.value = button.dataset.question;
    questionInput.focus();
  });
});
