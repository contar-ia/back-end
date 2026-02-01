"""Grafo LangGraph para pipeline de geração e validação de histórias infantis."""
import logging
from langgraph.graph import StateGraph, END
from story_state import StoryState
from story_agents import (
    generate_story,
    validate_safety,
    validate_requirements,
    review_final
)

logger = logging.getLogger(__name__)


def should_continue_after_safety(state: StoryState) -> str:
    """Decide se deve continuar após validação de segurança."""
    safety_ok = state.get("safety_ok", False)
    if safety_ok:
        logger.info("🔀 [DECISÃO] Após segurança: APROVADO → Continuando para Validador de Requisitos")
        return "validate_requirements"
    logger.warning("🔀 [DECISÃO] Após segurança: REPROVADO → Finalizando pipeline")
    return "end"


def should_continue_after_requirements(state: StoryState) -> str:
    """Decide se deve continuar após validação de requisitos."""
    requirements_ok = state.get("requirements_ok", False)
    if requirements_ok:
        logger.info("🔀 [DECISÃO] Após requisitos: APROVADO → Continuando para Revisor Final")
        return "review_final"
    logger.warning("🔀 [DECISÃO] Após requisitos: REPROVADO → Finalizando pipeline")
    return "end"


def build_story_graph() -> StateGraph:
    """
    Constrói o grafo LangGraph com o fluxo:
    1. Input → Gerador
    2. Gerador → Validador de Segurança
    3. Validador de Segurança → Validador de Requisitos (se safety_ok) OU fim (se não)
    4. Validador de Requisitos → Revisor Final (se requirements_ok) OU fim (se não)
    5. Revisor Final → fim
    """
    workflow = StateGraph(StoryState)
    
    # Adicionar nós (agentes) com metadados para melhor visualização no LangGraph Studio
    workflow.add_node(
        "generate_story", 
        generate_story
    )
    workflow.add_node(
        "validate_safety", 
        validate_safety
    )
    workflow.add_node(
        "validate_requirements", 
        validate_requirements
    )
    workflow.add_node(
        "review_final", 
        review_final
    )
    
    # Definir fluxo
    workflow.set_entry_point("generate_story")
    
    workflow.add_edge("generate_story", "validate_safety")
    
    # Condicional após validação de segurança
    workflow.add_conditional_edges(
        "validate_safety",
        should_continue_after_safety,
        {
            "validate_requirements": "validate_requirements",
            "end": END
        }
    )
    
    # Condicional após validação de requisitos
    workflow.add_conditional_edges(
        "validate_requirements",
        should_continue_after_requirements,
        {
            "review_final": "review_final",
            "end": END
        }
    )
    
    workflow.add_edge("review_final", END)
    
    return workflow.compile()


# Instância global do grafo compilado
story_graph = build_story_graph()
