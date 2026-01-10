# ⚡ Démarrage Rapide - 5 Minutes

Guide ultra-rapide pour démarrer avec MCP Brain/Slaves sur Windows.

## 🎯 Objectif

Avoir une plateforme IA qui peut exécuter des commandes sur votre machine Windows en 5 minutes.

## 📋 Prérequis (à installer si manquant)

1. **Python 3.11+** → https://www.python.org/downloads/
2. **Ollama** → https://ollama.com/download

## 🚀 Installation en 3 commandes

```powershell
# 1. Vérifier les prérequis
.\scripts\check-prerequisites.ps1

# 2. Installer automatiquement
.\scripts\install-windows.ps1

# 3. Démarrer la plateforme
.\scripts\start-all.ps1
```

## ✅ Vérification

```powershell
# Tester que tout fonctionne
.\scripts\test-platform.ps1
```

## 💡 Premier Test Manuel

```powershell
# Générer un token
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=test&scopes=*" -Method Post
$token = $response.token

# Créer une tâche
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    request = "Liste les 5 derniers événements du journal Application Windows"
    dry_run = $false
} | ConvertTo-Json

$task = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" -Method Post -Headers $headers -Body $body

# Voir le résultat
Start-Sleep -Seconds 3
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks/$($task.task_id)" -Headers $headers | ConvertTo-Json -Depth 10
```

## 🎯 Exemples de Prompts

Une fois la plateforme démarrée, vous pouvez envoyer des requêtes comme:

- "Liste tous les processus en cours"
- "Vérifie le statut du service Windows Update"
- "Lis les 10 premières lignes du fichier hosts"
- "Affiche l'utilisation CPU et mémoire"
- "Liste les services Windows arrêtés"

## 📊 Architecture

```
Votre PC Windows
├── Ollama (LLM) :11434
├── MCP Brain :8000 (décision IA)
└── MCP Slave Windows :8002 (exécution)
```

## 🛑 Arrêter la Plateforme

```powershell
.\scripts\stop-all.ps1
```

## 📚 Pour Aller Plus Loin

- **Guide complet**: `INSTALLATION_WINDOWS.md`
- **Exemples d'usage**: `docs/USAGE.md`
- **Documentation API**: `docs/API.md`
- **Architecture**: `docs/ARCHITECTURE.md`

## 🔧 Dépannage Rapide

### Python non trouvé
```powershell
# Vérifier l'installation
python --version

# Si erreur, télécharger depuis python.org
# IMPORTANT: Cocher "Add Python to PATH"
```

### Ollama non accessible
```powershell
# Vérifier qu'Ollama tourne
Invoke-WebRequest -Uri "http://localhost:11434/api/tags"

# Si erreur, lancer Ollama depuis le menu Démarrer
```

### Port déjà utilisé
```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

## 🎉 C'est Tout !

Vous avez maintenant une plateforme IA qui peut:
- ✅ Comprendre vos demandes en langage naturel
- ✅ Planifier les actions nécessaires
- ✅ Exécuter des commandes Windows de manière sécurisée
- ✅ Vous retourner les résultats

Prochaine étape: Déployer des slaves sur vos machines distantes (Linux/Windows) !
