from __future__ import annotations

import asyncio
import contextlib
import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .tools import list_historical_concepts, run_reference_mission


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _clean_text(value: str, limit: int = 1500) -> str:
    return " ".join(str(value).split()).strip()[:limit]


AGENT_ROSTER: list[dict[str, str]] = [
    {"id": "kira", "name": "KIRA", "role": "Dirección, integración y entrega"},
    {"id": "orion", "name": "ORION", "role": "Contrato de misión y prioridades"},
    {"id": "vigia", "name": "VIGÍA", "role": "Radar de antecedentes y oportunidades"},
    {"id": "nyx", "name": "NYX-7", "role": "Fallos, contradicciones y dependencias"},
    {"id": "vega", "name": "VEGA", "role": "Evidencia, hipótesis y pruebas"},
    {"id": "atlas", "name": "ATLAS-9", "role": "Arquitectura y diseño manufacturable"},
    {"id": "spark", "name": "SPARK", "role": "Simulación y ejecución local"},
    {"id": "aureus", "name": "AUREUS-7", "role": "Monetización, precios y capital"},
    {"id": "bastion", "name": "BASTION", "role": "Seguridad, legalidad y aprobaciones"},
    {"id": "echo", "name": "ECHO", "role": "Proveniencia, límites y trazabilidad"},
    {"id": "vanta", "name": "VANTA-0", "role": "Rutas alternativas legítimas"},
]


def _default_profile() -> dict[str, Any]:
    return {
        "human": "Dr. Arisnachy Gómez Díaz",
        "objective": (
            "Diseñar una solución asequible, fabricable localmente y sin electricidad "
            "para conservar alimentos mediante enfriamiento pasivo."
        ),
        "beneficiaries": [
            "pequeños productores",
            "comunidades con electricidad inestable",
            "organizaciones de salud y desarrollo",
        ],
        "preferred_outcomes": [
            "impacto humano medible",
            "ingreso sostenible",
            "propiedad intelectual documentada",
            "entrega reproducible",
        ],
        "payment_channel_configured": bool(os.getenv("ORPHEUS_PAYMENT_HANDLE")),
    }


def classify_goal(goal: str) -> dict[str, Any]:
    """Classify whether the current deterministic repository can verify the goal.

    ORPHEUS currently has one validated deterministic mission family: passive
    cooling for food preservation. Other goals enter discovery mode and must not
    inherit a false technical verification from the reference mission.
    """

    normalized = _clean_text(goal, 2000).lower()
    cooling_terms = {
        "enfriamiento",
        "refrigeración",
        "refrigeracion",
        "conservar alimentos",
        "conservación de alimentos",
        "conservacion de alimentos",
        "sin electricidad",
        "sin red eléctrica",
        "pasivo",
        "passive cooling",
        "food preservation",
    }
    matches = sorted(term for term in cooling_terms if term in normalized)
    supported = len(matches) >= 2 or (
        any(term in normalized for term in {"enfriamiento", "refrigeración", "refrigeracion"})
        and any(term in normalized for term in {"alimento", "comida", "food"})
    )
    return {
        "mode": "verification" if supported else "discovery",
        "supported": supported,
        "mission_family": "passive_food_cooling" if supported else "unmapped",
        "matched_terms": matches,
        "reason": (
            "El objetivo coincide con la misión determinista de enfriamiento pasivo."
            if supported
            else "No existe todavía un simulador determinista específico para este objetivo."
        ),
    }


def _mission_contract(goal: str, classification: dict[str, Any]) -> dict[str, Any]:
    if classification["supported"]:
        return {
            "objective": goal,
            "victory_conditions": [
                "costo estimado ≤ USD 65",
                "temperatura interna con incertidumbre ≤ 24 °C",
                "reducción térmica con incertidumbre ≥ 7 °C",
                "fabricación local",
                "consumo eléctrico = 0 kWh",
            ],
            "verification_mode": "deterministic",
        }
    return {
        "objective": goal,
        "victory_conditions": [
            "definir una métrica primaria de beneficio",
            "identificar una línea base verificable",
            "crear al menos un instrumento de prueba",
            "separar evidencia de hipótesis",
            "definir quién recibe el beneficio y cómo se medirá",
        ],
        "verification_mode": "discovery_required",
    }


