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

# --- MÉMOIRE DU CHATBOT (NOUVEAU) ---
# Liste pour stocker l'historique de la session active
# Structure : [{'role': 'user', 'content': '...'}, {'role': 'assistant', 'content': '...'}]
CHAT_HISTORY = []

# --- FONCTIONS UTILITAIRES ---

def load_json_data(filename, directory='datav1'):
    """Charge un fichier JSON depuis le dossier spécifié (défaut: datav1/)"""
    filepath = os.path.join(os.path.dirname(__file__), '../../', directory, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def get_security_status(data):
    """Détermine la couleur du statut sécurité"""
    if not data: return "grey"
    score = data.get('score', 0)
    if score >= 80: return "success"
    if score >= 50: return "warning"
    return "danger"

def get_system_context():
    """Résume l'état actuel du système (Audit, Perf, Anomalies)"""
    context = "--- ÉTAT RÉEL DU SYSTÈME (Données Live) ---\n"
    
    # Sécurité
    sec = load_json_data('last_audit.json', directory='datav1')
    if sec:
        risques = [r['nom'] for r in sec.get('risques', [])]
        context += f"[SÉCURITÉ] Score: {sec.get('score')}/100. Risques: {', '.join(risques[:3])}.\n"
    
    # Performance
    perf = load_json_data('query_analysis.json')
    if perf and isinstance(perf, list):
        exemples = [q.get('sql_id') for q in perf[:2]]
        context += f"[PERFORMANCE] {len(perf)} requêtes lentes. Ex: {', '.join(exemples)}.\n"
    
    # Anomalies
    anom = load_json_data('detected_anomalies.json', directory='datav1')
    if anom and isinstance(anom, list):
        critiques = [a for a in anom if a.get('classification') == 'CRITIQUE']
        context += f"[ANOMALIES] {len(critiques)} menaces CRITIQUES détectées.\n"
        
    return context

def get_conversation_history(limit=3):
    """
    Formate les derniers échanges pour le prompt (3 paires de questions/réponses max)
    """
    if not CHAT_HISTORY:
        return "Aucun historique précédent."
    
    history_str = ""
    # On prend les 'limit' derniers messages
    recent_msgs = CHAT_HISTORY[-limit:]
    for msg in recent_msgs:
        role = "UTILISATEUR" if msg['role'] == 'user' else "ASSISTANT"
        history_str += f"{role}: {msg['content']}\n"
    return history_str

# --- ROUTES ---

@app.route('/')
def index():
    sec_data = load_json_data('last_audit.json', directory='datav1')
    perf_data = load_json_data('query_analysis.json')
    anom_data = load_json_data('detected_anomalies.json', directory='datav1') or []
    
    anomalies_alert = [a for a in anom_data if a.get('classification') in ['CRITIQUE', 'SUSPECT']]
    has_critical = any(a.get('classification') == 'CRITIQUE' for a in anomalies_alert)

    stats = {
        'sec_score': sec_data.get('score', 'N/A') if sec_data else 'N/A',
        'sec_color': get_security_status(sec_data),
        'slow_queries': len(perf_data) if perf_data else 0,
        'anomalies_count': len(anomalies_alert),
        'anom_color': 'danger' if has_critical else 'warning' if anomalies_alert else 'success'
    }
    
    # Préparation des données pour les graphes
    # On passe les données brutes, le JS se chargera du reste
    return render_template('index.html', stats=stats, perf_data=perf_data or [], anom_data=anom_data or [])

@app.route('/security')
def security():
    data = load_json_data('last_audit.json', directory='datav1')
    return render_template('security.html', data=data or {'score': 0, 'risques': [], 'recommandations': []})

@app.route('/performance')
def performance():
    data = load_json_data('query_analysis.json')
    return render_template('performance.html', queries=data or [])

@app.route('/backup')
def backup():
    plan = load_json_data('backup_plan.json', directory='datav1') or {}
    rman_path = os.path.join(os.path.dirname(__file__), '../../datav1', 'backup_script.rman')
    rman_content = "Aucun script généré."
    if os.path.exists(rman_path):
        with open(rman_path, 'r', encoding='utf-8') as f:
            rman_content = f.read()
    return render_template('backup.html', plan=plan, rman=rman_content)

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

# --- GESTION DES SESSIONS (PERSISTANCE) ---
import uuid
import glob
from datetime import datetime

CHATS_DIR = os.path.join(os.path.dirname(__file__), '../../datav1', 'chats')
os.makedirs(CHATS_DIR, exist_ok=True)

def save_chat_session(session_id, messages):
    """Sauvegarde l'historique d'une session dans un fichier JSON."""
    filename = f"session_{session_id}.json"
    filepath = os.path.join(CHATS_DIR, filename)
    
    # Création d'un titre basé sur le premier message utilisateur s'il existe
    title = "Nouvelle conversation"
    if messages:
        first_user_msg = next((m['content'] for m in messages if m['role'] == 'user'), None)
        if first_user_msg:
            title = first_user_msg[:30] + "..." if len(first_user_msg) > 30 else first_user_msg

    data = {
        'id': session_id,
        'last_update': datetime.now().isoformat(),
        'title': title,
        'messages': messages
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_chat_session(session_id):
    """Charge une session existante ou retourne une liste vide."""
    filename = f"session_{session_id}.json"
    filepath = os.path.join(CHATS_DIR, filename)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('messages', [])
        except:
            return []
    return []

def list_chat_sessions():
    """Liste toutes les sessions disponibles triées par date récente."""
    sessions = []
    files = glob.glob(os.path.join(CHATS_DIR, "session_*.json"))
    for fpath in files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                sessions.append({
                    'id': data.get('id'),
                    'title': data.get('title', 'Conversation sans titre'),
                    'last_update': data.get('last_update', '')
                })
        except:
            continue
    # Tri décroissant par date
    sessions.sort(key=lambda x: x['last_update'], reverse=True)
    return sessions

# --- API CHATBOT AVEC SESSIONS ---

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """
    Endpoint intelligent : RAG + Données Live + Historique Persistant
    Payload attendu: { "message": "...", "session_id": "..." (optionnel) }
    """
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id')
    
    # Gestion de la session
    if not session_id:
        session_id = str(uuid.uuid4())
        history = []
    else:
        history = load_chat_session(session_id)
    
    # 1. Récupération des Contextes
    docs, _ = rag_system.retrieve_context(user_message)
    rag_context = "\n".join(docs)
    system_live_data = get_system_context()
    
    # 2. Récupération de l'Historique récent pour le prompt
    # history contient toute la conversation, on prend les derniers échanges pour le LLM
    recent_history_str = ""
    limit = 6
    if history:
        for msg in history[-limit:]:
            role = "UTILISATEUR" if msg['role'] == 'user' else "ASSISTANT"
            recent_history_str += f"{role}: {msg['content']}\n"
    else:
        recent_history_str = "Aucun historique précédent."
    
    # 3. Construction du Prompt Complet
    system_instruction = (
        "Tu es l'assistant DBA intelligent. "
        "Tu as accès à :\n"
        "1. L'HISTORIQUE DE LA CONVERSATION.\n"
        "2. L'ÉTAT RÉEL DU SYSTÈME (Audit, Perf...).\n"
        "3. LA DOCUMENTATION (RAG).\n"
        "Utilise ces informations pour répondre de manière concise."
    )
    
    full_prompt = (
        f"{system_instruction}\n\n"
        f"--- ÉTAT SYSTÈME ACTUEL ---\n{system_live_data}\n\n"
        f"--- HISTORIQUE RÉCENT ---\n{recent_history_str}\n\n"
        f"--- DOCUMENTATION (RAG) ---\n{rag_context}\n\n"
        f"UTILISATEUR: {user_message}"
    )
    
    # 4. Génération
    bot_reply = llm_engine.generate(full_prompt)
    
    # 5. Mise à jour et sauvegarde de la session
    history.append({'role': 'user', 'content': user_message})
    history.append({'role': 'assistant', 'content': bot_reply})
    save_chat_session(session_id, history)
    
    return jsonify({
        'response': bot_reply,
        'session_id': session_id
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Retourne la liste des sessions passées."""
    return jsonify(list_chat_sessions())

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session_details(session_id):
    """Retourne le contenu complet d'une session."""
    messages = load_chat_session(session_id)
    return jsonify({'messages': messages})

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session_endpoint(session_id):
    """Supprime une session."""
    filename = f"session_{session_id}.json"
    filepath = os.path.join(CHATS_DIR, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return jsonify({'status': 'deleted'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)