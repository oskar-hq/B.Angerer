# Übergabe an Flo (POLYNEO): bettina-angerer.de auf Vercel

Statische Seite plus eine Funktion für das Formular. Kein Framework, kein Build auf Vercel.

## Vercel einrichten

1. Neues Projekt aus dem GitHub-Repository, Framework „Other“, Build Command leer, Output Directory `.`.
   Vercel installiert nur `nodemailer` (aus `package.json`) für `api/anfrage.js`.
2. Production Branch: der Hauptzweig des Repositorys.
3. Domains: `www.bettina-angerer.de` als Hauptdomain, `bettina-angerer.de` leitet auf www weiter. DNS beim Domain-Anbieter umstellen.
4. Environment Variables (Production): `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `MAIL_TO=info@bettina-angerer.de`, `MAIL_FROM=website@bettina-angerer.de`. Am besten ein eigenes Postfach `website@` anlegen und SPF/DKIM der Domain prüfen.
5. Funktion läuft in `fra1` (Frankfurt), siehe `vercel.json`.

## Was `vercel.json` macht

- 301 von allen alten WordPress-Seiten auf die neuen Seiten (Liste im README)
- `trailingSlash: true`, Sicherheits-Header, langes Caching für Schriften
- `noindex` für `/logo-varianten/` (Abstimmungsseite)

Vorschauadressen (`*.vercel.app`) setzen automatisch `noindex`, die echte Domain nicht.

## Inhalte und Pflege

- Texte in `content/inhalte.json`, Bettina bearbeitet sie über Pages CMS (`.pages.yml`).
- Bei jeder Änderung an `content/`, `partials/` oder `build.py` baut die GitHub-Action (`.github/workflows/build.yml`) die HTML-Dateien neu und committet sie. Vercel deployt danach automatisch.
- Lokal: `python3 build.py`, dann `python3 -m http.server`.

## Bitte noch klären

- Datenschutz: Vercel als Auftragsverarbeiter (DPA, Region Frankfurt) und den E-Mail-Anbieter in die Erklärung aufnehmen, Speicherdauer der Logs. Die Stellen sind in `/datenschutz/` gelb markiert.
- Impressum: neue Rechtsform und vertretungsberechtigte Personen.
- Formular: `CONTACT_EMAIL` in `assets/js/main.js` (Ersatzweg) auf `info@bettina-angerer.de` stellen, Testanfrage schicken.
- Alte WordPress-Seite abschalten, sobald die DNS umgestellt ist. Die Blogbeiträge werden bewusst nicht übernommen.
