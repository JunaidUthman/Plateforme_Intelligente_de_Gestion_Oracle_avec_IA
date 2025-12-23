import os
import chromadb
from chromadb.utils import embedding_functions

class OracleRAG:
    def __init__(self, db_path="data/chroma_db"):
        """Initialise ChromaDB avec un modèle d'embedding local [cite: 55, 58]"""
        # Création du dossier de base s'il n'existe pas
        if not os.path.exists("data"):
            os.makedirs("data")

        # Initialisation du client persistant (stockage sur disque) 
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Modèle local : all-MiniLM-L6-v2 (rapide, léger et gratuit) [cite: 13, 234]
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Création ou récupération de la collection 
        self.collection = self.client.get_or_create_collection(
            name="oracle_docs", 
            embedding_function=self.emb_fn
        )
        print("✅ Base Vectorielle ChromaDB prête (Mode Local).")

    def add_documents(self, folder_path):
        """Lit les fichiers .txt et les indexe dans la base [cite: 59]"""
        if not os.path.exists(folder_path):
            print(f"⚠️ Dossier {folder_path} introuvable.")
            return

        documents = []
        ids = []
        metadatas = []

        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
                    ids.append(filename) # L'ID est le nom du fichier
                    metadatas.append({"source": filename})
        
        if documents:
            # Utilisation de upsert pour éviter les erreurs d'ID existant
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            print(f"📖 {len(documents)} documents indexés/mis à jour avec succès.")
        else:
            print("⚠️ Aucun fichier .txt trouvé dans le dossier.")

    def retrieve_context(self, query, n_results=3):
        """Recherche par similarité sémantique [cite: 65]"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]

# --- BLOC DE TEST POUR VÉRIFICATION ---
if __name__ == "__main__":
    rag = OracleRAG()
    
    # Étape 1 : Indexation (Pointer vers votre dossier de texte)
    # Assurez-vous d'avoir créé 'data/knowledge/' avec vos fichiers .txt
    rag.add_documents("data/knowledge") 

    # Étape 2 : Test de récupération [cite: 66]
    test_query = "Comment optimiser un index lent ?"
    print(f"\n🔍 Recherche : {test_query}")
    
    try:
        context = rag.retrieve_context(test_query)
        print(f"💡 Premier résultat trouvé :\n{context[0][:200]}...")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération : {e}")