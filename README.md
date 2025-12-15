# 🚀 n8n Workflow Builder MCP Server

Ein **mega-geiler** MCP Server für n8n, der dir hilft, Workflows zu bauen, zu optimieren und zu debuggen - direkt aus Claude heraus! 🎯

## 🌟 Features

### 🧠 AI-Powered Workflow Design
- **Smart Node Suggestions**: Beschreib einfach, was du bauen willst, und der Server schlägt die perfekten Nodes vor
- **Template Generator**: Generiert komplette Workflow-Strukturen aus natürlicher Sprache
- **Best Practices**: Kennt die n8n Best Practices und warnt dich vor typischen Fehlern

### 🔍 Workflow Analysis & Debugging
- **Workflow Analyzer**: Scannt deine Workflows nach Problemen und Optimierungspotential
- **Error Debugger**: Hilft dir, Workflow-Fehler zu verstehen und zu fixen
- **Security Checker**: Findet hardcoded Credentials und andere Sicherheitsprobleme

### 📊 Workflow Management
- **List & Filter**: Overview of all workflows with status and info
- **Details View**: Detailed information about each workflow
- **Execution Tracking**: View past executions with status and errors
- **Workflow Editing**: Edit workflows - change names, modify nodes, adjust settings
  - ⚠️ Note: `active` and `tags` fields are read-only and can only be changed in the n8n UI

### ⚡ Workflow Execution & Monitoring
- **Manual Trigger**: Start workflows directly from Claude (only for workflows with Manual/Webhook triggers)
- **Custom Input Data**: Pass dynamic data to your workflows
- **Execution Details**: Retrieve complete node input/output data for each execution
- **Execution History**: List of all past executions with status

### 📚 Knowledge Base
- **Node Encyclopedia**: Detaillierte Erklärungen zu allen wichtigen n8n Nodes
- **Use Cases & Examples**: Praktische Beispiele für jeden Node-Typ
- **Configuration Tips**: Wie man jeden Node optimal konfiguriert

## 🎯 Use Cases

### 1. Workflow-Idee zu fertiger Struktur
```
Du: "Ich brauche einen Workflow, der täglich um 9 Uhr Daten aus unserer Postgres-DB holt, 
     Metriken berechnet und dann einen Report per Slack verschickt"

Claude + MCP: Generiert komplette Workflow-Struktur mit:
- Schedule Trigger (täglich 9 Uhr)
- Postgres Node (mit Query-Beispiel)
- Function Node (Metrik-Berechnung)
- Set Node (Report-Formatierung)
- Slack Node (mit Best Practices)
```

### 2. Workflow-Debugging
```
Du: "Mein Workflow wirft 'timeout exceeded' Fehler"

Claude + MCP: Analysiert und schlägt vor:
- Timeout-Settings erhöhen
- Retry-Logic hinzufügen
- Daten in Batches verarbeiten
- Externe Service-Performance prüfen
```

### 3. Workflow-Optimierung
```
Du: "Analysiere meinen Workflow 'Daily Report Generator'"

Claude + MCP: Findet:
- 3 hardcoded API Keys (Security Issue!)
- Workflow könnte in 2 Sub-Workflows aufgeteilt werden
- Error Handling fehlt
- Node "HTTP Request" sollte umbenannt werden
```

## 📦 Installation

### 1. Dependencies installieren
```bash
cd n8n-workflow-builder
pip install -r requirements.txt
```

### 2. Konfiguration
```bash
# .env Datei erstellen
cp .env.example .env

# n8n API Key holen:
# 1. Geh zu deiner n8n Instanz: https://your-n8n-instance.com
# 2. Settings > API
# 3. "Create New API Key"
# 4. Key kopieren und in .env einfügen
```

**Deine .env sollte so aussehen:**
```env
N8N_API_URL=https://your-n8n-instance.com
N8N_API_KEY=n8n_api_abc123xyz...
```

### 3. Server testen
```bash
# Quick Test
python server.py
# Sollte keine Errors werfen - wenn ja, check deine .env!
```

### 4. Claude Desktop Integration

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

