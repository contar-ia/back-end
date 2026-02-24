"""
Modelos de dados (Schemas) da API utilizando Pydantic.

Este módulo define todas as estruturas de entrada (requests) e saída (responses)
utilizadas pelos endpoints da aplicação FastAPI.

Responsabilidades dos modelos:

• Validação automática de dados recebidos pela API
• Serialização de respostas JSON
• Tipagem forte para maior segurança e previsibilidade
• Documentação automática no OpenAPI/Swagger
• Conversão entre tipos Python e JSON

Os modelos estão organizados por domínio:

- Autenticação e perfil de usuário
- Integração com LLM
- Geração e persistência de histórias
- Listagem e estatísticas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

# ============================================================================
# LLM / PROMPTS
# ============================================================================
class PromptRequest(BaseModel):
    """
    Request para envio de prompt a um modelo de linguagem (LLM).

    Utilizado pelo endpoint de geração de texto.

    Attributes:
        prompt (str):
            Texto de entrada que será enviado ao agente LLM.
    """
    prompt: str

# ============================================================================
# AUTENTICAÇÃO E USUÁRIOS
# ============================================================================
class RegisterRequest(BaseModel):
    """
    Request para registro de um novo usuário.

    Attributes:
        username (str):
            Nome de usuário único.

        email (str):
            Email do usuário (também único).

        password (str):
            Senha em texto puro (será transformada em hash no backend).
    """
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    """
    Request para autenticação de usuário.

    Attributes:
        email (str):
            Email cadastrado.

        password (str):
            Senha em texto puro para verificação.
    """
    email: str
    password: str

class UpdateProfileRequest(BaseModel):
    """
    Request para atualização de dados do perfil do usuário autenticado.

    Attributes:
        username (str):
            Novo nome de usuário.

        email (str):
            Novo email.

        institution (Optional[str]):
            Instituição associada ao usuário (opcional).

        bio (Optional[str]):
            Biografia ou descrição pessoal (opcional).
    """
    username: str
    email: str
    institution: Optional[str] = None
    bio: Optional[str] = None

# ============================================================================
# GERAÇÃO DE HISTÓRIAS (LLM + SISTEMA)
# ============================================================================
class StoryGenerationRequest(BaseModel):
    """
    Request para geração automática de histórias infantis.

    Contém todos os elementos narrativos necessários para que o
    agente LLM produza uma história coerente.

    Attributes:
        theme (str):
            Tema principal da história (ex: aventura, amizade).

        age_group (str):
            Faixa etária alvo (ex: 3-5 anos, 6-8 anos).

        educational_value (str):
            Valor educativo desejado (ex: honestidade, coragem).

        setting (str):
            Ambiente ou cenário onde a história ocorre.

        characters (List[str]):
            Lista de personagens principais.

        title (Optional[str]):
            Título sugerido pelo usuário (opcional).

        creator_id (Optional[Union[str, int]]):
            Identificador do usuário criador.
            Pode vir como string ou inteiro dependendo da origem.
    """
    theme: str
    age_group: str
    educational_value: str
    setting: str
    characters: List[str]
    title: Optional[str] = None
    creator_id: Optional[Union[str, int]] = None

class StoryGenerationResponse(BaseModel):
    """
    Response retornada após tentativa de geração da história.

    Pode representar sucesso ou falha (ex.: validação de segurança).

    Attributes:
        story_markdown (Optional[str]):
            História gerada em formato Markdown.

        issues (List[str]):
            Lista de problemas detectados (ex: conteúdo impróprio).
            Vazio se a geração foi bem-sucedida.

        story_id (Optional[str]):
            Identificador da história salva no banco (se persistida).
    """
    story_markdown: Optional[str] = None
    issues: List[str] = Field(default_factory=list)
    story_id: Optional[str] = None

# ============================================================================
# PERSISTÊNCIA DE HISTÓRIAS
# ============================================================================
class StorySaveRequest(BaseModel):
    """
    Request para salvar uma história no banco de dados.

    Attributes:
        creator_id (str):
            ID do usuário que criou a história.

        title (str):
            Título da história.

        contents (str):
            Conteúdo completo da história.
    """
    creator_id: str
    title: str
    contents: str

class StoryUpdateRequest(BaseModel):
    """
    Request para atualização de uma história existente.

    Todos os campos são opcionais, permitindo atualização parcial.

    Attributes:
        title (Optional[str]):
            Novo título da história.

        contents (Optional[str]):
            Novo conteúdo da história.
    """
    title: Optional[str] = None
    contents: Optional[str] = None

# ============================================================================
# LISTAGEM E DETALHES DE HISTÓRIAS
# ============================================================================
class StoryListItem(BaseModel):
    """
    Representa uma história em listagens.

    Usado em endpoints que retornam múltiplas histórias.

    Attributes:
        id (str):
            Identificador da história.

        creator_id (str):
            ID do usuário criador.

        title (str):
            Título da história.

        contents (str):
            Conteúdo da história.

        created_at (datetime):
            Data e hora de criação.
    """
    id: str
    creator_id: str
    title: str
    contents: str
    created_at: datetime

class StoryDetailResponse(BaseModel):
    """
    Response detalhada de uma única história.

    Estrutura semelhante ao StoryListItem, mas usada quando
    a API retorna um único recurso.

    Attributes:
        id (str):
            Identificador da história.

        creator_id (str):
            ID do criador.

        title (str):
            Título da história.

        contents (str):
            Conteúdo completo.

        created_at (datetime):
            Timestamp de criação.
    """
    id: str
    creator_id: str
    title: str
    contents: str
    created_at: datetime

# ============================================================================
# ESTATÍSTICAS DE HISTÓRIAS
# ============================================================================
class StoryStatsResponse(BaseModel):
    """
    Response com estatísticas relacionadas às histórias do usuário.

    Attributes:
        created_count (int):
            Quantidade de histórias criadas pelo usuário.

        reads_count (int):
            Quantidade total de leituras registradas.

        saved_count (int):
            Quantidade de histórias salvas/favoritadas.
    """
    created_count: int
    reads_count: int
    saved_count: int
