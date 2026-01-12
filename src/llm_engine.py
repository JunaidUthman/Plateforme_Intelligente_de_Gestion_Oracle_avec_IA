import os
import yaml
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        """Initialisation de DeepSeek engine"""
        self.api_key = os.getenv("DEEP_SEEK_API_KEY")
        if not self.api_key:
            raise ValueError("❌ Clé API DeepSeek manquante dans le fichier .env (DEEP_SEEK_API_KEY)")
        
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.model_name = "deepseek-chat"
        
        # Chargement du fichier prompts.yaml
        try:
            with open("data/prompts.yaml", "r", encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
            print(f"✅ LLMEngine initialisé avec {self.model_name}.")
        except FileNotFoundError:
            print("❌ Erreur : Fichier data/prompts.yaml introuvable.")
            self.prompts = {}

    def generate(self, user_message, system_context=""):
        """Méthode de base pour l'appel au LLM via DeepSeek API"""
        try:
            system_role = self.prompts.get('system_role', 'You are a helpful assistant.')
            # Combine system context if provided
            if system_context:
                system_content = f"{system_role}\n\nCONTEXTE :\n{system_context}"
            else:
                system_content = system_role

            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']

        except Exception as e:
            return f"❌ Erreur DeepSeek : {str(e)}"

    def analyze_query(self, sql, plan, context):
        """Module 5 : Optimisation de requêtes"""
        template = self.prompts['optimization']['prompt']
        prompt_final = template.format(query=sql, plan=plan, context=context)
        return self.generate(prompt_final)

    def assess_security(self, config, context):
        """Module 4 : Audit de sécurité"""
        template = self.prompts['security']['prompt']
        prompt_final = template.format(config=config, context=context)
        return self.generate(prompt_final)
        
    def detect_anomaly(self, log_entry, context):
        """Module 6 : Détection d'anomalies"""
        template = self.prompts['anomaly']['prompt']
        # On passe le log et le contexte au template
        prompt_final = template.format(logs=log_entry, context=context)
        return self.generate(prompt_final)

# --- TEST DE VALIDATION DU MODULE ---
if __name__ == "__main__":
    engine = LLMEngine()
    
    # Test : Expliquer un plan d'exécution simple
    test_sql = "SELECT name FROM employees WHERE id = 100"
    test_plan = "INDEX UNIQUE SCAN ON EMP_PK"
    test_context = "L'opération INDEX UNIQUE SCAN est optimale pour les recherches par clé primaire."
    
    print("\n🤖 Envoi du test d'optimisation (DeepSeek)...")
    reponse = engine.analyze_query(test_sql, test_plan, test_context)
    print(f"\nRésultat de l'IA :\n{reponse}")