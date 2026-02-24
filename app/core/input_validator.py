"""
Validador de input para detectar conteúdo sensível/impróprio antes de gerar histórias.

Este módulo implementa um mecanismo de validação inteligente baseado em LLM
(Modelo de Linguagem) para garantir que os parâmetros fornecidos para geração
de histórias infantis sejam apropriados para crianças.

A validação ocorre em múltiplas etapas:

1. Verificação rápida por termos explicitamente impróprios (bloqueio imediato)
2. Análise contextual via LLM (mais sofisticada)
3. Tratamento de falsos positivos do modelo
4. Estratégia conservadora em caso de dúvida ou erro
"""
import logging
from typing import List, Tuple
from app.services.agents import send_prompt

# Logger específico do módulo
logger = logging.getLogger(__name__)

async def validate_input_safety(
    theme: str,
    age_group: str,
    educational_value: str,
    setting: str,
    characters: List[str]
) -> Tuple[bool, List[str]]:
    """
    Valida se o input contém conteúdo sensível ou impróprio para histórias infantis.

    Esta função utiliza um modelo de linguagem (LLM) para analisar o contexto
    completo do input, permitindo uma detecção mais precisa do que simples
    filtros baseados em palavras-chave.

    Fluxo de validação:

    1) Verificação rápida por termos explicitamente impróprios
       — evita chamadas desnecessárias ao LLM

    2) Análise contextual via LLM
       — avalia significado e intenção do conteúdo

    3) Tratamento de respostas ambíguas ou erros do modelo

    4) Política conservadora
       — em caso de dúvida, o conteúdo é rejeitado por segurança

    Parâmetros:
        theme (str):
            Tema principal da história.

        age_group (str):
            Faixa etária alvo da história.

        educational_value (str):
            Valor educativo pretendido (ex.: amizade, respeito).

        setting (str):
            Cenário onde a história ocorre.

        characters (List[str]):
            Lista de personagens da história.

    Retorno:
        Tuple[bool, List[str]]:
            - is_safe (bool):
                True se o conteúdo é apropriado.
                False se contém material sensível/impróprio.

            - issues (List[str]):
                Lista de problemas encontrados ou mensagens explicativas.
                Vazia se o conteúdo for aprovado.

    Observações importantes:
        - O sistema prioriza aprovação quando não há evidência clara de problema.
        - Falsos positivos do LLM são tratados para evitar bloqueios indevidos.
        - Em caso de falha técnica, o conteúdo é rejeitado por segurança.
    """
    logger.info("🔍 [VALIDAÇÃO INPUT] Analisando input com LLM...")
    logger.info(f"   Tema: {theme}")
    logger.info(f"   Faixa etária: {age_group}")
    logger.info(f"   Cenário: {setting}")
    logger.info(f"   Personagens: {', '.join(characters)}")
    logger.info(f"   Valor educativo: {educational_value}")
    
    # Verificação rápida de termos obviamente impróprios (antes de chamar LLM)
    all_text = f"{theme} {setting} {' '.join(characters)} {educational_value}".lower()
    obviously_inappropriate = [
        "cabaré", "cabare", "prostituição", "prostituicao", "strip-tease", "striptease",
        "boate", "bar adulto", "nightclub", "clube noturno", "hitler", "stalin",
        "holocausto", "genocídio", "genocidio", "campos de concentração"
    ]
    
    for term in obviously_inappropriate:
        if term in all_text:
            logger.warning(f"❌ [VALIDAÇÃO INPUT] Termo impróprio detectado na verificação rápida")
            logger.warning(f"   Termo bloqueado: '{term}'")
            logger.warning(f"   Contexto completo: Tema='{theme}', Cenário='{setting}', Personagens={characters}, Valor='{educational_value}'")
            return False, ["Conteúdo sensível detectado"]
    
    # Construir prompt para validação (otimizado para ser mais rápido)
    validation_prompt = f"""Valide se este conteúdo é apropriado para histórias infantis:

Tema: {theme}
Cenário: {setting}
Personagens: {', '.join(characters)}
Valor educativo: {educational_value}

REGRAS DE APROVAÇÃO (APROVE se):
- Temas comuns: aventura, fantasia, mistério, amizade, coragem, etc.
- Personagens típicos: cavaleiros, animais falantes, princesas, heróis, crianças, robôs, etc.
- Valores educativos: honestidade, amizade, coragem, respeito, etc.
- Cenários normais: florestas, castelos, cidades, escolas, etc.

REJEITE APENAS se contiver EXPLICITAMENTE:
- Figuras históricas problemáticas pelo nome (Hitler, Stalin) - NÃO rejeite por termos genéricos
- Eventos sensíveis específicos (Holocausto, genocídio) - NÃO rejeite por termos genéricos
- Violência extrema explícita (tortura, assassinato gráfico) - NÃO rejeite por aventura ou ação leve
- Conteúdo sexual explícito (cabaré, prostituição) - NÃO rejeite por termos genéricos
- Drogas ilícitas pelo nome (cocaína, heroína) - NÃO rejeite por termos genéricos

IMPORTANTE: 
- APROVE por padrão se não houver conteúdo CLARAMENTE impróprio
- Animais falantes, cavaleiros, aventuras são SEMPRE apropriados
- Só rejeite se houver menção EXPLÍCITA a conteúdo impróprio
- NÃO rejeite por cautela ou "pode ser problemático" - só rejeite se FOR problemático

RESPONDA EXATAMENTE (sem variações, sem sinônimos):
- "APROVADO" (em maiúsculas, sem ponto) se o conteúdo for apropriado para crianças
- "REPROVADO: [razão]" APENAS se houver conteúdo EXPLICITAMENTE impróprio mencionado acima

REGRAS CRÍTICAS:
- Se não houver menção EXPLÍCITA a conteúdo impróprio, APROVE
- NÃO rejeite por "cautela" ou "pode ser problemático" - só rejeite se FOR problemático
- Animais falantes, cavaleiros, aventuras são SEMPRE apropriados - APROVE
- Se tiver dúvida, APROVE (é melhor aprovar do que rejeitar conteúdo apropriado)

NÃO use sinônimos como "Apoiado", "Permitido", "Válido", etc. Use APENAS "APROVADO" ou "REPROVADO".

Resposta:"""

    try:
        # Chamar LLM para validar (com timeout adequado)
        response = await send_prompt(validation_prompt, timeout=60)
        response_upper = response.upper().strip()
        response_lower = response.lower().strip()
        
        logger.info(f"📝 [VALIDAÇÃO INPUT] Resposta completa do LLM: {response[:200]}")
        
        # Limpar resposta para análise (remove espaços, pontuação, acentos)
        response_clean = response_upper.replace(" ", "").replace(".", "").replace(",", "").replace("!", "").replace("?", "")
        
        # Verificar se parece "APROVADO" mesmo com erros de digitação comuns
        # Aceita: APROVADO, APOrovado, APIOVADO, APOVOADO, etc.
        def looks_like_approved(text):
            """Verifica se o texto parece 'APROVADO' mesmo com erros de digitação"""
            if len(text) < 5:
                return False
            
            # Deve começar com "AP"
            if not text.startswith("AP"):
                return False
            
            # Remove "AP" e verifica o restante
            remaining = text[2:]  # Remove "AP"
            
            # Verifica padrões comuns de "ROVADO", "IOVADO", "OVOADO", etc.
            # Aceita: ROVADO, IOVADO, OVOADO, ROVAD, IOVAD, OVAD, ROVA, IOVA, OVA, etc.
            if len(remaining) >= 3:
                # Verifica se contém "OVADO", "IVADO", ou "OVOADO" (completo)
                if "OVADO" in remaining or "IVADO" in remaining or "OVOADO" in remaining:
                    return True
                # Verifica se começa com "ROV", "IOV", ou "OVO" (erros comuns de digitação)
                if remaining.startswith("ROV") or remaining.startswith("IOV") or remaining.startswith("OVO"):
                    return True
                # Verifica se contém "ROV", "IOV", ou "OVO" nas primeiras posições
                if "ROV" in remaining[:5] or "IOV" in remaining[:5] or "OVO" in remaining[:5]:
                    return True
                # Verifica se contém "OVAD" ou "IVAD" (sem o O final)
                if "OVAD" in remaining[:6] or "IVAD" in remaining[:6]:
                    return True
            
            return False
        
        # Verificar aprovação explícita
        is_approved = looks_like_approved(response_clean[:15])
        has_approved_keyword = "aprovado" in response_lower[:30]
        
        logger.info(f"🔍 [VALIDAÇÃO INPUT] Análise de aprovação:")
        logger.info(f"   Texto limpo: '{response_clean[:15]}'")
        logger.info(f"   looks_like_approved: {is_approved}")
        logger.info(f"   Contém 'aprovado': {has_approved_keyword}")
        
        if is_approved or has_approved_keyword:
            logger.info("✅ [VALIDAÇÃO INPUT] Input aprovado pelo LLM")
            logger.info(f"   Resposta interpretada como: APROVADO (detectado: '{response_clean[:15]}')")
            return True, []
        
        # Se reprovado, extrair a razão e verificar se é falso positivo
        if "REPROVADO" in response_upper or "reprovado" in response_lower:
            # Extrair a razão da reprovação
            if ":" in response:
                reason = response.split(":", 1)[-1].strip()
            else:
                reason = "Conteúdo impróprio detectado pelo validador"
            
            # Verificar se é falso positivo - se a razão não menciona conteúdo explicitamente impróprio
            reason_lower = reason.lower()
            explicit_problems = [
                "hitler", "stalin", "holocausto", "genocídio", "genocidio",
                "cabaré", "cabare", "prostituição", "prostituicao", "strip-tease", "striptease",
                "boate", "bar adulto", "cocaína", "cocaina", "heroína", "heroina",
                "tortura", "assassinato", "violência extrema", "violencia extrema"
            ]
            
            # Se a razão não menciona conteúdo explicitamente impróprio, pode ser falso positivo
            has_explicit_problem = any(problem in reason_lower for problem in explicit_problems)
            
            # Se menciona "cuidadosa", "pode ser", "deve ser", "atenção" sem conteúdo explícito, é falso positivo
            false_positive_indicators = ["cuidadosa", "cuidadoso", "pode ser", "deve ser", "atenção", "cuidado", "precaução"]
            has_false_positive_language = any(indicator in reason_lower for indicator in false_positive_indicators) and not has_explicit_problem
            
            if has_false_positive_language:
                logger.warning(f"⚠️ [VALIDAÇÃO INPUT] Possível falso positivo detectado: {reason}")
                logger.warning(f"   A razão menciona cautela mas não conteúdo explícito - APROVANDO")
                logger.info("✅ [VALIDAÇÃO INPUT] Input aprovado (falso positivo detectado)")
                return True, []
            
            if not has_explicit_problem:
                logger.warning(f"⚠️ [VALIDAÇÃO INPUT] Reprovação sem conteúdo explícito: {reason}")
                logger.warning(f"   Não há menção a conteúdo explicitamente impróprio - APROVANDO")
                logger.info("✅ [VALIDAÇÃO INPUT] Input aprovado (sem conteúdo explícito impróprio)")
                return True, []
            
            # Se tem conteúdo explicitamente impróprio, rejeitar
            issues = [f"Conteúdo sensível detectado: {reason}"]
            logger.warning(f"❌ [VALIDAÇÃO INPUT] Input rejeitado pelo LLM")
            logger.warning(f"   Razão: {reason}")
            logger.warning(f"   Resposta completa: {response[:300]}")
            return False, issues
        
        # Se a resposta não for clara, verificar se menciona aprovação/apropriação
        approval_keywords = ["aprovado", "apropriado", "adequado", "seguro", "bom", "ok", "aceito", "apoiado", "permitido", "válido"]
        if any(keyword in response_lower[:100] for keyword in approval_keywords):
            logger.warning(f"⚠️ [VALIDAÇÃO INPUT] Resposta não clara mas parece aprovar: {response[:100]}")
            logger.warning(f"   Resposta completa: {response[:300]}")
            logger.info("✅ [VALIDAÇÃO INPUT] Interpretando como APROVADO (resposta menciona aprovação/apropriação)")
            return True, []
        
        # Se a resposta não for clara e não menciona aprovação, ser conservador e rejeitar
        logger.warning(f"⚠️ [VALIDAÇÃO INPUT] Resposta do LLM não foi clara e não menciona aprovação")
        logger.warning(f"   Resposta recebida: {response[:300]}")
        logger.warning(f"   Texto limpo analisado: {response_clean[:30]}")
        logger.warning(f"   Rejeitando por segurança")
        return False, ["Não foi possível validar o conteúdo. Por favor, revise as informações fornecidas."]
        
    except Exception as e:
        logger.exception(f"❌ [VALIDAÇÃO INPUT] Erro ao validar com LLM: {str(e)}")
        # Em caso de erro, ser conservador e rejeitar por segurança
        # É melhor bloquear conteúdo potencialmente problemático do que permitir
        logger.warning("⚠️ [VALIDAÇÃO INPUT] Erro na validação - rejeitando por segurança")
        return False, ["Erro ao validar o conteúdo. Por favor, tente novamente ou revise as informações fornecidas."]
