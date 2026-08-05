const refs = {
  readyPill: document.querySelector("#readyPill"),
  runnerMini: document.querySelector("#runnerMini"),
  runnerMiniLabel: document.querySelector("#runnerMiniLabel"),
  backend: document.querySelector("#backend"),
  backendInspector: document.querySelector("#backendInspector"),
  model: document.querySelector("#model"),
  modelInspector: document.querySelector("#modelInspector"),
  dependency: document.querySelector("#dependency"),
  sessionStatus: document.querySelector("#sessionStatus"),
  errors: document.querySelector("#errors"),
  missionForm: document.querySelector("#missionForm"),
  goal: document.querySelector("#goal"),
  userId: document.querySelector("#userId"),
  sessionId: document.querySelector("#sessionId"),
  runButton: document.querySelector("#runButton"),
  clearButton: document.querySelector("#clearButton"),
  refreshButton: document.querySelector("#refreshButton"),
  newMission: document.querySelector("#newMission"),
  truth: document.querySelector("#truth"),
  traceStatus: document.querySelector("#traceStatus"),
  conversationScroll: document.querySelector("#conversationScroll"),
  timeline: document.querySelector("#timeline"),
  finalOutput: document.querySelector("#finalOutput"),
  finalText: document.querySelector("#finalText"),
  agentList: document.querySelector("#agentList"),
  agentCount: document.querySelector("#agentCount"),
  eventMetric: document.querySelector("#eventMetric"),
  toolMetric: document.querySelector("#toolMetric"),
  errorMetric: document.querySelector("#errorMetric"),
  finalMetric: document.querySelector("#finalMetric"),
};

const displayNames = {
  orion: "ORION",
  vigia: "VIGÍA",
  nyx_7: "NYX-7",
  vega: "VEGA",
  atlas_9: "ATLAS-9",
  forja_core: "FORJA Ω · CORE",
  forja_test: "FORJA Ω · TEST",
  forja_ux: "FORJA Ω · UX",
  spark: "SPARK",
  recursor_omega: "RECURSOR-Ω",
  nemesis_omega: "NÉMESIS-Ω",
  helix_8: "HELIX-8",
  aureus_7: "AUREUS-7",
  bastion: "BASTION",
  echo: "ECHO",
  rift: "RIFT",
  vanta_0: "VANTA-0",
  kira: "KIRA Ω",
};

const roleNames = {
  orion: "Contrato de misión",
  vigia: "Evidencia y procedencia",
  nyx_7: "Riesgos y contradicciones",
  vega: "Pruebas y umbrales",
  atlas_9: "Diseño de candidatos",
  forja_core: "Arquitectura y contratos",
  forja_test: "Pruebas y regresiones",
  forja_ux: "Experiencia y demostración",
  spark: "Herramientas deterministas",
  recursor_omega: "Auditoría evolutiva",
  nemesis_omega: "Falsificación implacable",
  helix_8: "Puntuación basada en evidencia",
  aureus_7: "Sostenibilidad y capital",
  bastion: "Seguridad y aprobaciones",
  echo: "Trazabilidad",
  rift: "Desbloqueos legítimos",
  vanta_0: "Rutas no convencionales",
  kira: "Decisión final",
};

let readiness = null;
let topology = null;
let running = false;
let eventCount = 0;
let toolCount = 0;
let errorCount = 0;
let finalObserved = false;
let outputKeyOwners = new Map();
let knownAgents = new Set();

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

