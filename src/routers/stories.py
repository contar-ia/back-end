"""Router para endpoints de geração de histórias."""
import logging
from fastapi import APIRouter, HTTPException
from models import StoryGenerationRequest, StoryGenerationResponse
from database import db_manager
from story_graph import story_graph
from story_state import StoryState

logger = logging.getLogger(__name__)
stories_router = APIRouter()


@stories_router.post("/generate", response_model=StoryGenerationResponse)
async def generate_story(request: StoryGenerationRequest):
    """
    Endpoint para gerar histórias infantis usando o pipeline LangGraph.
    
    Recebe StoryGenerationRequest e retorna StoryGenerationResponse.
    """
    try:
        # Inicializar estado do grafo
        initial_state: StoryState = {
            "input": request,
            "draft_story": None,
            "safety_ok": False,
            "requirements_ok": False,
            "final_story": None,
            "issues": []
        }
        
        logger.info("=" * 60)
        logger.info("🚀 [PIPELINE] Iniciando geração de história")
        logger.info(f"   Tema: {request.theme}")
        logger.info(f"   Faixa etária: {request.age_group}")
        logger.info(f"   Personagens: {', '.join(request.characters)}")
        logger.info("=" * 60)
        
        # Executar o grafo
        final_state = await story_graph.ainvoke(initial_state)
        
        logger.info("=" * 60)
        logger.info("📊 [PIPELINE] Resumo da execução:")
        logger.info(f"   ✅ Agente 1 (Gerador): {'OK' if final_state.get('draft_story') else 'FALHOU'}")
        logger.info(f"   {'✅' if final_state.get('safety_ok') else '❌'} Agente 2 (Segurança): safety_ok={final_state.get('safety_ok')}")
        logger.info(f"   {'✅' if final_state.get('requirements_ok') else '❌'} Agente 3 (Requisitos): requirements_ok={final_state.get('requirements_ok')}")
        logger.info(f"   {'✅' if final_state.get('final_story') else '⏭️'} Agente 4 (Revisor): {'Executado' if final_state.get('final_story') else 'Não executado (validações falharam)'}")
        logger.info(f"   Issues encontrados: {len(final_state.get('issues', []))}")
        if final_state.get('issues'):
            for issue in final_state.get('issues', []):
                logger.warning(f"      - {issue}")
        logger.info("=" * 60)
        
        # Preparar resposta
        story_markdown = final_state.get("final_story")
        issues = final_state.get("issues", [])
        draft_story = final_state.get("draft_story")
        
        # Se não há história final, tentar usar draft_story
        if not story_markdown:
            if draft_story and len(draft_story.strip()) > 0:
                # Se passou nas validações mas não teve revisão final, usar draft
                if final_state.get("safety_ok") and final_state.get("requirements_ok"):
                    logger.info("Usando draft_story pois passou nas validações mas não teve revisão final")
                    story_markdown = draft_story
                # Se não passou nas validações mas tem draft, ainda retornar (com issues)
                else:
                    logger.warning(f"Usando draft_story mesmo com validações falhadas. safety_ok={final_state.get('safety_ok')}, requirements_ok={final_state.get('requirements_ok')}")
                    story_markdown = draft_story
        
        # Se ainda não tem história, adicionar issue genérico
        if not story_markdown or len(story_markdown.strip()) == 0:
            if not issues:
                issues.append("Não foi possível gerar a história. Verifique os logs do servidor.")
            logger.error(f"História não gerada ou vazia. Issues: {issues}, draft_story existe: {bool(draft_story)}")
            story_markdown = None

        # Salvar história no banco de dado
        if story_markdown and getattr(request, "creator_id", None):
            try:
                title_to_save = request.title or request.theme
                insert_query = "INSERT INTO stories (creator_id, title, contents) VALUES ($1, $2, $3) RETURNING id"
                row = await db_manager.fetchrow(insert_query, request.creator_id, title_to_save, story_markdown)
                saved_id = row["id"] if row and "id" in row else None
                logger.info(f"História salva no DB, id={saved_id}")
            except Exception as e:
                logger.exception(f"Falha ao salvar história no banco: {e}")
                issues.append(f"Falha ao salvar história no banco: {str(e)}")

        return StoryGenerationResponse(
            story_markdown=story_markdown,
            issues=issues
        )
        
    except Exception as e:
        logger.exception(f"Erro ao gerar história: {str(e)}")
        # Em caso de erro, retornar resposta com issues
        return StoryGenerationResponse(
            story_markdown=None,
            issues=[f"Erro ao gerar história: {str(e)}"]
        )
