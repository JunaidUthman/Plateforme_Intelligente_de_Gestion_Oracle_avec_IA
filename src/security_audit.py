import pandas as pd
import json
import os
from llm_engine import LLMEngine
from rag_setup import OracleRAG

class SecurityAuditor:
    def __init__(self):
        self.engine = LLMEngine() 
        self.rag = OracleRAG()     

    def run_audit(self, config_file="data/security_config.csv"):
        """Exécute l'audit et retourne un objet JSON [cite: 81, 89]"""
        if not os.path.exists(config_file):
            return {"error": f"Fichier {config_file} introuvable."}

        # 1. Chargement des données [cite: 83]
        df = pd.read_csv(config_file)
        config_summary = df.to_string(index=False)
        
        # 2. Récupération du contexte [cite: 56]
        context_docs = self.rag.retrieve_context("privilèges DBA critiques, sécurité des mots de passe, rôles Oracle")
        context_text = "\n".join(context_docs)
        
        # 3. Génération du rapport via LLM [cite: 74, 84]
        print("🕵️ Analyse des vulnérabilités en cours par Gemini (Format JSON)...")
        report_raw = self.engine.assess_security(config_summary, context_text)
        
        # 4. Conversion de la réponse texte en JSON 
        try:
            # Nettoyage des balises Markdown (```json ... ```) si présentes
            clean_json = report_raw.replace("```json", "").replace("```", "").strip()
            report_data = json.loads(clean_json)
            
            # Sauvegarde du rapport pour le Dashboard (Module 9)
            with open("data/last_audit.json", "w", encoding='utf-8') as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)
                
            return report_data
        except Exception as e:
            print(f"⚠️ Erreur de parsing JSON. Retour du texte brut. Erreur: {e}")
            return {"raw_report": report_raw}

if __name__ == "__main__":
    auditor = SecurityAuditor()
    print("\n🛡️  LANCEMENT DE L'AUDIT DE SÉCURITÉ (MODE JSON)")
    
    rapport_json = auditor.run_audit()
    
    # Affichage propre du JSON dans la console
    print(json.dumps(rapport_json, indent=4, ensure_ascii=False))