"""Agentes do pipeline LangGraph para geração e validação de histórias infantis."""
import logging
import services
from story_state import StoryState

logger = logging.getLogger(__name__)


async def generate_story(state: StoryState) -> StoryState:
    """
    Agente 1: Gerador de História
    
    Recebe o input e gera a história inicial sem validação.
    Atualiza draft_story no estado.
    """
    logger.info("=" * 60)
    logger.info("🤖 [AGENTE 1] Gerador de História - INICIANDO")
    logger.info(f"   Tema: {state['input'].theme}")
    logger.info(f"   Faixa etária: {state['input'].age_group}")
    logger.info(f"   Personagens: {', '.join(state['input'].characters)}")
    
    input_data = state["input"]
    
    prompt = f"""Crie uma história infantil com as seguintes características:

Tema: {input_data.theme}
Faixa etária: {input_data.age_group}
Valor educativo: {input_data.educational_value}
Cenário: {input_data.setting}
Personagens: {', '.join(input_data.characters)}

Instruções:
- Crie uma história completa e envolvente
- Use linguagem apropriada para a faixa etária {input_data.age_group}
- Inclua todos os personagens mencionados: {', '.join(input_data.characters)}
- O tema deve ser {input_data.theme}
- O valor educativo {input_data.educational_value} deve estar presente na história
- Seja criativo e apropriado para crianças
"""
    
    try:
        logger.info("   Enviando prompt para Ollama...")
        draft_story = await services.send_prompt(prompt)
        logger.info(f"✅ [AGENTE 1] História gerada: {len(draft_story) if draft_story else 0} caracteres")
        
        if not draft_story or len(draft_story.strip()) == 0:
            logger.error("❌ [AGENTE 1] História gerada está vazia!")
            return {
                **state,
                "draft_story": None,
                "issues": state.get("issues", []) + ["Erro: História não foi gerada pelo modelo"]
            }
        
        logger.info(f"✅ [AGENTE 1] CONCLUÍDO - Próximo: Validador de Segurança")
        logger.info("=" * 60)
        return {
            **state,
            "draft_story": draft_story
        }
    except Exception as e:
        logger.exception(f"❌ [AGENTE 1] Erro ao gerar história: {str(e)}")
        return {
            **state,
            "draft_story": None,
            "issues": state.get("issues", []) + [f"Erro ao gerar história: {str(e)}"]
        }


async def validate_safety(state: StoryState) -> StoryState:
    """
    Agente 2: Validador de Conteúdo Infantil
    
    Valida se a história não contém conteúdo impróprio:
    - Palavrões
    - Obscenidade
    - Pornografia
    - Gore
    - Violência excessiva
    - Linguagem imprópria para crianças
    
    Atualiza safety_ok e issues no estado.
    """
    logger.info("=" * 60)
    logger.info("🔒 [AGENTE 2] Validador de Segurança - INICIANDO")
    
    draft_story = state.get("draft_story")
    
    if not draft_story:
        logger.error("❌ [AGENTE 2] História não foi gerada - pulando validação")
        return {
            **state,
            "safety_ok": False,
            "issues": state.get("issues", []) + ["História não foi gerada"]
        }
    
    logger.info(f"   Analisando história de {len(draft_story)} caracteres...")
    
    validation_prompt = f"""Analise a seguinte história infantil e verifique se ela é apropriada para crianças.

Verifique especificamente se há:
- Palavrões ou linguagem ofensiva
- Conteúdo sexual ou pornográfico
- Gore ou descrições gráficas de violência
- Violência excessiva ou desnecessária
- Qualquer linguagem imprópria para crianças

História para análise:
{draft_story}

Responda APENAS com "APROVADO" se a história for completamente apropriada para crianças, ou "REPROVADO: [razão]" se houver algum problema. Seja específico sobre o que está errado."""
    
    logger.info("   Enviando prompt de validação para Ollama...")
    validation_result = await services.send_prompt(validation_prompt)
    
    # Melhorar lógica de validação: verificar se começa com APROVADO ou se REPROVADO está presente
    validation_upper = validation_result.upper().strip()
    has_approved = validation_upper.startswith("APROVADO") or ("APROVADO" in validation_upper and "REPROVADO" not in validation_upper[:50])
    has_reproved = "REPROVADO" in validation_upper
    
    safety_ok = has_approved and not has_reproved
    issues = state.get("issues", [])
    
    logger.info(f"   Resposta completa do validador: {validation_result}")
    logger.info(f"   Análise: has_approved={has_approved}, has_reproved={has_reproved}, safety_ok={safety_ok}")
    
    if not safety_ok:
        # Extrair a razão da reprovação
        if "REPROVADO:" in validation_result.upper():
            reason = validation_result.split(":", 1)[-1].strip()
            issues.append(f"Problema de segurança: {reason}")
            logger.warning(f"❌ [AGENTE 2] REPROVADO: {reason}")
        else:
            issues.append("História contém conteúdo impróprio para crianças")
            logger.warning("❌ [AGENTE 2] REPROVADO: Conteúdo impróprio detectado")
    else:
        logger.info("✅ [AGENTE 2] APROVADO - História é segura para crianças")
    
    logger.info(f"✅ [AGENTE 2] CONCLUÍDO - safety_ok={safety_ok}")
    logger.info("=" * 60)
    
    return {
        **state,
        "safety_ok": safety_ok,
        "issues": issues
    }


