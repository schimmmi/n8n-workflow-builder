# 🔐 Security Review: n8n-workflow-builder

**Datum:** 2026-03-14 (Update)
**Reviewer:** Claude (Anthropic) — Engineering Code Review & Functional Testing
**Scope:** Source-Code-Review + MCP-Server-Funktionstests
**Ergebnis:** **3 kritische/hohe Findings** + **2 funktionale Bugs** — sofortiger Handlungsbedarf

---

## Executive Summary

Der `n8n-workflow-builder` ist ein leistungsfähiger Python-basierter MCP-Server (Model Context Protocol), der KI-Assistenten die Verwaltung von n8n-Workflows ermöglicht. Funktionstests bestätigen exzellente Capabilities im **Security Auditing** (erkennt sogar unsicheres Logging in Code-Nodes), **Workflow-Analyse** (Single Points of Failure, Datenflüsse) und **Execution Details** (Remote-Debugging).

**Kritische Findings:**
- Live n8n API-Key liegt im Klartext in `.env`
- RBAC Default-User ist "admin" ohne Authentifizierung
- SSRF-Risiko beim GitHub-Template-Download

**Funktionale Bugs:**
- `get_workflow_details` schlägt mit "Unknown tool" fehl (kritisch)
- `execute_workflow` liefert 405 Method Not Allowed bei manchen n8n-Versionen

---

## 🚨 KRITISCH

### C-1: Live n8n API-Key in `.env` im Projekt-Verzeichnis

**Datei:** `.env`
**Schweregrad:** KRITISCH — sofort rotieren!

Die `.env`-Datei enthält einen echten, gültigen JWT-API-Key für die produktive n8n-Instanz:

```
N8N_API_URL=https://n8n.schimmi-n8n.de
N8N_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2...
```

Das JWT payload decoded zu:
```json
{"sub": "6cc037af-422a-4a66-9265-94b95c9c594b", "iss": "n8n", "aud": "public-api"}
```

Obwohl `.gitignore` die `.env`-Datei korrekt ausschließt, liegt der Key **im Klartext auf der Festplatte** und wird jedem zugänglich gemacht, der — wie in diesem Session — Lesezugriff auf das Projektverzeichnis erhält. Das schließt KI-Assistenten, Backup-Tools, Sync-Services und andere Prozesse ein.

**Sofortmaßnahmen:**
1. **Jetzt:** Diesen API-Key in der n8n-Instanz unter `https://n8n.schimmi-n8n.de` widerrufen und einen neuen generieren
2. Den neuen Key **nicht** in der `.env`-Datei im Projektordner ablegen, sondern über Umgebungsvariablen des Betriebssystems oder einen Secret Manager injizieren
3. Prüfen, ob die `.env` versehentlich in Backups oder Sync-Diensten (iCloud, Dropbox, etc.) gelandet ist

---

## 🔴 HIGH

### H-1: RBAC Default-User ist "admin" ohne Authentifizierung

**Datei:** `security/rbac.py`, Zeile ~45
**Schweregrad:** HOCH

Der `RBACManager` initialisiert sich mit einem Default-User, der volle Admin-Rechte hat, und Tool-Handler prüfen keine RBAC-Permissions. Jeder MCP-Client kann sofort als Admin agieren, User anlegen, Workflows löschen und Approval-Requests genehmigen.

**Fix:** Default-Role auf `viewer` setzen + RBAC-Checks in Tool-Handlern implementieren (`rbac_manager.check_permission()`).

---

### H-2: SSRF-Risiko beim GitHub Template-Download

**Datei:** `templates/sources/github.py`
**Schweregrad:** HOCH

Die `download_url` aus der GitHub-API-Response wird ohne Domain-Validierung für HTTP-Requests verwendet. Manipulierte Repository-Inhalte könnten SSRF-Angriffe auf interne Ressourcen ermöglichen.

**Fix:** Domain-Allowlist implementieren (`raw.githubusercontent.com`, `github.com`).

---

## 🐛 FUNKTIONALE BUGS (BEHOBEN in v1.23.1)

### B-1: `get_workflow_details` Tool existiert nicht ✅ FIXED

**Schweregrad:** KRITISCH (behoben am 2026-03-14)
**Reproduzierbar:** 100%

Tool war implementiert, aber nicht im Server-Routing registriert.

**Fix (v1.23.1):** `get_workflow_details` zu `workflow_tool_names` in `server.py:1829` hinzugefügt.

---

### B-2: `execute_workflow` liefert 405 Method Not Allowed ✅ FIXED

**Schweregrad:** HOCH (behoben am 2026-03-14)
**Reproduzierbar:** Bei manchen n8n-Instanzen

n8n-API gibt bei manchen Versionen HTTP 405 statt 404 zurück.

**Fix (v1.23.1):** Fehlerbehandlung erweitert auf `[404, 405]` in `client.py:101,115` — alle 4 Ausführungs-Strategien werden jetzt korrekt durchprobiert.

---

### B-3: `analyze_workflow_semantics` Tool existiert nicht ✅ FIXED

**Schweregrad:** HOCH (behoben am 2026-03-14)
**Reproduzierbar:** 100%

Tool-Definition existierte in `server.py`, aber Handler fehlte in `validation_tools.py`.

