const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

const refs = {
  sidebar: $("#sidebar"), mobileMenu: $("#mobileMenu"), topGoal: $("#topGoal"),
  userGoal: $("#userGoal"), goalTime: $("#goalTime"), autoBadge: $("#autoBadge"),
  runState: $("#runState"), cycleMeta: $("#cycleMeta"), progressLabel: $("#progressLabel"),
  progressFill: $("#progressFill"), cycleNo: $("#cycleNo"), decisionTitle: $("#decisionTitle"),
  modeChip: $("#modeChip"), statusBanner: $("#statusBanner"), technicalStatus: $("#technicalStatus"),
  statusReason: $("#statusReason"), decisionMode: $("#decisionMode"), recommendation: $("#recommendation"),
  humanBenefit: $("#humanBenefit"), beneficiaries: $("#beneficiaries"), whyNow: $("#whyNow"),
  metricTemp: $("#metricTemp"), metricDelta: $("#metricDelta"), metricUncertainty: $("#metricUncertainty"),
  metricEnergy: $("#metricEnergy"), nextAction: $("#nextAction"), missionStatus: $("#missionStatus"),
  candidateRows: $("#candidateRows"), completedActions: $("#completedActions"), opportunityGrid: $("#opportunityGrid"),
  pipelineOutput: $("#pipelineOutput"), technicalLimits: $("#technicalLimits"), disclaimer: $("#disclaimer"),
  historyTable: $("#historyTable"), recentCycles: $("#recentCycles"), railStatus: $("#railStatus"),
  railGoal: $("#railGoal"), liveDot: $("#liveDot"), runNow: $("#runNow"), toggleAutonomy: $("#toggleAutonomy"),
  stageCount: $("#stageCount"), stageList: $("#stageList"), approvalCount: $("#approvalCount"),
  approvalList: $("#approvalList"), agentCount: $("#agentCount"), agentList: $("#agentList"),
  eventList: $("#eventList"), composerForm: $("#composerForm"), messageInput: $("#messageInput"),
  assistantIntro: $("#assistantIntro"), assistantTime: $("#assistantTime"), newMission: $("#newMission"),
  decisionModal: $("#decisionModal"), modalClose: $("#modalClose"), modalTitle: $("#modalTitle"),
  modalDescription: $("#modalDescription"), decisionNote: $("#decisionNote"), approveAction: $("#approveAction"),
  declineAction: $("#declineAction"), toast: $("#toast"),
};

let runtimeState = null;
let selectedActionId = null;
let refreshBusy = false;
let toastTimer = null;

const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[char]);

const money = (value) => {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "—";
  return new Intl.NumberFormat("en-US", {style: "currency", currency: "USD", maximumFractionDigits: 0}).format(parsed);
};
const number = (value, digits = 1) => Number.isFinite(Number(value)) ? Number(value).toFixed(digits) : "—";
const localTime = (value) => {
  if (!value) return "sin ejecutar";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "actualizado";
  return new Intl.DateTimeFormat("es-DO", {hour: "2-digit", minute: "2-digit", second: "2-digit"}).format(date);
};
const shortDate = (value) => {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "—";
  return new Intl.DateTimeFormat("es-DO", {day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit"}).format(date);
};

async function api(path, options = {}) {
  const response = await fetch(path, {headers: {"Content-Type": "application/json", ...(options.headers || {})}, ...options});
  if (!response.ok) {
    let message = `Error ${response.status}`;
    try { message = (await response.json()).detail || message; } catch {}
    throw new Error(message);
  }
  return response.json();
}

function showToast(message) {
  refs.toast.textContent = message;
  refs.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => refs.toast.classList.remove("show"), 2600);
}

function activeTab(name) {
  $$(".tab").forEach((button) => button.classList.toggle("active", button.dataset.tab === name));
  $$(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === `tab-${name}`));
}

