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
  orion: "Define objetivo, restricciones y victoria",
  vigia: "Busca evidencia y verifica procedencia",
  nyx_7: "Ataca riesgos, contradicciones y falsas certezas",
  vega: "Diseña pruebas, métricas y umbrales",
  atlas_9: "Construye y compara candidatos técnicos",
  forja_core: "Endurece arquitectura y contratos",
  forja_test: "Diseña regresiones y fallos inyectados",
  forja_ux: "Convierte la ejecución en una prueba entendible",
  spark: "Ejecuta herramientas y verificadores",
  recursor_omega: "Detecta deuda, reincidencias y cierres falsos",
  nemesis_omega: "Intenta falsificar la ruta preferida",
  helix_8: "Puntúa únicamente evidencia demostrada",
  aureus_7: "Evalúa beneficio, capital y sostenibilidad",
  bastion: "Aplica seguridad y aprobaciones humanas",
  echo: "Conserva trazabilidad y límites",
  rift: "Busca rutas legítimas ante bloqueos",
  vanta_0: "Explora alternativas no convencionales",
  kira: "Integra evidencia y toma la decisión final",
};

const activityNames = {
  orion: "Construyendo el contrato de misión",
  vigia: "Investigando fuentes y procedencia",
  nyx_7: "Auditando riesgos y contradicciones",
  vega: "Definiendo pruebas y criterios de rechazo",
  atlas_9: "Generando y comparando candidatos",
  forja_core: "Endureciendo la solución",
  forja_test: "Diseñando pruebas de cierre",
  forja_ux: "Preparando una entrega comprensible",
  spark: "Ejecutando herramientas verificables",
  recursor_omega: "Buscando defectos y deuda técnica",
  nemesis_omega: "Intentando destruir el falso éxito",
  helix_8: "Calculando la puntuación demostrable",
  aureus_7: "Evaluando beneficio y sostenibilidad",
  bastion: "Aplicando límites y aprobaciones",
  echo: "Construyendo el registro auditable",
  rift: "Abriendo una ruta alternativa",
  vanta_0: "Explorando una opción no convencional",
  kira: "Integrando la decisión final",
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
let agentCapsules = new Map();
let candidateSignatures = new Set();
let researchSignatures = new Set();

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
    row.append(copy, createElement("i", "agent-dot"));
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
  if (row) {
    row.classList.remove("running", "done", "error", "active");
    if (status) row.classList.add(status);
    if (status === "running") row.classList.add("active");
  }

  const capsule = agentCapsules.get(name);
  if (capsule) {
    capsule.article.dataset.status = status || "idle";
    capsule.status.textContent =
      status === "done" ? "Entrega completada" :
      status === "error" ? "Fallo detectado" :
      status === "running" ? "Trabajando ahora" : "En espera";
  }
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
  hero.append(createElement("div", "hero-mark", "Ω"));
  hero.append(createElement("h1", "", "¿Qué misión debe resolver la Constelación?"));
  hero.append(createElement(
    "p",
    "",
    "La interfaz resume trabajo público verificable. El razonamiento privado permanece protegido; aquí verás acciones, herramientas, evidencia, candidatos, rechazos y decisiones.",
  ));
  const tags = createElement("div", "hero-tags");
  for (const label of [
    "18 agentes ADK reales",
    "Cápsulas de trabajo",
    "Candidatos comparables",
    "Crossref en vivo",
    "Markdown legible",
  ]) {
    tags.append(createElement("span", "", label));
  }
  hero.append(tags);
  return hero;
}

function clearTrace({ keepSession = true } = {}) {
  eventCount = 0;
  toolCount = 0;
  errorCount = 0;
  finalObserved = false;
  agentCapsules = new Map();
  candidateSignatures = new Set();
  researchSignatures = new Set();
  updateMetrics();
  resetAgentStatuses();
  refs.finalText.replaceChildren();
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
  head.append(createElement("strong", "", "Tú"), createElement("span", "", shortTime()));
  body.append(head, createElement("p", "message-copy", goal));
  article.append(body, createElement("div", "message-avatar", "AG"));
  refs.timeline.append(article);
}

