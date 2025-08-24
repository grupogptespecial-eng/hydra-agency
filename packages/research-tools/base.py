from __future__ import annotations

import os
import time
from typing import Any, Dict, Iterable, Optional, Callable

import requests
import importlib.util
from pathlib import Path

from packages.tools.base import Tool
_path_spec = importlib.util.spec_from_file_location(
    "research_tools.common.pathing",
    Path(__file__).resolve().parent / "common" / "pathing.py",
)
_path_module = importlib.util.module_from_spec(_path_spec)
assert _path_spec.loader is not None  # pragma: no cover
_path_spec.loader.exec_module(_path_module)  # type: ignore
build_key = _path_module.build_key  # type: ignore

# Carrega módulo db dinamicamente pois o diretório possui hífen no nome
_db_spec = importlib.util.spec_from_file_location(
    "py_utils.db", Path(__file__).resolve().parents[1] / "py-utils" / "db.py"
)
db = importlib.util.module_from_spec(_db_spec)
assert _db_spec.loader is not None  # pragma: no cover - segurança
_db_spec.loader.exec_module(db)  # type: ignore


class ResearchTool(Tool):
    """Tool especializada para consultas a APIs de pesquisa.

    Fornece utilitários de requisição HTTP com *retry*, respeito a
    ``rate_limit`` simples e helpers de datas.
    """

    def __init__(
        self,
        *,
        name: str,
        category: str,
        scope: str,
        inputs_schema: Iterable[str],
        output_schema: str,
        providers: Iterable[Callable[..., Dict[str, Any]]],
        ttl: Any,
        side_effects: Dict[str, Iterable[str]],
        allowed_agents: Iterable[str],
        base_url: str = "",
        default_headers: Optional[Dict[str, str]] = None,
        required_env_keys: Iterable[str] = (),
        optional_env_keys: Iterable[str] = (),
        max_retries: int = 2,
        backoff_base_s: float = 1.2,
        rate_limit_per_sec: Optional[float] = None,
        timeout_s: int = 30,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            name=name,
            category=category,
            scope=scope,
            inputs_schema=inputs_schema,
            output_schema=output_schema,
            providers=providers,
            ttl=ttl,
            side_effects=side_effects,
            allowed_agents=allowed_agents,
            **kwargs,
        )
        self.base_url = base_url
        self.default_headers = default_headers or {}
        self.required_env_keys = tuple(required_env_keys)
        self.optional_env_keys = tuple(optional_env_keys)
        self.max_retries = max_retries
        self.backoff_base_s = backoff_base_s
        self.rate_limit_per_sec = rate_limit_per_sec
        self.timeout_s = timeout_s
        self._last_call_ts = 0.0

    # ------------------------------------------------------------------
    # Helpers de cache/persistência
    # ------------------------------------------------------------------
    def _db_key(self, ctx: Dict[str, Any]) -> Optional[str]:
        """Constrói a chave hierárquica ``tipo/nivel/codigo``.

        Espera que ``ctx`` contenha ``data_type``, ``level`` e ``code`` ou
        ``identifier``. Caso algum esteja ausente, a função retorna
        ``None``, indicando que a ferramenta não utilizará cache
        persistente para este contexto.
        """

        data_type = ctx.get("data_type")
        level = ctx.get("level")
        identifier = ctx.get("identifier") or ctx.get("code")
        if not all([data_type, level, identifier]):
            return None
        return build_key(str(data_type), str(level), str(identifier))

    def fetch_from_db(self, ctx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        key = self._db_key(ctx)
        if not key:
            return None
        return db.fetch(key)

    def save_to_db(self, ctx: Dict[str, Any], data: Dict[str, Any]) -> None:
        key = self._db_key(ctx)
        if not key:
            return
        db.save(key, data)

    # ------------------------------------------------------------------
    # Helpers de ambiente e rate limit
    # ------------------------------------------------------------------
    def _get_env(self) -> Dict[str, Optional[str]]:
        env = {k: os.getenv(k) for k in self.required_env_keys + self.optional_env_keys}
        missing = [k for k in self.required_env_keys if not env.get(k)]
        if missing:
            raise RuntimeError(f"[{self.name}] missing required env vars: {missing}")
        return env

    def _respect_rate_limit(self) -> None:
        if not self.rate_limit_per_sec:
            return
        min_interval = 1.0 / self.rate_limit_per_sec
        now = time.time()
        elapsed = now - self._last_call_ts
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_call_ts = time.time()

    # ------------------------------------------------------------------
    # Helpers de requisição HTTP
    # ------------------------------------------------------------------
    def _request_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        hdrs = dict(self.default_headers)
        if headers:
            hdrs.update(headers)
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            self._respect_rate_limit()
            try:
                resp = requests.get(url, headers=hdrs, timeout=self.timeout_s)
                if resp.status_code == 429:
                    time.sleep(self.backoff_base_s * (attempt + 1))
                    continue
                resp.raise_for_status()
                ctype = resp.headers.get("Content-Type", "").lower()
                if "json" in ctype or url.endswith(".json"):
                    return resp.json()
                try:
                    return resp.json()
                except Exception:
                    return {"raw": resp.text}
            except Exception as err:  # pragma: no cover - best effort
                last_err = err
                time.sleep(self.backoff_base_s * (attempt + 1))
        raise RuntimeError(f"[{self.name}] error requesting {url}: {last_err}")

    def _request_bytes(self, url: str, headers: Optional[Dict[str, str]] = None) -> bytes:
        hdrs = dict(self.default_headers)
        if headers:
            hdrs.update(headers)
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            self._respect_rate_limit()
            try:
                resp = requests.get(url, headers=hdrs, timeout=self.timeout_s)
                if resp.status_code == 429:
                    time.sleep(self.backoff_base_s * (attempt + 1))
                    continue
                resp.raise_for_status()
                return resp.content
            except Exception as err:  # pragma: no cover - best effort
                last_err = err
                time.sleep(self.backoff_base_s * (attempt + 1))
        raise RuntimeError(f"[{self.name}] error requesting {url}: {last_err}")

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------
    @staticmethod
    def span_years(start_year: int, end_year: int) -> str:
        if end_year < start_year:
            raise ValueError("end_year < start_year")
        return f"{start_year}:{end_year}"

    # ------------------------------------------------------------------
    # Implementação padrão de call_providers
    # ------------------------------------------------------------------
    def call_providers(self, ctx: Dict[str, Any], chunk: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.providers:
            raise RuntimeError("no provider configured")
        provider = self.providers[0]
        if callable(provider):
            return provider(ctx, chunk)
        raise RuntimeError("provider must be callable")

    # ------------------------------------------------------------------
    # Execução com cache em banco
    # ------------------------------------------------------------------
    def execute(self, ctx: Dict[str, Any], *, run_id: str, agent_id: str) -> "ToolResult":
        cached = self.fetch_from_db(ctx)
        if cached is not None:
            meta = {"run_id": run_id, "tool_name": self.name, "db_key": self._db_key(ctx)}
            from packages.tools.base import ToolResult  # import local para evitar ciclo

            return ToolResult(kind=self.output_schema, data=cached, meta=meta, errors=[])

        result = super().execute(ctx, run_id=run_id, agent_id=agent_id)
        self.save_to_db(ctx, result.data)
        result.meta["db_key"] = self._db_key(ctx)
        return result


__all__ = ["ResearchTool"]
