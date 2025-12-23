import pandas as pd
import json
import os
from llm_engine import LLMEngine
from rag_setup import OracleRAG

class BackupRecommender:
    def __init__(self):
        self.engine = LLMEngine() # Module 3
        self.rag = OracleRAG()     # Module 2

    def generate_strategy(self, rpo, rto, budget):
        """Génère une stratégie de sauvegarde optimale basée sur les besoins utilisateur"""
        
        # 1. Simulation de récupération des métriques de la base (Module 1/7)
        # En production, cela viendrait d'une requête sur V$INSTANCE ou V$DATAFILE [cite: 135]
        db_metrics = {
            "taille_go": 500,
            "volume_transactions": "Haut",
            "criticite": "Critique"
        }
        
        # 2. Récupération du contexte RAG (Module 2) [cite: 133]
        # On cherche les bonnes pratiques RPO/RTO
        context_docs = self.rag.retrieve_context("stratégie sauvegarde RMAN, RPO RTO Oracle, sauvegarde incrémentale")
        context_text = "\n".join(context_docs)
        
        # 3. Appel à l'IA pour la recommandation [cite: 140-141]
        print("🤖 Génération de la stratégie de sauvegarde intelligente...")
        prompt_template = self.engine.prompts['backup']['prompt']
        analysis_raw = self.engine.generate(
            user_message=prompt_template.format(
                metrics=json.dumps(db_metrics),
                rpo=rpo,
                rto=rto,
                budget=budget,
                context=context_text
            )
        )
        
        try:
            # Nettoyage et conversion en JSON [cite: 144]
            clean_json = analysis_raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
            
            # Sauvegarde pour le Dashboard
            with open("data/backup_strategy.json", "w", encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
                
            return result
        except Exception as e:
            print(f"⚠️ Erreur de parsing JSON : {e}")
            return {"raw_output": analysis_raw}

if __name__ == "__main__":
    recommender = BackupRecommender()
    
    # Simulation des 3 questions utilisateur 
    print("\n--- CONFIGURATION DU PLAN DE SAUVEGARDE ---")
    u_rpo = "15 minutes (Zéro perte de données souhaitée)"
    u_rto = "Moins de 2 heures"
    u_budget = "Moyen (Stockage sur disque local et export cloud)"
    
    plan = recommender.generate_strategy(u_rpo, u_rto, u_budget)
    
    # Affichage du résultat [cite: 151]
    print(json.dumps(plan, indent=4, ensure_ascii=False))