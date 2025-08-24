import pathlib
import sys

# Garante que o diretório raiz do repositório esteja no PYTHONPATH
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from packages.agents.agente import (
    Agente,
    AgentResult,
    ModeloConfig,
    PromptSpec,
)


def test_agente_execucao_basica():
    modelo = ModeloConfig(
        provedor="openai",
        modelo="gpt-4o-mini",
        api_funcao="chat_completions",
    )
    prompt = PromptSpec(estatica="Olá {nome}", variaveis_esperadas=["nome"])

    agente = Agente(
        id="teste",
        nome="Agente de Teste",
        role="Você é um agente de teste",
        modelo=modelo,
        prompt=prompt,
    )

    resultado = agente.executar({"nome": "Bob"}, ferramentas_disponiveis={})

    assert isinstance(resultado, AgentResult)
    assert resultado.texto == "RESPOSTA_FAKE_OPENAI"
    assert resultado.ferramentas_usadas == []
    assert resultado.metadados["provider"] == "openai"
