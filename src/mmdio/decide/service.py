"""Typed decision service shared by Typer and FastMCP projections."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import asdict, is_dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Any, Mapping

from mmdio.decide.backend import DecisionBackend, ScikitDecideBackend
from mmdio.decide.mermaid import match_to_mermaid, rollout_to_mermaid
from mmdio.decide.models import (
    DecisionCatalog,
    DecisionMatch,
    DecisionRefusal,
    DecisionRun,
    DecisionStatus,
    DecisionStep,
    RefusalCode,
)

_RECEIPT_SCHEMA = "mmdio.scikit-decide-receipt/1"
_CLAIM_CEILING = "REGISTERED_DOMAIN_SOLVER_MATCH_AND_BOUNDED_ROLLOUT_ONLY"
_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _symbol_name(value: Any) -> str:
    return str(getattr(value, "__name__", value))


def _termination(value: Any) -> bool:
    if isinstance(value, Mapping):
        flags = [bool(flag) for flag in value.values()]
        return bool(flags) and all(flags)
    return bool(value)


def to_jsonable(value: Any) -> Any:
    """Convert common solver/domain values into stable JSON-compatible data."""
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Enum):
        return to_jsonable(value.value)
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): to_jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, tuple | list):
        return [to_jsonable(item) for item in value]
    if isinstance(value, set | frozenset):
        converted = [to_jsonable(item) for item in value]
        return sorted(converted, key=_canonical_json)
    if hasattr(value, "_asdict"):
        return to_jsonable(value._asdict())
    if hasattr(value, "to_json"):
        rendered = value.to_json()
        try:
            return to_jsonable(json.loads(rendered))
        except (TypeError, json.JSONDecodeError):
            return str(rendered)
    if hasattr(value, "__dict__"):
        public = {
            key: item
            for key, item in vars(value).items()
            if not key.startswith("_") and not callable(item)
        }
        if public:
            return to_jsonable(public)
    rendered = _ADDRESS_RE.sub("<address>", str(value))
    if rendered:
        return rendered
    raise DecisionRefusal(
        RefusalCode.SERIALIZATION_FAILED,
        f"cannot serialize value of type {type(value).__name__}",
    )


class DecisionService:
    """Construct, match, solve, visualize, and receipt formal decision problems."""

    def __init__(self, backend: DecisionBackend | None = None) -> None:
        self._backend = backend or ScikitDecideBackend()

    def catalog(self) -> DecisionCatalog:
        """Return the deterministic registry catalog."""
        return DecisionCatalog(
            domains=tuple(self._backend.list_domains()),
            solvers=tuple(self._backend.list_solvers()),
        )

    def match(
        self,
        domain: str,
        *,
        domain_arguments: dict[str, Any] | None = None,
    ) -> DecisionMatch:
        """Instantiate a domain and return compatible registered solvers."""
        arguments = domain_arguments or {}
        domain_instance = self._construct_domain(domain, arguments)
        compatible = tuple(
            sorted(_symbol_name(item) for item in self._backend.match_solvers(domain_instance))
        )
        return DecisionMatch(
            domain=domain,
            compatible_solvers=compatible,
            domain_arguments=to_jsonable(arguments),
        )

    def match_mermaid(
        self,
        domain: str,
        *,
        domain_arguments: dict[str, Any] | None = None,
    ) -> str:
        """Render compatible solvers as a Mermaid flowchart."""
        return match_to_mermaid(self.match(domain, domain_arguments=domain_arguments))

    def solve(
        self,
        domain: str,
        *,
        solver: str | None = None,
        domain_arguments: dict[str, Any] | None = None,
        solver_arguments: dict[str, Any] | None = None,
        max_steps: int = 100,
    ) -> DecisionRun:
        """Solve a registered domain and capture a deterministic bounded rollout."""
        if max_steps < 1:
            raise DecisionRefusal(
                RefusalCode.INVALID_ARGUMENTS,
                "max_steps must be at least 1",
                details={"max_steps": max_steps},
            )

        domain_args = domain_arguments or {}
        solver_args = solver_arguments or {}
        domain_type = self._backend.load_domain(domain)
        domain_instance = self._construct_domain(domain, domain_args, domain_type=domain_type)
        match = self.match(domain, domain_arguments=domain_args)
        selected_solver = solver or (match.compatible_solvers[0] if match.compatible_solvers else None)
        if selected_solver is None:
            raise DecisionRefusal(
                RefusalCode.SOLVER_INCOMPATIBLE,
                f"no compatible solver registered for domain {domain}",
                details={"domain": domain},
            )
        if selected_solver not in match.compatible_solvers:
            raise DecisionRefusal(
                RefusalCode.SOLVER_INCOMPATIBLE,
                f"solver {selected_solver} is not compatible with domain {domain}",
                details={
                    "domain": domain,
                    "solver": selected_solver,
                    "compatible_solvers": list(match.compatible_solvers),
                },
            )

        solver_type = self._backend.load_solver(selected_solver)

        def domain_factory() -> Any:
            return domain_type(**domain_args)

        try:
            solver_instance = solver_type(domain_factory=domain_factory, **solver_args)
            context = (
                solver_instance if hasattr(solver_instance, "__enter__") else nullcontext(solver_instance)
            )
            with context as active_solver:
                active_solver.solve()
                initial = domain_instance.reset()
                observation = initial
                steps: list[DecisionStep] = []
                for index in range(max_steps):
                    action = active_solver.sample_action(observation)
                    outcome = domain_instance.step(action)
                    terminated = _termination(getattr(outcome, "termination", False))
                    next_observation = getattr(outcome, "observation", outcome)
                    steps.append(
                        DecisionStep(
                            index=index,
                            observation=to_jsonable(observation),
                            action=to_jsonable(action),
                            next_observation=to_jsonable(next_observation),
                            value=to_jsonable(getattr(outcome, "value", None)),
                            termination=terminated,
                            info=to_jsonable(getattr(outcome, "info", None)),
                        )
                    )
                    observation = next_observation
                    if terminated:
                        break
        except DecisionRefusal:
            raise
        except Exception as error:
            raise DecisionRefusal(
                RefusalCode.SOLVE_FAILED,
                f"solver execution failed for {domain} with {selected_solver}",
                details={"domain": domain, "solver": selected_solver, "error": str(error)},
            ) from error

        initial_json = to_jsonable(initial)
        step_tuple = tuple(steps)
        mermaid = rollout_to_mermaid(initial_json, step_tuple)
        terminal = bool(step_tuple and step_tuple[-1].termination)
        input_subject = {
            "domain": domain,
            "solver": selected_solver,
            "domain_arguments": to_jsonable(domain_args),
            "solver_arguments": to_jsonable(solver_args),
            "max_steps": max_steps,
        }
        trajectory = [step.as_dict() for step in step_tuple]
        input_sha = _sha256(input_subject)
        trajectory_sha = _sha256(trajectory)
        mermaid_sha = hashlib.sha256(mermaid.encode()).hexdigest()
        receipt_subject = {
            "schema": _RECEIPT_SCHEMA,
            "status": DecisionStatus.SOLVED.value if terminal else DecisionStatus.BOUNDED.value,
            "input_sha256": input_sha,
            "trajectory_sha256": trajectory_sha,
            "mermaid_sha256": mermaid_sha,
            "claim_ceiling": _CLAIM_CEILING,
        }
        return DecisionRun(
            schema=_RECEIPT_SCHEMA,
            status=DecisionStatus.SOLVED if terminal else DecisionStatus.BOUNDED,
            domain=domain,
            solver=selected_solver,
            domain_arguments=to_jsonable(domain_args),
            solver_arguments=to_jsonable(solver_args),
            initial_observation=initial_json,
            steps=step_tuple,
            terminal=terminal,
            max_steps=max_steps,
            mermaid=mermaid,
            input_sha256=input_sha,
            trajectory_sha256=trajectory_sha,
            mermaid_sha256=mermaid_sha,
            receipt_sha256=_sha256(receipt_subject),
            claim_ceiling=_CLAIM_CEILING,
        )

    def _construct_domain(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        domain_type: type[Any] | None = None,
    ) -> Any:
        resolved = domain_type or self._backend.load_domain(name)
        try:
            return resolved(**arguments)
        except DecisionRefusal:
            raise
        except Exception as error:
            raise DecisionRefusal(
                RefusalCode.DOMAIN_CONSTRUCTION_FAILED,
                f"failed to construct domain {name}",
                details={
                    "domain": name,
                    "arguments": to_jsonable(arguments),
                    "error": str(error),
                },
            ) from error
