import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH pour que les imports 'brain.xxx' fonctionnent
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Maintenant importer et lancer l'application
from brain.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
