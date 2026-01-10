# 🚀 Installation Complète - Windows

Guide d'installation pas à pas pour mettre en place la plateforme MCP Brain/Slaves sur Windows.

## ✅ Prérequis à installer

### 1. Python 3.11+

**Télécharger et installer Python:**

1. Aller sur https://www.python.org/downloads/
2. Télécharger Python 3.11 ou supérieur (recommandé: 3.11.7)
3. **IMPORTANT**: Cocher "Add Python to PATH" pendant l'installation
4. Installer avec les options par défaut

**Vérifier l'installation:**
```powershell
python --version
# Devrait afficher: Python 3.11.x
```

Si ça ne fonctionne pas, redémarrer PowerShell ou ajouter Python au PATH manuellement.

### 2. Ollama (LLM Local)

**Installer Ollama:**

1. Aller sur https://ollama.com/download
2. Télécharger Ollama pour Windows
3. Installer l'application
4. Ollama démarre automatiquement en arrière-plan

**Télécharger le modèle Qwen:**
```powershell
ollama pull qwen2.5-coder:14b
```

⏱️ **Attention**: Le téléchargement fait ~8GB, cela peut prendre 10-30 minutes selon votre connexion.

**Modèles alternatifs (plus légers):**
```powershell
# Si 14B est trop lourd, utiliser 7B:
ollama pull qwen2.5-coder:7b

# Ou encore plus léger (3B):
ollama pull qwen2.5-coder:3b
```

**Vérifier qu'Ollama fonctionne:**
```powershell
# Tester l'API
Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing
```

### 3. Git (optionnel mais recommandé)

**Installation de Git:**

Si pas déjà installé:
1. Télécharger depuis https://git-scm.com/download/win
2. Installer avec les options par défaut

**Configuration Git pour Windsurf:**

Après l'installation, configurer Git pour qu'il fonctionne avec Windsurf:

```powershell
# Configurer votre identité Git
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Configurer Windsurf comme éditeur par défaut
git config --global core.editor "code --wait"

# Configurer les fins de ligne pour Windows
git config --global core.autocrlf true

# Activer les couleurs dans le terminal
git config --global color.ui auto

# Vérifier la configuration
git config --list
```

**Intégration avec Windsurf:**

Windsurf détecte automatiquement Git. Pour vérifier:
1. Ouvrir Windsurf
2. Ouvrir le projet: `C:\Users\sarma\CascadeProjects\mcp-brain-slaves`
3. Le panneau Source Control (Ctrl+Shift+G) devrait afficher le repo Git
4. Vous pouvez maintenant faire des commits, push, pull directement depuis Windsurf

**Initialiser le repo Git (si pas déjà fait):**

```powershell
cd C:\Users\sarma\CascadeProjects\mcp-brain-slaves

# Initialiser le repo
git init

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit: MCP Brain/Slaves platform"
```

## 📦 Installation de la Plateforme

### Étape 1: Préparer l'environnement

```powershell
# Naviguer vers le projet
cd C:\Users\sarma\CascadeProjects\mcp-brain-slaves

# Vérifier que Python fonctionne
python --version
```

### Étape 2: Installer MCP Brain

```powershell
# Aller dans le dossier brain
cd brain

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Si erreur de politique d'exécution, exécuter:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier de configuration
copy .env.example .env

# Retour au dossier racine
cd ..
```

**Éditer `brain/.env`:**
```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b
LLM_API_BASE=http://localhost:11434
BRAIN_HOST=0.0.0.0
BRAIN_PORT=8000
```

### Étape 3: Installer MCP Slave Windows

```powershell
# Aller dans le dossier slave Windows
cd slaves\windows

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier de configuration
copy .env.example .env

# Retour au dossier racine
cd ..\..
```

## 🚀 Démarrage de la Plateforme

### Option 1: Démarrage Manuel (Recommandé pour la première fois)

**Terminal 1 - MCP Brain:**
```powershell
cd C:\Users\sarma\CascadeProjects\mcp-brain-slaves\brain
.\venv\Scripts\Activate.ps1
python main.py
```

Vous devriez voir:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Générer le token:**
```powershell
# Attendre que le Brain soit démarré (5 secondes)
Start-Sleep -Seconds 5

# Générer un token pour le slave
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=windows-slave-01&scopes=*" -Method Post
$token = $response.token
Write-Host "Token: $token"

# Sauvegarder le token
$token | Out-File -FilePath "C:\Users\sarma\CascadeProjects\mcp-brain-slaves\slaves\windows\.env" -Append -Encoding UTF8
Add-Content -Path "C:\Users\sarma\CascadeProjects\mcp-brain-slaves\slaves\windows\.env" -Value "AUTH_TOKEN=$token"
```

**Terminal 3 - MCP Slave Windows:**
```powershell
cd C:\Users\sarma\CascadeProjects\mcp-brain-slaves\slaves\windows
.\venv\Scripts\Activate.ps1
python main.py
```

Vous devriez voir:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8002
```

### Option 2: Démarrage Automatique (Une fois que tout fonctionne)

```powershell
.\scripts\start-all.ps1
```

## ✅ Vérification

**Vérifier que tout fonctionne:**

```powershell
# Brain
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Windows Slave
Invoke-RestMethod -Uri "http://localhost:8002/health"

# Lister les tools disponibles
Invoke-RestMethod -Uri "http://localhost:8002/tools"
```

## 🧪 Premier Test

**Créer une tâche de test:**

```powershell
# Générer un token de test
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/token?slave_id=test-user&scopes=*" -Method Post
$token = $response.token

# Créer une tâche (dry run)
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    request = "Liste les processus en cours sur Windows"
    dry_run = $true
} | ConvertTo-Json

$task = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks" -Method Post -Headers $headers -Body $body

Write-Host "Task ID: $($task.task_id)"
Write-Host "Status: $($task.status)"

# Voir les détails de la tâche
Start-Sleep -Seconds 3
$taskDetails = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/tasks/$($task.task_id)" -Headers $headers
$taskDetails | ConvertTo-Json -Depth 10
```

## 🔧 Dépannage

### Python n'est pas reconnu
```powershell
# Vérifier l'installation
where.exe python

# Si vide, ajouter Python au PATH:
# Paramètres → Système → Paramètres système avancés → Variables d'environnement
# Ajouter: C:\Users\sarma\AppData\Local\Programs\Python\Python311
```

### Erreur "cannot be loaded because running scripts is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Ollama ne répond pas
```powershell
# Vérifier qu'Ollama tourne
Get-Process ollama

# Si absent, lancer Ollama depuis le menu Démarrer
# Ou redémarrer le service
```

### Port déjà utilisé
```powershell
# Trouver le processus qui utilise le port 8000
netstat -ano | findstr :8000

# Tuer le processus (remplacer PID)
taskkill /PID <PID> /F
```

### Le Brain ne trouve pas Ollama
Vérifier que `LLM_API_BASE=http://localhost:11434` dans `brain/.env`

## 📊 Prochaines Étapes

Une fois que tout fonctionne localement:

1. **Déployer sur machines distantes** (voir `docs/DEPLOYMENT.md`)
2. **Configurer la sécurité** (tokens, firewall)
3. **Tester des scénarios réels**
4. **Monitorer les logs**

## 🆘 Besoin d'aide ?

- Consulter `docs/USAGE.md` pour des exemples
- Consulter `docs/API.md` pour la documentation API
- Vérifier les logs dans les terminaux
