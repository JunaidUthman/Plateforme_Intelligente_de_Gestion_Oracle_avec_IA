import pandas as pd
import json
import os
from llm_engine import LLMEngine
from rag_setup import OracleRAG

class AnomalyDetector:
    def __init__(self):
        self.engine = LLMEngine() # Module 3 [cite: 71]
        self.rag = OracleRAG()     # Module 2 [cite: 55]

    def analyze_logs(self, logs_file="data/audit_logs.csv"):
        """Analyse les logs d'audit pour détecter des anomalies [cite: 115]"""
        if not os.path.exists(logs_file):
            return {"error": "Fichier de logs introuvable. Relancez le Module 1."}

        # 1. Chargement des logs d'audit
        df = pd.read_csv(logs_file)
        logs_text = df.to_string(index=False)
        
        # 2. Récupération du contexte de cybersécurité (RAG)
        # On cherche des infos sur les injections SQL et les accès suspects [cite: 63, 123]
        context_docs = self.rag.retrieve_context("patterns d'attaque SQL injection, escalade de privilèges, accès sensibles")
        context_text = "\n".join(context_docs)
        
        # 3. Analyse par Gemini (Module 3)
        print("🕵️ Analyse de cybersécurité en cours sur les logs...")
        analysis_raw = self.engine.generate(
            user_message=self.engine.prompts['anomaly']['prompt'].format(logs=logs_text, context=context_text)
        )
        
        try:
            # Nettoyage et conversion en JSON 
            clean_json = analysis_raw.replace("```json", "").replace("```", "").strip()
            results = json.loads(clean_json)
            
            # Sauvegarde pour le Dashboard
            with open("data/detected_anomalies.json", "w", encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)
                
            return results
        except Exception as e:
            print(f"⚠️ Erreur de parsing JSON : {e}")
            return {"raw_output": analysis_raw}

if __name__ == "__main__":
    detector = AnomalyDetector()
    print("\n--- DÉTECTION D'ANOMALIES & CYBERSÉCURITÉ ---")
    anomalies = detector.analyze_logs()
    
    # Affichage des alertes critiques détectées
    print(json.dumps(anomalies, indent=4, ensure_ascii=False))