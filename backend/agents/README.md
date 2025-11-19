# Agents - Système Multi-Agent

## Rôle
Agents spécialisés qui collaborent pour planifier les réunions.

## Organisation
Les agents sont des modules Python (fichiers `.py`) dans ce dossier :
- `agent_interface.py` : point d'entrée, validation et routage
- `agent_planner.py` : calcul des créneaux optimaux
- `agent_executor.py` : génération invitation et email
- `agent_report.py` : génération de rapport (optionnel)
- `agent_presentation.py` : génération de présentation PPTX (optionnel)

## Communication
- Appelés par `backend/services/agent_orchestrator.py`
- Chaque agent expose des fonctions Python (pas de HTTP MCP pour simplifier)
- Format de message : dictionnaire Python avec structure MCP-like

## Flux
```
orchestrator → agent_interface → agent_planner → agent_executor → [agent_report] → [agent_presentation]
```

## Implémentation
Chaque fichier contient les fonctions à implémenter (marquées avec des commentaires).
