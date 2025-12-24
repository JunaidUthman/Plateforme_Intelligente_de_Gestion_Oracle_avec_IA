import os
import json
import sys
from flask import Flask, render_template, request, jsonify

# Ajout du chemin parent pour importer vos modules existants
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_engine import LLMEngine
from rag_setup import OracleRAG

app = Flask(__name__)

# Initialisation unique du Moteur IA pour le chatbot
llm_engine = LLMEngine()
rag_system = OracleRAG()

# --- FONCTIONS UTILITAIRES DE CHARGEMENT DE DONNÉES ---

def load_json_data(filename):
    """Charge un fichier JSON depuis le dossier data/"""
    filepath = os.path.join(os.path.dirname(__file__), '../../data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_security_status(data):
    """Détermine la couleur du statut sécurité"""
    if not data: return "grey"
    score = data.get('score', 0)
    if score >= 80: return "success" # Vert
    if score >= 50: return "warning" # Orange
    return "danger" # Rouge

# --- ROUTES DES PAGES (VIEW) ---

@app.route('/')
def index():
    """Page d'accueil : Vue globale"""
    sec_data = load_json_data('last_audit.json')
    perf_data = load_json_data('query_analysis.json')
    anom_data = load_json_data('detected_anomalies.json')
    
    # Calcul des résumés pour le dashboard
    stats = {
        'sec_score': sec_data.get('score', 'N/A') if sec_data else 'N/A',
        'sec_color': get_security_status(sec_data),
        'slow_queries': len(perf_data) if perf_data else 0,
        'anomalies_crit': len([a for a in (anom_data or []) if a.get('classification') == 'CRITIQUE'])
    }
    return render_template('index.html', stats=stats)

@app.route('/security')
def security():
    """Page Module 4 : Audit de Sécurité"""
    data = load_json_data('last_audit.json')
    return render_template('security.html', data=data)

@app.route('/performance')
def performance():
    """Page Module 5 : Optimisation SQL"""
    data = load_json_data('query_analysis.json')
    return render_template('performance.html', queries=data)

@app.route('/backup')
def backup():
    """Page Module 7 : Sauvegardes"""
    plan = load_json_data('backup_plan.json')
    # On lit aussi le script RMAN brut s'il existe
    rman_path = os.path.join(os.path.dirname(__file__), '../../data', 'backup_script.rman')
    rman_content = ""
    if os.path.exists(rman_path):
        with open(rman_path, 'r', encoding='utf-8') as f:
            rman_content = f.read()
            
    return render_template('backup.html', plan=plan, rman=rman_content)

@app.route('/chatbot')
def chatbot_page():
    """Page Module 9 : Interface Chatbot"""
    return render_template('chatbot.html')

# --- API CHATBOT (AJAX) ---

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Endpoint qui reçoit le message utilisateur et renvoie la réponse IA"""
    user_message = request.json.get('message')
    
    # 1. Récupération du contexte RAG (Module 2)
    # Note : retrieve_context renvoie (docs, metas), on prend juste les docs
    context_docs, _ = rag_system.retrieve_context(user_message)
    context_text = "\n".join(context_docs)
    
    # 2. Construction du prompt système global
    system_prompt = (
        "Tu es l'assistant intelligent de la plateforme Oracle DBA. "
        "Tu as accès à la documentation technique via le RAG. "
        "Réponds de manière concise et professionnelle aux questions sur "
        "l'optimisation, la sécurité, les sauvegardes ou les anomalies."
    )
    
    # 3. Génération via LLMEngine (Module 3)
    full_prompt = f"{system_prompt}\n\nCONTEXTE RAG :\n{context_text}\n\nUSER: {user_message}"
    response = llm_engine.model.generate_content(full_prompt)
    
    return jsonify({'response': response.text})

if __name__ == '__main__':
    app.run(debug=True, port=5000)