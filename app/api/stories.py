"""
Router para endpoints de geração e gerenciamento de histórias infantis.

Este módulo define os endpoints responsáveis por todo o ciclo de vida
das histórias na aplicação, incluindo:

• Geração automática de histórias usando um pipeline baseado em agentes (LangGraph)
• Validação de segurança do conteúdo de entrada
• Persistência de histórias no banco de dados
• Listagem de histórias criadas e salvas
• Recuperação detalhada de histórias
• Estatísticas de uso do usuário
• Operações de salvar, remover, editar e excluir histórias
"""
import logging
from app.services import auth
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Header, status
from app.models.models import (
    StoryGenerationRequest,
    StoryGenerationResponse,
    StoryListItem,
    StoryDetailResponse,
    StoryStatsResponse,
    StorySaveRequest,
    StoryUpdateRequest,
)
from app.database.database import db_manager
from app.services.story_graph import story_graph
from app.models.story_state import StoryState
from app.core.input_validator import validate_input_safety

# Configuração do logger do módulo
logger = logging.getLogger(__name__)

# Instância do roteador responsável pelos endpoints de histórias
stories_router = APIRouter()

@stories_router.post("/generate", response_model=StoryGenerationResponse)
async def generate_story(request: StoryGenerationRequest):
    """
    Gera uma história infantil automaticamente usando um pipeline baseado em agentes.

    Fluxo de execução:

    1. Validação de segurança do input usando LLM
    2. Inicialização do estado do grafo de geração
    3. Execução do pipeline LangGraph (múltiplos agentes)
    4. Processamento do resultado
    5. Retorno da história gerada ou issues encontrados

    Agentes envolvidos no pipeline:

    - Gerador: cria o rascunho da história
    - Validador de segurança: verifica conteúdo impróprio
    - Validador de requisitos: garante adequação ao público-alvo
    - Revisor: produz a versão final da história

    Parâmetros:
        request (StoryGenerationRequest): Dados para geração da história,
        como tema, faixa etária, personagens, cenário e valores educativos.

    Retorno:
        StoryGenerationResponse contendo:
        - story_markdown: história gerada (ou None em caso de falha)
        - issues: lista de problemas encontrados durante o processo
        - story_id: identificador (se aplicável)

    Observações:
        - Caso o input seja considerado impróprio, a geração não é executada.
        - O sistema pode retornar um rascunho caso a revisão final falhe.
        - O endpoint nunca expõe detalhes sensíveis da validação.
    """
    try:
        # VALIDAff'O PRfVIA: Verificar se o input contém conteúdo sensível/impróprio usando LLM
        logger.info("=" * 60)
        logger.info("Y [VALIDAff'O INPUT] Verificando conteudo do input com LLM...")
        
        is_safe, input_issues = await validate_input_safety(
            theme=request.theme,
            age_group=request.age_group,
            educational_value=request.educational_value,
            setting=request.setting,
            characters=request.characters
        )
        
        if not is_safe:
            logger.warning("=" * 60)
            logger.warning("[VALIDACAO INPUT] Input rejeitado - conteudo sensivel detectado")
            logger.warning("=" * 60)
            
            # Retornar erro HTTP 400 com mensagem generica (sem especificar o problema)
            error_message = "As informacoes fornecidas contem conteudo sensivel ou improprio para historias infantis. Por favor, revise o tema, personagens, cenario e valores educativos."
            
            return StoryGenerationResponse(
                story_markdown=None,
                issues=[error_message]
            )
        
        logger.info("[VALIDACAO INPUT] Input aprovado - prosseguindo com geracao")
        logger.info("=" * 60)
        
        # Inicialização do estado do pipeline
        initial_state: StoryState = {
            "input": request,
            "draft_story": None,
            "safety_ok": False,
            "requirements_ok": False,
            "final_story": None,
            "issues": [],
            "retry_count": 0,
            "max_retries": 1,  # Maximo de 1 tentativa de regeneracao (para nao demorar muito)
            "feedback": None
        }
        
        logger.info("=" * 60)
        logger.info("Ys, [PIPELINE] Iniciando geracao de historia")
        logger.info(f"   Tema: {request.theme}")
        logger.info(f"   Faixa etaria: {request.age_group}")
        logger.info(f"   Personagens: {', '.join(request.characters)}")
        logger.info("=" * 60)
        
        # Execução do pipeline de geração
        final_state = await story_graph.ainvoke(initial_state)
        
        logger.info("=" * 60)
        logger.info("YoS [PIPELINE] Resumo da execucao:")
        logger.info(f"   Agente 1 (Gerador): {'OK' if final_state.get('draft_story') else 'FALHOU'}")
        logger.info(f"   Agente 2 (Seguranca): safety_ok={final_state.get('safety_ok')}")
        logger.info(f"   Agente 3 (Requisitos): requirements_ok={final_state.get('requirements_ok')}")
        logger.info(f"   Agente 4 (Revisor): {'Executado' if final_state.get('final_story') else 'Nao executado (validacoes falharam)'}")
        logger.info(f"   Issues encontrados: {len(final_state.get('issues', []))}")
        if final_state.get('issues'):
            for issue in final_state.get('issues', []):
                logger.warning(f"      - {issue}")
        logger.info("=" * 60)
        
        # Preparação da resposta
        story_markdown = final_state.get("final_story")
        issues = final_state.get("issues", [])
        draft_story = final_state.get("draft_story")
        
        # Se nao ha historia final, tentar usar draft_story
        if not story_markdown:
            if draft_story and len(draft_story.strip()) > 0:
                # Se passou nas validacoes mas nao teve revisao final, usar draft
                if final_state.get("safety_ok") and final_state.get("requirements_ok"):
                    logger.info("Usando draft_story pois passou nas validacoes mas nao teve revisao final")
                    story_markdown = draft_story
                # Se nao passou nas validacoes mas tem draft, ainda retornar (com issues)
                else:
                    logger.warning(f"Usando draft_story mesmo com validacoes falhadas. safety_ok={final_state.get('safety_ok')}, requirements_ok={final_state.get('requirements_ok')}")
                    story_markdown = draft_story
        
        # Se ainda nao tem historia, adicionar issue generico
        if not story_markdown or len(story_markdown.strip()) == 0:
            if not issues:
                issues.append("Nao foi possivel gerar a historia. Verifique os logs do servidor.")
            logger.error(f"Historia nao gerada ou vazia. Issues: {issues}, draft_story existe: {bool(draft_story)}")
            story_markdown = None
        
        # Limpar issues irrelevantes se a historia foi gerada com sucesso
        if story_markdown and len(story_markdown.strip()) > 0:
            # Remover issues que indicam que a historia nao foi gerada (ja que ela foi gerada)
            issues = [
                issue for issue in issues 
                if not any(phrase in issue.lower() for phrase in [
                    "historia nao foi gerada",
                    "historia nao foi gerada pelo modelo",
                    "erro: historia nao foi gerada"
                ])
            ]
            # Se passou nas validacoes, remover issues de validacao tambem
            if final_state.get("safety_ok") and final_state.get("requirements_ok"):
                issues = [
                    issue for issue in issues 
                    if not any(phrase in issue.lower() for phrase in [
                        "problema de seguranca",
                        "requisitos nao atendidos",
                        "historia contem conteudo improprio",
                        "historia nao atende aos requisitos"
                    ])
                ]

        logger.info("=" * 60)
        logger.info("[RESPOSTA] Preparando resposta para o cliente")
        logger.info(f"   Historia gerada: {bool(story_markdown)}, Tamanho: {len(story_markdown) if story_markdown else 0} caracteres")
        logger.info(f"   Issues: {len(issues)}")
        logger.info("=" * 60)
        
        response = StoryGenerationResponse(
            story_markdown=story_markdown,
            issues=issues,
            story_id=None
        )

        logger.info("[RESPOSTA] Resposta criada e sendo retornada")
        return response
        
    except Exception as e:
        logger.exception(f"Erro ao gerar historia: {str(e)}")
        # Em caso de erro, retornar resposta com issues
        return StoryGenerationResponse(
            story_markdown=None,
            issues=[f"Erro ao gerar historia: {str(e)}"]
        )