#### Option 1: With Virtual Environment (Recommended)
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "/ABSOLUTE/PATH/TO/n8n-workflow-builder/.venv/bin/python",
      "args": ["-m", "n8n_workflow_builder"],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Option 2: With Global Python
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "python",
      "args": [
        "-m", "n8n_workflow_builder"
      ],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_api_key_here",
        "PYTHONPATH": "/ABSOLUTE/PATH/TO/n8n-workflow-builder/src"
      }
    }
  }
}
```

#### Option 3: Direct with server.py (Legacy)
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "python",
      "args": [
        "/ABSOLUTE/PATH/TO/n8n-workflow-builder/src/n8n_workflow_builder/server.py"
      ],
      "env": {
        "N8N_API_URL": "https://your-n8n-instance.com",
        "N8N_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Option 4: With .env File (Most Secure)
```json
{
  "mcpServers": {
    "n8n-workflow-builder": {
      "command": "/ABSOLUTE/PATH/TO/n8n-workflow-builder/.venv/bin/python",
      "args": ["-m", "n8n_workflow_builder"],
      "cwd": "/ABSOLUTE/PATH/TO/n8n-workflow-builder"
    }
  }
}
```
With this option, credentials are read from the `.env` file.

**IMPORTANT**:
- Replace `/ABSOLUTE/PATH/TO/` with your actual path!
- Windows users: Use `\\` or `/` as path separator
- Windows Python path: `.venv\Scripts\python.exe` instead of `.venv/bin/python`

### 5. Claude Desktop neu starten
Komplett beenden und neu öffnen - dann sollte der MCP Server verfügbar sein! 🎉

## 🎮 Usage Examples

### Node-Vorschläge bekommen
```
Du: "Schlag mir Nodes vor für: API Endpoint der Daten validiert und in eine Datenbank schreibt"

Claude nutzt: suggest_workflow_nodes
→ Bekommst Vorschläge für Webhook, IF, HTTP Request, Postgres, etc.
```

### Kompletten Workflow generieren
```
Du: "Generiere mir einen Workflow für tägliche Sales Reports aus Postgres nach Slack"

Claude nutzt: generate_workflow_template
→ Bekommst komplette Struktur mit allen Nodes, Connections und Config-Tips
```

### Workflow analysieren
```
Du: "Analysiere meinen Workflow mit ID abc-123"

Claude nutzt: analyze_workflow
→ Findet Issues, Security-Probleme, gibt Optimierungs-Vorschläge
```

### Node-Details erkunden
```
Du: "Erkläre mir den HTTP Request Node"

Claude nutzt: explain_node
→ Bekommst detaillierte Erklärung, Use Cases, Best Practices, Beispiele
```

### Fehler debuggen
```
Du: "Mein Workflow wirft: Error 401 Unauthorized"

Claude nutzt: debug_workflow_error
→ Bekommst Troubleshooting-Steps, wahrscheinliche Ursachen, Lösungen
```

### Workflows auflisten
```
Du: "Zeig mir alle aktiven Workflows"

Claude nutzt: list_workflows
→ Liste aller Workflows mit Status, Node-Count, Update-Datum
```

### Workflow ausführen
```
Du: "Führe Workflow 'Test API' mit Input {userId: 123} aus"

Claude nutzt: execute_workflow
→ Workflow wird getriggert, du siehst Execution-Status
```

### Edit Workflow
```
You: "Rename workflow abc-123 to 'Production Data Sync'"

Claude uses: update_workflow
→ Workflow is renamed
```

### Get Execution Details
```
You: "Show me details for execution 47885"

Claude uses: get_execution_details
→ Shows complete node input/output data, errors, status, etc.
```

**Important:** To see execution data, the following options must be enabled in n8n Settings > Executions:
- ✅ Save manual executions
- ✅ Save execution progress

## 🧠 Knowledge Base

Der Server kennt diese Node-Kategorien:

### Triggers
- **Webhook**: API Endpoints, externe Integrations
- **Schedule**: Cron-Jobs, periodische Tasks
- **Manual**: Testing, manuelle Interventions

### Logic Nodes
- **IF**: Conditional branching
- **Switch**: Multi-way branching
- **Merge**: Combine data streams
- **Code**: Custom JavaScript/Python

### Data Operations
- **HTTP Request**: API calls
- **Set**: Data transformation
- **Function**: Complex data processing

### Storage
- **Postgres**: Relationale Datenbank
- **Redis**: Caching, Session Storage

### Integrations
- **Slack**: Messaging & Notifications
- **Telegram**: Bot Integration
- **Gmail**: Email Automation

## 🛠️ Advanced Features

### Custom Templates
Der Server kommt mit vordefinierten Templates:
- `api_endpoint`: Simple REST API
- `scheduled_report`: Daily/Hourly Reports
- `data_sync`: Database Synchronization

### Security Checks
- Findet hardcoded Credentials
- Warnt vor fehlender Authentifizierung
- Checkt auf unsichere Patterns

### Performance Analysis
- Workflow-Komplexität berechnen
- Zu große Workflows erkennen
- Split-Vorschläge für bessere Wartbarkeit

## 🐛 Troubleshooting

### Server startet nicht
```bash
# Check Python Version (sollte 3.8+)
python --version