function appendSystemNotice(message, tone = "neutral") {
  const notice = createElement("section", `system-notice ${tone}`);
  notice.append(createElement("span", "system-notice-icon", tone === "error" ? "!" : "Ω"));
  notice.append(createElement("p", "", message));
  refs.timeline.append(notice);
}

function safeHref(value) {
  try {
    const url = new URL(value, window.location.origin);
    if (!["http:", "https:", "mailto:"].includes(url.protocol)) return "#";
    return url.href;
  } catch {
    return "#";
  }
}

function inlineMarkdown(raw) {
  const tokens = [];
  let source = text(raw).replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, href) => {
    const token = `\u0000LINK${tokens.length}\u0000`;
    tokens.push(`<a href="${escapeHtml(safeHref(href))}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`);
    return token;
  });
  source = escapeHtml(source);
  source = source
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/__([^_]+)__/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>")
    .replace(/(^|[\s(])_([^_\n]+)_/g, "$1<em>$2</em>");
  tokens.forEach((html, index) => {
    source = source.replace(`\u0000LINK${index}\u0000`, html);
  });
  return source;
}

function escapeHtml(value) {
  return text(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function isTableSeparator(line) {
  return /^\s*\|?[\s:|-]+\|[\s:|-|]*\s*$/.test(line);
}

function splitTableRow(line) {
  return line.trim().replace(/^\||\|$/g, "").split("|").map((cell) => cell.trim());
}

function renderMarkdown(source) {
  const root = createElement("div", "markdown-body");
  const lines = text(source).replace(/\r\n?/g, "\n").split("\n");
  let index = 0;

  const appendParagraph = (parts) => {
    const p = createElement("p");
    p.innerHTML = inlineMarkdown(parts.join(" ").trim());
    root.append(p);
  };

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }

    if (/^```/.test(line.trim())) {
      const language = line.trim().slice(3).trim();
      const code = [];
      index += 1;
      while (index < lines.length && !/^```/.test(lines[index].trim())) {
        code.push(lines[index]);
        index += 1;
      }
      index += 1;
      const pre = createElement("pre", "code-block");
      if (language) pre.dataset.language = language;
      pre.append(createElement("code", "", code.join("\n")));
      root.append(pre);
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      const node = createElement(`h${Math.min(heading[1].length + 1, 5)}`);
      node.innerHTML = inlineMarkdown(heading[2]);
      root.append(node);
      index += 1;
      continue;
    }

    if (/^\s*---+\s*$/.test(line)) {
      root.append(document.createElement("hr"));
      index += 1;
      continue;
    }

    if (line.includes("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
      const table = createElement("div", "table-scroll");
      const tableNode = document.createElement("table");
      const headers = splitTableRow(line);
      const thead = document.createElement("thead");
      const headerRow = document.createElement("tr");
      headers.forEach((cell) => {
        const th = document.createElement("th");
        th.innerHTML = inlineMarkdown(cell);
        headerRow.append(th);
      });
      thead.append(headerRow);
      tableNode.append(thead);
      index += 2;
      const tbody = document.createElement("tbody");
      while (index < lines.length && lines[index].includes("|") && lines[index].trim()) {
        const tr = document.createElement("tr");
        splitTableRow(lines[index]).forEach((cell) => {
          const td = document.createElement("td");
          td.innerHTML = inlineMarkdown(cell);
          tr.append(td);
        });
        tbody.append(tr);
        index += 1;
      }
      tableNode.append(tbody);
      table.append(tableNode);
      root.append(table);
      continue;
    }

    if (/^\s*>\s?/.test(line)) {
      const quote = [];
      while (index < lines.length && /^\s*>\s?/.test(lines[index])) {
        quote.push(lines[index].replace(/^\s*>\s?/, ""));
        index += 1;
      }
      const blockquote = document.createElement("blockquote");
      blockquote.innerHTML = inlineMarkdown(quote.join(" "));
      root.append(blockquote);
      continue;
    }

    if (/^\s*[-*+]\s+/.test(line) || /^\s*\d+\.\s+/.test(line)) {
      const ordered = /^\s*\d+\.\s+/.test(line);
      const list = document.createElement(ordered ? "ol" : "ul");
      const pattern = ordered ? /^\s*\d+\.\s+/ : /^\s*[-*+]\s+/;
      while (index < lines.length && pattern.test(lines[index])) {
        const li = document.createElement("li");
        li.innerHTML = inlineMarkdown(lines[index].replace(pattern, ""));
        list.append(li);
        index += 1;
      }
      root.append(list);
      continue;
    }

    const paragraph = [line];
    index += 1;
    while (
      index < lines.length &&
      lines[index].trim() &&
      !/^(#{1,4})\s+/.test(lines[index]) &&
      !/^```/.test(lines[index].trim()) &&
      !/^\s*[-*+]\s+/.test(lines[index]) &&
      !/^\s*\d+\.\s+/.test(lines[index]) &&
      !/^\s*>\s?/.test(lines[index]) &&
      !(lines[index].includes("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1]))
    ) {
      paragraph.push(lines[index]);
      index += 1;
    }
    appendParagraph(paragraph);
  }

  return root;
}

function stripMarkdown(value) {
  return text(value)
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
    .replace(/[#*_`>|]/g, " ")
    .replace(/\$\\?([^$]+)\$/g, "$1")
    .replace(/\s+/g, " ")
    .trim();
}

function truncate(value, limit = 260) {
  const cleaned = stripMarkdown(value);
  return cleaned.length > limit ? `${cleaned.slice(0, limit - 1)}…` : cleaned;
}

function capsuleFor(agentName, timestamp) {
  if (agentCapsules.has(agentName)) return agentCapsules.get(agentName);

  const article = createElement("article", "agent-capsule");
  article.dataset.agent = agentName;
  article.dataset.status = "running";

  const header = createElement("header", "capsule-header");
  header.append(createElement("div", "capsule-avatar", initials(agentName)));
  const identity = createElement("div", "capsule-identity");
  identity.append(createElement("strong", "", displayNames[agentName] || agentName));
  identity.append(createElement("span", "", roleNames[agentName] || "Agente especialista"));
  const status = createElement("span", "capsule-status", "Trabajando ahora");
  header.append(identity, status);

  const activity = createElement("div", "capsule-activity");
  activity.append(createElement("i", "activity-pulse"));
  activity.append(createElement("span", "", activityNames[agentName] || "Procesando una entrega verificable"));

  const badges = createElement("div", "capsule-badges");
  badges.append(createElement("span", "capsule-badge public", "Actividad pública"));
  badges.append(createElement("span", "capsule-badge protected", "Razonamiento privado protegido"));

  const preview = createElement("p", "capsule-preview", "Esperando la primera salida pública…");
  const tools = createElement("div", "capsule-tools");

  const details = document.createElement("details");
  details.className = "capsule-details";
  details.hidden = true;
  const summary = document.createElement("summary");
  summary.textContent = "Ver entrega completa";
  const rendered = createElement("div", "capsule-rendered");
  details.append(summary, rendered);

  const footer = createElement("footer", "capsule-footer");
  footer.append(createElement("span", "", `Iniciado ${shortTime(timestamp)}`));
  const evidence = createElement("span", "", "0 evidencias · 0 herramientas");
  footer.append(evidence);

  article.append(header, activity, badges, preview, tools, details, footer);
  refs.timeline.append(article);

  const capsule = {
    article,
    status,
    activity: activity.querySelector("span"),
    preview,
    tools,
    details,
    rendered,
    evidence,
    text: "",
    evidenceCount: 0,
    toolCount: 0,
  };
  agentCapsules.set(agentName, capsule);
  return capsule;
}

function updateCapsuleMetrics(capsule) {
  capsule.evidence.textContent = `${capsule.evidenceCount} evidencias · ${capsule.toolCount} herramientas`;
}

function addToolChip(capsule, label, tone = "running") {
  const chip = createElement("span", `tool-chip ${tone}`, label);
  capsule.tools.append(chip);
}

function unwrapPayload(value) {
  let payload = value;
  for (let index = 0; index < 3; index += 1) {
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) break;
    if (payload.result && typeof payload.result === "object") payload = payload.result;
    else if (payload.output && typeof payload.output === "object") payload = payload.output;
    else if (payload.value && typeof payload.value === "object") payload = payload.value;
    else break;
  }
  return payload;
}