@stories_router.get("/user/{user_id}", response_model=List[StoryListItem])
async def list_user_stories(user_id: str):
    """
    Lista todas as histórias criadas por um usuário específico.

    Parâmetros:
        user_id (str): Identificador do usuário criador.

    Retorno:
        Lista de StoryListItem ordenada pela data de criação (mais recentes primeiro).

    Exceções:
        400 — user_id não fornecido
        500 — erro ao acessar o banco de dados
    """
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")

    query = """
        SELECT id, creator_id, title, contents, created_at
        FROM stories
        WHERE creator_id = $1
        ORDER BY created_at DESC
    """
    try:
        rows = await db_manager.fetch(query, user_id)
        result = []
        for r in rows:
            d = dict(r)
            if "id" in d:
                d["id"] = str(d["id"])
            if "creator_id" in d:
                d["creator_id"] = str(d["creator_id"])
            result.append(d)
        return result
    except Exception as e:
        logger.exception(f"Erro ao listar historias do usuario: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar historias")

@stories_router.get("/saved/{user_id}", response_model=List[StoryListItem])
async def list_saved_stories(user_id: str):
    """
    Lista as histórias que um usuário salvou.

    Parâmetros:
        user_id (str): Identificador do usuário.

    Retorno:
        Lista de histórias salvas ordenadas pela data de salvamento.
    """
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")

    query = """
        SELECT s.id, s.creator_id, s.title, s.contents, s.created_at
        FROM story_saves ss
        JOIN stories s ON s.id = ss.story_id
        WHERE ss.user_id = $1
        ORDER BY ss.saved_at DESC
    """
    try:
        rows = await db_manager.fetch(query, user_id)
        result = []
        for r in rows:
            d = dict(r)
            if "id" in d:
                d["id"] = str(d["id"])
            if "creator_id" in d:
                d["creator_id"] = str(d["creator_id"])
            result.append(d)
        return result
    except Exception as e:
        logger.exception(f"Erro ao listar historias salvas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao listar historias salvas")

