# Angerer Consulting

Statische Website für Angerer Consulting (Bettina Angerer und Marvin Angerer). Durchgehend in der Wir-Form, nur Bettinas persönlicher Text und ihr Werdegang auf „Über uns“ stehen in der Ich-Form.

## Aufbau

- `content/inhalte.json` enthält die Texte, Kennzahlen und Schalter, die sich am ehesten ändern (Leistungen, FAQ, Ablauf, Über uns, Marvin, Fallbeispiele, Werdegang). Diese Datei bearbeitet Bettina über das Redaktionssystem.
- `build.py` erzeugt daraus alle HTML-Seiten, `sitemap.xml` und `robots.txt`. Seitenaufbau und seltener geänderte Texte stehen im Skript.
- `partials/` enthält wiederkehrende Teile (Symbole, Anfragefenster, Logo-Varianten).
- `content/legal/` enthält die Rechtstexte der bisherigen Website als Quelle.
- `assets/` enthält Styles, Skript, Schriften und Bilder. Alles liegt auf dem eigenen Server, es wird nichts von fremden Servern geladen.
- `api/anfrage.js` verschickt das Anfrageformular als E-Mail (Vercel-Funktion, Region Frankfurt).
- `vercel.json` enthält die 301-Weiterleitungen der alten WordPress-Seite und Sicherheits-Header.
- `.github/workflows/build.yml` baut die Seiten automatisch neu, sobald `content/`, `partials/` oder `build.py` geändert werden.
- `.pages.yml` ist die Einrichtung für das Redaktionssystem Pages CMS.

Lokal nach einer Änderung:

    python3 build.py

Die erzeugten Dateien werden mit eingecheckt. Vercel liefert sie nur aus, es baut nichts.

## Texte ändern ohne Code (Pages CMS)

1. Repository liegt in einem GitHub-Konto, auf das Bettina Zugriff hat.
2. Bettina meldet sich auf pagescms.org mit GitHub an und wählt das Repository.
3. Unter „Texte der Website“ ändert sie Texte, Kennzahlen, Schalter und Fallbeispiele in Formularen und lädt Fotos hoch.
4. Speichern erzeugt einen Commit. Die GitHub-Action baut die Seiten neu, Vercel veröffentlicht nach etwa einer Minute.

Pages CMS ist kostenlos und speichert nichts außerhalb von GitHub. Was nicht in `inhalte.json` steht (Seitenaufbau, Design, Rechtstexte), bleibt Entwicklungsarbeit.

## Schalter

In `content/inhalte.json` unter `schalter` sowie in den übrigen Feldern:

| Feld | Stand | Wirkung |
| --- | --- | --- |
| `team_zeigen` | aus | Hero-Fassung mit Marvins Team, Leistungen mit `nur_mit_team` erscheinen |
| `kundenlogos_zeigen` + `kundenlogos` | an, 12 Logos | Laufendes Banner „Kunden aus unserem Netzwerk“ unter dem Hero |
| `bvmw_siegel_zeigen` | an | Siegel „Zertifizierte Beratung“, gilt bis mindestens Ende 2027. Aus = überall weg |
| `kennzahlen` | 2 Werte | „Hunderte“ durch die echte Netzwerkzahl ersetzen |
| `fallbeispiele` | leer | Abschnitt „Aus der Praxis“ erscheint erst mit Inhalt |
| `video` / `video_platzhalter` | leer / an | Video auf „Über uns“, selbst gehostet als MP4. Bis dahin steht dort „Video folgt“ |
| `marvin` | Platzhalter | Foto und Text von Marvin Angerer |

## Seiten

Startseite (mit allen Leistungen in kurzer Form), Über uns, Kontakt, Impressum, Datenschutz, Datenverarbeitung, Fehlerseite. Eigene Leistungsseiten gibt es nicht mehr, alte Adressen leiten auf `/#leistungen` weiter.

