import sys
from pathlib import Path

# Ajouter le dossier parent au PYTHONPATH
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Importer et lancer l'application
from slaves.windows.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")
