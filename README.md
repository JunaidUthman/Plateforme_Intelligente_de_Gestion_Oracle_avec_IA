# Plateforme Intelligente de Gestion Oracle avec IA

Ce projet est une plateforme intelligente pour l'assistance à l'administration de bases de données Oracle. Il combine l'extraction de données (réelles ou simulées), l'analyse par IA (LLM DeepSeek) et une base de connaissances RAG pour fournir des audits de sécurité, des optimisations de requêtes et des recommandations de sauvegarde.

## Prérequis

- **Python 3.8+**
- **Clé API DeepSeek** (dans un fichier `.env`)
- **Base de données Oracle** (optionnel si utilisation du simulateur)
  - Pour une connexion réelle : Accès `SYSDBA` ou utilisateur avec privilèges d'audit.

## Installation

1. **Cloner le projet**
   Navigate to the project root.

2. **Configuration de l'environnement**
   Il est recommandé d'utiliser un environnement virtuel :
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration API**
   Créez un fichier `.env` à la racine (si absent) et ajoutez votre clé :
   ```
   DEEP_SEEK_API_KEY=votre_clé_api
   ```
   
   *Note : Le projet utilise le dossier `datav1/` pour stocker les données et résultats.*

## Usage

### 1. Extraction de Données

Vous avez deux modes : **Simulation** ou **Connexion Réelle**.

- **Mode Réel** (Connexion à une DB Oracle) :
  Configurez `DB_CONFIG` dans `src/real_data_extractor.py` puis lancez :
  ```bash
  python src/real_data_extractor.py
  ```
  Cela générera les CSV dans `datav1/`.

- **Mode Simulation** (Génération de fausses données) :
  ```bash
  python src/data_extractor.py
  ```
  *(Note : Par défaut ce script peut écrire dans `data/`, assurez-vous de déplacer/copier dans `datav1/` ou modifier le script si nécessaire pour l'analyse IA).*

### 2. Analyse et IA

Les modules d'analyse utilisent les données de `datav1/`.

- **Initialisation RAG** (Base de connaissances) :
  ```bash
  python src/rag_setup.py
  ```

- **Détection d'Anomalies** :
  ```bash
  python src/anomaly_detector.py
  ```
  Génère `datav1/detected_anomalies.json`.

- **Optimisation de Requêtes** :
  ```bash
  python src/query_optimizer.py
  ```
  Génère `datav1/query_analysis.json`.

- **Audit de Sécurité** :
  ```bash
  python src/security_audit.py
  ```
  Génère `datav1/last_audit.json`.

- **Recommandation de Sauvegarde** :
  ```bash
  python src/backup_recommender.py
  ```
  Génère `datav1/backup_plan.json` et `datav1/backup_script.rman`.

### 3. Interface Web (Dashboard)

Pour visualiser les résultats et interagir avec le Chatbot DBA :

```bash
python src/webapp/app.py
```
Accédez ensuite à [http://localhost:5000](http://localhost:5000) dans votre navigateur.

## Architecture des Dossiers

- `src/` : Code source des modules Python.
- `src/webapp/` : Application Flask et templates HTML.
- `datav1/` : Dossier principal pour les données (CSV extraits, JSON résultats, Base Vectorielle ChromaDB).
- `data/` : Dossier legacy (à ignorer).