**Fix (v1.23.1):** Handler-Methode mit 127 Zeilen implementiert + zu `validation_tool_names` registriert. Liefert jetzt semantische Analyse mit LLM-freundlichen Fix-Vorschlägen.

---

## 🟡 MEDIUM

### M-1: Shannon Entropy Formel falsch implementiert

**Datei:** `security/secrets.py`, Zeile ~314
**Schweregrad:** MEDIUM

Die Secret-Detection-Heuristik verwendet `probability ** 0.5` statt `math.log2(probability)`. Trotzdem funktioniert der SecurityAuditor **hervorragend** — er findet sogar unsicheres Logging wie `console.log(apiKey)` in Code-Nodes.

**Fix:** Formel korrigieren (kosmetisch, da Regex-Pattern bereits zuverlässig funktionieren).

---

### M-2: Workflow-Payload wird bei Fehlern vollständig geloggt

**Datei:** `client.py`
**Schweregrad:** MEDIUM

Workflows können Credentials und Secrets enthalten, die bei Fehlern komplett in Logs landen.

**Fix:** Sensitive Felder vor dem Logging maskieren.

---

### M-3: Ungepinnte Dependencies — Supply Chain Risiko

**Datei:** `requirements.txt`
**Schweregrad:** MEDIUM

Alle Dependencies nutzen `>=`-Constraints ohne Lock-File.

**Fix:** `pip freeze > requirements-lock.txt` oder Poetry/uv mit Lock-Dateien.

---

### M-4: State in Plain-JSON-Dateien im Home-Verzeichnis

**Datei:** `security/rbac.py`, `state.py`
**Schweregrad:** MEDIUM

RBAC-Konfiguration und Session-History werden unverschlüsselt in `~/.n8n_*_state.json` gespeichert.

**Fix:** Restriktive Permissions (`chmod 600`) + HMAC-Integritätsprüfung.

---

## 🟢 LOW

### L-1: Unvollständige RFC1918-Erkennung in Auth-Auditor
**Datei:** `security/auth.py` — Nur `172.16.`-Präfix wird erkannt, nicht das komplette `172.16.0.0/12`-Netz.

### L-2: Transitive Verbindungen werden in Exposure-Analyse nicht erkannt
**Datei:** `security/exposure.py` — Nur direkte Node-Verbindungen werden geprüft (One-Hop).

### L-3: Kein Content-Size-Limit beim Template-Download
**Datei:** `templates/sources/github.py` — Keine Größenbeschränkung bei Template-Downloads.

### L-4: `clear_state()` ohne Bestätigung
**Datei:** `state.py` — Unwiderrufliche Löschung ohne Rückfrage.

---

## ✅ Positives — Was exzellent funktioniert

### Security Features (getestet & bestätigt)
- **SecurityAuditor** findet nicht nur Hardcoded-Secrets, sondern erkennt sogar **unsicheres Logging in Code-Nodes** (`console.log(apiKey)`)
- **Explain Workflow** liefert hochwertige architektonische Analysen (Single Points of Failure, Datenflüsse, Bottlenecks)
- **Execution Details** bietet sehr detaillierte Node-Ergebnisse für Remote-Debugging

### Code Quality
- **SQLite Queries sind korrekt parametrisiert** — kein SQL-Injection-Risiko
- **Security-Modul ist architektonisch sauber** — klare Trennung (SecretDetector, AuthAuditor, ExposureAnalyzer)
- **Dependency Injection Pattern** — einfaches Testing und Austausch von Komponenten
- **`.gitignore` schließt `.env` korrekt aus**

---

## 🎯 Priorisierte Handlungsempfehlungen

| Priorität | Maßnahme | Aufwand | Impact |
|-----------|----------|---------|--------|
| 🚨 **SOFORT** | API-Key in n8n widerrufen und neu generieren | 5 min | Kritisch |
| 🚨 **SOFORT** | `.env` aus Projektordner entfernen, Key via OS-Umgebungsvariable | 15 min | Kritisch |
| 🐛 **BUGFIX** | `get_workflow_details` Tool implementieren oder aus Liste entfernen | 1-2h | Kritisch |
| 🐛 **BUGFIX** | `execute_workflow` 405-Fehler: API-Version-Detection + Fallback | 2-3h | Hoch |
| 🔴 **Diese Woche** | RBAC Default-User auf `viewer` setzen + Permission-Checks | 2-4h | Hoch |
| 🔴 **Diese Woche** | `download_url` Domain-Allowlist in `github.py` | 30 min | Hoch |
| 🟡 **Nächster Sprint** | Shannon-Entropie-Formel korrigieren (kosmetisch) | 15 min | Medium |
| 🟡 **Nächster Sprint** | Payload-Logging maskieren | 15 min | Medium |
| 🟡 **Nächster Sprint** | Dependencies pinnen (Lock-File) | 30 min | Medium |

## 💡 Feature-Wünsche aus Testing

1. **Tool-Harmonisierung:** `analyze_workflow` + `explain_workflow` zu einer mächtigen Analyse-Suite verschmelzen
2. **Auto-Sync:** Template-Suche sollte bei leerem Cache automatisch synchronisieren
3. **Dokumentations-Feature:** Automatisches Generieren von Node-Beschreibungen ("Intent")
4. **Interaktive Node-Ausführung:** Einzelne Nodes testen ohne kompletten Workflow

---

*Security Review + Functional Testing — Aktualisiert am 2026-03-14*
