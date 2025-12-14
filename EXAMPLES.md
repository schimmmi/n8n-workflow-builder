# 📖 n8n Workflow Builder - Beispiele & Use Cases

Konkrete Beispiele, wie du den MCP Server nutzen kannst! 🎯

## 🎬 Scenario 1: API Endpoint erstellen

### Was du willst:
REST API Endpoint der User-Daten validiert und in Postgres speichert

### Wie du's machst:

**Du fragst Claude:**
```
"Ich brauche einen n8n Workflow für ein API Endpoint. 
Der Endpoint soll:
- POST Requests empfangen
- User-Daten validieren (name, email, age)
- In Postgres speichern
- Success/Error Response zurückgeben"
```

**Claude nutzt:** `suggest_workflow_nodes` + `generate_workflow_template`

**Du bekommst:**
```markdown
# Workflow: User Registration API

## Suggested Structure:

1. **Webhook**
   - Empfängt POST Requests
   - Path: /api/users/register
   - Authentication: Header Auth empfohlen

2. **IF Node**
   - Validierung: email vorhanden?
   - Validierung: age > 18?
   - True → weiter, False → Error Response

3. **Set Node**
   - Formatiere Daten für DB
   - Füge timestamp hinzu
   - Sanitize inputs

4. **Postgres Node**
   - INSERT INTO users
   - Handle duplicates

5. **Respond to Webhook**
   - Success: 201 Created
   - Error: 400 Bad Request

## Best Practices:
- Webhook Authentication aktivieren!
- Input Sanitization gegen SQL Injection
- Use prepared statements
- Return proper HTTP Status Codes
```

---

## 🎬 Scenario 2: Täglicher Report

### Was du willst:
Jeden Tag um 9 Uhr Sales-Metriken aus DB holen und per Slack verschicken

### Wie du's machst:

**Du fragst Claude:**
```
"Erstelle mir einen Workflow der täglich um 9 Uhr morgens:
- Sales-Daten aus Postgres holt (letzten 24h)
- Metriken berechnet (total revenue, orders, avg order value)
- Als schönen Report formatiert
- Per Slack an #sales-team schickt"
```

**Claude nutzt:** `generate_workflow_template` (Type: `scheduled_report`)

**Du bekommst:**
```markdown
# Workflow: Daily Sales Report

## Template: Daily Report Generator

1. Schedule Trigger (Daily at 9AM)
   - Cron: 0 9 * * *
   - Timezone: Europe/Berlin

2. Postgres (Fetch Data)
   - Query: SELECT * FROM orders 
           WHERE created_at > NOW() - INTERVAL '24 hours'
   - Return data as JSON

3. Function (Calculate Metrics)
   ```javascript
   const orders = $input.all();
   const total_revenue = orders.reduce((sum, o) => sum + o.amount, 0);
   const order_count = orders.length;
   const avg_value = total_revenue / order_count;
   
   return [{
     json: {
       revenue: total_revenue,
       orders: order_count,
       avg_order: avg_value
     }
   }];
   ```

4. Set (Format Report)
   - message: "📊 Daily Sales Report\n💰 Revenue: {{$json.revenue}}€\n..."

5. Slack (Send to Slack)
   - Channel: #sales-team
   - Message: {{$json.message}}

## Best Practices:
✅ Error Handling hinzufügen!
✅ Bei Fehlern Benachrichtigung an Admin
✅ Timezone beachten!
```

---

## 🎬 Scenario 3: Workflow debuggen

### Was du hast:
Workflow wirft Fehler "Error: getaddrinfo ENOTFOUND api.example.com"

### Wie du's löst:

**Du fragst Claude:**
```
"Mein Workflow wirft diesen Fehler:
'Error: getaddrinfo ENOTFOUND api.example.com'

Der HTTP Request Node kann die API nicht erreichen."
```

**Claude nutzt:** `debug_workflow_error`

**Du bekommst:**
```markdown
# Workflow Error Debug

## Probable Cause: DNS/Network Error

Der Fehler "getaddrinfo ENOTFOUND" bedeutet, dass der Hostname 
nicht aufgelöst werden kann.

**Mögliche Ursachen:**

1. **URL Typo**
   - Check: Ist "api.example.com" korrekt geschrieben?
   - Häufiger Fehler: https://api.example.com vs http://

2. **Network/Firewall**
   - Kann n8n auf externe APIs zugreifen?
   - Proxy-Config notwendig?
   - Firewall-Regel blockiert Traffic?

3. **DNS Problem**
   - Ist der Domain-Name gültig?
   - DNS Server erreichbar?

**Lösungsschritte:**

1. Test im Browser: Öffne https://api.example.com
2. Check URL im HTTP Request Node (Typos?)
3. Teste mit curl: `curl https://api.example.com`
4. Prüfe n8n Netzwerk-Settings
5. Bei self-hosted: Check Docker networking

