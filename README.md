# Smart Recycle Bot

## Executive Summary
Smart Recycle Bot ist ein kleines KI-Projekt, das dabei hilft, Müll richtig zu trennen.
Die Anwendung nimmt eine kurze Beschreibung eines Gegenstands entgegen,
Ordnet ihn einer passenden Entsorgungskategorie zu.
Im Hintergrund arbeitet eine Vektor-Datenbank (Qdrant), die über semantische Ähnlichkeit passende Beispiele findet.
Statt einfach irgendetwas zu raten, gibt das System bewusst „unknown“ zurück, wenn es sich nicht sicher genug ist.
Dieses Verhalten ist gewollt und soll falsche Antworten vermeiden.
Die gesamte Anwendung ist containerisiert und kann lokal mit Docker Compose gestartet werden.
Zusätzlich gibt es Kubernetes-Manifeste für den Einsatz in einem Cluster.
Das Projekt dient als realistischer Proof of Concept für KI im Umweltkontext.

## Ziele des Projekts
Das Projekt soll Menschen dabei unterstützen, Müll im Alltag besser zu trennen.
Viele sind unsicher, ob etwas in Restmüll, Papier oder Glas gehört, was oft zu Fehlwürfen führt.
Solche Fehler verschlechtern die Qualität von Recyclingprozessen.
Die Idee ist zu zeigen, dass auch kleine KI-Systeme hier sinnvoll helfen können.
Gleichzeitig erfüllt das Projekt die technischen Anforderungen aus dem Kurs (KI, Docker, Kubernetes).
Ein weiteres Ziel war es, eine einfache, aber saubere Microservice-Architektur umzusetzen.
Dabei wird klar zwischen Klassifikationslogik und API getrennt.
Am Ende steht eine Lösung, die sowohl lokal als auch im Cluster gleich funktioniert.

## Anwendung und Nutzung
Die Anwendung richtet sich vor allem an Studierende, Lernende und technisch Interessierte.
Sie kann ohne grafische Oberfläche direkt über API-Endpunkte genutzt werden.
Man schickt zum Beispiel einen Text wie „leere Glasflasche mit Etikett“ an die API.
Als Antwort erhält man eine Kategorie, einen Entsorgungshinweis und einen Confidence-Wert.
Falls die Unsicherheit zu hoch ist, gibt das System bewusst „unknown“ zurück.
Das macht die Nutzung transparent und nachvollziehbar.
Der Code ist hier verfügbar: https://github.com/MehmetTanit
Der Pitch ist hier zu finden: 


## Entwicklungsstand
Der aktuelle Stand ist ein funktionierender Prototyp mit klarer PoC-Reife.
Die wichtigste Funktion, also die Klassifikation von Müllgegenständen, ist umgesetzt.
Die Anwendung lässt sich lokal starten und direkt ausprobieren.
Dabei werden bewusst Dummy-Daten genutzt, wie es in der Aufgabe vorgesehen ist.
Die Qdrant-Datenbank wird automatisch befüllt, wenn sie noch leer ist.
So funktioniert das System direkt nach dem ersten Setup ohne zusätzliche Schritte.
Docker Compose für lokal und Kubernetes für den Cluster sind bereits vorhanden.
Damit läuft die Anwendung in beiden Umgebungen gleich und reproduzierbar.
Für den produktiven Einsatz fehlen aktuell noch echte Daten und Monitoring.

## Projektdetails
Das System besteht aus zwei Microservices mit klar getrennten Aufgaben.
Der Service „recycle-ai“ kümmert sich um Embeddings und die Kommunikation mit Qdrant.
Der Service „recycle-api“ stellt die REST-Endpunkte bereit.
Qdrant dient als Vektor-Datenbank und speichert die Beispiel-Daten.
Die Klassifikation basiert auf dem ähnlichsten Treffer und dessen Score.
Zusätzlich gibt es eine Schwelle, unter der keine sichere Aussage getroffen wird.
Eine Auto-Seeding-Funktion sorgt für initiale Daten beim ersten Start.
Alle wichtigen Parameter können über Environment-Variablen angepasst werden.

