# LLM Chat Vector App

Professionelles, lokal laufendes Chat-System mit LLM, Vektor-Datenbank und API-Backend.

---

## Systemprompt & Sprachlogik

- Das System antwortet automatisch immer in der Sprache der Eingabe.
- Halluzinationen und erfundene Fakten werden durch einen festen Systemprompt vermieden.
- Bei Unsicherheit gibt die KI eine ehrliche Rückmeldung.
- Der Systemprompt ist fest im Backend integriert und wird jedem LLM-Aufruf vorangestellt.

---

## Architektur & Konzept

- **Ziel:** Lokale, datenschutzfreundliche LLM-Chatlösung mit persistenter Speicherung und semantischer Suche.
- **Backend:** FastAPI (Python)
- **LLM:** Ollama (lokal, z.B. mit llama2)
- **Embeddings:** SentenceTransformers
- **Vektor-DB:** ChromaDB
- **Datenbank:** SQLite (SQLAlchemy)
- **API-Design:** Saubere Trennung von Routen (`/chat`, `/query`), Services und Modellen.

### Datenfluss
1. **User sendet Prompt** an `/chat` (POST):
    - Prompt wird an Ollama (LLM) geschickt.
    - Antwort wird empfangen (korrekte Streaming-Verarbeitung).
    - Embedding wird erzeugt.
    - Chat inkl. Metadaten wird in SQLite gespeichert.
    - Embedding + Metadaten werden in ChromaDB gespeichert.
2. **User nutzt `/query`** (POST):
    - Anfrage wird als Embedding verarbeitet.
    - Ähnliche Prompts/Antworten werden aus ChromaDB gesucht und zurückgegeben.

---

## Setup & Betrieb

1. **Abhängigkeiten installieren**
   ```sh
   pip install -r requirements.txt
   ```
2. **Ollama installieren & Modell laden**
   - [Ollama Download](https://ollama.com/)
   - Modell laden: `ollama pull llama2`
   - Server starten: `ollama serve`
3. **API starten**
   ```sh
   uvicorn app.main:app --reload
   ```
4. **Swagger/OpenAPI-Doku:**
   - [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## API-Endpoints

### `/chat` (POST)
- **Input:** `{ "prompt": "...", "model": "llama2" }`
- **Output:** `{ "response": "..." }`
- **Speichert** Chat in DB & Vektor-DB

### `/query` (POST)
- **Input:** `{ "query": "..." }`
- **Output:** Ähnliche Prompts/Antworten aus Vektor-DB

---

## Troubleshooting & Lessons Learned

- **500 Internal Server Error:**
  - Tritt auf, wenn Ollama kein Modell geladen hat oder nicht läuft.
  - Bei Änderungen am Datenbankschema ggf. `app.db` löschen und neu starten.
  - SQLite & ChromaDB erwarten unterschiedliche Formate für Zeitstempel (`datetime` vs. `isoformat`).
- **Port blockiert:**
  - Mit `netstat -ano | findstr :8000` und `taskkill /PID <PID> /F` lösen.
- **Streaming-Response:**
  - Ollama gibt mehrere JSON-Zeilen zurück, daher muss die Antwort zeilenweise zusammengebaut werden.

---

## Erweiterbarkeit & Nächste Schritte

- **Frontend:** Modernes React + Material UI mit Sidebar, Undo (in Planung), Chat-Löschen, Responsive Design.
- **Sidebar:** Zeigt alle bisherigen Sessions, Auswahl lädt Verlauf, "Neuer Chat"-Button, Sessions können gelöscht werden.
- **Session-Titel:** Die Session erhält automatisch den Text der ersten User-Nachricht als Titel.
- **Session-Löschung:** Beim Löschen erscheint ein Dialog mit der Option, auch die Embeddings aus der Vektor-Datenbank zu entfernen (Checkbox, standardmäßig aktiviert).
- **Undo:** Nach dem Löschen einer Session ist eine Undo-Funktion (Wiederherstellung) direkt im Frontend verfügbar (Snackbar mit Undo-Button). Vollständige Wiederherstellung inkl. Embeddings und Nachrichten.
- **ChromaDB-Sync:** Beim Löschen wird das Embedding aus ChromaDB entfernt (optional, Checkbox). Bei Undo wird es wiederhergestellt.
- **Export:** Sessions können einzeln als JSON-Datei exportiert werden (Export-Button in der Sidebar, Endpoint `/sessions/export/{session_id}`).
- **REST-API:**
  - `/chats` (GET): Alle bisherigen Chats
  - `/chats/{id}` (DELETE): Chat + Embedding löschen
  - `/chats/restore` (POST): Chat + Embedding exakt wiederherstellen
  - `/chat` (POST): Neuen Chat starten (Prompt → LLM → Antwort → Embedding)
  - `/query` (POST): Semantische Suche über alle bisherigen Chats (zeigt nur Ergebnisse zu existierenden Sessions)
  - `/sessions/export/{session_id}` (GET): Exportiert eine Session als JSON
- **Authentifizierung:** Zugangsschutz für API (optional, noch offen)
- **Logging & Monitoring:** Fehler und Nutzung überwachen (optional)
- **Weitere Modelle:** Verschiedene LLMs via Ollama testen (Dropdown im UI möglich)

---

## Frontend-Features (Stand: 2025-05-04)
- Sidebar mit Session-Liste, Auswahl, Session-Löschung (mit Dialog und Undo)
- Undo-Snackbar nach Session-Löschung (Wiederherstellung möglich)
- Export-Button pro Session (Download als JSON)
- Responsive Design, Material UI

---

## Projektstatus
- [x] LLM-Chat lokal lauffähig
- [x] Persistenz & Vektor-Suche funktionieren
- [x] API-Design sauber und modular
- [x] Modernes Frontend mit Sidebar, Session-Löschung, Delete-Dialog, Export
- [x] Konsistenz zwischen SQLite & ChromaDB
- [x] Undo-Funktion beim Session-Löschen (Frontend & Backend vollständig implementiert)
- [x] Multi-Message-Threads & Export (JSON)
- [ ] Auth
- [x] Faktenprüfung/RAG (Backend & Frontend fertig: Button im Chat, Wikipedia-Integration, asynchron & robust)
- [ ] Feinschliff: bessere Satztrennung, weitere Wissensquellen, Authentifizierung (optional)

---

## Faktenprüfung/RAG (neu)
- Faktencheck-Button unter jeder Assistant-Antwort im Chat
- Prüft Aussagen gegen Wikipedia (de), zeigt Snippet & Link, robust gegen Fehler
- Asynchrone Verarbeitung, kein Blockieren des Backends
- Maximal 5 Sätze pro Anfrage

---

## Maintainer
- Initial Setup & Architektur: KI-gestützt (Cascade)
- Weiterentwicklung: Siehe Issues & ToDo