function createElement(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = text(content);
  return element;
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

function normalizeName(value) {
  return text(value)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function initials(name) {
  const label = displayNames[name] || name || "Ω";
  if (name === "kira") return "K";
  if (name.startsWith("forja_")) return "F";
  if (name === "recursor_omega") return "R";
  if (name === "nemesis_omega") return "N";
  return label.replace(/[^A-ZÁÉÍÓÚÑ0-9]/gi, "").slice(0, 2).toUpperCase() || "Ω";
}

function flattenTopology(payload) {
  const agents = [];
  outputKeyOwners = new Map();
  for (const stage of payload?.stages || []) {
    if (Array.isArray(stage.sub_agents)) {
      for (const agent of stage.sub_agents) {
        agents.push({ ...agent, stage: stage.name });
        if (agent.output_key) outputKeyOwners.set(agent.output_key, agent.name);
      }
    } else if (stage.type === "LlmAgent") {
      agents.push({ name: stage.name, output_key: stage.output_key, stage: stage.name });
      if (stage.output_key) outputKeyOwners.set(stage.output_key, stage.name);
    }
  }
  return agents;
}

function renderAgents(payload) {
  const agents = flattenTopology(payload);
  knownAgents = new Set(agents.map((agent) => agent.name));
  refs.agentCount.textContent = `${agents.length} agentes`;
  refs.agentList.replaceChildren();

  for (const agent of agents) {
    const row = createElement("div", "agent-row");
    row.dataset.agent = agent.name;
    row.append(createElement("div", "agent-avatar", initials(agent.name)));
    const copy = createElement("div", "agent-copy");
    copy.append(createElement("strong", "", displayNames[agent.name] || agent.name));
    copy.append(createElement("span", "", roleNames[agent.name] || agent.stage || "Especialista"));
    row.append(copy);
    row.append(createElement("i", "agent-dot"));
    refs.agentList.append(row);
  }
}

function findAgentName(author) {
  const normalized = normalizeName(author);
  if (knownAgents.has(normalized)) return normalized;
  for (const agent of knownAgents) {
    if (normalized.includes(agent) || agent.includes(normalized)) return agent;
  }
  return null;
}

function setAgentStatus(name, status) {
  if (!name) return;
  const row = refs.agentList.querySelector(`[data-agent="${name}"]`);
  if (!row) return;
  row.classList.remove("running", "done", "error", "active");
  if (status) row.classList.add(status);
  if (status === "running") row.classList.add("active");
}

function resetAgentStatuses() {
  for (const row of refs.agentList.querySelectorAll(".agent-row")) {
    row.classList.remove("running", "done", "error", "active");
  }
}

function completeAgentsFromState(stateDelta) {
  if (!stateDelta || typeof stateDelta !== "object") return;
  for (const key of Object.keys(stateDelta)) {
    const owner = outputKeyOwners.get(key);
    if (owner) setAgentStatus(owner, "done");
  }
}

function updateMetrics() {
  refs.eventMetric.textContent = String(eventCount);
  refs.toolMetric.textContent = String(toolCount);
  refs.errorMetric.textContent = String(errorCount);
  refs.finalMetric.textContent = finalObserved ? "Sí" : "No";
}

function heroNode() {
  const hero = createElement("section", "hero");
  const mark = createElement("div", "hero-mark", "Ω");
  const title = createElement("h1", "", "¿Qué misión debe resolver la Constelación?");
  const copy = createElement(
    "p",
    "",
    "ORION define la victoria; evidencia y FORJA trabajan en paralelo; SPARK ejecuta; RECURSOR y NÉMESIS intentan destruir los falsos éxitos; HELIX puntúa la prueba; KIRA decide.",
  );
  const tags = createElement("div", "hero-tags");
  for (const label of [
    "18 agentes reales",
    "4 escuadrones paralelos",
    "Herramientas deterministas",
    "Sin chain-of-thought público",
  ]) {
    tags.append(createElement("span", "", label));
  }
  hero.append(mark, title, copy, tags);
  return hero;
}

function clearTrace({ keepSession = true } = {}) {
  eventCount = 0;
  toolCount = 0;
  errorCount = 0;
  finalObserved = false;
  updateMetrics();
  resetAgentStatuses();
  refs.finalText.textContent = "";
  refs.finalOutput.classList.remove("visible");
  refs.timeline.replaceChildren(heroNode());
  refs.traceStatus.textContent = readiness?.ready
    ? "Runner real listo para una misión."
    : "Configura Gemini o Vertex AI para ejecutar.";
  if (!keepSession) {
    refs.sessionId.value = "";
    refs.sessionStatus.textContent = "Nueva";
  }
}

function appendUserMessage(goal) {
  const article = createElement("article", "message user");
  const body = createElement("div", "message-body");
  const head = createElement("div", "message-head");
  head.append(createElement("strong", "", "Tú"));
  head.append(createElement("span", "", shortTime()));
  body.append(head, createElement("p", "message-copy", goal));
  article.append(body, createElement("div", "message-avatar", "AG"));
  refs.timeline.append(article);
}

function kindLabel(kind) {
  const labels = {
    session: "Sesión",
    model: "Modelo",
    tool_call: "Herramienta",
    tool_result: "Resultado",
    state: "Estado",
    final: "Respuesta final",
    complete: "Completado",
    error: "Error",
    event: "Evento",
  };
  return labels[kind] || kind.replaceAll("_", " ");
}

function kindGlyph(kind) {
  const glyphs = {
    session: "Ω",
    model: "✦",
    tool_call: "→",
    tool_result: "✓",
    state: "Δ",
    final: "K",
    complete: "✓",
    error: "!",
  };
  return glyphs[kind] || "·";
}

function addStructuredBlock(parent, title, value) {
  if (value === null || value === undefined) return;
  if (Array.isArray(value) && value.length === 0) return;
  if (!Array.isArray(value) && typeof value === "object" && Object.keys(value).length === 0) return;
  const block = createElement("div", "structured");
  block.append(createElement("strong", "", title));
  block.append(createElement("pre", "", pretty(value)));
  parent.append(block);
}

function appendEvent(record) {
  eventCount += 1;
  const calls = record.tool_calls || [];
  toolCount += calls.length;
  if (record.kind === "error" || record.error_message || record.error_code) errorCount += 1;
  if (record.is_final || record.kind === "final") finalObserved = true;
  updateMetrics();

  const authorName = findAgentName(record.author);
  if (authorName) setAgentStatus(authorName, record.kind === "error" ? "error" : "running");
  completeAgentsFromState(record.state_delta);

  const article = createElement("article", "message assistant");
  article.append(createElement("div", "message-avatar", initials(authorName || "orpheus")));

  const body = createElement("div", "message-body");
  const head = createElement("div", "message-head");
  head.append(createElement("strong", "", displayNames[authorName] || record.author || "ORPHEUS Ω"));
  head.append(createElement("span", "", shortTime(record.timestamp)));
  body.append(head);

  const visibleTexts = [];
  if (record.message) visibleTexts.push(record.message);
  for (const item of record.texts || []) visibleTexts.push(item);
  if (visibleTexts.length) body.append(createElement("p", "message-copy", visibleTexts.join("\n\n")));

  const kind = record.kind || "event";
  const card = createElement("section", `event-card ${kind}`);
  const summary = createElement("div", "event-summary");
  const kindElement = createElement("span", "event-kind");
  kindElement.append(createElement("i", "", kindGlyph(kind)));
  kindElement.append(document.createTextNode(kindLabel(kind)));
  summary.append(kindElement);
  summary.append(createElement("span", "event-seq", `#${record.sequence ?? eventCount}`));
  card.append(summary);

  const content = createElement("div", "event-content");
  for (const call of calls) {
    addStructuredBlock(content, `Llamada · ${call.name || "herramienta"}`, call.args || {});
  }
  for (const result of record.tool_results || []) {
    addStructuredBlock(content, `Resultado · ${result.name || "herramienta"}`, result.response || {});
  }
  addStructuredBlock(content, "Cambio de estado", record.state_delta);
  addStructuredBlock(content, "Artefactos", record.artifact_delta);
  addStructuredBlock(content, "Adjuntos seguros", record.attachments);
  if (record.error_message || record.error_code) {
    addStructuredBlock(content, "Fallo auditable", {
      code: record.error_code || null,
      message: record.error_message || "Error de ejecución",
    });
  }
  if (!content.childElementCount) {
    content.append(createElement("div", "structured", "Evento registrado sin carga pública adicional."));
  }
  card.append(content);
  body.append(card);
  article.append(body);
  refs.timeline.append(article);

  if (record.session_id) {
    refs.sessionStatus.textContent = record.session_id;
    refs.sessionId.value = record.session_id;
  }
  if (record.is_final && (record.texts || []).length) {
    refs.finalText.textContent = record.texts.join("\n");
    refs.finalOutput.classList.add("visible");
    if (authorName) setAgentStatus(authorName, "done");
  }
  if (kind === "complete") {
    for (const row of refs.agentList.querySelectorAll(".agent-row.running")) {
      row.classList.remove("running", "active");
      row.classList.add("done");
    }
    refs.traceStatus.textContent = record.final_response_observed
      ? "Misión completada con respuesta final observada."
      : "Misión terminada sin una respuesta final identificable.";
  }

  refs.conversationScroll.scrollTo({
    top: refs.conversationScroll.scrollHeight,
    behavior: "smooth",
  });
}

function setRunning(value) {
  running = value;
  refs.runButton.disabled = value || !readiness?.ready;
  refs.runButton.textContent = value ? "■" : "↑";
  refs.goal.disabled = value;
  refs.userId.disabled = value;
  refs.sessionId.disabled = value;
  refs.clearButton.disabled = value;
  refs.newMission.disabled = value;
  refs.refreshButton.disabled = value;
}

async function loadTopology() {
  try {
    const response = await fetch("/architecture/agents", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Topología ${response.status}`);
    topology = await response.json();
    renderAgents(topology);
  } catch (error) {
    refs.agentCount.textContent = "error";
    refs.agentList.replaceChildren();
    const row = createElement("div", "agent-row error");
    row.append(createElement("div", "agent-avatar", "!"));
    const copy = createElement("div", "agent-copy");
    copy.append(createElement("strong", "", "Topología no disponible"));
    copy.append(createElement("span", "", error.message));
    row.append(copy, createElement("i", "agent-dot"));
    refs.agentList.append(row);
  }
}

async function loadReadiness() {
  refs.readyPill.classList.remove("ready");
  refs.readyPill.querySelector("span").textContent = "Verificando";
  refs.runnerMini.classList.remove("ready");
  refs.runnerMiniLabel.textContent = "Verificando configuración";
  try {
    const response = await fetch("/adk/readiness", { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error(`Error ${response.status}`);
    readiness = await response.json();

    const backend = readiness.backend || "—";
    const model = readiness.model || "ORPHEUS Ω";
    refs.backend.textContent = backend;
    refs.backendInspector.textContent = backend;
    refs.model.textContent = model;
    refs.modelInspector.textContent = model;
    refs.dependency.textContent = readiness.dependency_available ? "Instalado" : "No instalado";
    refs.truth.textContent = readiness.truth_boundary || refs.truth.textContent;
    refs.readyPill.classList.toggle("ready", Boolean(readiness.ready));
    refs.readyPill.querySelector("span").textContent = readiness.ready ? "Runner listo" : "No configurado";
    refs.runnerMini.classList.toggle("ready", Boolean(readiness.ready));
    refs.runnerMiniLabel.textContent = readiness.ready ? "Gemini/Vertex preparado" : "Requiere credenciales reales";
    refs.errors.replaceChildren();
    for (const error of readiness.validation_errors || []) {
      refs.errors.append(createElement("li", "", error));
    }
    refs.traceStatus.textContent = readiness.ready
      ? "Runner real listo para una misión."
      : "Modo honesto: no se simulará una ejecución ADK.";
    refs.runButton.disabled = !readiness.ready;
  } catch (error) {
    readiness = { ready: false };
    refs.readyPill.querySelector("span").textContent = "Error";
    refs.runnerMiniLabel.textContent = "Estado no disponible";
    refs.errors.replaceChildren(createElement("li", "", error.message));
    refs.traceStatus.textContent = "No fue posible consultar el Runner.";
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

  if (buffer.trim()) {
    try {
      appendEvent(JSON.parse(buffer));
    } catch {
      appendEvent({
        kind: "error",
        author: "browser",
        timestamp: new Date().toISOString(),
        message: "El último evento NDJSON no pudo analizarse.",
        error_message: buffer.slice(0, 500),
      });
    }
  }
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
  refs.timeline.replaceChildren();
  appendUserMessage(goal);
  setRunning(true);
  refs.traceStatus.textContent = "Conectando con Google ADK…";
  setAgentStatus("orion", "running");

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
      message: "La misión no pudo completarse.",
      error_message: error.message,
    });
    refs.traceStatus.textContent = "Ejecución detenida por un fallo auditable.";
  } finally {
    setRunning(false);
  }
});

refs.clearButton.addEventListener("click", () => clearTrace());
refs.newMission.addEventListener("click", () => {
  clearTrace({ keepSession: false });
  refs.goal.focus();
});
refs.refreshButton.addEventListener("click", loadReadiness);
refs.goal.addEventListener("input", () => {
  refs.goal.style.height = "auto";
  refs.goal.style.height = `${Math.min(refs.goal.scrollHeight, 170)}px`;
});
refs.goal.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    refs.missionForm.requestSubmit();
  }
});

clearTrace();
Promise.all([loadTopology(), loadReadiness()]);
