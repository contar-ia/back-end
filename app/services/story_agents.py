"""Agentes do pipeline LangGraph para geração e validação de histórias infantis."""
import logging
from app import services
from app.models.story_state import StoryState

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
        draft_story = await services.send_prompt(prompt, timeout=120)  # Timeout maior para geração de histórias
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


async def regenerate_story(state: StoryState) -> StoryState:
    """
    Agente 1b: Regenerador de História com Feedback
    
    Regenera a história ajustando os problemas identificados pelos validadores.
    Usa feedback dos validadores para melhorar a história.
    """
    logger.info("=" * 60)
    logger.info("🔄 [AGENTE 1b] Regenerador de História - INICIANDO")
    
    retry_count = state.get("retry_count", 0) + 1
    feedback = state.get("feedback", "")
    input_data = state["input"]
    previous_story = state.get("draft_story", "")
    
    logger.info(f"   Tentativa de regeneração: {retry_count}")
    if feedback:
        logger.info(f"   Feedback recebido: {feedback}")
    
    # Acessar input como dicionário ou objeto (compatibilidade)
    def get_input_value(key: str):
        if isinstance(input_data, dict):
            return input_data.get(key, "")
        return getattr(input_data, key, "")
    
    theme = get_input_value("theme")
    age_group = get_input_value("age_group")
    educational_value = get_input_value("educational_value")
    setting = get_input_value("setting")
    characters = get_input_value("characters")
    if not isinstance(characters, list):
        characters = list(characters) if characters else []
    
    # Construir prompt com feedback
    feedback_section = ""
    if feedback:
        feedback_section = f"""

⚠️ PROBLEMAS ENCONTRADOS NA VERSÃO ANTERIOR:
{feedback}

IMPORTANTE: Você DEVE corrigir todos os problemas acima na nova versão da história.
"""
    
    prompt = f"""Crie uma nova versão desta história infantil.

Requisitos:
Tema: {theme}
Faixa etária: {age_group}
Valor educativo: {educational_value}
Cenário: {setting}
Personagens: {', '.join(characters)}

{feedback_section if feedback else ""}

História anterior:
{previous_story[:1500] if previous_story else ""}

INSTRUÇÕES:
- Mantenha o tema {theme} (pode ser similar ou relacionado)
- Mantenha o valor educativo {educational_value}
- Inclua os personagens: {', '.join(characters)} (nomes podem ser similares)
- Use linguagem apropriada para {age_group}
- Seja criativo e apropriado para crianças
- Crie uma história envolvente e positiva
{f"- CORRIJA: {feedback}" if feedback else ""}
"""
    
    try:
        logger.info("   Enviando prompt de regeneração para Ollama...")
        draft_story = await services.send_prompt(prompt, timeout=120)  # Timeout maior para geração de histórias
        logger.info(f"✅ [AGENTE 1b] História regenerada: {len(draft_story) if draft_story else 0} caracteres")
        
        if not draft_story or len(draft_story.strip()) == 0:
            logger.error("❌ [AGENTE 1b] História regenerada está vazia!")
            return {
                **state,
                "draft_story": None,
                "retry_count": retry_count,
                "issues": state.get("issues", []) + ["Erro: História regenerada não foi gerada pelo modelo"]
            }
        
        logger.info(f"✅ [AGENTE 1b] CONCLUÍDO - Próximo: Validador de Segurança")
        logger.info("=" * 60)
        return {
            **state,
            "draft_story": draft_story,
            "retry_count": retry_count,
            "feedback": None,  # Limpar feedback após regeneração
            "safety_ok": False,  # Resetar validações
            "requirements_ok": False
        }
    except Exception as e:
        logger.exception(f"❌ [AGENTE 1b] Erro ao regenerar história: {str(e)}")
        return {
            **state,
            "draft_story": None,
            "retry_count": retry_count,
            "issues": state.get("issues", []) + [f"Erro ao regenerar história: {str(e)}"]
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
    
    # Otimizar prompt para ser mais curto e direto (reduz tempo de processamento)
    # Limitar tamanho da história para análise mais rápida (primeiros 2000 caracteres)
    story_preview = draft_story[:2000] if len(draft_story) > 2000 else draft_story
    validation_prompt = f"""Analise se esta história infantil é apropriada para crianças.

História:
{story_preview}

REGRAS IMPORTANTES:
1. Seja MUITO PERMISSIVO - APROVE se a história for adequada para crianças
2. APENAS REPROVE se houver conteúdo REALMENTE impróprio:
   - Palavrões explícitos e ofensivos
   - Conteúdo sexual explícito
   - Violência gráfica ou gore
   - Linguagem claramente ofensiva

3. Se a história NÃO tem palavrões, conteúdo sexual ou violência excessiva → APROVE
4. Se a linguagem é apropriada para crianças → APROVE
5. Se a narrativa é positiva e educativa → APROVE

Responda APENAS na primeira linha:
- "APROVADO" se a história for adequada (seja permissivo)
- "REPROVADO: [razão]" APENAS se houver conteúdo REALMENTE impróprio

Primeira linha:"""
    
    logger.info("   Enviando prompt de validação para Ollama...")
    validation_result = await services.send_prompt(validation_prompt, timeout=120)  # Timeout aumentado para validações
    
    # Extrair apenas a primeira linha da resposta (onde deve estar APROVADO ou REPROVADO)
    first_line = validation_result.split('\n')[0].strip()
    validation_upper = first_line.upper().strip()
    
    # Verificar se a resposta completa menciona que é apropriado (mesmo que comece com REPROVADO)
    full_response_lower = validation_result.lower()
    is_appropriate_mentioned = any(phrase in full_response_lower for phrase in [
        "é apropriado", "é adequado", "é apropriada", "é adequada", 
        "apropriada para", "adequada para", "apropriado para", "adequado para",
        "apropriada para crianças", "adequada para crianças",
        "não contém palavrões", "não há palavrões",
        "linguagem é apropriada", "linguagem apropriada",
        "narrativa é positiva", "narrativa positiva",
        "tema adequado", "tema apropriado"
    ])
    
    # Melhorar lógica de validação: priorizar início da resposta e ser mais inteligente
    # Prioridade 1: Se começa com APROVADO, é aprovado
    if validation_upper.startswith("APROVADO"):
        safety_ok = True
        has_approved = True
        has_reproved = False
    # Prioridade 2: Se começa com REPROVADO mas menciona que é apropriado = FALSO POSITIVO
    elif validation_upper.startswith("REPROVADO") and is_appropriate_mentioned:
        # Falso positivo: diz REPROVADO mas explica que é apropriado
        logger.warning("⚠️ [AGENTE 2] Detectado falso positivo: resposta diz REPROVADO mas menciona que é apropriado. Aprovando.")
        safety_ok = True
        has_approved = True
        has_reproved = False
    # Prioridade 3: Se começa com REPROVADO e não menciona apropriado, verificar se há conteúdo realmente impróprio
    elif validation_upper.startswith("REPROVADO"):
        # Verificar se menciona conteúdo realmente impróprio
        has_bad_content = any(phrase in full_response_lower for phrase in [
            "palavrões", "conteúdo sexual", "violência excessiva", "gore",
            "linguagem ofensiva", "conteúdo impróprio", "inadequado"
        ])
        if not has_bad_content and is_appropriate_mentioned:
            logger.warning("⚠️ [AGENTE 2] REPROVADO mas sem conteúdo impróprio mencionado. Aprovando.")
            safety_ok = True
            has_approved = True
            has_reproved = False
        else:
            safety_ok = False
            has_approved = False
            has_reproved = True
    # Prioridade 4: Verificar se contém APROVADO nas primeiras 100 caracteres
    elif "APROVADO" in validation_upper[:100] and "REPROVADO" not in validation_upper[:100]:
        safety_ok = True
        has_approved = True
        has_reproved = False
    # Fallback: Se não encontrou padrão claro mas menciona apropriado, aprovar
    else:
        if is_appropriate_mentioned:
            logger.warning("⚠️ [AGENTE 2] Resposta não clara mas menciona apropriado. Aprovando.")
            safety_ok = True
            has_approved = True
            has_reproved = False
        else:
            logger.warning("⚠️ [AGENTE 2] Resposta não clara, sendo permissivo e aprovando.")
            safety_ok = True
            has_approved = True
            has_reproved = False
    issues = state.get("issues", [])
    
    logger.info(f"   Resposta completa do validador: {validation_result}")
    logger.info(f"   Análise: has_approved={has_approved}, has_reproved={has_reproved}, safety_ok={safety_ok}")
    
    feedback = None
    if not safety_ok:
        # Extrair a razão da reprovação
        if "REPROVADO:" in validation_result.upper():
            reason = validation_result.split(":", 1)[-1].strip()
            issues.append(f"Problema de segurança: {reason}")
            feedback = f"A história foi REPROVADA na validação de segurança. Problema encontrado: {reason}. Você deve regenerar a história removendo completamente este problema e garantindo que seja 100% apropriada para crianças."
            logger.warning(f"❌ [AGENTE 2] REPROVADO: {reason}")
        else:
            issues.append("História contém conteúdo impróprio para crianças")
            feedback = "A história foi REPROVADA na validação de segurança. Conteúdo impróprio detectado. Você deve regenerar a história garantindo que seja completamente apropriada para crianças, sem qualquer conteúdo ofensivo, violento ou impróprio."
            logger.warning("❌ [AGENTE 2] REPROVADO: Conteúdo impróprio detectado")
    else:
        logger.info("✅ [AGENTE 2] APROVADO - História é segura para crianças")
    
    logger.info(f"✅ [AGENTE 2] CONCLUÍDO - safety_ok={safety_ok}")
    logger.info("=" * 60)
    
    return {
        **state,
        "safety_ok": safety_ok,
        "issues": issues,
        "feedback": feedback if feedback else state.get("feedback")
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
    
    # Otimizar: limitar tamanho da história para análise mais rápida
    story_preview = draft_story[:2000] if len(draft_story) > 2000 else draft_story
    validation_prompt = f"""Verifique se esta história atende aos requisitos:

Requisitos:
- Tema: {input_data.theme}
- Personagens: {', '.join(input_data.characters)}
- Valor educativo: {input_data.educational_value}
- Faixa etária: {input_data.age_group}

História:
{story_preview}

IMPORTANTE: Seja PERMISSIVO e FLEXÍVEL:
- Tema pode ser similar ou relacionado (não precisa ser exatamente igual)
- Personagens podem aparecer com nomes similares ou descrições
- Valor educativo pode estar implícito ou explícito
- Linguagem deve ser apropriada para a faixa etária

APENAS REPROVE se:
- Tema completamente diferente
- Personagens principais ausentes
- Conteúdo claramente inadequado para a faixa etária

Responda APENAS na primeira linha:
- "APROVADO" se requisitos atendidos (seja flexível)
- "REPROVADO: [problemas]" APENAS se requisitos críticos não atendidos

Primeira linha:"""
    
    logger.info("   Enviando prompt de validação para Ollama...")
    validation_result = await services.send_prompt(validation_prompt, timeout=120)  # Timeout aumentado para validações
    
    # Extrair apenas a primeira linha da resposta (onde deve estar APROVADO ou REPROVADO)
    first_line = validation_result.split('\n')[0].strip()
    validation_upper = first_line.upper().strip()
    
    # Verificar se a resposta completa menciona que requisitos estão atendidos
    full_response_lower = validation_result.lower()
    requirements_met = any(phrase in full_response_lower for phrase in [
        "tema presente", "tema está presente", "tema aparece",
        "personagens aparecem", "personagens presentes", "todos personagens",
        "valor educativo", "valor educativo presente", "valor educativo explícito",
        "atende", "atendidos", "requisitos atendidos", "requisitos estão",
        "adequado", "apropriado", "linguagem apropriada"
    ])
    
    # Melhorar lógica de validação: priorizar início da resposta e ser mais flexível
    # Prioridade 1: Se começa com APROVADO, é aprovado
    if validation_upper.startswith("APROVADO"):
        requirements_ok = True
        has_approved = True
        has_reproved = False
    # Prioridade 2: Se começa com REPROVADO mas menciona que requisitos estão ok = FALSO POSITIVO
    elif validation_upper.startswith("REPROVADO") and requirements_met:
        # Falso positivo: diz REPROVADO mas menciona que requisitos estão ok
        logger.warning("⚠️ [AGENTE 3] Detectado falso positivo: requisitos atendidos mas resposta diz REPROVADO. Aprovando.")
        requirements_ok = True
        has_approved = True
        has_reproved = False
    # Prioridade 3: Se começa com REPROVADO, verificar se realmente não atende
    elif validation_upper.startswith("REPROVADO"):
        # Verificar se menciona que requisitos NÃO estão atendidos
        requirements_not_met = any(phrase in full_response_lower for phrase in [
            "tema não", "tema ausente", "personagens não aparecem", "personagens ausentes",
            "valor educativo não", "valor educativo ausente", "não atende", "não atendidos"
        ])
        if not requirements_not_met and requirements_met:
            logger.warning("⚠️ [AGENTE 3] REPROVADO mas requisitos parecem atendidos. Aprovando.")
            requirements_ok = True
            has_approved = True
            has_reproved = False
        else:
            requirements_ok = False
            has_approved = False
            has_reproved = True
    # Prioridade 4: Verificar se contém APROVADO nas primeiras 100 caracteres
    elif "APROVADO" in validation_upper[:100] and "REPROVADO" not in validation_upper[:100]:
        requirements_ok = True
        has_approved = True
        has_reproved = False
    # Fallback: Se não encontrou padrão claro mas menciona requisitos atendidos, aprovar
    else:
        if requirements_met:
            logger.warning("⚠️ [AGENTE 3] Resposta não clara mas requisitos parecem atendidos. Aprovando.")
            requirements_ok = True
            has_approved = True
            has_reproved = False
        else:
            logger.warning("⚠️ [AGENTE 3] Resposta não clara, sendo permissivo e aprovando.")
            requirements_ok = True
            has_approved = True
            has_reproved = False
    issues = state.get("issues", [])
    
    logger.info(f"   Resposta completa do validador: {validation_result}")
    logger.info(f"   Análise: has_approved={has_approved}, has_reproved={has_reproved}, requirements_ok={requirements_ok}")
    
    feedback = state.get("feedback", "")
    if not requirements_ok:
        # Extrair os problemas encontrados
        if "REPROVADO:" in validation_result.upper():
            problems = validation_result.split(":", 1)[-1].strip()
            issues.append(f"Requisitos não atendidos: {problems}")
            new_feedback = f"A história foi REPROVADA na validação de requisitos. Problemas encontrados: {problems}. Você deve regenerar a história corrigindo todos estes problemas."
            # Combinar feedbacks se já houver um anterior
            if feedback:
                feedback = f"{feedback}\n\n{new_feedback}"
            else:
                feedback = new_feedback
            logger.warning(f"❌ [AGENTE 3] REPROVADO: {problems}")
        else:
            issues.append("História não atende aos requisitos solicitados")
            new_feedback = "A história foi REPROVADA na validação de requisitos. A história não atende aos requisitos solicitados (tema, personagens, valor educativo ou faixa etária). Você deve regenerar a história garantindo que todos os requisitos sejam atendidos."
            if feedback:
                feedback = f"{feedback}\n\n{new_feedback}"
            else:
                feedback = new_feedback
            logger.warning("❌ [AGENTE 3] REPROVADO: Requisitos não atendidos")
    else:
        logger.info("✅ [AGENTE 3] APROVADO - Todos os requisitos atendidos")
    
    logger.info(f"✅ [AGENTE 3] CONCLUÍDO - requirements_ok={requirements_ok}")
    logger.info("=" * 60)
    
    return {
        **state,
        "requirements_ok": requirements_ok,
        "issues": issues,
        "feedback": feedback
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
- NÃO inclua resumos ou prévias - apenas a história completa
- NÃO repita a história duas vezes

Formato OBRIGATÓRIO em Markdown (SEM resumos, SEM duplicações):
# Título da História

[Texto COMPLETO da história em parágrafos, com todos os personagens: {', '.join(input_data.characters)}]

## Moral da história

[Texto explícito sobre o valor educativo: {input_data.educational_value}]

História original:
{draft_story}

Revise e formate a história seguindo EXATAMENTE o formato acima. IMPORTANTE: NÃO inclua resumos, prévias ou duplicações. Apenas a história completa uma única vez, seguida da moral."""
    
    logger.info("   Enviando prompt de revisão para Ollama...")
    final_story = await services.send_prompt(review_prompt, timeout=120)  # Timeout para revisão
    
    logger.info(f"✅ [AGENTE 4] Revisão concluída: {len(final_story)} caracteres")
    logger.info(f"✅ [AGENTE 4] CONCLUÍDO - História final formatada")
    logger.info("=" * 60)
    
    return {
        **state,
        "final_story": final_story
    }