function renderStatus(state) {
  const classification = state.classification || {};
  const mission = state.mission_result || {};
  const brief = state.decision_brief || {};
  const winner = mission.winner || {};
  const verified = Boolean((winner.verification || {}).approved);
  const discovery = classification.mode === "discovery";

  refs.topGoal.textContent = state.goal || "Sin objetivo";
  refs.userGoal.textContent = state.goal || "Define una misión.";
  refs.goalTime.textContent = state.last_started_at ? `Dirección activa · ${localTime(state.last_started_at)}` : "Dirección humana";
  refs.autoBadge.classList.toggle("paused", !state.enabled);
  refs.autoBadge.querySelector("span").textContent = state.enabled ? "Modo autónomo" : "Modo pausado";
  refs.railStatus.textContent = state.status === "running" ? "Trabajando" : state.enabled ? "Vigilando" : "Pausado";
  refs.railGoal.textContent = state.goal || "Sin objetivo";
  refs.liveDot.style.background = state.enabled ? "#1fbf83" : "#d8a82d";
  refs.toggleAutonomy.textContent = state.enabled ? "Pausar" : "Activar";

  refs.decisionTitle.textContent = brief.title || "Decisión recomendada por KIRA";
  refs.decisionMode.textContent = classification.mode ? classification.mode.toUpperCase() : "—";
  refs.recommendation.textContent = brief.recommendation || "Todavía no hay una recomendación.";
  refs.humanBenefit.textContent = brief.human_benefit || "El beneficio humano aparecerá tras completar el ciclo.";
  refs.nextAction.textContent = brief.next_action || "Sin acciones pendientes";
  refs.technicalLimits.textContent = brief.technical_limits || "Pendiente de evaluación.";

  refs.modeChip.className = "mode-chip";
  refs.statusBanner.className = "status-banner";
  if (verified) {
    refs.modeChip.classList.add("verified"); refs.modeChip.textContent = "VERIFICADO";
    refs.statusBanner.classList.add("verified"); refs.technicalStatus.textContent = "Misión técnica verificada";
    refs.statusReason.textContent = "El resultado pasó el simulador determinista y el verificador independiente.";
  } else if (discovery) {
    refs.modeChip.classList.add("discovery"); refs.modeChip.textContent = "DESCUBRIMIENTO";
    refs.statusBanner.classList.add("discovery"); refs.technicalStatus.textContent = "Objetivo en fase de descubrimiento";
    refs.statusReason.textContent = (mission.verification || {}).reason || classification.reason || "Hace falta una herramienta específica antes de declarar éxito.";
  } else {
    refs.modeChip.textContent = state.status === "running" ? "EJECUTANDO" : "ANALIZANDO";
    refs.technicalStatus.textContent = "Evaluación en curso";
    refs.statusReason.textContent = classification.reason || "ORPHEUS clasificará el objetivo antes de ejecutar.";
  }

  refs.beneficiaries.innerHTML = (brief.beneficiaries || []).map((item) => `<span>${escapeHtml(item)}</span>`).join("");
  refs.whyNow.innerHTML = (brief.why_now || ["Esperando análisis."]).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  refs.assistantTime.textContent = localTime(state.last_completed_at);
  if (state.status === "running") refs.assistantIntro.textContent = "KIRA está coordinando agentes y ejecutando las herramientas pertinentes.";
  else if (brief.recommendation) refs.assistantIntro.textContent = `${brief.recommendation} Las acciones externas y financieras siguen bajo control humano.`;
}

