# PyPost — Analyse Complète & Todo Liste d'Implémentation

> Application desktop de type Postman, 100% locale, open-source, sans système de connexion.
> Stack : Python + Flask + pywebview + HTML/Tailwind CSS

---

## 1. Vue d'ensemble du Projet

**PyPost** est un client HTTP desktop hybride. Le backend Python (Flask) gère toutes les requêtes réseau et la persistance locale, tandis que le frontend (HTML/CSS Tailwind + JS vanilla) fournit une interface moderne rendue dans une fenêtre native via pywebview. Aucune donnée ne quitte la machine de l'utilisateur.

### Objectifs

- Envoyer des requêtes HTTP (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- Visualiser les réponses avec syntax highlighting
- Organiser les requêtes en collections versionnables
- Gérer des environnements et variables
- Fonctionner hors ligne, sans compte, sans télémétrie

---

## 2. Architecture Technique

### 2.1 Stack Technologique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| Fenêtre native | `pywebview` | Encapsule l'UI web dans une fenêtre OS |
| Backend | `Flask` (Python) | API locale, proxy HTTP, logique métier |
| Client HTTP | `httpx` | Requêtes HTTP/1.1 et HTTP/2, async |
| Frontend | HTML + Tailwind CSS v4 CDN | Interface utilisateur |
| Interactivité | Alpine.js | Réactivité légère sans framework lourd |
| Syntax highlight | `highlight.js` (CDN) | Coloration du JSON/XML/HTML de réponse |
| Stockage | Fichiers JSON locaux | Collections, historique, environnements |
| Packaging | `PyInstaller` | Binaire distributable `.exe` / `.app` |

### 2.2 Schéma d'Architecture

```
┌──────────────────────────────────────────────────────┐
│                 Fenêtre pywebview                    │
│  ┌────────────────────────────────────────────────┐  │
│  │           UI (HTML + Tailwind + Alpine.js)     │  │
│  │                                                │  │
│  │  [Sidebar Collections] [Request Panel]         │  │
│  │  [Tabs]                [Response Viewer]       │  │
│  └───────────────────┬────────────────────────────┘  │
│                      │ fetch() HTTP local            │
│  ┌───────────────────▼────────────────────────────┐  │
│  │           Flask API (localhost:5000)            │  │
│  │                                                │  │
│  │  POST /api/send       → httpx → Internet       │  │
│  │  GET  /api/history    → data/history.json      │  │
│  │  CRUD /api/collections → data/collections/     │  │
│  │  CRUD /api/environments → data/environments/  │  │
│  └────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### 2.3 Structure des Fichiers

```
pypost/
├── main.py                    ← Point d'entrée : Flask + pywebview
├── requirements.txt
├── api/
│   ├── __init__.py
│   ├── routes_request.py      ← /api/send, /api/history
│   ├── routes_collections.py  ← CRUD collections
│   ├── routes_environments.py ← CRUD environnements
│   └── http_client.py         ← Wrapper httpx
├── core/
│   ├── storage.py             ← Lecture/écriture JSON
│   ├── variables.py           ← Résolution {{variables}}
│   └── auth.py                ← Helpers auth (Bearer, Basic, etc.)
├── data/                      ← Données persistées (gitignore optionnel)
│   ├── history.json
│   ├── collections/
│   │   └── *.json
│   └── environments/
│       └── *.json
└── ui/
    ├── index.html             ← Point d'entrée UI
    ├── js/
    │   ├── app.js             ← Logique principale Alpine.js
    │   ├── request.js         ← Gestion formulaire requête
    │   ├── response.js        ← Affichage et formatage réponse
    │   ├── collections.js     ← Sidebar collections
    │   └── environment.js     ← Gestion variables
    └── css/
        └── custom.css         ← Surcharges Tailwind si nécessaire
```

### 2.4 Communication Frontend ↔ Backend

Tout passe par des appels `fetch()` vers l'API Flask locale. Pas de bridge pywebview complexe — Flask sert à la fois les fichiers statiques et l'API JSON.

```python
# main.py
import webview
from api import create_app

app = create_app()

if __name__ == '__main__':
    window = webview.create_window(
        'PyPost',
        url='http://localhost:5000',
        width=1280,
        height=800,
        resizable=True,
        frameless=False
    )
    # Lancer Flask dans un thread, puis pywebview
    import threading
    t = threading.Thread(target=lambda: app.run(port=5000, debug=False))
    t.daemon = True
    t.start()
    webview.start()
```

---

## 3. Modèles de Données

### 3.1 Requête (Request)

```json
{
  "id": "uuid-v4",
  "name": "Get Users",
  "method": "GET",
  "url": "https://api.example.com/users",
  "headers": [
    { "key": "Authorization", "value": "Bearer {{token}}", "enabled": true }
  ],
  "params": [
    { "key": "page", "value": "1", "enabled": true }
  ],
  "body": {
    "type": "json",
    "raw": "{\"name\": \"John\"}",
    "form_data": [],
    "url_encoded": []
  },
  "auth": {
    "type": "bearer",
    "token": "{{token}}"
  },
  "pre_request_script": "",
  "tests": ""
}
```

### 3.2 Réponse (Response)

```json
{
  "status_code": 200,
  "status_text": "OK",
  "headers": {},
  "body": "...",
  "size_bytes": 1024,
  "time_ms": 142,
  "timestamp": "2026-04-03T15:30:00Z"
}
```

### 3.3 Collection

```json
{
  "id": "uuid-v4",
  "name": "My API",
  "description": "",
  "variables": [],
  "folders": [
    {
      "id": "uuid-v4",
      "name": "Users",
      "requests": []
    }
  ],
  "requests": []
}
```

### 3.4 Environnement

```json
{
  "id": "uuid-v4",
  "name": "Production",
  "variables": [
    { "key": "base_url", "value": "https://api.example.com", "enabled": true },
    { "key": "token", "value": "abc123", "enabled": true, "secret": true }
  ]
}
```

---

## 4. Fonctionnalités Détaillées

### 4.1 Envoi de Requêtes

- Méthodes : GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- URL avec résolution automatique des `{{variables}}`
- Query params via tableau clé/valeur (sync avec l'URL)
- Headers personnalisés + headers auto (Content-Type, etc.)
- Body : JSON, form-data, x-www-form-urlencoded, raw text, binaire
- Timeout configurable
- Suivi des redirections (option on/off)
- Support des certificats SSL (option de désactivation)

### 4.2 Authentification

| Type | Détails |
|------|---------|
| No Auth | — |
| Bearer Token | Ajout automatique du header `Authorization: Bearer ...` |
| Basic Auth | Username + Password encodés en base64 |
| API Key | Header ou query param |
| OAuth 2.0 | Client Credentials flow (MVP+) |

### 4.3 Visualisation de la Réponse

- Body avec syntax highlighting (JSON, XML, HTML, texte)
- Pretty print automatique du JSON
- Onglets : Body / Headers / Cookies / Info
- Status code avec badge coloré (2xx vert, 4xx orange, 5xx rouge)
- Temps de réponse et taille en octets
- Copie en un clic du body complet
- Recherche dans la réponse (Ctrl+F)

### 4.4 Collections & Organisation

- Création de collections avec icône et description
- Dossiers imbriqués (1 niveau de profondeur minimum, 2 pour MVP+)
- Drag & drop pour réorganiser (MVP+)
- Duplication de requêtes
- Export/import JSON (format propre, compatible Git)
- Recherche globale dans les collections

### 4.5 Environnements & Variables

- Plusieurs environnements (Dev, Staging, Prod…)
- Variables globales + variables par environnement
- Variables secrètes (masquées dans l'UI, jamais loguées)
- Résolution `{{variable}}` dans URL, headers, body, scripts
- Variable active surlignée en vert si résolue, rouge si manquante

### 4.6 Historique

- Dernières N requêtes envoyées (configurable, défaut 200)
- Rejouer une requête depuis l'historique
- Filtrage par méthode, URL, status code
- Effacement manuel ou auto après X jours

### 4.7 Onglets (Tabs)

- Plusieurs requêtes ouvertes simultanément
- État non sauvegardé indiqué par un point (•)
- Fermeture avec confirmation si non sauvegardé
- Restauration des onglets au redémarrage

---

## 5. UI/UX — Wireframe des Zones

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo PyPost]    [+ New Tab]  [Tab 1 ●] [Tab 2]        [Settings] │
├──────────────┬──────────────────────────────────────────────────────┤
│              │  GET  ▼  │ https://api.example.com/{{path}}    [Send]│
│  SIDEBAR     ├──────────────────────────────────────────────────────┤
│              │  [Params] [Headers] [Body] [Auth] [Scripts] [Tests]  │
│  Collections │──────────────────────────────────────────────────────│
│  ├ My API    │  KEY                    VALUE              ENABLED   │
│  │ ├ Users   │  ─────────────────────────────────────────────────── │
│  │ │ GET /   │  Authorization          Bearer {{token}}    ☑        │
│  │ └ POST /  │  Content-Type           application/json    ☑        │
│  └ Other     │  + Add Header                                        │
│              ├──────────────────────────────────────────────────────┤
│  Environments│  RESPONSE   200 OK  •  142ms  •  1.2 KB             │
│  > Production│  [Body] [Headers] [Cookies] [Info]                   │
│    Dev       │  {                                                    │
│    Staging   │    "users": [                                        │
│              │      { "id": 1, "name": "Alice" }                   │
│  History     │    ]                                                 │
│              │  }                                                    │
└──────────────┴──────────────────────────────────────────────────────┘
```

---

## 6. Roadmap MVP → Full

### Phase 1 — MVP (Semaines 1–2)

Objectif : une app utilisable au quotidien pour l'essentiel.

- [ ] Architecture du projet (structure fichiers, Flask, pywebview)
- [ ] Envoi de requêtes GET/POST/PUT/DELETE
- [ ] Affichage de la réponse (status, headers, body JSON pretty)
- [ ] Gestion des headers et query params (tableau clé/valeur)
- [ ] Body JSON raw
- [ ] Historique basique (50 dernières requêtes)
- [ ] UI de base : layout sidebar + request panel + response viewer
- [ ] Dark mode par défaut
- [ ] Bearer Token auth

**Livrable MVP :** binaire `.exe` / `.app` fonctionnel, 0 dépendance externe.

### Phase 2 — Productivité (Semaines 3–4)

Objectif : remplacer Postman pour 80% des cas d'usage.

- [ ] Collections CRUD (création, édition, suppression, dossiers)
- [ ] Sauvegarde des requêtes dans les collections
- [ ] Environnements et variables `{{variable}}`
- [ ] Résolution des variables dans URL/headers/body
- [ ] Onglets multiples avec état persisté
- [ ] Body : form-data, x-www-form-urlencoded
- [ ] Auth : Basic Auth, API Key
- [ ] Recherche dans les collections
- [ ] Export/Import JSON des collections

### Phase 3 — Avancé (Semaines 5–7)

Objectif : parité avec les fonctionnalités fréquentes de Postman.

- [ ] Pre-request scripts (JavaScript sandboxé)
- [ ] Tests automatiques sur la réponse (assertions JS)
- [ ] Variables dynamiques (timestamp, uuid, random…)
- [ ] Runner de collection (exécuter N requêtes en séquence)
- [ ] Cookies manager
- [ ] Body : fichier binaire / multipart avancé
- [ ] Proxy HTTP configurable
- [ ] SSL : désactivation par domaine
- [ ] Raccourcis clavier (Ctrl+Enter pour envoyer, etc.)

### Phase 4 — Polish & Distribution (Semaines 8–9)

- [ ] OAuth 2.0 (Client Credentials)
- [ ] WebSocket basique
- [ ] Import Postman Collection v2.1 (JSON)
- [ ] Import OpenAPI / Swagger (génération auto de requêtes)
- [ ] Thèmes (dark/light/custom)
- [ ] Paramètres : timeout, max redirects, certificats SSL
- [ ] Auto-update (GitHub Releases)
- [ ] Packaging final Windows + macOS + Linux

---

## 7. Todo Liste Complète

### 🏗️ Setup & Architecture

- [x] Initialiser le repo Git avec `.gitignore` Python
- [x] Créer l'environnement virtuel (`python -m venv .venv`)
- [x] Installer les dépendances : `flask httpx pywebview pyinstaller`
- [x] Créer `main.py` avec lancement Flask (thread daemon) + pywebview
- [ ] Créer `api/__init__.py` avec factory `create_app()`
- [ ] Créer `core/storage.py` : fonctions CRUD JSON génériques
- [ ] Créer `data/` avec fichiers JSON initiaux vides
- [ ] Servir le dossier `ui/` comme dossier statique Flask
- [ ] Configurer le hot-reload en mode développement (FLASK_ENV=development)

### 🔌 Backend — Requêtes HTTP

- [ ] `POST /api/send` : wrapper httpx, retourne status/headers/body/time_ms
- [ ] Gestion des erreurs réseau (timeout, DNS, SSL) avec messages lisibles
- [ ] Support des méthodes GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- [ ] Désactivation SSL vérification (paramètre optionnel)
- [ ] Suivi des redirections avec option on/off
- [ ] Timeout configurable par requête

### 📁 Backend — Collections

- [ ] `GET /api/collections` : liste toutes les collections
- [ ] `POST /api/collections` : crée une collection
- [ ] `PUT /api/collections/:id` : modifie une collection
- [ ] `DELETE /api/collections/:id` : supprime une collection
- [ ] `POST /api/collections/:id/requests` : ajoute une requête
- [ ] `PUT /api/collections/:id/requests/:rid` : modifie une requête
- [ ] `DELETE /api/collections/:id/requests/:rid` : supprime une requête

### 🌍 Backend — Environnements

- [ ] `GET /api/environments` : liste les environnements
- [ ] `POST /api/environments` : crée un environnement
- [ ] `PUT /api/environments/:id` : modifie un environnement
- [ ] `DELETE /api/environments/:id` : supprime un environnement
- [ ] `GET /api/environments/active` : retourne l'environnement actif
- [ ] `PUT /api/environments/active` : définit l'environnement actif

### 📜 Backend — Historique

- [ ] `GET /api/history` : retourne les N dernières requêtes
- [ ] Sauvegarde automatique après chaque requête envoyée
- [ ] `DELETE /api/history` : vide l'historique
- [ ] Limitation à N entrées (configurable, défaut 200)

### 🎨 Frontend — Layout & Base

- [ ] `index.html` avec structure 3 zones (sidebar / request / response)
- [ ] Intégration Tailwind CSS v4 via CDN
- [ ] Intégration Alpine.js via CDN
- [ ] Intégration highlight.js via CDN (JSON, XML, HTML)
- [ ] Dark mode par défaut avec toggle light/dark
- [ ] Composant Tab bar (onglets multiples)
- [ ] Sidebar redimensionnable (drag handle)
- [ ] Layout responsive (collapse sidebar sur petite fenêtre)

### 🎨 Frontend — Request Panel

- [ ] Dropdown méthode HTTP avec couleurs par méthode
- [ ] Champ URL avec auto-complétion depuis l'historique
- [ ] Bouton Send avec état loading (spinner)
- [ ] Onglets : Params / Headers / Body / Auth / Scripts / Tests
- [ ] Tableau clé/valeur réutilisable (params + headers)
  - [ ] Checkbox enable/disable par ligne
  - [ ] Bouton suppression par ligne
  - [ ] Ajout de ligne au focus sur la dernière ligne vide
- [ ] Body switcher : none / raw JSON / form-data / urlencoded / binary
- [ ] Éditeur raw avec syntax highlighting basique
- [ ] Auth panel : sélecteur de type + champs dynamiques
- [ ] Sync params ↔ URL (éditer l'URL met à jour le tableau et vice versa)

### 🎨 Frontend — Response Viewer

- [ ] Badge status code coloré (2xx/3xx/4xx/5xx)
- [ ] Affichage temps de réponse + taille
- [ ] Onglets : Body / Headers / Cookies / Info
- [ ] Pretty print JSON avec syntax highlighting (highlight.js)
- [ ] Toggle Raw / Pretty
- [ ] Bouton "Copy body"
- [ ] Recherche dans la réponse (Ctrl+F)
- [ ] Affichage des headers de réponse en tableau

### 🎨 Frontend — Collections Sidebar

- [ ] Liste des collections avec icône et nom
- [ ] Arborescence dossiers/requêtes (collapse/expand)
- [ ] Badge méthode HTTP coloré sur chaque requête
- [ ] Bouton "New Collection" + formulaire modal
- [ ] Bouton "New Request" contextuel
- [ ] Clic sur une requête → ouvre dans un onglet
- [ ] Menu contextuel (clic droit) : renommer, dupliquer, supprimer
- [ ] Champ de recherche global dans les collections

### 🎨 Frontend — Environnements

- [ ] Sélecteur d'environnement actif dans le header
- [ ] Modal de gestion des environnements
- [ ] Tableau de variables (clé / valeur / secret / activé)
- [ ] Variables secrètes : valeur masquée avec toggle reveal
- [ ] Indicateur visuel des variables non résolues dans l'URL

### 🎨 Frontend — Historique

- [ ] Panel historique dans la sidebar (onglet)
- [ ] Liste des requêtes avec méthode, URL tronquée, status, date
- [ ] Filtres : méthode, status code
- [ ] Clic → charge la requête dans l'onglet actif
- [ ] Bouton "Clear history"

### 🔧 Core — Variables & Scripting

- [ ] `core/variables.py` : résolution `{{variable}}` dans une chaîne
- [ ] Résolution dans URL, headers, body avant envoi
- [ ] Variables dynamiques : `{{$timestamp}}`, `{{$guid}}`, `{{$randomInt}}`
- [ ] Sandbox JS pour pre-request scripts (via `py_mini_racer` ou équivalent)
- [ ] Accès à `pm.environment.set/get` dans les scripts (MVP+)

### 📦 Packaging & Distribution

- [ ] `pypost.spec` pour PyInstaller (inclure `ui/`, `data/`)
- [ ] Build Windows : `pyinstaller --onefile --windowed`
- [ ] Build macOS : `.app` bundle
- [ ] Build Linux : AppImage ou binaire
- [ ] `README.md` avec instructions d'installation et de build
- [ ] `CHANGELOG.md`
- [ ] Workflow GitHub Actions pour build automatique sur tag

### ✅ Qualité & Tests

- [ ] Tests unitaires `core/variables.py` (pytest)
- [ ] Tests des routes Flask (pytest + Flask test client)
- [ ] Linter : `ruff` ou `flake8`
- [ ] Formatter : `black`
- [ ] Test manuel du packaging sur chaque OS cible

---

## 8. Dépendances Python

```txt
# requirements.txt
flask>=3.0
httpx[http2]>=0.27
pywebview>=5.0
pyinstaller>=6.0

# Optionnel — scripting JS
py-mini-racer>=0.12

# Dev
pytest
black
ruff
```

---

## 9. Points d'Attention Critiques

### Sécurité

- Flask tourne sur `localhost` uniquement — ne jamais binder sur `0.0.0.0`
- Les variables secrètes ne doivent pas apparaître dans les logs Flask
- Le sandbox JS des scripts doit être isolé (pas d'accès au filesystem)
- Valider les URLs côté Python avant de les passer à httpx

### Performance

- Les grandes réponses (>1MB) doivent être tronquées pour l'affichage UI (option de voir tout)
- Le pretty print JSON ne doit pas bloquer l'UI thread — traiter côté Python
- L'historique doit être paginé pour ne pas charger 200 entrées d'un coup

### Expérience Utilisateur

- L'état des onglets ouverts doit être persisté et restauré au redémarrage
- Les erreurs réseau doivent afficher un message clair (pas de stack trace Python)
- Le premier lancement doit proposer une requête exemple pour ne pas arriver sur un écran vide

---

*Document généré le 03/04/2026 — Version 1.0*
