"""Implementação da classe Agente e estruturas auxiliares.

Esta implementação segue o pseudocódigo discutido previamente e
fornece um esqueleto funcional para agentes que interagem com
modelos de linguagem e ferramentas restritas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AgentResult:
    """Resultado padronizado retornado por um agente."""

    texto: str
    ferramentas_usadas: List[str]
    metadados: Dict[str, Any]


@dataclass
class ModeloConfig:
    """Configurações do modelo a ser utilizado pelo agente."""

    provedor: str
    modelo: str
    api_funcao: str
    parametros: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptSpec:
    """Especificação de prompt: parte estática, variáveis e formato de saída."""

    estatica: str
    variaveis_esperadas: List[str]
    formato_saida: Optional[str] = None


def chamar_modelo(
    cfg: ModeloConfig,
    mensagens: List[Dict[str, str]],
    ferramentas_ok: List[str],
    timeout: int,
) -> tuple[str, Dict[str, Any]]:
    """Dispatcher simplificado para diferentes provedores de modelo.

    Retorna uma tupla ``(texto, metadados)``. Esta função não realiza chamadas
    reais aos provedores; ela apenas simula respostas para fins de prototipagem.
    """

    meta: Dict[str, Any] = {
        "provider": cfg.provedor,
        "model": cfg.modelo,
        "api": cfg.api_funcao,
        "tools": ferramentas_ok,
    }

    # Os blocos abaixo simulam a resposta de cada provedor.
    if cfg.provedor == "openai" and cfg.api_funcao == "chat_completions":
        texto = "RESPOSTA_FAKE_OPENAI"
        meta["tokens"] = 1234
        return texto, meta

    if cfg.provedor == "gemini" and cfg.api_funcao == "generate_content":
        texto = "RESPOSTA_FAKE_GEMINI"
        meta["tokens"] = 980
        return texto, meta

    if cfg.provedor == "anthropic" and cfg.api_funcao == "messages":
        texto = "RESPOSTA_FAKE_ANTHROPIC"
        meta["tokens"] = 1100
        return texto, meta

    if cfg.provedor == "local" and cfg.api_funcao == "http_post":
        texto = "RESPOSTA_FAKE_LOCAL"
        meta["tokens"] = 500
        return texto, meta

    # Caso não mapeado
    return "(erro: provedor/função não configurados)", meta


class Agente:
    """Entidade que representa um agente com papel definido."""

    def __init__(
        self,
        id: str,
        nome: str,
        role: str,
        modelo: ModeloConfig,
        prompt: PromptSpec,
        ferramentas_permitidas: Optional[List[str]] | None = None,
        ferramentas_bloqueadas: Optional[List[str]] | None = None,
        timeout_seg: int = 60,
        tags: Optional[List[str]] | None = None,
    ) -> None:
        self.id = id
        self.nome = nome
        self.role = role
        self.modelo = modelo
        self.prompt = prompt
        self.ferramentas_permitidas = set(ferramentas_permitidas or [])
        self.ferramentas_bloqueadas = set(ferramentas_bloqueadas or [])
        self.timeout_seg = timeout_seg
        self.tags = tags or []

    # ------------------------------------------------------------------
    def montar_prompt(self, contexto: Dict[str, Any]) -> str:
        """Valida e monta o prompt final com base no contexto fornecido."""

        faltando = [k for k in self.prompt.variaveis_esperadas if k not in contexto]
        if faltando:
            raise ValueError(f"Variáveis ausentes: {faltando}")

        try:
            corpo = self.prompt.estatica.format(**contexto)
        except Exception:
            # Fallback defensivo: inclui o contexto bruto para evitar falha total.
            corpo = f"{self.prompt.estatica}\n\n{contexto}"

        if self.prompt.formato_saida:
            corpo += f"\n\n[FORMATO_DESEJADO]: {self.prompt.formato_saida}"

        return corpo

    # ------------------------------------------------------------------
    def pode_usar(self, ferramenta: str) -> bool:
        """Aplica política simples de allowlist/denylist para ferramentas."""

        if not self.ferramentas_permitidas:
            return False
        if ferramenta in self.ferramentas_bloqueadas:
            return False
        return ferramenta in self.ferramentas_permitidas

    # ------------------------------------------------------------------
    def executar(
        self,
        contexto: Dict[str, Any],
        ferramentas_disponiveis: Dict[str, Callable[..., Any]],
    ) -> AgentResult:
        """Executa o ciclo do agente: monta prompt, filtra ferramentas e
        chama o modelo escolhido.
        """

        prompt_final = self.montar_prompt(contexto)
        mensagens = [
            {"role": "system", "content": self.role},
            {"role": "user", "content": prompt_final},
        ]

        ferramentas_ok = [
            nome
            for nome in ferramentas_disponiveis.keys()
            if self.pode_usar(nome)
        ]

        texto, meta = chamar_modelo(
            self.modelo, mensagens, ferramentas_ok, timeout=self.timeout_seg
        )

        return AgentResult(texto=texto, ferramentas_usadas=ferramentas_ok, metadados=meta)
