"""Fábrica de Podcasts de Ventas — CORTEXIA 777.

Pipeline en Python que toma el conocimiento real del proyecto (plan.yml),
lo convierte en una serie de podcasts a dos voces (guiones), genera los
briefs para producir el audio en NotebookLM (Audio Overview), lleva el
estado de cada episodio y publica un dashboard.

Flujo:  plan.yml  ->  serie  ->  guiones  ->  briefs NotebookLM
        ->  (audio manual)  ->  estado  ->  dashboard
"""

__version__ = "1.0.0"