function findResearchPayload(value) {
  const payload = unwrapPayload(value);
  if (!payload || typeof payload !== "object") return null;
  if (Array.isArray(payload.results) && payload.provider) return payload;
  if (payload.live_research && typeof payload.live_research === "object") return payload.live_research;
  return null;
}

function renderResearchBoard(payload, agentName = "vigia") {
  if (!payload || !Array.isArray(payload.results)) return false;
  const signature = `${payload.provider || "research"}:${payload.query || ""}:${payload.retrieved_at || ""}`;
  if (researchSignatures.has(signature)) return true;
  researchSignatures.add(signature);

  const board = createElement("section", "research-board");
  const head = createElement("div", "board-heading");
  const copy = createElement("div");
  copy.append(createElement("span", "eyebrow", "BÚSQUEDA EXTERNA COMPLETADA"));
  copy.append(createElement("h2", "", `${payload.result_count ?? payload.results.length} fuentes encontradas`));
  copy.append(createElement("p", "", `Consulta: ${payload.query || "sin consulta registrada"} · ${payload.provider || "fuente pública"}`));
  head.append(copy, createElement("span", `board-status ${payload.status === "ok" ? "ok" : "warning"}`, payload.status === "ok" ? "Evidencia recuperada" : "No disponible"));
  board.append(head);

  if (!payload.results.length) {
    board.append(createElement("p", "empty-board", payload.message || payload.reason || "La búsqueda no devolvió registros."));
  } else {
    const grid = createElement("div", "research-grid");
    payload.results.slice(0, 8).forEach((item, index) => {
      const card = createElement("article", "research-card");
      const top = createElement("div", "research-card-top");
      top.append(createElement("span", "research-index", String(index + 1).padStart(2, "0")));
      top.append(createElement("span", "research-type", item.type || "registro"));
      card.append(top);
      card.append(createElement("h3", "", item.title || "Fuente sin título"));
      const meta = [
        item.year || "año no informado",
        item.venue || "publicación no informada",
        Array.isArray(item.authors) && item.authors.length ? item.authors.slice(0, 3).join(", ") : "autoría no informada",
      ];
      card.append(createElement("p", "research-meta", meta.join(" · ")));
      const facts = createElement("div", "research-facts");
      if (item.citation_count !== null && item.citation_count !== undefined) {
        facts.append(createElement("span", "", `${item.citation_count} citas`));
      }
      if (item.doi) facts.append(createElement("span", "", `DOI ${item.doi}`));
      card.append(facts);
      if (item.url) {
        const link = createElement("a", "research-link", "Abrir fuente ↗");
        link.href = safeHref(item.url);
        link.target = "_blank";
        link.rel = "noreferrer";
        card.append(link);
      }
      grid.append(card);
    });
    board.append(grid);
  }

  board.append(createElement(
    "p",
    "board-boundary",
    payload.truth_boundary || "Estos registros ayudan a descubrir evidencia; no validan por sí solos la aplicación propuesta.",
  ));
  refs.timeline.append(board);
  const capsule = agentCapsules.get(agentName);
  if (capsule) {
    capsule.evidenceCount += payload.results.length;
    updateCapsuleMetrics(capsule);
  }
  return true;
}

