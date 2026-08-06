(() => {
  const shell = document.querySelector("#appShell");
  const leftToggle = document.querySelector("#leftRailToggle");
  const inspectorToggle = document.querySelector("#inspectorToggle");
  const backdrop = document.querySelector("#panelBackdrop");
  const executionProfile = document.querySelector("#executionProfile");
  const squadConcurrency = document.querySelector("#squadConcurrency");
  const executionProfileNote = document.querySelector("#executionProfileNote");

  if (!shell || !leftToggle || !inspectorToggle || !backdrop) return;

  const storageKeys = {
    left: "orpheus.shell.leftCollapsed",
    right: "orpheus.shell.rightCollapsed",
  };

  const desktopLeftCollapsed = () => localStorage.getItem(storageKeys.left) === "true";
  const desktopRightCollapsed = () => localStorage.getItem(storageKeys.right) === "true";
  const mobileLeft = () => window.matchMedia("(max-width: 820px)").matches;
  const mobileRight = () => window.matchMedia("(max-width: 1180px)").matches;

  function setExpanded(button, expanded, expandedTitle, collapsedTitle) {
    button.setAttribute("aria-expanded", String(expanded));
    button.title = expanded ? expandedTitle : collapsedTitle;
  }

  function syncDesktopState() {
    if (!mobileLeft()) {
      shell.classList.toggle("left-collapsed", desktopLeftCollapsed());
      shell.classList.remove("mobile-left-open");
    }
    if (!mobileRight()) {
      shell.classList.toggle("right-collapsed", desktopRightCollapsed());
      shell.classList.remove("mobile-right-open");
    }
    syncControls();
  }

  function syncControls() {
    const leftExpanded = mobileLeft()
      ? shell.classList.contains("mobile-left-open")
      : !shell.classList.contains("left-collapsed");
    const rightExpanded = mobileRight()
      ? shell.classList.contains("mobile-right-open")
      : !shell.classList.contains("right-collapsed");

    setExpanded(leftToggle, leftExpanded, "Colapsar navegación", "Expandir navegación");
    setExpanded(inspectorToggle, rightExpanded, "Colapsar inspector", "Expandir inspector");
  }

  function closeMobilePanels() {
    shell.classList.remove("mobile-left-open", "mobile-right-open");
    syncControls();
  }

  leftToggle.addEventListener("click", () => {
    if (mobileLeft()) {
      const next = !shell.classList.contains("mobile-left-open");
      shell.classList.toggle("mobile-left-open", next);
      if (next) shell.classList.remove("mobile-right-open");
    } else {
      const next = !shell.classList.contains("left-collapsed");
      shell.classList.toggle("left-collapsed", next);
      localStorage.setItem(storageKeys.left, String(next));
    }
    syncControls();
  });

  inspectorToggle.addEventListener("click", () => {
    if (mobileRight()) {
      const next = !shell.classList.contains("mobile-right-open");
      shell.classList.toggle("mobile-right-open", next);
      if (next) shell.classList.remove("mobile-left-open");
    } else {
      const next = !shell.classList.contains("right-collapsed");
      shell.classList.toggle("right-collapsed", next);
      localStorage.setItem(storageKeys.right, String(next));
    }
    syncControls();
  });

  backdrop.addEventListener("click", closeMobilePanels);

  window.addEventListener("resize", () => {
    closeMobilePanels();
    syncDesktopState();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMobilePanels();
    if (event.ctrlKey && !event.shiftKey && event.key.toLowerCase() === "b") {
      event.preventDefault();
      leftToggle.click();
    }
    if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === "b") {
      event.preventDefault();
      inspectorToggle.click();
    }
  });

  async function loadExecutionProfile() {
    try {
      const response = await fetch("/adk/readiness", {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) return;
      const state = await response.json();
      const profile = state.execution_profile || "parallel";
      const concurrency = state.squad_concurrency || "parallel";
      if (executionProfile) {
        executionProfile.textContent = profile === "free_safe" ? "Local seguro" : "Alto rendimiento";
      }
      if (squadConcurrency) {
        squadConcurrency.textContent = concurrency === "sequential" ? "Por turnos" : "En paralelo";
      }
      if (executionProfileNote) {
        executionProfileNote.textContent = profile === "free_safe"
          ? "Los 18 agentes siguen habilitados. Los escuadrones trabajan por turnos para evitar fallos por ráfagas en la cuota gratuita."
          : "Los escuadrones trabajan en paralelo. Este perfil está pensado para Vertex AI o una cuota suficiente.";
      }
    } catch {
      // The main readiness panel already reports connectivity errors.
    }
  }

  function createTextElement(tag, className, value) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    element.textContent = value === null || value === undefined ? "" : String(value);
    return element;
  }

  function appendRuntimeErrorCard(record) {
    const card = createTextElement("section", "runtime-error-card", "");
    const head = createTextElement("div", "runtime-error-head", "");
    head.append(createTextElement("div", "runtime-error-icon", "!"));
    const title = createTextElement("div", "", "");
    title.append(createTextElement("strong", "", "La ejecución se detuvo"));
    title.append(createTextElement(
      "span",
      "",
      record.error_code || record.error_type || "runtime_error",
    ));
    head.append(title);

    const body = createTextElement("div", "runtime-error-body", "");
    body.append(createTextElement(
      "p",
      "runtime-error-summary",
      record.error_message || record.message || "El Runner no entregó una causa pública.",
    ));

    const details = Array.isArray(record.error_details) ? record.error_details : [];
    if (details.length) {
      const list = createTextElement("ul", "runtime-error-causes", "");
      details.forEach((item) => {
        const li = createTextElement("li", "", "");
        li.append(createTextElement("code", "", item.type || "Error"));
        li.append(document.createTextNode(item.message || "Sin mensaje público."));
        list.append(li);
      });
      body.append(list);
    }

    if (record.recovery) {
      body.append(createTextElement("p", "runtime-error-recovery", record.recovery));
    }

    card.append(head, body);
    refs.timeline.append(card);
    refs.conversationScroll.scrollTo({
      top: refs.conversationScroll.scrollHeight,
      behavior: "smooth",
    });
  }

  if (typeof appendEvent === "function") {
    const baseAppendEvent = appendEvent;
    appendEvent = function enhancedAppendEvent(record) {
      baseAppendEvent(record);
      if (
        record &&
        record.kind === "error" &&
        (record.error_details || record.recovery || record.error_type)
      ) {
        const notices = refs.timeline.querySelectorAll(".system-notice.error");
        const lastNotice = notices[notices.length - 1];
        if (lastNotice) lastNotice.remove();
        appendRuntimeErrorCard(record);
      }
    };
  }

  if (refs?.missionForm && refs?.goal) {
    refs.missionForm.addEventListener("submit", () => {
      // The primary handler reads the goal and sets running synchronously before
      // this later listener executes. Clear only after the mission entered chat.
      if (!running) return;
      refs.goal.value = "";
      refs.goal.style.height = "auto";
      refs.goal.placeholder = "Añade una instrucción o inicia otra misión cuando termine…";
    });
  }

  syncDesktopState();
  loadExecutionProfile();
})();
