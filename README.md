# Angerer Consulting

Statische Website für Bettina Angerer (Angerer Consulting, Bayreuth).

## Aufbau

- `build.py` erzeugt alle HTML-Seiten, `sitemap.xml` und `robots.txt`. Inhalte und Texte stehen in diesem Skript.
- `partials/` enthält wiederkehrende Teile (Symbole, Anfragefenster).
- `content/legal/` enthält die Rechtstexte der bisherigen Website als Quelle.
- `assets/` enthält Styles, Skript, Schriften und Bilder.

Nach jeder inhaltlichen Änderung:

    python3 build.py

Die erzeugten Dateien werden mit eingecheckt. Der Hoster braucht nur die fertigen Dateien, kein Build.

## Lokal ansehen

    python3 -m http.server 8000

## Seiten

Startseite, Leistungen (Übersicht und vier Einzelseiten), Über Bettina, Soziales Engagement, Kontakt, Impressum, Datenschutz, Datenverarbeitung, Fehlerseite.

## Vor dem Livegang

- Empfängeradresse `CONTACT_EMAIL` in `assets/js/main.js` auf die endgültige Adresse stellen
- Platzhalter in Datenschutz (Hosting, Webanalyse) und Impressum (Bildnachweis) füllen und vom Datenschutzbeauftragten prüfen lassen
- Referenzlogos und deren Nutzung mit den Kunden abstimmen
- Domain in `build.py` (`SITE`) prüfen, danach Sitemap in der Search Console einreichen

Auf `github.io` und lokal setzt die Seite automatisch `noindex`. Auf der echten Domain ist sie indexierbar.