function renderRun(state) {
  const pipeline = state.pipeline || [];
  const completed = pipeline.filter((step) => step.status === "completed").length;
  const running = pipeline.find((step) => step.status === "running");
  const total = pipeline.length;
  refs.runState.textContent = running ? `${running.agent}: ${running.title}` : state.status === "running" ? "Ejecutando ciclo" : state.last_completed_at ? "Ciclo completado" : "Preparando ciclo autónomo";
  refs.cycleMeta.textContent = state.last_completed_at ? `Última salida ${localTime(state.last_completed_at)}` : "Sin ejecución todavía";
  refs.progressLabel.textContent = `${completed} / ${total} etapas`;
  refs.progressFill.style.width = `${total ? (completed / total) * 100 : 0}%`;
  refs.cycleNo.textContent = `Ciclo ${state.cycle_number || 0}`;
  refs.stageCount.textContent = `${completed}/${total}`;
  refs.stageList.innerHTML = pipeline.length ? pipeline.map((step) => `<div class="stage-item ${escapeHtml(step.status)}"><div class="stage-number">${step.status === "completed" ? "✓" : step.step}</div><div><strong>${escapeHtml(step.agent)}</strong><span>${escapeHtml(step.title)}</span></div><span class="stage-state">${escapeHtml(step.status)}</span></div>`).join("") : '<div class="empty-rail">El ciclo todavía no ha comenzado.</div>';
  refs.pipelineOutput.innerHTML = pipeline.length ? pipeline.map((step) => `<div class="pipeline-line"><div class="pipeline-number">${step.step}</div><div class="pipeline-agent">${escapeHtml(step.agent)}</div><div class="pipeline-copy"><strong>${escapeHtml(step.title)}</strong><span>${escapeHtml(step.output_summary || "Pendiente de ejecución.")}</span></div></div>`).join("") : '<div class="table-empty">No hay trazabilidad todavía.</div>';
}

function renderMission(state) {
  const mission = state.mission_result || {};
  const rows = mission.ranked_candidates || [];
  const winnerName = (mission.winner || {}).design;
  const simulation = ((mission.winner || {}).simulation || {});
  refs.metricTemp.textContent = Number.isFinite(Number(simulation.estimated_internal_c)) ? `${number(simulation.estimated_internal_c)} °C` : "—";
  refs.metricDelta.textContent = Number.isFinite(Number(simulation.cooling_delta_c)) ? `${number(simulation.cooling_delta_c)} °C` : "—";
  refs.metricUncertainty.textContent = Number.isFinite(Number(simulation.uncertainty_c)) ? `± ${number(simulation.uncertainty_c)} °C` : "—";
  refs.metricEnergy.textContent = Number.isFinite(Number(simulation.hourly_energy_kwh)) ? `${number(simulation.hourly_energy_kwh)} kWh` : "—";
  refs.missionStatus.textContent = mission.mission_status || "SIN EJECUTAR";
  refs.missionStatus.classList.toggle("ok", mission.mission_status === "CUMPLIDA");
  refs.candidateRows.innerHTML = rows.length ? rows.map((row) => {
    const sim = row.simulation || {};
    const isWinner = row.design === winnerName && (row.verification || {}).approved;
    return `<div class="candidate-row ${isWinner ? "winner" : ""}"><strong>${escapeHtml(row.design)}</strong><span>${number(sim.estimated_internal_c)} °C</span><span>${number(sim.cooling_delta_c)} °C</span><span>${number(sim.score)}</span><span class="result-pill ${isWinner ? "win" : ""}">${isWinner ? "GANADOR" : "RECHAZADO"}</span></div>`;
  }).join("") : '<div class="table-empty">No se ejecutó un simulador técnico para este objetivo.</div>';
}

