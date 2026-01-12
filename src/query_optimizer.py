import pandas as pd
import json
import os
from llm_engine import LLMEngine
from rag_setup import OracleRAG

class QueryOptimizer:
    def __init__(self):
        # Initialisation des briques précédentes
        self.engine = LLMEngine() # Module 3
        self.rag = OracleRAG()     # Module 2

    def analyze_slow_queries(self, metrics_file="data/performance_metrics.csv"):
        """Analyse toutes les requêtes lentes détectées dans le Module 1 """
        if not os.path.exists(metrics_file):
            return {"error": "Fichier de métriques introuvable. Relancez le Module 1."}

        # 1. Chargement des métriques de performance
        df = pd.read_csv(metrics_file)
        
        # On ne filtre plus, on prend toutes les requêtes pour analyse
        slow_queries = df
        
        results = []

        for _, row in slow_queries.iterrows():
            sql_text = row['SQL_TEXT']
            plan_op = row['PLAN_OPERATION']
            sql_id = row['SQL_ID']

            # 2. Récupération du contexte d'optimisation via le RAG (Module 2) [cite: 65]
            context_docs, _ = self.rag.retrieve_context(f"Comment optimiser une opération {plan_op} sur la table {row.get('OBJECT_NAME', '')}")
            context_text = "\n".join(context_docs)

            # 3. Génération de l'analyse via Gemini (Module 3) 
            print(f"⚡ Analyse de la requête {sql_id} en cours...")
            analysis_raw = self.engine.analyze_query(sql_text, plan_op, context_text)

            try:
                # Nettoyage et conversion en JSON
                clean_json = analysis_raw.replace("```json", "").replace("```", "").strip()
                analysis_data = json.loads(clean_json)
                analysis_data["sql_id"] = sql_id
                results.append(analysis_data)
            except Exception as e:
                print(f"⚠️ Erreur de parsing pour {sql_id}: {e}")
                results.append({"sql_id": sql_id, "raw_response": analysis_raw})

        # 4. Sauvegarde des analyses pour le Dashboard (Module 9)
        with open("data/query_analysis.json", "w", encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        return results

if __name__ == "__main__":
    optimizer = QueryOptimizer()
    print("\n--- ANALYSE D'OPTIMISATION SQL ---")
    analyses = optimizer.analyze_slow_queries()
    
    # Affichage du résultat final
    print(json.dumps(analyses, indent=4, ensure_ascii=False))