function extractField(section, labels) {
  for (const label of labels) {
    const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const pattern = new RegExp(
      `\\*\\*${escaped}:?\\*\\*\\s*([\\s\\S]*?)(?=\\n\\s*\\*\\s+\\*\\*|\\n---|\\n###\\s+CANDIDATO|\\n##\\s+)`,
      "i",
    );
    const match = section.match(pattern);
    if (match) return truncate(match[1], 420);
  }
  return "";
}

function extractCandidateCards(markdown) {
  const source = text(markdown);
  const headingPattern = /^###\s+CANDIDATO\s+(\d+)\s*:\s*(.+)$/gim;
  const matches = [...source.matchAll(headingPattern)];
  const candidates = [];

  matches.forEach((match, index) => {
    const start = match.index ?? 0;
    const end = index + 1 < matches.length ? matches[index + 1].index : source.length;
    const section = source.slice(start, end);
    const name = stripMarkdown(match[2]);
    const subtitleMatch = section.slice(match[0].length).match(/^\s*\*([^*\n]+)\*/m);
    const costMatch = section.match(/Costo Total BOM[^$\d]*(?:\\?\$)?\s*([0-9]+(?:\.[0-9]+)?)/i);
    candidates.push({
      rank: Number(match[1]),
      name,
      subtitle: subtitleMatch ? stripMarkdown(subtitleMatch[1]) : "",
      mechanism: extractField(section, ["Mecanismo Físico", "Mecanismo", "Physical Mechanism"]),
      benefit: extractField(section, ["Beneficio Esperado", "Expected Benefit"]),
      dependencies: extractField(section, ["Dependencias", "Dependencies"]),
      test: extractField(section, ["Método de Prueba", "Test Method"]),
      rejection: extractField(section, ["Regla de Rechazo", "Rejection Rule"]),
      localBuild: extractField(section, ["Ruta de Fabricación Local", "Local Manufacturing Route"]),
      bomUsd: costMatch ? Number(costMatch[1]) : null,
      status: "Candidato provisional",
    });
  });
  return candidates;
}