function renderPlan(state) {
  const plan = state.benefit_plan || {};
  const opportunities = plan.opportunities || [];
  const selectedId = (plan.selected_opportunity || {}).id;
  const actions = plan.actions || [];
  const completed = actions.filter((action) => action.status === "completed");
  refs.disclaimer.textContent = plan.disclaimer || "Las cifras comerciales deben tratarse como hipótesis hasta disponer de evidencia externa.";
  refs.completedActions.innerHTML = completed.length ? completed.map((action) => `<div class="work-card"><div class="work-icon">✓</div><div><strong>${escapeHtml(action.title)}</strong><span>${escapeHtml(action.agent)} · ${escapeHtml(action.artifact || "artefacto local")}</span></div></div>`).join("") : '<div class="table-empty">No hay trabajo local completado.</div>';
  refs.opportunityGrid.innerHTML = opportunities.length ? opportunities.map((item, index) => `<article class="opportunity-card ${item.id === selectedId ? "selected" : ""}"><div class="opportunity-rank">${index + 1}</div><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.benefit)}</p><div class="offer-label">OFERTA</div><div class="offer-value">${escapeHtml(item.offer)}</div><div class="economics"><div><span>Precio</span><strong>${money(item.price_hypothesis_usd)}</strong></div><div><span>Costo</span><strong>${money(item.unit_cost_hypothesis_usd)}</strong></div><div><span>Margen</span><strong>${money(item.gross_margin_hypothesis_usd)}</strong></div></div><div class="score-row"><span>${escapeHtml(item.revenue_model)}</span><strong>${number(item.priority_score)}</strong></div></article>`).join("") : '<div class="table-empty">No hay oportunidades calculadas.</div>';
  const gated = actions.filter((action) => action.requires_human_approval);
  refs.approvalCount.textContent = String(gated.filter((action) => action.status === "awaiting_approval").length);
  refs.approvalList.innerHTML = gated.length ? gated.map((action) => `<div class="approval-card ${action.status !== "awaiting_approval" ? "resolved" : ""}"><strong>${escapeHtml(action.title)}</strong><span>${escapeHtml(action.benefit)}</span><button data-action="${escapeHtml(action.id)}" ${action.status !== "awaiting_approval" ? "disabled" : ""}>${action.status === "awaiting_approval" ? "Revisar decisión" : escapeHtml(action.status)}</button></div>`).join("") : '<div class="empty-rail">No hay decisiones pendientes.</div>';
}

function renderAgents(state) {
  const agents = state.agents || [];
  refs.agentCount.textContent = String(agents.length);
  refs.agentList.innerHTML = agents.length ? agents.map((agent) => `<div class="agent-item"><div class="agent-symbol">${escapeHtml(agent.name.slice(0, 2))}</div><div><strong>${escapeHtml(agent.name)}</strong><span>${escapeHtml(agent.last_action || agent.role)}</span></div><span class="agent-status ${escapeHtml(agent.status)}">${escapeHtml(agent.status)}</span></div>`).join("") : '<div class="empty-rail">Sin agentes registrados.</div>';
}

function renderHistory(state) {
  const history = state.cycle_history || [];
  refs.historyTable.innerHTML = history.length ? history.map((item) => `<div class="history-row"><strong>#${item.number}</strong><div><strong>${escapeHtml(item.goal)}</strong><span>${escapeHtml(item.selected_opportunity || "—")}</span></div><span class="history-mode">${escapeHtml(item.mode)}</span><span class="history-status">${escapeHtml(item.status)}</span></div>`).join("") : '<div class="table-empty">Todavía no existe historial de ciclos.</div>';
  refs.recentCycles.innerHTML = history.length ? history.slice(0, 6).map((item, index) => `<button class="recent-item ${index === 0 ? "active" : ""}"><div><strong>${escapeHtml(item.goal)}</strong><span>${shortDate(item.completed_at)}</span></div><i>${escapeHtml(item.mode)}</i></button>`).join("") : '<div class="empty-mini">Sin ciclos todavía</div>';
}

function renderEvents(state) {
  const events = state.events || [];
  refs.eventList.innerHTML = events.length ? events.slice(0, 8).map((event) => `<div class="event-item"><strong>${escapeHtml(event.message)}</strong><span>${localTime(event.at)} · ${escapeHtml(event.type)}</span></div>`).join("") : '<div class="empty-rail">Sin actividad registrada.</div>';
}

function render(state) { runtimeState = state; renderStatus(state); renderRun(state); renderMission(state); renderPlan(state); renderAgents(state); renderHistory(state); renderEvents(state); }

