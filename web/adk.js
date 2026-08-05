const refs = {
  readyPill: document.querySelector("#readyPill"),
  backend: document.querySelector("#backend"),
  model: document.querySelector("#model"),
  dependency: document.querySelector("#dependency"),
  sessionStatus: document.querySelector("#sessionStatus"),
  errors: document.querySelector("#errors"),
  missionForm: document.querySelector("#missionForm"),
  goal: document.querySelector("#goal"),
  userId: document.querySelector("#userId"),
  sessionId: document.querySelector("#sessionId"),
  runButton: document.querySelector("#runButton"),
  clearButton: document.querySelector("#clearButton"),
  truth: document.querySelector("#truth"),
  traceStatus: document.querySelector("#traceStatus"),
  counter: document.querySelector("#counter"),
  timeline: document.querySelector("#timeline"),
  finalOutput: document.querySelector("#finalOutput"),
  finalText: document.querySelector("#finalText"),
};

let readiness = null;
let running = false;
let eventCount = 0;

function text(value) {
  return value === null || value === undefined ? "" : String(value);
}

function pretty(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return text(value);
  }
}

function shortTime(value) {
  const date = new Date(value || Date.now());
  if (Number.isNaN(date.getTime())) return "ahora";
  return new Intl.DateTimeFormat("es-DO", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(date);
}

function createElement(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = text(content);
  return element;
}

function eventBadge(record) {
  const labels = {
    session: "Ω",
    model: "LLM",
    tool_call: "→",
    tool_result: "✓",
    state: "Δ",
    final: "K",
    complete: "✓",
    error: "!",
    event: "·",
  };
  return labels[record.kind] || "·";
}

function addStructuredBlock(card, title, value) {
  if (value === null || value === undefined) return;
  if (Array.isArray(value) && value.length === 0) return;
  if (!Array.isArray(value) && typeof value === "object" && Object.keys(value).length === 0) return;

  const block = createElement("div", "tool");
  block.append(createElement("strong", "", title));
  block.append(createElement("pre", "", pretty(value)));
  card.append(block);
}

function appendEvent(record) {
  if (eventCount === 0) refs.timeline.replaceChildren();
  eventCount += 1;
  refs.counter.textContent = `${eventCount} ${eventCount === 1 ? "evento" : "eventos"}`;

  const kind = record.kind || "event";
  const row = createElement("article", `event ${kind}`);
  row.append(createElement("div", "event-icon", eventBadge(record)));

  const card = createElement("div", "event-card");
  const meta = createElement("div", "event-meta");
  const identity = createElement("div");
  identity.append(createElement("strong", "", record.author || "system"));
  identity.append(createElement("span", "kind", kind.replaceAll("_", " ")));
  meta.append(identity);
  meta.append(createElement("span", "", `#${record.sequence ?? eventCount} · ${shortTime(record.timestamp)}`));
  card.append(meta);

  if (record.message) card.append(createElement("p", "text-block", record.message));
  for (const item of record.texts || []) card.append(createElement("p", "text-block", item));

  for (const call of record.tool_calls || []) {
    addStructuredBlock(card, `Llamada · ${call.name || "herramienta"}`, call.args || {});
  }
  for (const result of record.tool_results || []) {
    addStructuredBlock(card, `Resultado · ${result.name || "herramienta"}`, result.response || {});
  }

  addStructuredBlock(card, "Cambio de estado", record.state_delta);
  addStructuredBlock(card, "Artefactos", record.artifact_delta);
  addStructuredBlock(card, "Adjuntos seguros", record.attachments);

  if (record.error_message || record.error_code) {
    row.classList.add("error");
    addStructuredBlock(card, "Error", {
      code: record.error_code || null,
      message: record.error_message || "Error de ejecución",
    });
  }

  row.append(card);
  refs.timeline.append(row);
  row.scrollIntoView({ behavior: "smooth", block: "nearest" });

  if (record.session_id) {
    refs.sessionStatus.textContent = record.session_id;
    refs.sessionId.value = record.session_id;
  }
  if (record.is_final && (record.texts || []).length) {
    refs.finalText.textContent = record.texts.join("\n");
    refs.finalOutput.classList.add("visible");
  }
  if (kind === "complete") {
    refs.traceStatus.textContent = record.final_response_observed
      ? "Invocación completada con respuesta final observada."
      : "Invocación completada sin una respuesta final identificable.";
  }
}

function clearTrace() {
  eventCount = 0;
  refs.counter.textContent = "0 eventos";
  refs.finalText.textContent = "";
  refs.finalOutput.classList.remove("visible");
  refs.traceStatus.textContent = readiness?.ready
    ? "Lista para ejecutar el Runner real."
    : "Configura Gemini o Vertex AI para ejecutar.";
  const empty = createElement("div", "empty");
  const copy = createElement("div");
  copy.append(createElement("strong", "", "Aquí aparecerá la ejecución real."));
  copy.append(document.createTextNode("La consola preservará la secuencia completa de eventos entregada por Google ADK."));
  empty.append(copy);
  refs.timeline.replaceChildren(empty);
}

function setRunning(value) {
  running = value;
  refs.runButton.disabled = value || !readiness?.ready;
  refs.runButton.textContent = value ? "Ejecutando…" : "Ejecutar ADK real";
  refs.goal.disabled = value;
  refs.userId.disabled = value;
  refs.sessionId.disabled = value;
  refs.clearButton.disabled = value;
}

async function loadReadiness() {
  try {
    const response = await fetch("/adk/readiness", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Error ${response.status}`);
    readiness = await response.json();

    refs.backend.textContent = readiness.backend || "—";
    refs.model.textContent = readiness.model || "—";
    refs.dependency.textContent = readiness.dependency_available ? "Instalado" : "No instalado";
    refs.truth.textContent = readiness.truth_boundary || refs.truth.textContent;
    refs.readyPill.classList.toggle("ready", Boolean(readiness.ready));
    refs.readyPill.querySelector("span").textContent = readiness.ready ? "Listo" : "No configurado";
    refs.errors.replaceChildren();
    for (const error of readiness.validation_errors || []) {
      refs.errors.append(createElement("li", "", error));
    }
    refs.traceStatus.textContent = readiness.ready
      ? "Runner real listo para recibir una misión."
      : "La consola permanece honesta: no ejecutará una simulación ADK.";
    refs.runButton.disabled = !readiness.ready;
  } catch (error) {
    readiness = { ready: false };
    refs.readyPill.querySelector("span").textContent = "Error";
    refs.errors.replaceChildren(createElement("li", "", error.message));
    refs.traceStatus.textContent = "No fue posible consultar el estado del Runner.";
    refs.runButton.disabled = true;
  }
}

async function readNdjson(response) {
  if (!response.body) throw new Error("El navegador no recibió un flujo de eventos.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        appendEvent(JSON.parse(line));
      } catch {
        appendEvent({
          kind: "error",
          author: "browser",
          timestamp: new Date().toISOString(),
          message: "Se recibió un evento NDJSON inválido.",
          error_message: line.slice(0, 500),
        });
      }
    }
    if (done) break;
  }

  if (buffer.trim()) appendEvent(JSON.parse(buffer));
}

refs.missionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (running || !readiness?.ready) return;
  const goal = refs.goal.value.trim();
  if (!goal) {
    refs.traceStatus.textContent = "Escribe una misión antes de ejecutar.";
    refs.goal.focus();
    return;
  }

  clearTrace();
  setRunning(true);
  refs.traceStatus.textContent = "Conectando con Google ADK…";

  try {
    const response = await fetch("/adk/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/x-ndjson" },
      body: JSON.stringify({
        goal,
        user_id: refs.userId.value.trim() || null,
        session_id: refs.sessionId.value.trim() || null,
      }),
    });

    if (!response.ok) {
      let message = `Error ${response.status}`;
      try {
        const payload = await response.json();
        message = payload.detail || message;
      } catch {}
      throw new Error(message);
    }

    refs.traceStatus.textContent = "Recibiendo eventos reales del Runner…";
    await readNdjson(response);
  } catch (error) {
    appendEvent({
      kind: "error",
      author: "ORPHEUS",
      timestamp: new Date().toISOString(),
      message: "La invocación no pudo completarse.",
      error_message: error.message,
    });
    refs.traceStatus.textContent = "Ejecución detenida por error.";
  } finally {
    setRunning(false);
  }
});

refs.clearButton.addEventListener("click", clearTrace);

clearTrace();
loadReadiness();
