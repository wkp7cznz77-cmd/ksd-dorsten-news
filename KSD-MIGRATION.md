# KSD iSiNAGE – unabhängiger Betrieb (Testfassung)

Diese Änderungen sind vorerst nur ein Vorschlag auf einem eigenen Branch. Die aktuell in iSiNAGE eingetragene ChatGPT-Site wird nicht verändert.

## Newsticker
- Der GitHub-Actions-Workflow `.github/workflows/update-news.yml` soll auf dem Standardbranch alle 30 Minuten `scripts/update_news.py` starten und `news.json` aktualisieren.
- Die Webseite `index.html` lädt `news.json` und aktuelle Open-Meteo-Wetterdaten.
- Die Hochformat-Version `tall/index.html` nutzt jetzt ebenfalls diese aktuellen Daten, statt fest hinterlegte September-Nachrichten und Wetterangaben.
- Bei unveränderten Texten wird die Laufschrift nicht unnötig zurückgesetzt.
- Bleibt `news.json` länger als 36 Stunden ohne Aktualisierung, zeigt die Webseite einen Hinweis statt vermeintlich aktueller Nachrichten.

## Noch zu prüfen
1. GitHub Actions muss für das Repository aktiviert sein und Schreibrechte für Workflow-Commits besitzen. Geplante Läufe können sich verzögern.
2. GitHub Pages muss im Repository eingerichtet sein. Die öffentliche Pages-URL ist erst nach erfolgreicher Bereitstellung zu verwenden.
3. Darstellung, Schriftgrößen, Laufgeschwindigkeit und Verhalten auf dem echten iiyama/iSiNAGE testen.
4. Das lokale RSS-Skript kann bei Quellenproblemen ältere lokale Schlagzeilen aus der vorherigen Datei übernehmen. Diese Fallback-Logik sollte vor dem Produktivwechsel überarbeitet werden.
5. Bestehende ChatGPT-Sites sind mit dieser GitHub-Version **nicht** automatisch 1:1 identisch. Ohne Zugriff auf die Original-Quellprojekte ist ein vollständiger Abgleich nicht möglich.

## Weitere KSD-Projekte
Die ChatGPT-Sites `ksd-unfallmeldungen.headhunter2422.chatgpt.site` und die Arbeitsschutz-Fragenanzeige sind noch **nicht migriert**. Für eine verlässliche unabhängige Version werden ihre ursprünglichen Dateien/Quellprojekte und die jeweils eingebundenen iSiNAGE-URLs benötigt. Die Recherche, PDF-Erstellung und Aktualisierung der Unfallmeldungen ist eine eigene Automatisierung und wird nicht durch den News-Workflow ersetzt.

**Keinen iSiNAGE-Link umstellen, bevor eine vollständige Testfreigabe vorliegt.**