@stories_router.post("/save")
async def save_new_story(request: StorySaveRequest, authorization: Optional[str] = Header(default=None)):
    """
    Salva uma nova história criada pelo usuário.

    Caso um token Bearer seja fornecido, a sessão é validada e o creator_id
    é ajustado para corresponder ao usuário autenticado.

    Parâmetros:
        request (StorySaveRequest): Dados da história a ser salva.
        authorization (str | None): Header Authorization opcional.

    Retorno:
        dict contendo o ID da história criada.
    """
    if not request.creator_id or not request.title or not request.contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="creator_id, title and contents are required")

    # Se houver token, validar sessao
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        user = await auth.get_user_by_session_token(token)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        # Forcar o creator_id a bater com o token
        request = StorySaveRequest(
            creator_id=str(user["user_id"]),
            title=request.title,
            contents=request.contents,
        )

    try:
        # Garantir que o creator_id existe no banco
        user_row = await db_manager.fetchrow("SELECT id FROM users WHERE id = $1", request.creator_id)
        if not user_row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        insert_story = "INSERT INTO stories (creator_id, title, contents) VALUES ($1, $2, $3) RETURNING id"
        row = await db_manager.fetchrow(insert_story, request.creator_id, request.title, request.contents)
        story_id = row["id"] if row and "id" in row else None

        if story_id:
            insert_save = """
                INSERT INTO story_saves (user_id, story_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, story_id) DO NOTHING
            """
            await db_manager.execute(insert_save, request.creator_id, story_id)

        return { "story_id": story_id }
    except Exception as e:
        logger.exception(f"Erro ao salvar nova historia: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao salvar historia")

