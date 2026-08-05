from __future__ import annotations

import asyncio
import contextlib
import os
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .tools import run_reference_mission


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


AGENT_ROSTER: list[dict[str, str]] = [
    {"id": "kira", "name": "KIRA", "role": "Dirección, integración y entrega"},
    {"id": "orion", "name": "ORION", "role": "Contrato de misión y prioridades"},
    {"id": "vigia", "name": "VIGÍA", "role": "Radar de oportunidades y antecedentes"},
    {"id": "vega", "name": "VEGA", "role": "Evidencia, hipótesis y pruebas"},
    {"id": "atlas", "name": "ATLAS", "role": "Arquitectura y diseño manufacturable"},
    {"id": "spark", "name": "SPARK", "role": "Prototipos, simulación y ejecución local"},
    {"id": "aureus", "name": "AUREUS-7", "role": "Monetización, precios y capital"},
    {"id": "bastion", "name": "BASTION", "role": "Seguridad, legalidad y aprobaciones"},
    {"id": "echo", "name": "ECHO", "role": "Proveniencia, límites y trazabilidad"},
    {"id": "vanta", "name": "VANTA-0", "role": "Rutas alternativas legítimas"},
]


def _default_profile() -> dict[str, Any]:
    return {
        "human": "Dr. Arisnachy Gómez Díaz",
        "objective": (
            "Crear soluciones técnicas útiles, verificables y monetizables que "
            "generen beneficio real para personas y comunidades."
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


def build_opportunity_plan(
    mission_result: dict[str, Any],
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a deterministic benefit and monetization plan from verified evidence.

    These are opportunity hypotheses derived from the repository mission. They are
    not presented as live grants, customers, prices, patents, or market validation.
    External outreach and financial commitments remain behind a human approval gate.
    """

    profile = deepcopy(profile or _default_profile())
    winner = mission_result.get("winner") or {}
    simulation = winner.get("simulation") or {}
    design_name = winner.get("design", "ORPHEUS hybrid prototype A")
    verified = bool((winner.get("verification") or {}).get("approved"))

    evidence_strength = 86 if verified else 45
    cooling_delta = float(simulation.get("cooling_delta_c", 0.0))
    estimated_cost = float(simulation.get("estimated_cost_usd", 64.0) or 64.0)

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
            "unit_cost_hypothesis_usd": round(max(estimated_cost, 64.0), 2),
            "gross_margin_hypothesis_usd": round(
                129 - max(estimated_cost, 64.0), 2
            ),
            "evidence_score": evidence_strength,
            "impact_score": min(98, round(70 + cooling_delta)),
            "execution_score": 82,
            "risk": "medium",
            "external_validation_needed": [
                "seguridad alimentaria",
                "ensayo de campo",
                "durabilidad",
                "costo real de fabricación",
            ],
        },
        {
            "id": "b2b-pilot",
            "title": "Piloto B2B para ONG, cooperativas y agrocomercio",
            "benefit": (
                "Ofrecer una prueba controlada con métricas de temperatura, merma "
                "evitada y costo por kilogramo conservado."
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
            "external_validation_needed": [
                "cliente piloto",
                "métricas de campo",
                "contrato",
                "revisión de responsabilidad",
            ],
        },
        {
            "id": "research-license",
            "title": "Paquete de investigación, licencia y transferencia",
            "benefit": (
                "Convertir la simulación, documentación y diseño en un activo "
                "licenciable para universidades, fabricantes o incubadoras."
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
            "external_validation_needed": [
                "búsqueda de anterioridad",
                "asesoría de propiedad intelectual",
                "validación académica",
                "negociación de licencia",
            ],
        },
    ]

    for item in opportunities:
        risk_penalty = {"low": 4, "medium": 12, "high": 22}[item["risk"]]
        item["priority_score"] = round(
            item["evidence_score"] * 0.30
            + item["impact_score"] * 0.35
            + item["execution_score"] * 0.35
            - risk_penalty,
            1,
        )

    opportunities.sort(key=lambda item: item["priority_score"], reverse=True)
    selected = opportunities[0]

    actions = [
        {
            "id": "prepare-evidence-pack",
            "agent": "ECHO",
            "title": "Preparar paquete de evidencia reproducible",
            "kind": "local",
            "status": "completed",
            "requires_human_approval": False,
            "benefit": "Aumenta credibilidad y reduce ambigüedad al presentar el proyecto.",
        },
        {
            "id": "generate-unit-economics",
            "agent": "AUREUS-7",
            "title": "Calcular precio, costo, margen y escenarios",
            "kind": "local",
            "status": "completed",
            "requires_human_approval": False,
            "benefit": "Convierte el prototipo en una oferta económicamente evaluable.",
        },
        {
            "id": "design-field-protocol",
            "agent": "VEGA",
            "title": "Diseñar protocolo de validación de campo",
            "kind": "local",
            "status": "completed",
            "requires_human_approval": False,
            "benefit": "Define cómo demostrar seguridad, rendimiento y beneficio humano.",
        },
        {
            "id": "contact-pilot-partners",
            "agent": "VIGÍA",
            "title": "Buscar y contactar socios piloto",
            "kind": "external",
            "status": "awaiting_approval",
            "requires_human_approval": True,
            "benefit": "Puede convertir la hipótesis en evidencia de mercado y primer ingreso.",
        },
        {
            "id": "publish-commercial-offer",
            "agent": "AUREUS-7",
            "title": "Publicar oferta comercial y canal de cobro",
            "kind": "financial",
            "status": "awaiting_approval",
            "requires_human_approval": True,
            "benefit": "Habilita cobro, pero exige revisión humana de precio, términos y receptor.",
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


class AutonomousRuntime:
    """In-process autonomous control loop for ORPHEUS Ω.

    It performs safe, reversible, local planning automatically. External outreach,
    publication, contracting, payments, account changes, and irreversible actions
    are queued for explicit human approval.
    """

    def __init__(self) -> None:
        interval = int(os.getenv("ORPHEUS_AUTONOMY_INTERVAL_SECONDS", "300"))
        self.interval_seconds = max(30, interval)
        self.autostart = _as_bool(os.getenv("ORPHEUS_AUTONOMY_ENABLED"), True)
        self._lock = asyncio.Lock()
        self._task: asyncio.Task[None] | None = None
        self._profile = _default_profile()
        self._state: dict[str, Any] = {
            "enabled": False,
            "status": "idle",
            "cycle_id": None,
            "cycle_number": 0,
            "last_started_at": None,
            "last_completed_at": None,
            "next_cycle_in_seconds": self.interval_seconds,
            "goal": self._profile["objective"],
            "agents": [
                {**agent, "status": "ready", "last_action": "Esperando ciclo"}
                for agent in AGENT_ROSTER
            ],
            "pipeline": [],
            "mission_result": None,
            "benefit_plan": None,
            "events": [
                {
                    "id": str(uuid4()),
                    "at": _utc_now(),
                    "type": "system",
                    "message": "Control autónomo inicializado.",
                }
            ],
        }

    async def start(self) -> dict[str, Any]:
        async with self._lock:
            self._state["enabled"] = True
            self._state["status"] = "ready"
            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._loop(), name="orpheus-autonomy")
            self._event("system", "Modo autónomo activado.")
            return deepcopy(self._state)

    async def stop(self) -> dict[str, Any]:
        async with self._lock:
            self._state["enabled"] = False
            self._state["status"] = "paused"
            task = self._task
            self._task = None
            self._event("system", "Modo autónomo pausado por el humano.")
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
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def set_goal(self, goal: str) -> dict[str, Any]:
        clean = " ".join(goal.split()).strip()
        if not clean:
            raise ValueError("goal cannot be empty")
        async with self._lock:
            self._state["goal"] = clean[:1500]
            self._event("human_direction", f"Nueva dirección humana: {clean[:240]}")
        return await self.snapshot()

    async def update_profile(self, profile: dict[str, Any]) -> dict[str, Any]:
        allowed = {"human", "objective", "beneficiaries", "preferred_outcomes"}
        clean = {key: value for key, value in profile.items() if key in allowed}
        async with self._lock:
            self._profile.update(clean)
            self._state["goal"] = self._profile.get(
                "objective", self._state["goal"]
            )
            self._event("profile", "Perfil de beneficio humano actualizado.")
        return await self.snapshot()

    async def approve(self, action_id: str) -> dict[str, Any]:
        async with self._lock:
            plan = self._state.get("benefit_plan") or {}
            actions = plan.get("actions") or []
            for action in actions:
                if action["id"] == action_id:
                    if not action.get("requires_human_approval"):
                        return deepcopy(self._state)
                    action["status"] = "approved"
                    action["approved_at"] = _utc_now()
                    self._event(
                        "approval",
                        f"Acción aprobada por el humano: {action['title']}",
                    )
                    return deepcopy(self._state)
        raise KeyError(f"unknown action: {action_id}")

    async def run_cycle(self, trigger: str = "scheduler") -> dict[str, Any]:
        cycle_id = str(uuid4())
        pipeline = [
            ("ORION", "Convertir el objetivo humano en un contrato medible"),
            ("VIGÍA", "Explorar oportunidades y rutas de beneficio"),
            ("VEGA", "Separar evidencia, hipótesis y vacíos"),
            ("ATLAS", "Diseñar la solución y el plan operativo"),
            ("SPARK", "Ejecutar simulaciones y tareas locales seguras"),
            ("AUREUS-7", "Calcular monetización, precio y captura de valor"),
            ("BASTION", "Bloquear acciones inseguras o no autorizadas"),
            ("ECHO", "Registrar evidencia, límites y procedencia"),
            ("KIRA", "Integrar el resultado y entregarlo al humano"),
        ]
        async with self._lock:
            if self._state["status"] == "running":
                return deepcopy(self._state)
            self._state.update(
                {
                    "status": "running",
                    "cycle_id": cycle_id,
                    "cycle_number": self._state["cycle_number"] + 1,
                    "last_started_at": _utc_now(),
                    "pipeline": [
                        {
                            "step": index + 1,
                            "agent": agent,
                            "title": title,
                            "status": "queued",
                        }
                        for index, (agent, title) in enumerate(pipeline)
                    ],
                }
            )
            self._event("cycle", f"Ciclo autónomo iniciado ({trigger}).")

        for index, (agent_name, title) in enumerate(pipeline):
            async with self._lock:
                self._state["pipeline"][index]["status"] = "running"
                self._set_agent(agent_name, "working", title)
            await asyncio.sleep(0)
            async with self._lock:
                self._state["pipeline"][index]["status"] = "completed"
                self._set_agent(agent_name, "completed", title)

        mission_result = run_reference_mission()
        benefit_plan = build_opportunity_plan(mission_result, self._profile)

        async with self._lock:
            self._state["mission_result"] = mission_result
            self._state["benefit_plan"] = benefit_plan
            self._state["last_completed_at"] = _utc_now()
            self._state["status"] = "watching" if self._state["enabled"] else "idle"
            selected = benefit_plan["selected_opportunity"]["title"]
            self._event(
                "result",
                f"Ciclo completado. Oportunidad priorizada: {selected}.",
            )
            return deepcopy(self._state)

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            return deepcopy(self._state)

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
        del events[80:]


runtime = AutonomousRuntime()