function renderCandidateBoard(candidates, sourceLabel = "ATLAS-9") {
  if (!Array.isArray(candidates) || !candidates.length) return false;
  const signature = candidates.map((item) => `${item.rank}:${item.name}`).join("|");
  if (candidateSignatures.has(signature)) return true;
  candidateSignatures.add(signature);

  const board = createElement("section", "candidate-board");
  const head = createElement("div", "board-heading");
  const copy = createElement("div");
  copy.append(createElement("span", "eyebrow", "CANDIDATOS GENERADOS AUTÓNOMAMENTE"));
  copy.append(createElement("h2", "", `${candidates.length} rutas técnicas para comparar`));
  copy.append(createElement("p", "", `${sourceLabel} las produjo a partir de la misión, el catálogo y la evidencia recuperada.`));
  head.append(copy, createElement("span", "board-status warning", "Ranking provisional"));
  board.append(head);

  const grid = createElement("div", "candidate-grid");
  candidates.forEach((candidate) => {
    const card = createElement("article", "candidate-card");
    const top = createElement("div", "candidate-top");
    top.append(createElement("span", "candidate-rank", `Ruta ${candidate.rank}`));
    top.append(createElement("span", "candidate-state", candidate.status || "Provisional"));
    card.append(top);
    card.append(createElement("h3", "", candidate.name));
    if (candidate.subtitle) card.append(createElement("p", "candidate-subtitle", candidate.subtitle));

    const metrics = createElement("div", "candidate-metrics");
    metrics.append(createElement("div", "", "Costo BOM"));
    metrics.lastChild.append(createElement("strong", "", candidate.bomUsd !== null ? `US$${candidate.bomUsd}` : "Pendiente"));
    metrics.append(createElement("div", "", "Validación"));
    metrics.lastChild.append(createElement("strong", "", "Aplicación pendiente"));
    card.append(metrics);

    const facts = createElement("dl", "candidate-facts");
    const addFact = (label, value) => {
      if (!value) return;
      facts.append(createElement("dt", "", label), createElement("dd", "", value));
    };
    addFact("Mecanismo", candidate.mechanism);
    addFact("Beneficio esperado", candidate.benefit);
    addFact("Dependencias", candidate.dependencies);
    addFact("Prueba", candidate.test);
    addFact("Regla de rechazo", candidate.rejection);
    addFact("Fabricación local", candidate.localBuild);
    card.append(facts);
    grid.append(card);
  });

  board.append(grid);
  board.append(createElement(
    "p",
    "board-boundary",
    "Estas rutas son propuestas de diseño. Ninguna se presenta como ganadora hasta que SPARK ejecute verificadores y KIRA resuelva evidencia, riesgos y rechazo.",
  ));
  refs.timeline.append(board);

  const atlas = agentCapsules.get("atlas_9");
  if (atlas) {
    atlas.preview.textContent = `Generó ${candidates.length} candidatos comparables y los dejó listos para verificación.`;
    atlas.evidenceCount += candidates.length;
    updateCapsuleMetrics(atlas);
  }
  return true;
}

