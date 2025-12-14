# ⚡ Quick Start - n8n Workflow Builder

Los geht's in 5 Minuten! 🚀

## 1️⃣ API Key holen (2 Min)

1. Geh zu: https://n8n.schimmi-n8n.de
2. **Settings** (unten links) > **API**
3. **"Create New API Key"** klicken
4. Key kopieren (sieht aus wie: `n8n_api_...`)

## 2️⃣ Setup (1 Min)

```bash
# Dependencies
pip install httpx mcp python-dotenv

# .env erstellen
cat > .env << EOF
N8N_API_URL=https://n8n.schimmi-n8n.de
N8N_API_KEY=DEIN_KEY_HIER
EOF
```

## 3️⃣ Test (30 Sek)

```bash
python server.py
# Keine Errors? → Perfekt! 
# Errors? → Check .env
```

## 4️⃣ Claude Config (1 Min)

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "python",
      "args": ["/ABSOLUTER/PFAD/n8n-workflow-builder/server.py"],
      "env": {
        "N8N_API_URL": "https://n8n.schimmi-n8n.de",
        "N8N_API_KEY": "DEIN_KEY_HIER"
      }
    }
  }
}
```

**WICHTIG**: Absoluter Pfad! Nutze `pwd` im Terminal.

## 5️⃣ Ready! (30 Sek)

1. **Claude Desktop komplett beenden**
2. **Neu starten**
3. **Testen**:

```
Du: "Zeig mir alle meine n8n workflows"
```

## 🎉 Das war's!

### Erste Schritte:

**Node-Vorschläge:**
```
"Schlag mir Nodes vor für einen Workflow der täglich Sales-Daten aus Postgres holt und per Telegram verschickt"
```

**Workflow generieren:**
```
"Generiere mir einen Workflow-Template für ein API Endpoint das Daten validiert und speichert"
```

**Workflow analysieren:**
```
"Analysiere meinen Workflow 'Daily Report' auf Probleme"
```

**Node erklären:**
```
"Erkläre mir den HTTP Request Node mit Best Practices"
```

---

## 💥 Troubleshooting

### Claude findet den Server nicht
- Claude **komplett** beenden (auch Hintergrund-Prozesse!)
- Config-Datei auf **Syntax-Fehler** prüfen (gültiges JSON?)
- **Absoluter Pfad** verwenden, nicht relativ!
- Claude neu starten

### Authentication Error
- API Key **nochmal neu** generieren in n8n
- Keine **Leerzeichen** im Key
- `.env` Datei korrekt formatiert?

### Server crashed
```bash
# Logs anschauen
python server.py

# Dependencies neu installieren  
pip install -r requirements.txt --force-reinstall
```

---

**Happy n8n Building! 🚀**
