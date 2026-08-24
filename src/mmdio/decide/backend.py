"""Backend abstraction over scikit-decide's registry and solver contracts."""

from __future__ import annotations

from typing import Any, Protocol

from mmdio.decide.models import DecisionRefusal, RefusalCode


class DecisionBackend(Protocol):
    """Minimal backend contract consumed by :class:`DecisionService`."""

    def list_domains(self) -> list[str]:
        """Return registered domain names."""

    def list_solvers(self) -> list[str]:
        """Return registered solver names."""

    def load_domain(self, name: str) -> type[Any]:
        """Resolve a registered domain class."""

    def load_solver(self, name: str) -> type[Any]:
        """Resolve a registered solver class."""

    def match_solvers(self, domain: Any) -> list[type[Any]]:
        """Return solver classes compatible with ``domain``."""


class ScikitDecideBackend:
    """Lazy adapter for the optional scikit-decide dependency."""

    @staticmethod
    def _utils() -> Any:
        try:
            from skdecide import utils
        except ImportError as error:
            raise DecisionRefusal(
                RefusalCode.DEPENDENCY_UNAVAILABLE,
                "scikit-decide is unavailable; install mmdio[decision] under Python 3.12",
                details={"dependency": "scikit-decide", "required_runtime": "CPython 3.12"},
            ) from error
        return utils

    def list_domains(self) -> list[str]:
        """Return registered domain names in deterministic order."""
        return sorted(str(name) for name in self._utils().get_registered_domains())

    def list_solvers(self) -> list[str]:
        """Return registered solver names in deterministic order."""
        return sorted(str(name) for name in self._utils().get_registered_solvers())

    def load_domain(self, name: str) -> type[Any]:
        """Resolve a domain class or refuse with a stable code."""
        try:
            return self._utils().load_registered_domain(name)
        except Exception as error:
            raise DecisionRefusal(
                RefusalCode.DOMAIN_UNKNOWN,
                f"registered domain not found: {name}",
                details={"domain": name},
            ) from error

    def load_solver(self, name: str) -> type[Any]:
        """Resolve a solver class or refuse with a stable code."""
        try:
            return self._utils().load_registered_solver(name)
        except Exception as error:
            raise DecisionRefusal(
                RefusalCode.SOLVER_UNKNOWN,
                f"registered solver not found: {name}",
                details={"solver": name},
            ) from error

    def match_solvers(self, domain: Any) -> list[type[Any]]:
        """Return compatible solver classes for an instantiated domain."""
        return list(self._utils().match_solvers(domain))