function addRawDetails(parent, title, value) {
  if (value === null || value === undefined) return;
  if (Array.isArray(value) && value.length === 0) return;
  if (!Array.isArray(value) && typeof value === "object" && Object.keys(value).length === 0) return;
  const details = document.createElement("details");
  details.className = "raw-details";
  const summary = document.createElement("summary");
  summary.textContent = title;
  details.append(summary, createElement("pre", "", pretty(value)));
  parent.append(details);
}

function renderToolResult(capsule, result) {
  const payload = unwrapPayload(result.response || {});
  const research = findResearchPayload(payload);
  if (research) renderResearchBoard(research, "vigia");

  if (result.name === "runtime_readiness") {
    const facts = createElement("div", "tool-facts");
    facts.append(createElement("span", "", `Backend: ${payload.llm_backend || "—"}`));
    facts.append(createElement("span", "", `Modelo: ${payload.model || "—"}`));
    facts.append(createElement("span", "", payload.ready ? "Runner preparado" : "Runner no preparado"));
    capsule.tools.append(facts);
  }

  addRawDetails(capsule.tools, `Datos completos · ${result.name || "herramienta"}`, payload);
}

function renderStateDelta(record, capsule) {
  const delta = record.state_delta;
  if (!delta || typeof delta !== "object" || Array.isArray(delta)) return;
  const keys = Object.keys(delta);
  if (!keys.length) return;

  const memory = createElement("div", "memory-update");
  memory.append(createElement("span", "memory-icon", "Δ"));
  memory.append(createElement("span", "", `Memoria compartida actualizada: ${keys.join(", ")}`));
  capsule.tools.append(memory);

  if (typeof delta.candidate_architecture === "string") {
    renderCandidateBoard(extractCandidateCards(delta.candidate_architecture), "ATLAS-9");
  }

  const ownerText = keys
    .map((key) => delta[key])
    .find((value) => typeof value === "string" && value.trim());
  if (ownerText && !capsule.text) {
    capsule.text = ownerText;
    capsule.preview.textContent = truncate(ownerText);
    capsule.rendered.replaceChildren(renderMarkdown(ownerText));
    capsule.details.hidden = false;
    capsule.details.open = false;
  }

  addRawDetails(capsule.tools, "Estado técnico completo", delta);
}

function publicActivity(record, agentName) {
  const calls = record.tool_calls || [];
  const results = record.tool_results || [];
  if (calls.length) return `Ejecutando ${calls.map((item) => item.name || "herramienta").join(", ")}`;
  if (results.length) return `Procesando resultados de ${results.map((item) => item.name || "herramienta").join(", ")}`;
  if (record.kind === "error") return "La ejecución produjo un fallo auditable";
  if (record.state_delta && Object.keys(record.state_delta).length) return "Guardando la entrega en memoria compartida";
  return activityNames[agentName] || "Produciendo una salida verificable";
}

