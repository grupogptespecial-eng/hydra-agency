from __future__ import annotations

"""Base classes para ferramentas do sistema Hermes."""
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional
import hashlib
import json
import time

# cache simples em memória para demonstração
_CACHE: Dict[str, Dict[str, Any]] = {}


def _parse_ttl(ttl: Any) -> int:
    """Converte a representação de TTL em segundos."""
    if ttl in (None, 0, "0"):
        return 0
    if isinstance(ttl, int):
        return ttl
    if isinstance(ttl, str):
        if ttl.endswith("h"):
            return int(ttl[:-1]) * 3600
        if ttl.endswith("d"):
            return int(ttl[:-1]) * 86400
    return 0


@dataclass
class ToolResult:
    """Resultado padrão de uma execução de ferramenta."""
    kind: str
    data: Dict[str, Any]
    meta: Dict[str, Any]
    errors: List[Any] = field(default_factory=list)


class Tool:
    """Classe base para todas as ferramentas.

    A implementação segue um contrato simples: valida entradas, verifica cache,
    chama providers, normaliza dados, gera snapshot e retorna um ``ToolResult``.
    """

    def __init__(
        self,
        name: str,
        category: str,
        scope: str,
        inputs_schema: Iterable[str],
        output_schema: str,
        providers: Iterable[str],
        ttl: Any,
        side_effects: Dict[str, Iterable[str]],
        allowed_agents: Iterable[str],
        rate_limit: Optional[str] = None,
        license_notes: Optional[str] = None,
    ) -> None:
        self.name = name
        self.category = category
        self.scope = scope
        self.inputs_schema = set(inputs_schema)
        self.output_schema = output_schema
        self.providers = list(providers)
        self.ttl = ttl
        self.side_effects = side_effects
        self.allowed_agents = set(allowed_agents)
        self.rate_limit = rate_limit
        self.license_notes = license_notes
        self._ttl_seconds = _parse_ttl(ttl)

    # --------------------- métodos obrigatórios ---------------------
    def validate(self, ctx: Dict[str, Any]) -> None:
        """Valida entradas obrigatórias conforme ``inputs_schema``."""
        missing = [k for k in self.inputs_schema if not k.endswith("?") and k not in ctx]
        if missing:
            raise ValueError(f"Missing inputs: {missing}")

    def cache_key(self, ctx: Dict[str, Any]) -> str:
        parts = [self.name, self.scope]
        for k in sorted(ctx.keys()):
            parts.append(f"{k}={ctx[k]}")
        return "|".join(parts)

    # Hooks que podem ser sobreescritos pelas ferramentas específicas
    def pre_execute(self, ctx: Dict[str, Any]) -> None:
        return None

    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError

    def normalize(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def snapshot(self, data: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """Salva um snapshot simples em JSON e retorna o manifest."""
        manifest = {
            "paths": [],
            "checksum": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
        }
        return manifest

    def post_execute(self, result: ToolResult) -> ToolResult:
        return result

    # ------------------------- helpers internos ---------------------
    def _merge_payload(self, base: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        if not base:
            return new
        merged = base.copy()
        if isinstance(base, dict) and isinstance(new, dict):
            merged.update(new)
            return merged
        return new

    def _dedupe_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data

    # ------------------------- execução principal -------------------
    def execute(self, ctx: Dict[str, Any], *, run_id: str, agent_id: str) -> ToolResult:
        if self.allowed_agents and agent_id not in self.allowed_agents:
            raise PermissionError("Agente não autorizado")

        self.validate(ctx)
        self.pre_execute(ctx)

        key = self.cache_key(ctx)
        now = time.time()
        cached = _CACHE.get(key)
        if cached and self._ttl_seconds > 0 and now - cached["ts"] < self._ttl_seconds:
            cached_res = cached["result"]
            return ToolResult(
                kind=self.output_schema,
                data=cached_res["data"],
                meta=cached_res["meta"],
                errors=cached_res["errors"],
            )

        # processamento simples sem slicing
        manifests: List[Dict[str, Any]] = []
        merged_data: Dict[str, Any] = {}
        errors: List[Any] = []

        try:
            raw = self.call_providers(ctx, None)
            data = self.normalize(raw)
            snap = self.snapshot(data, meta={"run_id": run_id, "tool_name": self.name})
            manifests.append(snap)
            merged_data = self._merge_payload(merged_data, data)
        except Exception as exc:  # pragma: no cover - simplicidade
            errors.append(str(exc))

        merged_data = self._dedupe_payload(merged_data)
        meta = {"run_id": run_id, "tool_name": self.name, "manifests": manifests}
        result = ToolResult(kind=self.output_schema, data=merged_data, meta=meta, errors=errors)

        _CACHE[key] = {"ts": now, "result": {"data": merged_data, "meta": meta, "errors": errors}}
        return self.post_execute(result)