async def validate_requirements(state: StoryState) -> StoryState:
    """
    Agente 3: Validador de Requisitos
    
    Verifica se:
    - O tema foi respeitado
    - Todos os personagens aparecem (nomes exatamente iguais)
    - O valor educativo está explícito
    - A linguagem condiz com a faixa etária
    
    Atualiza requirements_ok e issues no estado.
    """
    logger.info("=" * 60)
    logger.info("✅ [AGENTE 3] Validador de Requisitos - INICIANDO")
    
    draft_story = state.get("draft_story")
    input_data = state["input"]
    
    if not draft_story:
        logger.error("❌ [AGENTE 3] História não foi gerada - pulando validação")
        return {
            **state,
            "requirements_ok": False,
            "issues": state.get("issues", []) + ["História não foi gerada"]
        }
    
    logger.info(f"   Verificando requisitos:")
    logger.info(f"   - Tema: {input_data.theme}")
    logger.info(f"   - Personagens esperados: {', '.join(input_data.characters)}")
    logger.info(f"   - Valor educativo: {input_data.educational_value}")
    
    validation_prompt = f"""Analise a seguinte história infantil e verifique se ela atende aos requisitos solicitados.

Requisitos:
- Tema: {input_data.theme}
- Faixa etária: {input_data.age_group}
- Valor educativo: {input_data.educational_value}
- Personagens que DEVEM aparecer: {', '.join(input_data.characters)}

História para análise:
{draft_story}

Verifique:
1. O tema "{input_data.theme}" está presente e respeitado na história?
2. Todos os personagens listados aparecem na história? (nomes devem ser exatamente iguais)
3. O valor educativo "{input_data.educational_value}" está explícito na história?
4. A linguagem é apropriada para a faixa etária {input_data.age_group}?

Responda APENAS com "APROVADO" se todos os requisitos forem atendidos, ou "REPROVADO: [lista de problemas]" se houver algum problema. Liste cada problema encontrado."""
    
    logger.info("   Enviando prompt de validação para Ollama...")
    validation_result = await services.send_prompt(validation_prompt)
    
    # Melhorar lógica de validação: verificar se começa com APROVADO ou se REPROVADO está presente
    validation_upper = validation_result.upper().strip()
    has_approved = validation_upper.startswith("APROVADO") or ("APROVADO" in validation_upper and "REPROVADO" not in validation_upper[:50])
    has_reproved = "REPROVADO" in validation_upper
    
    requirements_ok = has_approved and not has_reproved
    issues = state.get("issues", [])
    
    logger.info(f"   Resposta completa do validador: {validation_result}")
    logger.info(f"   Análise: has_approved={has_approved}, has_reproved={has_reproved}, requirements_ok={requirements_ok}")
    
    if not requirements_ok:
        # Extrair os problemas encontrados
        if "REPROVADO:" in validation_result.upper():
            problems = validation_result.split(":", 1)[-1].strip()
            issues.append(f"Requisitos não atendidos: {problems}")
            logger.warning(f"❌ [AGENTE 3] REPROVADO: {problems}")
        else:
            issues.append("História não atende aos requisitos solicitados")
            logger.warning("❌ [AGENTE 3] REPROVADO: Requisitos não atendidos")
    else:
        logger.info("✅ [AGENTE 3] APROVADO - Todos os requisitos atendidos")
    
    logger.info(f"✅ [AGENTE 3] CONCLUÍDO - requirements_ok={requirements_ok}")
    logger.info("=" * 60)
    
    return {
        **state,
        "requirements_ok": requirements_ok,
        "issues": issues
    }


async def review_final(state: StoryState) -> StoryState:
    """
    Agente 4: Revisor Final
    
    Executa apenas se safety_ok e requirements_ok são True.
    
    Responsabilidades:
    - Melhorar fluidez e clareza
    - Ajustar linguagem à faixa etária
    - Manter nomes dos personagens exatamente iguais
    - Não adicionar personagens
    - Não mudar tema nem valor educativo
    - Formato obrigatório em Markdown:
      # Título da História
      
      Texto da história em parágrafos.
      
      ## Moral da história
      Texto explícito sobre o valor educativo.
    
    Atualiza final_story no estado.
    """
    logger.info("=" * 60)
    logger.info("📝 [AGENTE 4] Revisor Final - INICIANDO")
    
    draft_story = state.get("draft_story")
    input_data = state["input"]
    
    if not draft_story:
        logger.error("❌ [AGENTE 4] História não foi gerada - pulando revisão")
        return {
            **state,
            "final_story": None,
            "issues": state.get("issues", []) + ["História não foi gerada"]
        }
    
    logger.info(f"   Revisando e formatando história ({len(draft_story)} caracteres)...")
    logger.info(f"   Formato: Markdown com título e moral")
    
    review_prompt = f"""Revise e melhore a seguinte história infantil, garantindo que ela esteja no formato correto.

Requisitos IMPORTANTES:
- Mantenha o tema: {input_data.theme}
- Mantenha o valor educativo: {input_data.educational_value}
- Mantenha TODOS os personagens exatamente como estão: {', '.join(input_data.characters)}
- NÃO adicione novos personagens
- NÃO mude o tema nem o valor educativo
- Use linguagem apropriada para {input_data.age_group}
- Melhore a fluidez e clareza da narrativa

Formato OBRIGATÓRIO em Markdown:
# Título da História

[Texto da história em parágrafos, com todos os personagens: {', '.join(input_data.characters)}]

## Moral da história

[Texto explícito sobre o valor educativo: {input_data.educational_value}]

História original:
{draft_story}

Revise e formate a história seguindo EXATAMENTE o formato acima, mantendo todos os personagens e requisitos."""
    
    logger.info("   Enviando prompt de revisão para Ollama...")
    final_story = await services.send_prompt(review_prompt)
    
    logger.info(f"✅ [AGENTE 4] Revisão concluída: {len(final_story)} caracteres")
    logger.info(f"✅ [AGENTE 4] CONCLUÍDO - História final formatada")
    logger.info("=" * 60)
    
    return {
        **state,
        "final_story": final_story
    }