@stories_router.get("/by-id/{story_id}", response_model=StoryDetailResponse)
async def get_story(story_id: str, user_id: Optional[str] = None):
    """
    Recupera os detalhes completos de uma história.

    Opcionalmente registra a leitura da história pelo usuário.

    Parâmetros:
        story_id (str): Identificador da história.
        user_id (str | None): Identificador do usuário que está lendo.

    Retorno:
        StoryDetailResponse com dados completos da história.
    """
    if not story_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="story_id is required")

    query = """
        SELECT id, creator_id, title, contents, created_at
        FROM stories
        WHERE id = $1
    """
    row = await db_manager.fetchrow(query, story_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia nao encontrada")

    # Registrar leitura, se user_id for fornecido
    if user_id:
        try:
            insert_read = """
                INSERT INTO story_reads (user_id, story_id)
                VALUES ($1, $2)
                ON CONFLICT (user_id, story_id) DO NOTHING
            """
            await db_manager.execute(insert_read, user_id, story_id)
        except Exception as e:
            logger.warning(f"Falha ao registrar leitura: {e}")

    d = dict(row)
    if "id" in d:
        d["id"] = str(d["id"])
    if "creator_id" in d:
        d["creator_id"] = str(d["creator_id"])
    return d

@stories_router.get("/stats/{user_id}", response_model=StoryStatsResponse)
async def get_user_story_stats(user_id: str):
    """
    Retorna estatísticas de uso de histórias para um usuário.

    Métricas incluídas:

    - Quantidade de histórias criadas
    - Quantidade de leituras realizadas
    - Quantidade de histórias salvas

    Parâmetros:
        user_id (str): Identificador do usuário.

    Retorno:
        StoryStatsResponse com contadores agregados.
    """
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id is required")

    try:
        created_query = "SELECT COUNT(*) FROM stories WHERE creator_id = $1"
        reads_query = "SELECT COUNT(*) FROM story_reads WHERE user_id = $1"
        saves_query = "SELECT COUNT(*) FROM story_saves WHERE user_id = $1"

        created_row = await db_manager.fetchrow(created_query, user_id)
        reads_row = await db_manager.fetchrow(reads_query, user_id)
        saves_row = await db_manager.fetchrow(saves_query, user_id)

        return StoryStatsResponse(
            created_count=int(created_row["count"]) if created_row else 0,
            reads_count=int(reads_row["count"]) if reads_row else 0,
            saved_count=int(saves_row["count"]) if saves_row else 0,
        )
    except Exception as e:
        logger.exception(f"Erro ao buscar estatisticas: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao buscar estatisticas")

@stories_router.post("/{story_id}/save")
async def save_story(story_id: str, user_id: Optional[str] = None):
    """
    Marca uma história existente como salva para um usuário.
    """
    if not story_id or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="story_id and user_id are required")

    try:
        insert_save = """
            INSERT INTO story_saves (user_id, story_id)
            VALUES ($1, $2)
            ON CONFLICT (user_id, story_id) DO NOTHING
        """
        await db_manager.execute(insert_save, user_id, story_id)
        return { "status": "saved" }
    except Exception as e:
        logger.exception(f"Erro ao salvar historia: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao salvar historia")

@stories_router.post("/{story_id}/unsave")
async def unsave_story(story_id: str, user_id: Optional[str] = None):
    """
    Remove o marcador de história salva para um usuário.
    """
    if not story_id or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="story_id and user_id are required")

    try:
        delete_save = "DELETE FROM story_saves WHERE user_id = $1 AND story_id = $2"
        await db_manager.execute(delete_save, user_id, story_id)
        return { "status": "unsaved" }
    except Exception as e:
        logger.exception(f"Erro ao remover historia salva: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao remover historia salva")

@stories_router.put("/{story_id}")
async def update_story(story_id: str, request: StoryUpdateRequest, user_id: Optional[str] = None):
    """
    Atualiza o título e/ou conteúdo de uma história existente.

    Apenas o criador da história pode realizar alterações.
    """
    if not story_id or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="story_id and user_id are required")
    if request.title is None and request.contents is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title or contents is required")

    try:
        current_story = await db_manager.fetchrow(
            "SELECT creator_id, title, contents FROM stories WHERE id = $1",
            story_id,
        )
        if not current_story:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia nao encontrada")

        creator_id = str(current_story["creator_id"])
        if creator_id != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Somente o criador pode editar a historia")

        new_title = request.title if request.title is not None else current_story["title"]
        new_contents = request.contents if request.contents is not None else current_story["contents"]

        await db_manager.execute(
            "UPDATE stories SET title = $1, contents = $2 WHERE id = $3",
            new_title,
            new_contents,
            story_id,
        )

        return {"status": "updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao editar historia: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao editar historia")

@stories_router.delete("/{story_id}")
async def delete_story(story_id: str, user_id: Optional[str] = None):
    """
    Exclui uma história ou remove-a da lista de salvos do usuário.

    Comportamento:

    - Se o usuário for o criador → a história é excluída permanentemente
    - Caso contrário → apenas remove dos salvos do usuário
    """
    if not story_id or not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="story_id and user_id are required")

    try:
        owner_query = "SELECT creator_id FROM stories WHERE id = $1"
        owner_row = await db_manager.fetchrow(owner_query, story_id)

        if not owner_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Historia nao encontrada")

        creator_id = str(owner_row["creator_id"])

        if creator_id == str(user_id):
            delete_story_query = "DELETE FROM stories WHERE id = $1 AND creator_id = $2"
            await db_manager.execute(delete_story_query, story_id, user_id)
            return {"status": "deleted"}

        delete_save_query = "DELETE FROM story_saves WHERE user_id = $1 AND story_id = $2"
        await db_manager.execute(delete_save_query, user_id, story_id)
        return {"status": "unsaved"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao excluir historia: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao excluir historia")
