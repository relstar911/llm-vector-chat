import chromadb
import os

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
print(f"[ChromaDB-DEBUG] Initialisiere PersistentClient mit Pfad: {os.path.abspath(CHROMA_DB_PATH)}")

chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = chroma_client.get_or_create_collection("chat_data")

def add_to_vector_db(text: str, embedding: list, metadata: dict = None):
    import logging
    import traceback
    print(f"[ChromaDB-DEBUG] add_to_vector_db called with id={metadata.get('id') if metadata else None}")
    try:
        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}],
            ids=[metadata.get("id") if metadata and "id" in metadata else None]
        )
        logging.info(f"[ChromaDB] Embedding erfolgreich gespeichert: {metadata.get('id') if metadata else None}")
        print(f"[ChromaDB] Embedding erfolgreich gespeichert: {metadata.get('id') if metadata else None}")
        import os
        chroma_dir = os.path.abspath("chroma_db")
        print(f"[ChromaDB-DEBUG] chroma_db exists? {os.path.exists(chroma_dir)}")
        if os.path.exists(chroma_dir):
            print(f"[ChromaDB-DEBUG] Inhalt von chroma_db: {os.listdir(chroma_dir)}")
        else:
            print(f"[ChromaDB-DEBUG] chroma_db nicht vorhanden")
        # Versuche, persist() aufzurufen, falls verfügbar
        try:
            if hasattr(collection, 'persist'):
                collection.persist()
                print("[ChromaDB-DEBUG] collection.persist() wurde aufgerufen.")
            elif hasattr(globals().get('chroma_client', None), 'persist'):
                chroma_client.persist()
                print("[ChromaDB-DEBUG] chroma_client.persist() wurde aufgerufen.")
        except Exception as persist_exc:
            print(f"[ChromaDB-DEBUG] Fehler beim Persistieren: {persist_exc}")
    except Exception as e:
        print(f"[ChromaDB-DEBUG] Fehler beim Hinzufügen zu ChromaDB: {e}")
        traceback.print_exc()

def remove_from_vector_db(chat_id: str):
    """Entfernt einen Eintrag aus der ChromaDB-Collection anhand der ID."""
    print(f"[ChromaDB-DEBUG] remove_from_vector_db called with id={chat_id}")
    try:
        collection.delete(ids=[chat_id])
        if hasattr(collection, 'persist'):
            collection.persist()
            print("[ChromaDB-DEBUG] collection.persist() nach Delete aufgerufen.")
        elif hasattr(globals().get('chroma_client', None), 'persist'):
            chroma_client.persist()
            print("[ChromaDB-DEBUG] chroma_client.persist() nach Delete aufgerufen.")
    except Exception as e:
        print(f"[ChromaDB-DEBUG] Fehler beim Entfernen aus ChromaDB: {e}")

def query_vector_db(query_embedding: list, n_results: int = 5, score_threshold: float = 0.5):
    """
    Gibt nur Ergebnisse zurück, deren Score >= score_threshold ist. Score wird mitgeliefert.
    """
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results, include=['documents', 'metadatas', 'distances'])
    # Chroma gibt Distanzen zurück, wir wandeln sie in Ähnlichkeit um: similarity = 1 - distance
    filtered = {'documents': [[]], 'metadatas': [[]], 'scores': [[]]}
    for doc, meta, dist in zip(results.get('documents', [[]])[0], results.get('metadatas', [[]])[0], results.get('distances', [[]])[0]):
        score = 1.0 - dist if dist is not None else 0.0
        if score >= score_threshold:
            filtered['documents'][0].append(doc)
            filtered['metadatas'][0].append(meta)
            filtered.setdefault('scores', [[]])[0].append(score)
    return filtered