**Quick Fix:**
- Nutze IP-Adresse statt Hostname (temporary)
- Check n8n Logs: Settings > Log Streaming
```

---

## 🎬 Scenario 4: Workflow optimieren

### Was du hast:
Bestehender Workflow der langsam ist und viele Nodes hat

### Wie du's verbesserst:

**Du fragst Claude:**
```
"Analysiere meinen Workflow 'Customer Onboarding' (ID: abc-123) 
und gib mir Optimierungsvorschläge"
```

**Claude nutzt:** `analyze_workflow`

**Du bekommst:**
```markdown
# Workflow Analysis: Customer Onboarding

**Complexity:** High
**Total Nodes:** 23

## ⚠️ Issues Found:

- Node 'HTTP Request 3' contains hardcoded API key
- Node 'Set 1' contains hardcoded password
- No error handling detected

## 💡 Suggestions:

- Consider splitting into sub-workflows (23 nodes is complex!)
- Rename default node names: HTTP Request, Set, IF
- Add Error Trigger node for better error handling
- Move credentials to n8n Credential Manager
- Consider batching HTTP requests

## 🚀 Optimization Plan:

1. **Security First:**
   - Move ALL credentials to Credential Manager
   - Never hardcode API keys/passwords

2. **Split Workflow:**
   - Main Flow: "Customer Onboarding - Main"
   - Sub-Workflow 1: "Send Welcome Email"
   - Sub-Workflow 2: "Setup User Account"
   - Sub-Workflow 3: "Notify Teams"

3. **Performance:**
   - Batch HTTP requests where possible
   - Use Redis for caching
   - Reduce sequential dependencies

4. **Maintainability:**
   - Rename all nodes meaningfully
   - Add notes/documentation
   - Use consistent naming scheme
```

---

## 🎬 Scenario 5: Node lernen

### Was du willst:
Verstehen wie man den Redis Node richtig nutzt

### Wie du's machst:

**Du fragst Claude:**
```
"Erkläre mir den Redis Node mit Use Cases und Best Practices"
```

**Claude nutzt:** `explain_node`

**Du bekommst:**
```markdown
# Redis Node

**Description:** Redis key-value store integration für Caching, 
Session Storage und Rate Limiting

## Use Cases:

- **Caching**: API Responses cachen für bessere Performance
- **Rate Limiting**: User Requests limitieren
- **Session Storage**: User Sessions speichern
- **Temporary Data**: Daten mit TTL speichern
- **Pub/Sub**: Message Queue für Event-basierte Workflows

## Best Practices:

✅ **Immer TTL setzen**
   - Verhindert Memory-Overflow
   - Automatisches Cleanup
   ```javascript
   key: "user:123"
   value: {...}
   ttl: 3600  // 1 hour
   ```

✅ **Richtige Data Types nutzen**
   - String: Simple values
   - Hash: Object data
   - Set: Unique lists
   - Sorted Set: Ranked data

✅ **Error Handling**
   - Redis-Connection kann fehlschlagen
   - Implement Fallback-Logic
   - Log Redis errors

✅ **Key Naming Convention**
   - Nutze Prefixes: "user:123", "cache:api:endpoint"
   - Hierarchisch: "app:feature:entity:id"
   - Konsistent bleiben!

## Example: API Response Caching

```javascript
// Check cache first
GET key: "cache:api:users:{{$json.userId}}"

// If miss → fetch from API → cache result
SET key: "cache:api:users:{{$json.userId}}"
    value: {{$json}}
    ttl: 600  // 10 minutes
```

## Common Pitfalls:

❌ Keine TTL → Memory voll
❌ Zu lange TTLs → Stale data
❌ Keine Connection Error Handling
❌ Keys ohne Structure → Chaos
```

---

## 🎯 Power Combos

### Combo 1: Workflow erstellen + analysieren
```
1. "Generiere Workflow für XYZ"
2. → Workflow in n8n bauen
3. "Analysiere Workflow ABC"
4. → Optimierungen umsetzen
```

### Combo 2: Node lernen + Template generieren
```
1. "Erkläre mir Postgres Node"
2. → Best Practices lernen
3. "Generiere Template mit Postgres + Slack"
4. → Optimalen Workflow bekommen
```

### Combo 3: Error → Debug → Fix
```
1. Workflow schlägt fehl
2. "Debug Error: [Error Message]"
3. → Lösung bekommen
4. → Fix implementieren
5. "Analysiere Workflow nochmal"
6. → Bestätigung dass fix funktioniert
```

---

## 💡 Pro Tips aus der Praxis

### Tipp 1: Iteratives Design
```
Start: "Schlag Nodes vor für: Daily Report"
→ Outline bekommen
→ Details verfeinern: "Erkläre Postgres Node"
→ Template generieren: "Erstelle kompletten Workflow"
→ Nach Bau analysieren: "Analysiere Workflow"
```

### Tipp 2: Template als Basis
```
Nutze Templates als Startpunkt:
"Generiere scheduled_report Template für Sales Metrics"
→ Anpassen an deine Needs
→ Erweitern mit eigener Logic
```

### Tipp 3: Security Check before Production
```
Vor Deployment IMMER:
"Analysiere Workflow XYZ auf Security-Issues"
→ Hardcoded Credentials fixen
→ Authentication hinzufügen
→ Input Validation checken
```

---

**Happy Building! 🚀**

Weitere Fragen? Einfach Claude fragen! 😉