def _discovery_mission(goal: str) -> dict[str, Any]:
    return {
        "mission_status": "DESCUBRIMIENTO",
        "winner": None,
        "ranked_candidates": [],
        "goal": goal,
        "verification": {
            "approved": False,
            "reason": (
                "ORPHEUS no ejecutó la misión de referencia porque no corresponde "
                "al objetivo actual. Se requiere un simulador, conjunto de datos o "
                "protocolo de prueba específico antes de declarar éxito."
            ),
        },
    }


def build_opportunity_plan(
    mission_result: dict[str, Any],
    profile: dict[str, Any] | None = None,
    classification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an evidence-labelled benefit and sustainability plan.

    Commercial numbers are explicit hypotheses. Nothing in this function claims
    a live customer, grant, patent position, demand signal, or guaranteed revenue.
    """

    profile = deepcopy(profile or _default_profile())
    classification = classification or {"supported": True, "mode": "verification"}
    winner = mission_result.get("winner") or {}
    simulation = winner.get("simulation") or {}
    design_name = winner.get("design", "concepto en descubrimiento")
    verified = bool((winner.get("verification") or {}).get("approved"))

    evidence_strength = 86 if verified else 36
    cooling_delta = float(simulation.get("cooling_delta_c", 0.0) or 0.0)
    reference_cost = 64.0 if classification.get("supported") else 0.0

    if classification.get("supported"):
        opportunities = [
            {
                "id": "community-kit",
                "title": "Kit comunitario de conservación pasiva",
                "benefit": (
                    "Reducir pérdidas de alimentos donde la refrigeración eléctrica "
                    "es costosa o inestable."
                ),
                "beneficiaries": ["pequeños productores", "hogares", "mercados rurales"],
                "offer": f"Kit demostrativo basado en {design_name}",
                "revenue_model": "venta directa + instalación + mantenimiento",
                "price_hypothesis_usd": 129,
                "unit_cost_hypothesis_usd": reference_cost,
                "gross_margin_hypothesis_usd": 129 - reference_cost,
                "evidence_score": evidence_strength,
                "impact_score": min(98, round(70 + cooling_delta)),
                "execution_score": 82,
                "risk": "medium",
                "validation_needed": [
                    "seguridad alimentaria",
                    "ensayo de campo",
                    "durabilidad",
                    "costo real de fabricación",
                ],
            },
            {
                "id": "b2b-pilot",
                "title": "Piloto para ONG, cooperativas y agrocomercio",
                "benefit": (
                    "Medir temperatura, merma evitada y costo por kilogramo "
                    "conservado durante un piloto controlado."
                ),
                "beneficiaries": ["ONG", "cooperativas", "programas de desarrollo"],
                "offer": "Piloto técnico de 30 días con informe verificable",
                "revenue_model": "honorario de piloto + licencia + soporte",
                "price_hypothesis_usd": 2500,
                "unit_cost_hypothesis_usd": 950,
                "gross_margin_hypothesis_usd": 1550,
                "evidence_score": evidence_strength,
                "impact_score": 92,
                "execution_score": 74,
                "risk": "medium",
                "validation_needed": [
                    "socio piloto",
                    "métricas de campo",
                    "contrato",
                    "revisión de responsabilidad",
                ],
            },
            {
                "id": "research-license",
                "title": "Transferencia tecnológica y licencia de evaluación",
                "benefit": (
                    "Convertir la simulación, documentación y diseño en un activo "
                    "evaluable por universidades, fabricantes o incubadoras."
                ),
                "beneficiaries": ["universidades", "fabricantes", "incubadoras"],
                "offer": "Dossier técnico + licencia de evaluación + asistencia",
                "revenue_model": "licencia no exclusiva + consultoría",
                "price_hypothesis_usd": 5000,
                "unit_cost_hypothesis_usd": 1200,
                "gross_margin_hypothesis_usd": 3800,
                "evidence_score": evidence_strength,
                "impact_score": 78,
                "execution_score": 68,
                "risk": "high",
                "validation_needed": [
                    "búsqueda de anterioridad",
                    "asesoría de propiedad intelectual",
                    "validación académica",
                    "negociación de licencia",
                ],
            },
        ]
    else:
        opportunities = [
            {
                "id": "discovery-sprint",
                "title": "Sprint de descubrimiento verificable",
                "benefit": (
                    "Convertir el objetivo abierto en un contrato medible, un mapa "
                    "de evidencia y un prototipo de prueba."
                ),
                "beneficiaries": profile.get("beneficiaries") or ["usuario objetivo"],
                "offer": "Sprint de 10 días con dossier de evidencia y prueba mínima",
                "revenue_model": "servicio de investigación aplicada",
                "price_hypothesis_usd": 1500,
                "unit_cost_hypothesis_usd": 600,
                "gross_margin_hypothesis_usd": 900,
                "evidence_score": evidence_strength,
                "impact_score": 72,
                "execution_score": 79,
                "risk": "medium",
                "validation_needed": [
                    "definición del problema",
                    "fuentes primarias",
                    "métrica de resultado",
                    "protocolo de prueba",
                ],
            },
            {
                "id": "research-brief",
                "title": "Brief de inteligencia técnica",
                "benefit": (
                    "Reducir incertidumbre antes de invertir en desarrollo, compra "
                    "o alianza."
                ),
                "beneficiaries": profile.get("beneficiaries") or ["decisor técnico"],
                "offer": "Informe de antecedentes, riesgos y rutas de validación",
                "revenue_model": "informe + sesión estratégica",
                "price_hypothesis_usd": 650,
                "unit_cost_hypothesis_usd": 220,
                "gross_margin_hypothesis_usd": 430,
                "evidence_score": evidence_strength,
                "impact_score": 64,
                "execution_score": 88,
                "risk": "low",
                "validation_needed": ["fuentes primarias", "alcance", "criterio de decisión"],
            },
            {
                "id": "prototype-contract",
                "title": "Contrato de prototipo con hitos",
                "benefit": (
                    "Financiar el desarrollo por etapas sin prometer rendimiento "
                    "antes de probarlo."
                ),
                "beneficiaries": profile.get("beneficiaries") or ["organización patrocinadora"],
                "offer": "Prototipo por hitos con revisión independiente",
                "revenue_model": "pago por hitos",
                "price_hypothesis_usd": 3500,
                "unit_cost_hypothesis_usd": 1700,
                "gross_margin_hypothesis_usd": 1800,
                "evidence_score": evidence_strength,
                "impact_score": 76,
                "execution_score": 62,
                "risk": "high",
                "validation_needed": [
                    "patrocinador",
                    "alcance técnico",
                    "propiedad intelectual",
                    "criterios de aceptación",
                ],
            },
        ]

    risk_penalties = {"low": 4, "medium": 12, "high": 22}
    for item in opportunities:
        item["priority_score"] = round(
            item["evidence_score"] * 0.30
            + item["impact_score"] * 0.35
            + item["execution_score"] * 0.35
            - risk_penalties[item["risk"]],
            1,
        )
        item["economics_status"] = "hypothesis"

    opportunities.sort(key=lambda item: item["priority_score"], reverse=True)
    selected = opportunities[0]

    actions = [
        {
            "id": "prepare-decision-brief",
            "agent": "ECHO",
            "title": "Preparar memo de decisión y límites",
            "kind": "local",
            "status": "completed",
            "requires_human_approval": False,
            "artifact": "decision_brief",
            "benefit": "Entrega una decisión legible, auditable y reutilizable.",
        },
        {
            "id": "generate-unit-economics",
            "agent": "AUREUS-7",
            "title": "Calcular escenarios de precio, costo y margen",
            "kind": "local",
            "status": "completed",
            "requires_human_approval": False,
            "artifact": "unit_economics",
            "benefit": "Hace explícitos los supuestos económicos antes de cobrar.",
        },
        {
            "id": "design-validation-protocol",
            "agent": "VEGA",
            "title": "Diseñar protocolo de validación",
            "kind": "local",
            "status": "completed",
            "requires_human_approval": False,
            "artifact": "validation_protocol",
            "benefit": "Define cómo convertir hipótesis en evidencia.",
        },
        {
            "id": "contact-pilot-partners",
            "agent": "VIGÍA",
            "title": "Buscar y contactar socios piloto",
            "kind": "external",
            "status": "awaiting_approval",
            "requires_human_approval": True,
            "benefit": "Puede producir validación de mercado y un primer piloto.",
        },
        {
            "id": "publish-commercial-offer",
            "agent": "AUREUS-7",
            "title": "Publicar oferta y canal de cobro",
            "kind": "financial",
            "status": "awaiting_approval",
            "requires_human_approval": True,
            "benefit": "Habilita cobro tras revisar precio, términos y receptor.",
        },
    ]

    return {
        "generated_at": _utc_now(),
        "profile": profile,
        "selected_opportunity": selected,
        "opportunities": opportunities,
        "actions": actions,
        "disclaimer": (
            "Los precios, márgenes y rutas son hipótesis de planificación. "
            "No equivalen a demanda confirmada, subvenciones activas, libertad "
            "de operación, aprobación sanitaria ni ingresos garantizados."
        ),
    }


def build_decision_brief(
    goal: str,
    classification: dict[str, Any],
    mission_result: dict[str, Any],
    benefit_plan: dict[str, Any],
) -> dict[str, Any]:
    selected = benefit_plan["selected_opportunity"]
    winner = mission_result.get("winner") or {}
    verified = bool((winner.get("verification") or {}).get("approved"))
    return {
        "title": "Decisión recomendada por KIRA",
        "goal": goal,
        "mode": classification["mode"],
        "technical_status": "verified" if verified else "discovery",
        "recommendation": f"Avanzar con «{selected['title']}» como siguiente experimento de valor.",
        "why_now": [
            "es la opción con mejor combinación de evidencia, impacto y ejecución",
            "mantiene separados los hechos de las hipótesis comerciales",
            "permite completar trabajo local antes de solicitar aprobación externa",
        ],
        "human_benefit": selected["benefit"],
        "beneficiaries": selected["beneficiaries"],
        "next_action": next(
            action["title"]
            for action in benefit_plan["actions"]
            if action["status"] == "awaiting_approval"
        ),
        "technical_limits": (
            mission_result.get("verification", {}).get("reason")
            if not verified
            else "El modelo térmico sigue siendo un proxy: no es CFD ni validación de campo."
        ),
        "generated_at": _utc_now(),
    }


def render_decision_markdown(state: dict[str, Any]) -> str:
    brief = state.get("decision_brief") or {}
    plan = state.get("benefit_plan") or {}
    selected = plan.get("selected_opportunity") or {}
    lines = [
        "# ORPHEUS Ω — Memo de decisión",
        "",
        f"**Objetivo:** {brief.get('goal', state.get('goal', '—'))}",
        f"**Modo:** {brief.get('mode', '—')}",
        f"**Estado técnico:** {brief.get('technical_status', '—')}",
        "",
        "## Recomendación",
        brief.get("recommendation", "Sin recomendación disponible."),
        "",
        "## Beneficio humano",
        brief.get("human_benefit", "Pendiente de definir."),
        "",
        "## Oportunidad priorizada",
        f"- Oferta: {selected.get('offer', '—')}",
        f"- Modelo: {selected.get('revenue_model', '—')}",
        f"- Precio hipotético: USD {selected.get('price_hypothesis_usd', '—')}",
        f"- Costo hipotético: USD {selected.get('unit_cost_hypothesis_usd', '—')}",
        f"- Margen bruto hipotético: USD {selected.get('gross_margin_hypothesis_usd', '—')}",
        "",
        "## Próxima acción",
        brief.get("next_action", "—"),
        "",
        "## Límites",
        brief.get("technical_limits", "—"),
        "",
        f"> {plan.get('disclaimer', '')}",
    ]
    return "\n".join(lines).strip() + "\n"


class AutonomousRuntime:
    """Autonomous, evidence-labelled control loop.

    Safe local planning runs automatically. External communication, publication,
    contracting, payments, account changes, private-data disclosure, and
    irreversible actions remain approval-gated.
    """

    def __init__(self, state_path: str | Path | None = None) -> None:
        interval = int(os.getenv("ORPHEUS_AUTONOMY_INTERVAL_SECONDS", "300"))
        self.interval_seconds = max(30, interval)
        self.autostart = _as_bool(os.getenv("ORPHEUS_AUTONOMY_ENABLED"), True)
        configured_path = os.getenv("ORPHEUS_STATE_PATH")
        self.state_path = Path(state_path or configured_path) if (state_path or configured_path) else None
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._profile = _default_profile()
        self._state = self._initial_state()
        self._load_state()

    def _initial_state(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "enabled": False,
            "status": "idle",
            "cycle_id": None,
            "cycle_number": 0,
            "last_started_at": None,
            "last_completed_at": None,
            "next_cycle_in_seconds": self.interval_seconds,
            "goal": self._profile["objective"],
            "classification": None,
            "agents": [
                {**agent, "status": "ready", "last_action": "Esperando ciclo"}
                for agent in AGENT_ROSTER
            ],
            "pipeline": [],
            "mission_result": None,
            "benefit_plan": None,
            "decision_brief": None,
            "cycle_history": [],
            "events": [
                {
                    "id": str(uuid4()),
                    "at": _utc_now(),
                    "type": "system",
                    "message": "Control autónomo v2 inicializado.",
                }
            ],
        }

    def _load_state(self) -> None:
        if not self.state_path or not self.state_path.exists():
            return
        try:
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return
        if loaded.get("schema_version") != 2:
            return
        loaded["enabled"] = False
        loaded["status"] = "restored"
        self._state.update(loaded)
        profile = (loaded.get("benefit_plan") or {}).get("profile")
        if isinstance(profile, dict):
            self._profile.update(profile)
        self._event("system", "Estado restaurado desde almacenamiento local.")

    def _persist(self) -> None:
        if not self.state_path:
            return
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.state_path.with_suffix(self.state_path.suffix + ".tmp")
        temp.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temp.replace(self.state_path)

    async def start(self) -> dict[str, Any]:
        async with self._lock:
            self._state["enabled"] = True
            self._state["status"] = "ready"
            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._loop(), name="orpheus-autonomy-v2")
            self._event("system", "Modo autónomo activado.")
            self._persist()
            return deepcopy(self._state)

    async def stop(self) -> dict[str, Any]:
        async with self._lock:
            self._state["enabled"] = False
            self._state["status"] = "paused"
            task = self._task
            self._task = None
            self._event("system", "Modo autónomo pausado por el humano.")
            self._persist()
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        return await self.snapshot()

    async def shutdown(self) -> None:
        async with self._lock:
            self._state["enabled"] = False
            task = self._task
            self._task = None
            self._persist()
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def set_goal(self, goal: str) -> dict[str, Any]:
        clean = _clean_text(goal)
        if not clean:
            raise ValueError("goal cannot be empty")
        async with self._lock:
            self._state["goal"] = clean
            self._state["classification"] = classify_goal(clean)
            self._event("human_direction", f"Nueva dirección humana: {clean[:240]}")
            self._persist()
        return await self.snapshot()

    async def update_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        allowed = {"human", "objective", "beneficiaries", "preferred_outcomes"}
        clean = {key: value for key, value in profile.items() if key in allowed}
        async with self._lock:
            self._profile.update(clean)
            if "objective" in clean:
                self._state["goal"] = _clean_text(str(clean["objective"]))
            self._event("profile", "Perfil de beneficio humano actualizado.")
            self._persist()
        return await self.snapshot()

    async def decide_action(
        self, action_id: str, decision: str, note: str | None = None
    ) -> dict[str, Any]:
        normalized = decision.strip().lower()
        if normalized not in {"approve", "decline"}:
            raise ValueError("decision must be approve or decline")
        async with self._lock:
            plan = self._state.get("benefit_plan") or {}
            for action in plan.get("actions") or []:
                if action["id"] != action_id:
                    continue
                if not action.get("requires_human_approval"):
                    raise ValueError("local completed actions do not require a decision")
                action["status"] = "approved" if normalized == "approve" else "declined"
                action["decided_at"] = _utc_now()
                action["decision_note"] = _clean_text(note or "", 500)
                self._event(
                    "approval",
                    f"Acción {action['status']}: {action['title']}.",
                )
                self._persist()
                return deepcopy(self._state)
        raise KeyError(f"unknown action: {action_id}")

    async def approve(self, action_id: str) -> dict[str, Any]:
        return await self.decide_action(action_id, "approve")

    async def run_cycle(
        self,
        trigger: str = "scheduler",
        run_key: str | None = None,
    ) -> dict[str, Any]:
        cycle_id = str(uuid4())
        classification = classify_goal(self._state["goal"])
        pipeline = [
            ("ORION", "Definir contrato de misión"),
            ("VIGÍA", "Mapear antecedentes y oportunidades"),
            ("NYX-7", "Detectar fallos y dependencias"),
            ("VEGA", "Separar evidencia, hipótesis y vacíos"),
            ("ATLAS-9", "Diseñar solución y ruta operativa"),
            ("SPARK", "Ejecutar herramientas deterministas disponibles"),
            ("AUREUS-7", "Modelar beneficio, precio y sostenibilidad"),
            ("BASTION", "Aplicar límites y puertas de aprobación"),
            ("ECHO", "Construir memo y trazabilidad"),
            ("KIRA", "Integrar la decisión para el humano"),
        ]

        async with self._lock:
            if self._state["status"] == "running":
                return deepcopy(self._state)
            if run_key and self._state.get("last_run_key") == run_key:
                self._event("cycle", f"Ciclo duplicado ignorado: {run_key}.")
                return deepcopy(self._state)
            self._state.update(
                {
                    "status": "running",
                    "cycle_id": cycle_id,
                    "cycle_number": self._state["cycle_number"] + 1,
                    "last_started_at": _utc_now(),
                    "last_run_key": run_key,
                    "classification": classification,
                    "pipeline": [
                        {
                            "step": index + 1,
                            "agent": agent,
                            "title": title,
                            "status": "queued",
                            "started_at": None,
                            "completed_at": None,
                            "output_summary": None,
                        }
                        for index, (agent, title) in enumerate(pipeline)
                    ],
                }
            )
            self._event("cycle", f"Ciclo autónomo iniciado ({trigger}).")
            self._persist()

        catalog = list_historical_concepts()
        contract = _mission_contract(self._state["goal"], classification)
        mission_result: dict[str, Any] | None = None
        stage_outputs = [
            f"{len(contract['victory_conditions'])} condiciones de victoria definidas.",
            (
                f"{catalog['count']} conceptos catalogados; "
                f"{len(catalog['source_verification_pending'])} requieren fuente primaria."
            ),
            "Riesgos críticos: evidencia histórica, validación de campo y propiedad intelectual.",
            (
                "Misión verificable con simulador existente."
                if classification["supported"]
                else "Objetivo en descubrimiento; prohibido heredar verificación de otra misión."
            ),
            (
                "Se usarán candidatos del paquete de referencia."
                if classification["supported"]
                else "Se requiere diseñar instrumento, datos y prototipo de prueba."
            ),
            "Herramienta determinista ejecutada." if classification["supported"] else "No se ejecutó simulador no pertinente.",
            "Escenarios económicos etiquetados como hipótesis.",
            "Acciones externas y financieras enviadas a aprobación humana.",
            "Memo de decisión y límites preparados.",
            "Resultado integrado y listo para revisión humana.",
        ]

        for index, (agent_name, title) in enumerate(pipeline):
            async with self._lock:
                step = self._state["pipeline"][index]
                step["status"] = "running"
                step["started_at"] = _utc_now()
                self._set_agent(agent_name, "working", title)
                self._persist()
            await asyncio.sleep(0)
            if agent_name == "SPARK":
                mission_result = (
                    run_reference_mission()
                    if classification["supported"]
                    else _discovery_mission(self._state["goal"])
                )
            async with self._lock:
                step = self._state["pipeline"][index]
                step["status"] = "completed"
                step["completed_at"] = _utc_now()
                step["output_summary"] = stage_outputs[index]
                self._set_agent(agent_name, "completed", stage_outputs[index])
                self._persist()

        assert mission_result is not None
        benefit_plan = build_opportunity_plan(
            mission_result, self._profile, classification
        )
        decision_brief = build_decision_brief(
            self._state["goal"], classification, mission_result, benefit_plan
        )

        async with self._lock:
            self._state["mission_result"] = mission_result
            self._state["benefit_plan"] = benefit_plan
            self._state["decision_brief"] = decision_brief
            self._state["last_completed_at"] = _utc_now()
            self._state["status"] = "watching" if self._state["enabled"] else "idle"
            selected = benefit_plan["selected_opportunity"]["title"]
            self._state["cycle_history"].insert(
                0,
                {
                    "cycle_id": cycle_id,
                    "number": self._state["cycle_number"],
                    "goal": self._state["goal"],
                    "mode": classification["mode"],
                    "status": mission_result["mission_status"],
                    "selected_opportunity": selected,
                    "completed_at": self._state["last_completed_at"],
                },
            )
            del self._state["cycle_history"][20:]
            self._event(
                "result",
                f"Ciclo completado en modo {classification['mode']}. "
                f"Oportunidad priorizada: {selected}.",
            )
            self._persist()
            return deepcopy(self._state)

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            return deepcopy(self._state)

    async def export_markdown(self) -> str:
        async with self._lock:
            return render_decision_markdown(deepcopy(self._state))

    async def _loop(self) -> None:
        await asyncio.sleep(0.05)
        while True:
            async with self._lock:
                enabled = bool(self._state["enabled"])
            if not enabled:
                return
            await self.run_cycle("autostart")
            await asyncio.sleep(self.interval_seconds)

    def _set_agent(self, name: str, status: str, last_action: str) -> None:
        for agent in self._state["agents"]:
            if agent["name"] == name:
                agent["status"] = status
                agent["last_action"] = last_action
                agent["updated_at"] = _utc_now()
                return

    def _event(self, event_type: str, message: str) -> None:
        events = self._state["events"]
        events.insert(
            0,
            {
                "id": str(uuid4()),
                "at": _utc_now(),
                "type": event_type,
                "message": message,
            },
        )
        del events[100:]


runtime = AutonomousRuntime()
