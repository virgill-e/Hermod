import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid

# Le dossier data à la racine du projet
DATA_DIR = Path(__file__).parent.parent / "data"

def _get_file_path(resource: str, item_id: Optional[str] = None) -> Path:
    if resource == "history":
        return DATA_DIR / "history.json"
    
    dir_path = DATA_DIR / resource
    dir_path.mkdir(parents=True, exist_ok=True)
    if item_id:
        return dir_path / f"{item_id}.json"
    return dir_path

def read_json_file(path: Path) -> Any:
    if not path.exists():
        return [] if path.name == "history.json" else {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return [] if path.name == "history.json" else {}

def write_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def list_items(resource: str) -> List[Dict]:
    """Liste tous les items pour une ressource donnée (ex: 'collections')."""
    if resource == "history":
        return read_json_file(_get_file_path("history"))
        
    items = []
    dir_path = _get_file_path(resource)
    if dir_path.exists() and dir_path.is_dir():
        for file in dir_path.glob("*.json"):
            items.append(read_json_file(file))
    return items

def get_item(resource: str, item_id: str) -> Optional[Dict]:
    """Récupère un item par son ID."""
    path = _get_file_path(resource, item_id)
    if path.exists():
        return read_json_file(path)
    return None

def create_item(resource: str, data: Dict) -> Dict:
    """Crée un nouvel item."""
    if resource == "history":
        history = list_items("history")
        data["id"] = data.get("id", str(uuid.uuid4()))
        history.insert(0, data)
        # Limiter à 200 entrées pour l'historique
        history = history[:200]
        write_json_file(_get_file_path("history"), history)
        return data

    item_id = data.get("id", str(uuid.uuid4()))
    data["id"] = item_id
    write_json_file(_get_file_path(resource, item_id), data)
    return data

def update_item(resource: str, item_id: str, data: Dict) -> Optional[Dict]:
    """Met à jour un item existant."""
    path = _get_file_path(resource, item_id)
    if not path.exists():
        return None
    
    # On force l'id pour éviter qu'il soit écrasé
    data["id"] = item_id
    write_json_file(path, data)
    return data

def delete_item(resource: str, item_id: str) -> bool:
    """Supprime un item."""
    if resource == "history":
        history = list_items("history")
        new_history = [item for item in history if item.get("id") != item_id]
        if len(new_history) != len(history):
            write_json_file(_get_file_path("history"), new_history)
            return True
        return False
        
    path = _get_file_path(resource, item_id)
    if path.exists():
        path.unlink()
        return True
    return False

def clear_history() -> None:
    """Vide l'historique."""
    write_json_file(_get_file_path("history"), [])
