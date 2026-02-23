"""
Ponto de entrada para o LangGraph Studio.
Exporta o grafo compilado para visualização e debug.
"""
import sys
import os

# Adicionar o diretório src ao path para imports relativos
sys.path.insert(0, os.path.dirname(__file__))

from app.services.story_graph import story_graph

# Exportar o grafo para o LangGraph Studio
graph = story_graph
