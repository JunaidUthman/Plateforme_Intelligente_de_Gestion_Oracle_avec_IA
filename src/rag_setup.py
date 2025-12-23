import os
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai
from chromadb.utils import embedding_functions

load_dotenv()

# 1. Configuration de Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # À mettre dans un fichier .env
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY non trouvée dans le fichier .env")
    
genai.configure(api_key=GOOGLE_API_KEY)

class OracleRAG:
    def __init__(self, db_path="data/chroma_db"):
        # Initialisation de ChromaDB (Stockage local)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Création (ou récupération) de la collection "oracle_docs"
        # On utilise une fonction d'embedding personnalisée via Gemini
        self.collection = self.client.get_or_create_collection(name="oracle_docs")
        print("✅ Base Vectorielle ChromaDB prête.")

    def add_documents(self, folder_path):
        """Lit les fichiers texte et les ajoute à la Vector DB"""
        if not os.path.exists(folder_path):
            print(f"⚠️ Dossier {folder_path} introuvable.")
            return

        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # 2. Vectorisation via Gemini (Embedding)
                    # Note : Dans une version réelle, on découperait le texte en morceaux (chunks)
                    response = genai.embed_content(
                        model="models/embedding-001",
                        content=content,
                        task_type="retrieval_document"
                    )
                    embedding = response['embedding']

                    # 3. Stockage dans ChromaDB
                    self.collection.add(
                        ids=[filename],
                        embeddings=[embedding],
                        documents=[content],
                        metadatas=[{"source": filename}]
                    )
                    print(f"📖 Document '{filename}' indexé.")

    def retrieve_context(self, query, n_results=3):
        """Fonction de recherche par similarité [cite: 65]"""
        # Vectorisation de la question de l'utilisateur
        query_embedding = genai.embed_content(
            model="models/embedding-001",
            content=query,
            task_type="retrieval_query"
        )['embedding']

        # Recherche des documents les plus proches
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0]

# --- TEST DU MODULE 2 ---
if __name__ == "__main__":
    rag = OracleRAG()
    
    # Étape d'ingestion (à faire une seule fois ou lors de nouveaux docs)
    # rag.add_documents("data/knowledge") 

    # Étape de test de récupération 
    query = "Comment optimiser un index lent ?"
    context = rag.retrieve_context(query)
    print(f"\n🔍 Question : {query}")
    print(f"💡 Contexte trouvé : {context[0][:200]}...")