## Innovation
Die Besonderheit liegt in der Kombination aus Umweltanwendung und kontrollierter KI-Logik.
Anstatt freie Texte zu generieren, nutzt das System gezielt semantische Suche.
Dadurch bleiben die Antworten näher an den vorhandenen Daten.
Das reduziert typische Probleme wie Halluzinationen.
Ein wichtiger Punkt ist der bewusste Umgang mit Unsicherheit.
Wenn das System sich nicht sicher ist, sagt es das auch klar.
Gerade in Lernkontexten ist das sehr hilfreich.

## Wirkung (Impact)
Das Projekt kann helfen, typische Fehler bei der Mülltrennung zu reduzieren.
Nutzer:innen bekommen schnell eine Orientierung für Alltagsgegenstände.
Das ist besonders praktisch, ohne lange Regeln nachlesen zu müssen.
Auch im Bildungsbereich lässt sich das System gut einsetzen.
Da nur Dummy-Daten verwendet werden, entstehen keine Datenschutzprobleme.
Das macht den Einstieg unkompliziert und sicher.
Langfristig könnte das System mit lokalen Regeln erweitert werden.
So trägt es zu besserem Recycling und mehr Umweltbewusstsein bei.

## Technische Exzellenz
Das Backend basiert auf Python und FastAPI.
Für die Embeddings wird die OpenAI API verwendet.
Als Modell kommt „text-embedding-3-small“ mit 1536 Dimensionen zum Einsatz.
Qdrant dient als Vektor-Datenbank mit Cosine-Distanz.
Die gesamte Anwendung ist über Docker containerisiert.
Für den Clusterbetrieb werden Kubernetes-Ressourcen genutzt.
Konfigurationen laufen über ConfigMaps und Secrets.
Die API enthält zusätzlich Logik für unsichere Fälle und Fehlerbehandlung.

## Ethik, Transparenz und Inklusion
Das System legt Wert auf transparente Entscheidungen.
Jede Antwort enthält neben der Kategorie auch einen Confidence-Wert.
Bei Unsicherheit wird bewusst keine eindeutige Empfehlung gegeben.
So werden falsche Informationen vermieden.
Es werden keine personenbezogenen Daten verarbeitet.
Die Datengrundlage ist offen und nachvollziehbar.
Die API ist bewusst einfach gehalten, um leicht zugänglich zu sein.
Zukünftig kann sie um Mehrsprachigkeit erweitert werden.

## Zukunftsvision
In den nächsten Jahren könnte das System weiter ausgebaut werden.
Eine Integration in kommunale Anwendungen wäre denkbar.
Dabei könnten lokale Recyclingregeln berücksichtigt werden.
Mit größeren Datensätzen würde die Genauigkeit steigen.
Auch eine Bilderkennung für Müllgegenstände wäre möglich.
Zusätzliche Rückfragen könnten die Klassifikation verbessern.
Technisch wären Monitoring und bessere Sicherheitsmechanismen sinnvoll.
Langfristig könnte daraus ein zuverlässiger Alltagsassistent werden.

## Technische Nachweise 

### 1) Docker Compose
```bash
docker compose up -d
docker compose ps
```

### 2) API-Test lokal
```bash
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/classify \
	-H "Content-Type: application/json" \
	-d '{"item":"Leere Glasflasche mit Etikett"}'
```

### 3) Kubernetes anwenden
```bash
kubectl apply -f k8s/secret-openai.yaml
kubectl apply -f k8s/configmap-recycle-chat.yaml
kubectl apply -f k8s/deployment-qdrant.yaml
kubectl apply -f k8s/service-qdrant.yaml
kubectl apply -f k8s/deployment-recycle-chat.yaml
kubectl apply -f k8s/deployment-recycle-api.yaml
kubectl apply -f k8s/service-recycle-api.yaml
kubectl apply -f k8s/service-recycle-chat.yaml
kubectl get pods,svc,deploy
```

### 4) Port-Forward und API im Cluster testen
```bash
kubectl port-forward svc/recycle-api 18080:8080
curl -s http://localhost:18080/health
curl -s -X POST http://localhost:18080/classify \
	-H "Content-Type: application/json" \
	-d '{"item":"Alte AA Batterie"}'
```