async function refresh() {
  if (refreshBusy) return;
  refreshBusy = true;
  try { render(await api("/autonomy/state")); } catch (error) { showToast(error.message); } finally { refreshBusy = false; }
}
async function runCycle() {
  refs.runNow.disabled = true;
  try { render(await api("/autonomy/cycle", {method: "POST"})); showToast("Ciclo autónomo completado."); }
  catch (error) { showToast(error.message); } finally { refs.runNow.disabled = false; }
}
async function toggleAutonomy() {
  const enabling = !runtimeState?.enabled;
  try { render(await api(enabling ? "/autonomy/start" : "/autonomy/stop", {method: "POST"})); showToast(enabling ? "Modo autónomo activado." : "Modo autónomo pausado."); }
  catch (error) { showToast(error.message); }
}
function openDecision(actionId) {
  const action = (runtimeState?.benefit_plan?.actions || []).find((item) => item.id === actionId);
  if (!action) return;
  selectedActionId = actionId; refs.modalTitle.textContent = action.title; refs.modalDescription.textContent = action.benefit;
  refs.decisionNote.value = ""; refs.decisionModal.hidden = false;
}
function closeDecision() { selectedActionId = null; refs.decisionModal.hidden = true; }
async function decide(decision) {
  if (!selectedActionId) return;
  try {
    const state = await api(`/autonomy/actions/${encodeURIComponent(selectedActionId)}/decision`, {method: "POST", body: JSON.stringify({decision, note: refs.decisionNote.value.trim() || null})});
    render(state); closeDecision(); showToast(decision === "approve" ? "Acción aprobada." : "Acción rechazada.");
  } catch (error) { showToast(error.message); }
}

$$(".tab").forEach((button) => button.addEventListener("click", () => activeTab(button.dataset.tab)));
$$(".nav-item").forEach((button) => button.addEventListener("click", () => {
  $$(".nav-item").forEach((item) => item.classList.remove("active")); button.classList.add("active");
  const view = button.dataset.view; if (["opportunities", "evidence", "history"].includes(view)) activeTab(view); else if (view === "chat") activeTab("decision");
  refs.sidebar.classList.remove("open");
}));
refs.mobileMenu.addEventListener("click", () => refs.sidebar.classList.toggle("open"));
refs.runNow.addEventListener("click", runCycle); refs.toggleAutonomy.addEventListener("click", toggleAutonomy); refs.autoBadge.addEventListener("click", toggleAutonomy);
refs.newMission.addEventListener("click", () => { refs.messageInput.value = ""; refs.messageInput.focus(); refs.sidebar.classList.remove("open"); showToast("Describe la nueva misión."); });
refs.messageInput.addEventListener("input", () => { refs.messageInput.style.height = "auto"; refs.messageInput.style.height = `${Math.min(refs.messageInput.scrollHeight, 120)}px`; });
refs.composerForm.addEventListener("submit", async (event) => {
  event.preventDefault(); const message = refs.messageInput.value.trim(); if (!message) return; refs.messageInput.disabled = true;
  try { const result = await api("/chat", {method: "POST", body: JSON.stringify({message})}); refs.messageInput.value = ""; refs.messageInput.style.height = "auto"; refs.assistantIntro.textContent = result.assistant_message; render(result.state); activeTab("decision"); showToast("La nueva dirección fue ejecutada."); }
  catch (error) { showToast(error.message); } finally { refs.messageInput.disabled = false; refs.messageInput.focus(); }
});
refs.approvalList.addEventListener("click", (event) => { const button = event.target.closest("[data-action]"); if (button && !button.disabled) openDecision(button.dataset.action); });
refs.modalClose.addEventListener("click", closeDecision); refs.decisionModal.addEventListener("click", (event) => { if (event.target === refs.decisionModal) closeDecision(); });
refs.approveAction.addEventListener("click", () => decide("approve")); refs.declineAction.addEventListener("click", () => decide("decline"));
document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeDecision(); if ((event.ctrlKey || event.metaKey) && event.key === "Enter") refs.composerForm.requestSubmit(); });
refresh(); setInterval(refresh, 2500);