`/logo-varianten/` ist eine Abstimmungsseite für die Strähne im Logo. Sie ist nicht verlinkt, steht nicht in der Sitemap und ist auf `noindex` gesetzt.

## Anfrageformular

1. Normalfall: Der Browser schickt die Angaben an `/api/anfrage`. Die Funktion verschickt sie über das E-Mail-Postfach von Bettina an `info@bettina-angerer.de`. Nichts wird gespeichert.
2. Ersatzweg: Antwortet der Server nicht (z. B. auf GitHub Pages, oder solange in Vercel noch kein Postfach eingetragen ist), öffnet sich das E-Mail-Programm, und der Text lässt sich kopieren.

In Vercel unter Settings > Environment Variables eintragen:

| Variable | Beispiel |
| --- | --- |
| `SMTP_HOST` | Mailserver des E-Mail-Anbieters |
| `SMTP_PORT` | `465` (oder `587`) |
| `SMTP_USER` / `SMTP_PASS` | Zugang zu einem Postfach der Domain, am besten ein eigenes wie `website@bettina-angerer.de` |
| `MAIL_TO` | `info@bettina-angerer.de` |
| `MAIL_FROM` | `website@bettina-angerer.de` |

Außerdem in `assets/js/main.js` `CONTACT_EMAIL` von der Testadresse auf `info@bettina-angerer.de` stellen und eine echte Testanfrage schicken.

## Weiterleitungen der alten Seite

Die alte WordPress-Seite hatte diese Seiten. Sie werden per 301 umgeleitet (`vercel.json`):

| Alt | Neu |
| --- | --- |
| /projektstrategie/, /service-engineering/, /unternehmensnachfolge/, /marketing-und-vertrieb/, /dienstleistungen/, /bildungsallianz/, /versteckte-steuererhoehung-durch-kurzarbeitergeld/, /leistungen/… | /#leistungen |
| /ueber-mich/, /bvmw/, /unterstuetzung-oberfranken-regio-bayreuth-stadt/ | /ueber-uns/ |
| /kontaktdaten/ | /kontakt/ |
| /die-zeit-wird-knapp/ | / |
| /kontakt/, /impressum/, /datenschutz/ | bleiben gleich |
| /bettina-angerer-blog/… (Beiträge 2020 bis 2022) | entfallen, Fehlerseite |

GitHub Pages kann keine Weiterleitungen, dort gelten sie nicht.

## Suchmaschinen

Auf `github.io`, auf Vercel-Vorschauadressen (`*.vercel.app`) und lokal setzt die Seite automatisch `noindex, nofollow`. Auf `www.bettina-angerer.de` greift das nicht, dort ist sie indexierbar. Nichts manuell umstellen.

## Vor dem Livegang

- Vercel-Projekt mit dem Repository verbinden (Framework: Other, kein Build-Befehl), Domain `www.bettina-angerer.de` eintragen, `bettina-angerer.de` auf www weiterleiten, DNS beim Domain-Anbieter umstellen
- Formular wie oben einrichten und testen
- Impressum: Rechtsform und vertretungsberechtigte Personen für die neue Firmierung eintragen
- Datenschutz: Vercel als Hosting-Anbieter mit Auftragsverarbeitung und Region Frankfurt sowie den E-Mail-Anbieter ergänzen, vom Datenschutzbeauftragten prüfen lassen
- Netzwerkzahl, Text und Foto von Marvin, Fallbeispiele eintragen
- Logo: Variante auswählen, Reinzeichnung einbauen (`partials/symbols.html`, `assets/img/logo-mark.svg`, `assets/img/og.png`)
- Größenstufen im Formular (`partials/wizard.html`) nach Absprache mit Bettina festlegen
- Sitemap in der Google Search Console einreichen

## Lokal ansehen

    python3 -m http.server 8000

Schriften: Source Serif 4 und Libre Franklin, beide unter der SIL Open Font License, lokal eingebunden.
