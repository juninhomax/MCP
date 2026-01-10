# Déploiement d'un Slave Windows distant

Ce guide explique comment déployer un Slave Windows sur un serveur distant et le connecter au Brain central.

## 📋 Prérequis

**Sur le serveur distant (Windows 10) :**
- Python 3.10 ou supérieur installé
- Accès réseau au Brain (port 8000)
- PowerShell

**Sur ta machine locale (Brain) :**
- Brain en cours d'exécution
- Connexion réseau accessible depuis le serveur distant

## 🚀 Étapes de déploiement

### 1. Préparer le package sur ta machine locale

```powershell
# Créer le package du Slave
.\package-slave.ps1

# Démarrer le serveur HTTP pour partager les fichiers
.\start-http-server.ps1
```

Le script affichera ton adresse IP locale, par exemple : `http://192.168.1.100:8080`

### 2. Configurer le Brain pour accepter les connexions distantes

**Option A : Modifier le firewall Windows**

```powershell
# Autoriser le port 8000 dans le firewall
New-NetFirewallRule -DisplayName "MCP Brain" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

**Option B : Vérifier que le Brain écoute sur 0.0.0.0**

Le Brain est déjà configuré pour écouter sur `0.0.0.0:8000` (toutes les interfaces).

### 3. Sur le serveur distant Windows 10

**Télécharger et installer le Slave :**

```powershell
# Télécharger le package
Invoke-WebRequest -Uri 'http://VOTRE_IP_LOCAL:8080/slave-windows.zip' -OutFile 'slave.zip'

# Extraire
Expand-Archive -Path 'slave.zip' -DestinationPath 'C:\MCP-Slave'

# Aller dans le dossier
cd C:\MCP-Slave

# Lancer l'installation
.\install.ps1
```

**Pendant l'installation, vous devrez fournir :**
- L'URL du serveur HTTP (ex: `http://192.168.1.100:8080`)
- L'URL du Brain sera demandée (ex: `http://192.168.1.100:8000`)

### 4. Démarrer le Slave distant

```powershell
cd C:\MCP-Slave
.\start-slave.ps1
```

Le Slave démarrera sur le port 8003 par défaut.

### 5. Enregistrer le Slave auprès du Brain

Le Slave doit s'enregistrer auprès du Brain. Depuis ta machine locale :

```powershell
# Tester l'enregistrement
$brainUrl = "http://localhost:8000"
$slaveUrl = "http://IP_SERVEUR_DISTANT:8003"

# Générer un token
$token = (Invoke-RestMethod -Uri "$brainUrl/api/v1/auth/token?slave_id=windows-remote-01&scopes=*" -Method Post).token

# Enregistrer le Slave
$body = @{
    slave_id = "windows-remote-01"
    slave_type = "windows"
    endpoint = $slaveUrl
    capabilities = @("powershell", "file_operations", "system_info")
} | ConvertTo-Json

Invoke-RestMethod -Uri "$brainUrl/api/v1/slaves/register" -Method Post -Headers @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
} -Body $body
```

### 6. Tester la communication

```powershell
# Depuis ta machine locale, tester une commande sur le Slave distant
.\chat-simple.ps1
```

Puis dans le chat :
```
liste les processus sur windows-remote-01
```

## 🔧 Configuration avancée

### Configurer le Slave comme service Windows

Pour que le Slave démarre automatiquement :

```powershell
# Créer un service Windows (nécessite des droits admin)
$serviceName = "MCPSlaveWindows"
$exePath = "C:\MCP-Slave\venv\Scripts\python.exe"
$scriptPath = "C:\MCP-Slave\start.py"

New-Service -Name $serviceName -BinaryPathName "$exePath $scriptPath" -DisplayName "MCP Slave Windows" -StartupType Automatic
Start-Service $serviceName
```

### Ports utilisés

- **Brain** : 8000 (doit être accessible depuis les Slaves)
- **Slave local** : 8002
- **Slave distant** : 8003 (configurable)

### Firewall sur le serveur distant

```powershell
# Autoriser le port du Slave
New-NetFirewallRule -DisplayName "MCP Slave" -Direction Inbound -LocalPort 8003 -Protocol TCP -Action Allow
```

## 🐛 Dépannage

### Le Slave ne peut pas contacter le Brain

1. Vérifier que le Brain est accessible :
   ```powershell
   Invoke-RestMethod -Uri "http://IP_BRAIN:8000/health"
   ```

2. Vérifier le firewall sur la machine du Brain

3. Vérifier que le Brain écoute sur 0.0.0.0 et pas seulement localhost

### Le Brain ne peut pas contacter le Slave

1. Vérifier que le Slave est démarré :
   ```powershell
   Invoke-RestMethod -Uri "http://IP_SLAVE:8003/health"
   ```

2. Vérifier le firewall sur le serveur distant

3. Vérifier que l'URL du Slave est correcte dans l'enregistrement

## 📊 Architecture réseau

```
┌─────────────────────┐
│   Machine locale    │
│                     │
│  ┌──────────────┐   │
│  │    Brain     │   │ Port 8000
│  │ (Orchestrator)│◄──┼────────────┐
│  └──────────────┘   │            │
│         │           │            │
│         │           │            │
│  ┌──────▼───────┐   │            │
│  │ Slave local  │   │ Port 8002  │
│  │  (Windows)   │   │            │
│  └──────────────┘   │            │
└─────────────────────┘            │
                                   │
        Réseau local / Internet    │
                                   │
┌─────────────────────┐            │
│  Serveur distant    │            │
│   (Windows 10)      │            │
│                     │            │
│  ┌──────────────┐   │            │
│  │Slave distant │   │ Port 8003  │
│  │  (Windows)   │◄──┼────────────┘
│  └──────────────┘   │
└─────────────────────┘
```

## ✅ Vérification finale

Pour vérifier que tout fonctionne :

1. Le Brain est accessible : `http://localhost:8000/health`
2. Le Slave local est accessible : `http://localhost:8002/health`
3. Le Slave distant est accessible : `http://IP_DISTANT:8003/health`
4. Le Slave distant est enregistré auprès du Brain
5. Tu peux exécuter des commandes sur le Slave distant via le chat

## 🎯 Prochaines étapes

- Déployer d'autres Slaves (Linux, macOS)
- Configurer l'authentification sécurisée
- Mettre en place HTTPS/TLS
- Configurer des Slaves derrière un VPN
