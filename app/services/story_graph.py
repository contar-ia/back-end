"""Grafo LangGraph para pipeline de geração e validação de histórias infantis."""
import logging
from langgraph.graph import StateGraph, END
from app.models.story_state import StoryState
from app.services.story_agents import (
    generate_story,
    regenerate_story,
    validate_safety,
    validate_requirements,
    review_final
)

logger = logging.getLogger(__name__)


def should_continue_after_safety(state: StoryState) -> str:
    """Decide se deve continuar após validação de segurança."""
    safety_ok = state.get("safety_ok", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 1)
    
    if safety_ok:
        logger.info("🔀 [DECISÃO] Após segurança: APROVADO → Continuando para Validador de Requisitos")
        return "validate_requirements"
    
    # Se não passou na segurança, verificar se pode tentar novamente
    # retry_count é incrementado em regenerate_story ANTES de chamar esta função
    # Então se retry_count já é >= max_retries, não deve tentar mais
    if retry_count < max_retries:
        logger.warning(f"🔀 [DECISÃO] Após segurança: REPROVADO → Voltando ao Gerador (tentativa {retry_count + 1}/{max_retries})")
        return "regenerate_story"
    
    logger.error(f"🔀 [DECISÃO] Após segurança: REPROVADO → Máximo de tentativas ({max_retries}) atingido (retry_count={retry_count}). Finalizando.")
    return "end"


def should_continue_after_requirements(state: StoryState) -> str:
    """Decide se deve continuar após validação de requisitos."""
    requirements_ok = state.get("requirements_ok", False)
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 1)
    
    if requirements_ok:
        logger.info("🔀 [DECISÃO] Após requisitos: APROVADO → Continuando para Revisor Final")
        return "review_final"
    
    # Se não passou nos requisitos, verificar se pode tentar novamente
    # retry_count é incrementado em regenerate_story ANTES de chamar esta função
    # Então se retry_count já é >= max_retries, não deve tentar mais
    if retry_count < max_retries:
        logger.warning(f"🔀 [DECISÃO] Após requisitos: REPROVADO → Voltando ao Gerador (tentativa {retry_count + 1}/{max_retries})")
        return "regenerate_story"
    
    logger.error(f"🔀 [DECISÃO] Após requisitos: REPROVADO → Máximo de tentativas ({max_retries}) atingido (retry_count={retry_count}). Finalizando.")
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
        "regenerate_story",
        regenerate_story
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
    
    # Regeneração volta para validação de segurança
    workflow.add_edge("regenerate_story", "validate_safety")
    
    # Condicional após validação de segurança
    workflow.add_conditional_edges(
        "validate_safety",
        should_continue_after_safety,
        {
            "validate_requirements": "validate_requirements",
            "regenerate_story": "regenerate_story",
            "end": END
        }
    )
    
    # Condicional após validação de requisitos
    workflow.add_conditional_edges(
        "validate_requirements",
        should_continue_after_requirements,
        {
            "review_final": "review_final",
            "regenerate_story": "regenerate_story",
            "end": END
        }
    )
    
    workflow.add_edge("review_final", END)
    
    return workflow.compile()


# Instância global do grafo compilado
story_graph = build_story_graph()
