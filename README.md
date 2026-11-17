# Bettina Angerer Consulting

Statische Website für Bettina Angerer Consulting (Bettina Angerer und Marvin Angerer).

## Aufbau

- `build.py` erzeugt alle HTML-Seiten, `sitemap.xml` und `robots.txt`. Inhalte und Texte stehen in diesem Skript.
- `partials/` enthält wiederkehrende Teile (Symbole, Anfragefenster, Logo-Varianten).
- `content/legal/` enthält die Rechtstexte der bisherigen Website als Quelle.
- `assets/` enthält Styles, Skript, Schriften und Bilder. Alles liegt auf dem eigenen Server, es wird nichts von fremden Servern geladen.
- `anfrage.php` verschickt das Anfrageformular als E-Mail (braucht PHP auf dem Webspace).
- `.htaccess` enthält die 301-Weiterleitungen der alten WordPress-Seite (braucht Apache).

Nach jeder inhaltlichen Änderung:

    python3 build.py

Die erzeugten Dateien werden mit eingecheckt. Der Hoster braucht nur die fertigen Dateien, kein Build.

## Schalter in `build.py`

Ganz oben im Block `SCHALTER`:

| Schalter | Stand | Wirkung |
| --- | --- | --- |
| `SHOW_TEAM` | aus | Hero-Fassung mit Marvins Team, zusätzliche Leistungen „Betreuung großer Kunden“ und „Produktdesign“ |
| `SHOW_CLIENT_LOGOS` + `CLIENT_LOGOS` | aus, leer | Kundenlogos unter dem Hero und auf den Leistungsseiten. Erst nach Freigabe eintragen |
| `SHOW_BVMW_SEAL` | an | Siegel „Zertifizierte Beratung“, gilt bis mindestens Ende 2027. Aus = überall weg |
| `STATS` | 2 Werte | Kennzahlen im Hero. „Hunderte“ durch die echte Netzwerkzahl ersetzen |
| `CASES` | leer | Fallbeispiele (Ausgangslage, Vorgehen, Ergebnis). Abschnitt erscheint erst mit Inhalt |
| `VIDEO` | keins | Kurzes Video im Über-mich-Teil, selbst gehostet als MP4 |
| `MARVIN` | Platzhalter | Foto und Text von Marvin Angerer |

## Seiten

Startseite, Leistungen (Übersicht und fünf Einzelseiten: Strategie und Sanierung, Netzwerk und Politik, Coaching, Vertrieb, Marketing und Social Media), Über mich, Kontakt, Impressum, Datenschutz, Datenverarbeitung, Fehlerseite.

`/logo-varianten/` ist eine Abstimmungsseite für die Strähne im Logo. Sie ist nicht verlinkt, steht nicht in der Sitemap und ist auf `noindex` gesetzt.

## Anfrageformular

1. Normalfall: Der Browser schickt die Angaben an `anfrage.php`, das sie als E-Mail an `info@bettina-angerer.de` weiterleitet. Nichts wird gespeichert.
2. Ersatzweg: Antwortet der Server nicht (z. B. auf GitHub Pages, dort läuft kein PHP), öffnet sich wie bisher das E-Mail-Programm, und der Text lässt sich kopieren.

Vor dem Livegang:
- in `anfrage.php` Empfänger (`RECIPIENT`) und Absender (`SENDER`) prüfen. Der Absender muss zur Domain gehören, sonst landen die Mails im Spam (SPF beim Hoster prüfen)
- in `assets/js/main.js` `CONTACT_EMAIL` von der Testadresse auf `info@bettina-angerer.de` stellen
- einmal eine echte Testanfrage schicken

## Weiterleitungen der alten Seite

Die alte WordPress-Seite hatte diese Seiten. Sie werden per 301 umgeleitet (`.htaccess`):

| Alt | Neu |
| --- | --- |
| /projektstrategie/, /service-engineering/, /unternehmensnachfolge/, /versteckte-steuererhoehung-durch-kurzarbeitergeld/ | /leistungen/strategie/ |
| /marketing-und-vertrieb/ | /leistungen/vertrieb/ |
| /dienstleistungen/ | /leistungen/ |
| /bildungsallianz/ | /leistungen/coaching/ |
| /bvmw/, /unterstuetzung-oberfranken-regio-bayreuth-stadt/ | /ueber-mich/ |
| /kontaktdaten/ | /kontakt/ |
| /die-zeit-wird-knapp/ | / |
| /ueber-mich/, /kontakt/, /impressum/, /datenschutz/ | bleiben gleich |
| /bettina-angerer-blog/… (Beiträge 2020 bis 2022) | 410, dauerhaft entfernt |

Das funktioniert nur auf einem Apache-Webspace mit PHP (typisch für den bisherigen WordPress-Hoster). GitHub Pages kann keine 301-Weiterleitungen.

## Suchmaschinen

Auf `github.io` und lokal setzt die Seite automatisch `noindex, nofollow`. Auf `www.bettina-angerer.de` greift das nicht, dort ist sie indexierbar. Nichts manuell umstellen.

## Vor dem Livegang

- Hosting klären (Apache mit PHP), Domain umziehen, Sitemap in der Search Console einreichen
- Formular wie oben einrichten und testen
- Impressum: Rechtsform und vertretungsberechtigte Personen für die neue Firmierung eintragen
- Datenschutz: Hosting-Anbieter, Auftragsverarbeitung und Speicherdauer der Logdateien ergänzen, vom Datenschutzbeauftragten prüfen lassen
- Netzwerkzahl in `STATS`, Text und Foto von Marvin, Fallbeispiele eintragen
- Logo: Variante auswählen, Reinzeichnung einbauen (`partials/symbols.html`, `assets/img/logo-mark.svg`, `assets/img/og.png`)
- Größenstufen im Formular (`partials/wizard.html`) nach Absprache mit Bettina festlegen

## Lokal ansehen

    python3 -m http.server 8000

Schriften: Source Serif 4 und Libre Franklin, beide unter der SIL Open Font License, lokal eingebunden.
