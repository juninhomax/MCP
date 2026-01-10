# Contributing to MCP Brain/Slaves

Merci de votre intérêt pour contribuer au projet MCP Brain/Slaves !

## 🎯 Philosophie du projet

Le projet suit une philosophie stricte :
- **Le LLM ne se fait jamais confiance**
- Chaque action doit être justifiée, validée, traçable et réversible
- Sécurité avant tout
- Séparation stricte entre décision (Brain) et exécution (Slaves)

## 🛠️ Configuration de développement

### Prérequis
- Python 3.11+
- Git
- Ollama (pour le LLM local)

### Installation

```bash
# Cloner le repo
git clone https://github.com/your-org/mcp-brain-slaves.git
cd mcp-brain-slaves

# Installer les dépendances de développement
pip install -r tests/requirements.txt

# Configurer pre-commit hooks
pip install pre-commit
pre-commit install
```

## 📝 Standards de code

### Python
- PEP 8 compliance
- Type hints obligatoires
- Docstrings pour toutes les fonctions publiques
- Maximum 100 caractères par ligne

### Exemple
```python
from typing import Optional

def execute_command(
    command: str,
    timeout: int = 30,
    dry_run: bool = False
) -> ToolExecutionResult:
    """
    Execute a command with validation.
    
    Args:
        command: Command to execute
        timeout: Execution timeout in seconds
        dry_run: If True, simulate execution
        
    Returns:
        ToolExecutionResult with execution details
    """
    pass
```

## 🧪 Tests

### Exécuter les tests
```bash
# Tous les tests
pytest tests/ -v

# Tests spécifiques
pytest tests/test_validator.py -v

# Avec couverture
pytest tests/ --cov=brain --cov=slaves --cov=shared
```

### Écrire des tests
- Un test par fonctionnalité
- Noms descriptifs
- Arrange-Act-Assert pattern

```python
def test_command_validation_rejects_dangerous_commands():
    # Arrange
    validator = CommandValidator()
    
    # Act
    is_valid, msg = validator.validate("rm -rf /")
    
    # Assert
    assert is_valid is False
    assert "Dangerous pattern" in msg
```

## 🔐 Sécurité

### Règles de sécurité
1. Ne jamais commit de tokens/secrets
2. Toujours valider les commandes
3. Logger toutes les actions
4. Tester les patterns dangereux

### Ajouter une validation
```python
# Dans shared/security/validator.py
DANGEROUS_PATTERNS = [
    r"nouveau_pattern_dangereux",
]
```

## 🎨 Structure du code

### Ajouter un nouveau tool

1. **Définir le tool** (`slaves/*/tools/registry.py`):
```python
registry.register(
    ToolDefinition(
        name="mon_tool",
        description="Description claire",
        tool_type=ToolType.LINUX,
        input_schema=ToolInputSchema(
            properties={
                "param": {"type": "string"}
            },
            required=["param"]
        )
    ),
    None
)
```

2. **Implémenter l'exécution** (`slaves/*/executor.py`):
```python
elif tool_name == "mon_tool":
    command = f"ma_commande {parameters.get('param')}"
    return await self.execute_command(command, dry_run=dry_run)
```

3. **Ajouter des tests** (`tests/test_mon_tool.py`):
```python
def test_mon_tool_execution():
    # Test implementation
    pass
```

## 📚 Documentation

### Documenter une fonctionnalité
- Mettre à jour `docs/API.md` pour les endpoints
- Mettre à jour `docs/USAGE.md` pour les exemples
- Mettre à jour `docs/ARCHITECTURE.md` pour les changements structurels

## 🔄 Workflow de contribution

1. **Fork** le projet
2. **Créer une branche** (`git checkout -b feature/ma-fonctionnalite`)
3. **Commiter** (`git commit -m 'feat: ajouter ma fonctionnalité'`)
4. **Tester** (`pytest tests/ -v`)
5. **Push** (`git push origin feature/ma-fonctionnalite`)
6. **Pull Request**

### Format des commits
Suivre [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: ajouter support pour kubectl logs
fix: corriger validation des commandes Windows
docs: mettre à jour guide de déploiement
test: ajouter tests pour auth manager
refactor: simplifier slave manager
```

## 🐛 Rapporter un bug

Utiliser le template suivant :

```markdown
**Description**
Description claire du bug

**Reproduction**
1. Étapes pour reproduire
2. Comportement attendu
3. Comportement observé

**Environnement**
- OS: [Linux/Windows]
- Python: [version]
- LLM: [Ollama/GLM-4]

**Logs**
```
Logs pertinents
```
```

## 💡 Proposer une fonctionnalité

1. Vérifier qu'elle n'existe pas déjà
2. Ouvrir une issue avec le tag `enhancement`
3. Décrire le cas d'usage
4. Proposer une implémentation

## 📋 Checklist PR

- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Code formaté (black, isort)
- [ ] Type hints ajoutés
- [ ] Logs structurés ajoutés
- [ ] Sécurité validée
- [ ] Pas de secrets dans le code

## 🎯 Priorités actuelles

### Phase 2 - Tools & Sécurité
- [ ] Améliorer la tool registry
- [ ] Renforcer la validation des schémas
- [ ] Implémenter la rotation des tokens
- [ ] Ajouter plus de logs structurés

### Phase 3 - Multi-slaves
- [ ] Routing intelligent
- [ ] Retry & fallback
- [ ] Load balancing

### Phase 4 - IA avancée
- [ ] Multi-step reasoning amélioré
- [ ] Séparation planning/execution
- [ ] Support contexte long
- [ ] RAG pour docs infra

## 📞 Contact

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Email: [votre-email]

## 📄 Licence

En contribuant, vous acceptez que vos contributions soient sous licence MIT.