# Dependencies neu installieren
pip install -r requirements.txt --force-reinstall

# .env überprüfen
cat .env
# Sollte N8N_API_URL und N8N_API_KEY enthalten
```

### "Authentication failed"
- Check ob dein API Key korrekt ist
- Geh zu n8n Settings > API und erstelle einen neuen Key
- Stelle sicher, dass keine Leerzeichen im Key sind

### "Connection refused"
- Ist deine n8n Instanz erreichbar?
- Check: `curl https://your-n8n-instance.com/healthz`
- Firewall/VPN könnte blockieren

### Claude Desktop erkennt Server nicht
1. Claude komplett beenden (auch im Hintergrund!)
2. Config-Datei überprüfen (gültiges JSON?)
3. Pfade absolut (nicht relativ!)
4. Claude neu starten
5. Schaue in Claude: Settings > Developer > MCP Servers

## 💡 Pro Tips

### 1. Workflow-Naming
- Benenn Nodes **immer** um! "HTTP Request 1" ist schlecht, "Fetch User Data" ist gut
- Nutze Präfixe für Kategorien: "[API] Get Users", "[DB] Insert Record"

### 2. Error Handling
- **Immer** Error Handling einbauen bei kritischen Workflows
- Nutze "Error Trigger" Node für globales Error Handling
- Logge Errors in Slack/Telegram für Monitoring

### 3. Testing
- Entwickle immer mit "Manual Trigger" statt direktem Webhook
- Nutze "Pinned Data" für konsistente Tests
- Split production/development workflows

### 4. Performance
- Batche API Calls wo möglich
- Nutze Redis für Caching
- Vermeide zu viele sequentielle HTTP Requests

### 5. Security
- **NIE** API Keys hardcoden - immer Credentials verwenden
- Webhook Authentication aktivieren
- Sensitive Daten nur verschlüsselt speichern

## 🔄 Updates & Erweiterungen

### Eigene Nodes zur Knowledge Base hinzufügen
Edit `server.py` und erweitere `NODE_KNOWLEDGE`:

```python
NODE_KNOWLEDGE["integrations"]["notion"] = {
    "name": "Notion",
    "desc": "Notion database integration",
    "use_cases": ["Knowledge base", "Project management"],
    "best_practices": ["Use database IDs", "Batch updates"]
}
```

### Eigene Templates erstellen
Edit `WORKFLOW_TEMPLATES` in `server.py`:

```python
WORKFLOW_TEMPLATES["my_template"] = {
    "name": "My Custom Template",
    "nodes": [...],
    "connections": "custom"
}
```

## 📊 API Reference

Der Server nutzt die offizielle n8n REST API:
- Basis-URL: `https://your-n8n-instance.com/api/v1`
- Docs: https://docs.n8n.io/api/

Genutzte Endpoints:
- `GET /workflows` - List workflows
- `GET /workflows/{id}` - Get workflow details
- `POST /workflows` - Create workflow
- `PATCH /workflows/{id}` - Update workflow
- `POST /workflows/{id}/execute` - Execute workflow
- `GET /executions` - Get execution history

## 🤝 Contributing

Ideen? Issues? PRs welcome! 🎉

## 📝 License

MIT - Do whatever you want! 

## 🙏 Credits

- Built for awesome n8n automation 🚀
- Powered by Claude MCP ⚡
- Made with ❤️ for DevOps Engineers

---

**Happy Automating!** 🎊

Bei Fragen oder Problemen: Einfach Claude fragen! 😉
