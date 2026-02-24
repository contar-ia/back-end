"""
Ponto de entrada para o LangGraph Studio.

Este módulo tem como finalidade expor o grafo compilado da aplicação
para ferramentas externas de visualização e depuração, como o
LangGraph Studio.
"""
import sys
import os

# Adicionar o diretório src ao path para imports relativos
sys.path.insert(0, os.path.dirname(__file__))

from app.services.story_graph import story_graph

# Exportar o grafo para o LangGraph Studio
graph = story_graph
