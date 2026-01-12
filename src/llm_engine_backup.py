import os
import yaml
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self):
        """Initialisation de Gemini avec le modèle validé par le diagnostic [cite: 71]"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("❌ Clé API Gemini manquante dans le fichier .env")
        
        genai.configure(api_key=api_key)
        
        # Utilisation du nom exact trouvé dans votre diagnostic
        self.model_name = 'models/gemini-2.5-flash'
        self.model = genai.GenerativeModel(model_name=self.model_name)
        
        # Chargement du fichier prompts.yaml [cite: 76]
        try:
            with open("data/prompts.yaml", "r", encoding='utf-8') as f:
                self.prompts = yaml.safe_load(f)
            print(f"✅ LLMEngine initialisé avec {self.model_name}.")
        except FileNotFoundError:
            print("❌ Erreur : Fichier data/prompts.yaml introuvable.")

    def generate(self, user_message, system_context=""):
        """Méthode de base pour l'appel au LLM [cite: 72]"""
        try:
            # On combine le rôle système et le contexte pour guider l'IA
            full_prompt = f"{self.prompts['system_role']}\n\nCONTEXTE :\n{system_context}\n\nQUESTION :\n{user_message}"
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"❌ Erreur Gemini : {str(e)}"

    def analyze_query(self, sql, plan, context):
        """Module 5 : Optimisation de requêtes [cite: 73]"""
        template = self.prompts['optimization']['prompt']
        prompt_final = template.format(query=sql, plan=plan, context=context)
        return self.generate(prompt_final)

    def assess_security(self, config, context):
        """Module 4 : Audit de sécurité [cite: 74]"""
        template = self.prompts['security']['prompt']
        prompt_final = template.format(config=config, context=context)
        return self.generate(prompt_final)
        
    def detect_anomaly(self, log_entry, context):
        """Module 6 : Détection d'anomalies """
        template = self.prompts['anomaly']['prompt']
        # On passe le log et le contexte au template
        prompt_final = template.format(logs=log_entry, context=context)
        return self.generate(prompt_final)

# --- TEST DE VALIDATION DU MODULE 3 ---
if __name__ == "__main__":
    engine = LLMEngine()
    
    # Test : Expliquer un plan d'exécution simple [cite: 78]
    test_sql = "SELECT name FROM employees WHERE id = 100"
    test_plan = "INDEX UNIQUE SCAN ON EMP_PK"
    test_context = "L'opération INDEX UNIQUE SCAN est optimale pour les recherches par clé primaire."
    
    print("\n🤖 Envoi du test d'optimisation...")
    reponse = engine.analyze_query(test_sql, test_plan, test_context)
    print(f"\nRésultat de l'IA :\n{reponse}")