function appendAgentEvent(record, agentName) {
  const capsule = capsuleFor(agentName, record.timestamp);
  setAgentStatus(agentName, record.kind === "error" ? "error" : "running");
  capsule.activity.textContent = publicActivity(record, agentName);

  const calls = record.tool_calls || [];
  calls.forEach((call) => {
    capsule.toolCount += 1;
    addToolChip(capsule, `Ejecutando · ${call.name || "herramienta"}`, "running");
    addRawDetails(capsule.tools, `Parámetros · ${call.name || "herramienta"}`, call.args || {});
  });

  const results = record.tool_results || [];
  results.forEach((result) => {
    capsule.evidenceCount += 1;
    addToolChip(capsule, `Completado · ${result.name || "herramienta"}`, "done");
    renderToolResult(capsule, result);
  });

  const visibleTexts = [];
  if (record.message) visibleTexts.push(record.message);
  for (const item of record.texts || []) {
    if (item && !visibleTexts.includes(item)) visibleTexts.push(item);
  }
  if (visibleTexts.length) {
    const combined = visibleTexts.join("\n\n");
    capsule.text = combined;
    capsule.preview.textContent = truncate(combined);
    capsule.rendered.replaceChildren(renderMarkdown(combined));
    capsule.details.hidden = false;

    if (agentName === "atlas_9") {
      renderCandidateBoard(extractCandidateCards(combined), "ATLAS-9");
    }
  }

  if (record.thought_parts_count) {
    let badge = capsule.article.querySelector(".capsule-badge.thought-count");
    if (!badge) {
      badge = createElement("span", "capsule-badge thought-count");
      capsule.article.querySelector(".capsule-badges").append(badge);
    }
    badge.textContent = `${record.thought_parts_count} segmentos internos protegidos`;
  }

  renderStateDelta(record, capsule);
  updateCapsuleMetrics(capsule);

  if (record.error_message || record.error_code) {
    const failure = createElement("div", "capsule-error");
    failure.append(createElement("strong", "", record.error_code || "Fallo de ejecución"));
    failure.append(createElement("p", "", record.error_message || "Error sin detalle público."));
    capsule.tools.append(failure);
  }

  if (record.is_final || (record.state_delta && Object.keys(record.state_delta).some((key) => outputKeyOwners.get(key) === agentName))) {
    setAgentStatus(agentName, record.kind === "error" ? "error" : "done");
  }

  const isKiraTerminal = agentName === "kira" && visibleTexts.length > 0 && record.is_final;
  if (isKiraTerminal) {
    finalObserved = true;
    refs.finalText.replaceChildren(renderMarkdown(visibleTexts.join("\n\n")));
    refs.finalOutput.classList.add("visible");
    setAgentStatus("kira", "done");
  }
}

function appendEvent(record) {
  eventCount += 1;
  const calls = record.tool_calls || [];
  toolCount += calls.length;
  if (record.kind === "error" || record.error_message || record.error_code) errorCount += 1;
  updateMetrics();

  const authorName = findAgentName(record.author);
  completeAgentsFromState(record.state_delta);

  if (record.session_id) {
    refs.sessionStatus.textContent = record.session_id;
    refs.sessionId.value = record.session_id;
  }

  if (authorName) {
    appendAgentEvent(record, authorName);
  } else if (record.kind === "session") {
    appendSystemNotice("Google ADK inició una ejecución real y creó una sesión auditable.", "success");
  } else if (record.kind === "complete") {
    for (const row of refs.agentList.querySelectorAll(".agent-row.running")) {
      row.classList.remove("running", "active");
      row.classList.add("done");
    }
    appendSystemNotice(
      finalObserved
        ? "La invocación terminó y KIRA entregó una decisión final."
        : "La invocación terminó, pero no se recibió una decisión terminal de KIRA.",
      finalObserved ? "success" : "warning",
    );
    refs.traceStatus.textContent = finalObserved
      ? "Misión completada con decisión final de KIRA."
      : "Misión terminada sin una decisión final identificable de KIRA.";
  } else if (record.kind === "error") {
    appendSystemNotice(record.error_message || record.message || "La ejecución produjo un fallo.", "error");
  } else if (record.message) {
    appendSystemNotice(record.message);
  }

  updateMetrics();
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
  appendSystemNotice("KIRA recibió la misión. ORION prepara el contrato y la Constelación continuará sin detenerse ante ambigüedades que puedan resolverse con rutas condicionales.");
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

    refs.traceStatus.textContent = "Constelación trabajando: acciones, herramientas y entregas aparecerán en cápsulas.";
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
