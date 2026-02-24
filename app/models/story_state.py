"""
Definição do estado compartilhado utilizado no pipeline de geração de histórias.

Este módulo define a estrutura de dados que representa o estado interno
do fluxo de execução (workflow) baseado em LangGraph para criação de histórias.

O estado é implementado como um TypedDict, permitindo:

• Tipagem estática forte sem overhead de classes
• Mutabilidade controlada entre etapas do pipeline
• Clareza sobre quais dados são produzidos e consumidos por cada nó
• Compatibilidade com ferramentas de análise estática (mypy, pyright)
• Serialização simples

Cada campo representa um artefato intermediário ou final do processo
de geração, validação e refinamento da história.

Fluxo típico do pipeline:

1. Recebe input do usuário
2. Gera rascunho da história
3. Valida segurança do conteúdo
4. Verifica requisitos pedagógicos/narrativos
5. Produz versão final
6. Registra problemas encontrados (se houver)
"""
from typing import TypedDict, List, Optional
from app.models.models import StoryGenerationRequest

class StoryState(TypedDict):
    """
    Estado compartilhado do pipeline LangGraph para geração de histórias.

    Este dicionário tipado é passado entre os nós do grafo de processamento,
    permitindo que cada etapa leia e modifique partes específicas do estado.

    Campos:

        input (StoryGenerationRequest):
            Dados originais fornecidos pelo usuário para geração da história.
            Contém tema, personagens, cenário, faixa etária, etc.

        draft_story (Optional[str]):
            Primeira versão gerada da história (rascunho).
            Pode ser None antes da etapa de geração inicial.

        safety_ok (bool):
            Indica se o conteúdo passou nas verificações de segurança
            (ex.: conteúdo sensível ou impróprio).

        requirements_ok (bool):
            Indica se a história atende aos requisitos definidos,
            como valor educativo, adequação etária e coerência.

        final_story (Optional[str]):
            Versão final da história após revisões e validações.
            Pode ser None caso o processo não tenha sido concluído.

        issues (List[str]):
            Lista de problemas detectados durante o pipeline.
            Exemplos:
                • Conteúdo inadequado
                • Falha em requisitos pedagógicos
                • Erro de geração
                • Inconsistências narrativas

            Lista vazia indica que não houve problemas relevantes.
    """
    input: StoryGenerationRequest
    draft_story: Optional[str]
    safety_ok: bool
    requirements_ok: bool
    final_story: Optional[str]
    issues: List[str]
