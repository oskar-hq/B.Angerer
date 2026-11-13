#!/usr/bin/env python3
"""Baut die statische Website von Angerer Consulting.

Aufruf:  python3 build.py
Erzeugt alle HTML-Seiten, sitemap.xml und robots.txt im Projektordner.
Inhalte stehen in diesem Skript, wiederkehrende Teile in partials/.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://www.bettina-angerer.de"
VERSION = "11"

ORG = {
    "name": "Angerer Consulting",
    "person": "Bettina Angerer",
    "street": "Heinrich-Fickenscher-Str. 5A",
    "zip": "95448",
    "city": "Bayreuth",
    "phone": "+49 172 8640338",
    "phone_display": "+49 (0) 172 / 86 40 338",
    "email": "info@bettina-angerer.de",
    "vat": "DE298988354",
}

SYMBOLS = (ROOT / "partials/symbols.html").read_text()
WIZARD = (ROOT / "partials/wizard.html").read_text()

# ---------------------------------------------------------------- Logos
LOGOS = {
    "Red Bull": ("redbull.svg", 2.593, 1.45), "DZ Bank": ("dzbank.svg", 7.594, 0.62),
    "Netflix": ("netflix.svg", 0.55, 1.15), "Joyn": ("joyn.svg", 2.375, 0.8),
    "ZDF": ("zdf.svg", 1.711, 0.95), "ITV Studios": ("itv.svg", 1.391, 1.35),
    "Miss Germany": ("missgermany.svg", 4.09, 0.8), "Knabe Malz": ("knabe.png", 2.665, 0.85),
    "HR": ("hr.svg", 1.222, 1.25), "BR": ("br.svg", 1.248, 0.95), "WDR": ("wdr.svg", 3.441, 0.6), "NDR": ("ndr.svg", 1.047, 1.0),
}


def logo_list(names, cls, R):
    out = []
    for n in names:
        if n in LOGOS:
            f, ar, k = LOGOS[n]
            u = f"{R}assets/img/logos/{f}"
            out.append(f'<li><span class="logo" role="img" aria-label="{n}" style="-webkit-mask-image:url({u});mask-image:url({u});aspect-ratio:{ar};--k:{k}"></span></li>')
        else:
            out.append(f'<li><span class="logo-text">{n}</span></li>')
    return f'<ul class="{cls}" aria-label="Referenzen">' + "".join(out) + "</ul>"


ARROW = '<svg class="arrow" width="16" height="16" aria-hidden="true"><use href="#arrow"/></svg>'


def cta(R, label="Erstgespräch anfragen", cls="btn"):
    return f'<a class="{cls}" href="{R}kontakt/" data-open-wizard>{label} {ARROW}</a>'


# ---------------------------------------------------------------- Leistungen
SERVICES = [
    {
        "slug": "vertrieb", "num": "I", "name": "Vertrieb", "tag": "Moderne Sales-Beratung",
        "lead": "Neue Kunden gewinnen, ohne Ihre Mannschaft von den bestehenden abzuziehen.",
        "intro": "Viele Mittelständler leben von Empfehlungen und Stammkunden. Das trägt lange, wächst aber nicht von allein. Wir bauen Ihnen einen zweiten Weg zu neuen Kunden auf: planbar, messbar und so, dass Ihr Team dabei entlastet wird.",
        "pains": [
            ("Empfehlungen reichen nicht mehr", "Der Auftragseingang hängt an wenigen Kontakten. Fällt einer weg, fehlt Umsatz."),
            ("Kaltakquise frisst Zeit", "Niemand im Team hat Lust und Luft, täglich fremde Menschen anzuschreiben und nachzufassen."),
            ("Neue Märkte sind ein Risiko", "Sie vermuten Potenzial in einer neuen Zielgruppe, wollen dafür aber nicht gleich Personal umschichten."),
        ],
        "items": [
            ("Automatische Akquise über Social Media", "Ein System findet Ihre Zielkunden und schreibt sie persönlich an.",
             "Unser System sucht auf LinkedIn und Instagram nach Menschen, die zu Ihrer Zielgruppe passen, und prüft vorab deren Unternehmen. Jede Nachricht geht einzeln und persönlich raus. Wer nicht antwortet, wird zur richtigen Zeit erinnert. Der tägliche Aufwand liegt bei rund zehn Minuten, und Sie sehen schwarz auf weiß, welche Ansprache funktioniert."),
            ("Neue Vertriebswege testen", "Erst im kleinen Versuch prüfen, ob sich eine Zielgruppe lohnt.",
             "Bevor Sie Mitarbeiter und Budget auf einen neuen Markt ansetzen, starten wir einen Testballon: eine klar umrissene Zielgruppe, eine begrenzte Laufzeit, messbare Antworten. Danach entscheiden Sie anhand von Zahlen, ob Sie den Weg weitergehen."),
            ("Vertriebsstrategie", "Ein klarer Plan, wer wen wann anspricht.",
             "Wir ordnen Ihre Vertriebsrichtungen: Fachkunden, Endkunden, Großkunden. Für jede Richtung legen wir fest, welche Ansprache passt, welche Kanäle sich lohnen und woran Sie Erfolg erkennen."),
            ("Betreuung großer Kunden", "Erfahrung aus der Arbeit mit Konzernen und Sendern.",
             "Große Kunden haben eigene Abläufe, Einkaufsregeln und Erwartungen. Das Team kennt diese Welt aus der täglichen Arbeit und begleitet Sie von der ersten Anfrage bis zur laufenden Zusammenarbeit."),
        ],
        "refs": ["Red Bull", "DZ Bank", "Netflix", "Joyn"],
        "title": "Vertrieb für den Mittelstand | Bettina Angerer, Bayreuth",
        "desc": "Neue Kunden gewinnen mit automatischer Akquise über Social Media, Testläufen für neue Zielgruppen und klarer Vertriebsstrategie. Angerer Consulting, Bayreuth.",
    },
    {
        "slug": "marketing", "num": "II", "name": "Marketing", "tag": "Content statt Werbung",
        "lead": "Inhalte, die Ihre Kunden dort abholen, wo sie wirklich sind.",
        "intro": "Klassische Werbung verliert an Wirkung, weil Ihr Publikum sich verändert hat. Die Antwort heißt nicht mehr Werbung, sondern Inhalte, die Menschen freiwillig ansehen. Systematisch geplant, verlässlich produziert und messbar in der Wirkung.",
        "pains": [
            ("Anzeigen verpuffen", "Was vor fünf Jahren noch getragen hat, bringt heute kaum Rückmeldung."),
            ("Kein Gesicht nach außen", "Ihre Kunden wollen sehen, wer hinter dem Unternehmen steht. Im Netz finden sie wenig."),
            ("Social Media bleibt liegen", "Das Thema steht auf jeder Liste, aber niemand im Haus hat Zeit oder Erfahrung dafür."),
        ],
        "items": [
            ("Content-Strategie", "Was Sie zeigen, wem und wo. Ein Plan, der zu Ihnen passt.",
             "Wir klären, welche Themen Ihr Unternehmen glaubwürdig besetzen kann, auf welchen Plattformen Ihre Kunden unterwegs sind und in welchem Rhythmus Inhalte erscheinen. Das Ergebnis ist ein Redaktionsplan, den Sie verstehen und freigeben können."),
            ("Content-Erstellung", "Wir kommen zu Ihnen, drehen, schneiden und liefern fertige Beiträge.",
             "Ein eingespieltes Team übernimmt Dreh, Schnitt, Grafik und Text. Sie stellen Ihr Wissen und Ihre Menschen vor die Kamera, wir kümmern uns um alles Weitere und liefern Beiträge, die zur Plattform passen."),
            ("Personal Branding", "Ihr Auftritt als Person und als Marke, vom Logo bis zum Profil.",
             "Menschen kaufen von Menschen. Wir entwickeln Ihren persönlichen Auftritt: Positionierung, Bildsprache, Logo und Profile. So werden Sie als Unternehmer sichtbar, ohne sich zu verbiegen."),
            ("Influencer-Marketing", "Die richtigen Gesichter für Ihr Produkt, wenn es schneller gehen soll.",
             "Über das Netzwerk des Teams erreichen Sie Creator, die zu Ihrem Produkt und Ihrer Zielgruppe passen. Wir wählen aus, verhandeln und begleiten die Zusammenarbeit."),
            ("Produktdesign", "Verpackung und Auftritt, die im Regal und im Bild funktionieren.",
             "Vom Getränkekühlschrank bis zur Verpackung: Wir gestalten Produkte so, dass sie im Handel auffallen und auf Fotos und Videos gut aussehen."),
        ],
        "refs": ["Red Bull", "Knabe Malz", "Miss Germany", "ITV Studios"],
        "title": "Marketing und Content für den Mittelstand | Bettina Angerer",
        "desc": "Content-Strategie, Content-Erstellung, Personal Branding, Influencer-Marketing und Produktdesign für mittelständische Unternehmen. Angerer Consulting, Bayreuth.",
    },
    {
        "slug": "personal", "num": "III", "name": "Personal", "tag": "Potenzial heben",
        "lead": "Mehr aus dem Team herausholen, das Sie schon haben, und Lücken gezielt schließen.",
        "intro": "Beim Thema Personal denken viele zuerst an Kosten. Wir schauen zuerst auf das Potenzial: Was können Ihre Mitarbeiter lernen, welche Aufgaben übernimmt besser ein Spezialist auf Zeit, und mit wem lohnt sich eine Partnerschaft?",
        "pains": [
            ("Wissen fehlt im Haus", "Neue Werkzeuge und Kanäle kommen schneller, als das Team sie lernen kann."),
            ("Eine feste Stelle lohnt nicht", "Die Aufgabe ist wichtig, füllt aber keine volle Stelle oder nur für ein paar Monate."),
            ("Fachkräfte sind schwer zu finden", "Stellen bleiben offen, während die Arbeit sich stapelt."),
        ],
        "items": [
            ("Weiterbildung", "Workshops vor Ort, von Praktikern für Ihre Mitarbeiter.",
             "Praktiker aus dem Team schulen Ihre Mitarbeiter direkt bei Ihnen im Haus, an echten Aufgaben aus Ihrem Alltag. So bleibt das Wissen im Unternehmen und wird sofort angewendet."),
            ("Freelance-Experten", "Geprüfte Spezialisten auf Zeit, wenn eine feste Stelle zu viel wäre.",
             "Aus einem gewachsenen Pool vermitteln wir Fachleute für Gestaltung, Video, Social Media und Vertrieb. Sie arbeiten projektweise mit, ohne dass Sie eine Stelle schaffen müssen."),
            ("Kooperationen", "Partner aus dem Netzwerk, die zu Ihrem Vorhaben passen.",
             "Manches lässt sich gemeinsam besser lösen. Bettina Angerer bringt Sie mit Unternehmen, Dienstleistern und Institutionen aus ihrem Netzwerk zusammen, die Ihr Vorhaben voranbringen."),
        ],
        "refs": ["ZDF", "HR", "BR", "WDR", "NDR"],
        "title": "Personal: Weiterbildung und Experten auf Zeit | Bettina Angerer",
        "desc": "Weiterbildung vor Ort, Freelance-Experten auf Zeit und Kooperationen aus dem Netzwerk. Personalentwicklung für den Mittelstand von Angerer Consulting.",
    },
    {
        "slug": "finanzierung", "num": "IV", "name": "Finanzierung", "tag": "Den Wandel bezahlbar machen",
        "lead": "Das Budget für die ersten drei Felder liegt oft schon in Ihrem Unternehmen.",
        "intro": "Veränderung kostet Geld. Bevor Sie neues ausgeben, schauen wir gemeinsam, wo vorhandenes besser eingesetzt werden kann, welche Förderungen Ihnen zustehen und wie ein Vorhaben sauber geplant wird. Aus roten Zahlen werden schwarze.",
        "pains": [
            ("Kein Spielraum im Etat", "Für Neues ist scheinbar kein Geld da, obwohl an anderer Stelle Kosten ohne Wirkung laufen."),
            ("Förderung bleibt liegen", "Programme sind unübersichtlich, Anträge aufwendig. Am Ende wird nichts beantragt."),
            ("Projekte laufen aus dem Ruder", "Ohne klaren Rahmen wird aus einer guten Idee schnell ein teures Experiment."),
        ],
        "items": [
            ("Finanzoptimierung", "Unnötige Kosten finden und Luft im Etat schaffen.",
             "Wir analysieren Zahlen, Strukturen und Abläufe und zeigen, wo Geld ohne Gegenwert abfließt. Das frei werdende Budget finanziert die Schritte, die Ihr Unternehmen nach vorn bringen."),
            ("Staatliche Förderung", "Fördergelder, die Ihnen zustehen, auch wirklich abrufen.",
             "Für Digitalisierung, Weiterbildung und Beratung gibt es Förderprogramme. Wir prüfen, welche für Ihr Vorhaben in Frage kommen, und begleiten Sie durch den Antrag."),
            ("Projektbudgetierung", "Ein klarer Rahmen, bevor das erste Geld fließt.",
             "Jedes Vorhaben bekommt ein Budget, Meilensteine und Kennzahlen. So wissen Sie zu jedem Zeitpunkt, was es kostet und was es bringt."),
        ],
        "refs": [],
        "title": "Finanzierung und Förderung für den Mittelstand | Bettina Angerer",
        "desc": "Finanzoptimierung, staatliche Förderung und Projektbudgetierung: So wird der Wandel in Ihrem Unternehmen bezahlbar. Angerer Consulting, Bayreuth.",
    },
]

FAQ = [
    ("Für wen ist das Angebot gedacht?", "Für Inhaber und Geschäftsführer im Mittelstand, die wissen, dass sie bei Vertrieb, Marketing oder Personal nachziehen müssen, aber keinen Zugang zu den richtigen Leuten haben."),
    ("Muss ich mich mit Social Media auskennen?", "Nein. Genau dafür gibt es das Dolmetscher-Prinzip. Sie sagen, was Sie erreichen wollen. Wir übersetzen das in Maßnahmen und erklären jeden Schritt in klarer Sprache."),
    ("Was passiert nach meiner Anfrage?", "Ihre Angaben gehen direkt an Bettina Angerer. Sie prüft, ob wir zu Ihrem Anliegen passen, und meldet sich für ein Erstgespräch bei Ihnen."),
    ("Was ist ein Testballon?", "Ein kleiner, zeitlich begrenzter Versuch. Zum Beispiel sprechen wir eine neue Zielgruppe über LinkedIn an und messen, wie viele antworten. So sehen Sie mit geringem Einsatz, ob sich ein neuer Weg lohnt."),
    ("Was bedeutet zertifizierte Beratung?", "Bettina Angerer ist zertifizierte Beraterin im Beratungsnetzwerk Mittelstand des BVMW, des Bundesverbands mittelständische Wirtschaft."),
    ("Arbeiten Sie nur in Oberfranken?", "Der Sitz ist Bayreuth. Die Projekte des Teams laufen regional, bundesweit und international."),
]

NAV = [("leistungen/", "Leistungen"), ("ueber-bettina/", "Über Bettina"), ("engagement/", "Engagement")]
MOBILE_NAV = NAV + [("kontakt/", "Kontakt")]


# ---------------------------------------------------------------- Rahmen
def page(path, title, desc, body, current="", schema=None, crumbs=None):
    """path: Zielpfad relativ zum Projekt, z. B. 'leistungen/vertrieb/index.html'."""
    depth = path.count("/")
    R = "../" * depth
    url_path = path[:-len("index.html")] if path.endswith("index.html") else path
    canonical = f"{SITE}/{url_path}"
    schemas = list(schema or [])
    if crumbs:
        schemas.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{u}"}
                                for i, (u, n) in enumerate([("", "Startseite")] + crumbs)],
        })
    ld = "\n".join(f'  <script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)

    def nav_link(href, label):
        cur = ' aria-current="page"' if current == href else ""
        return f'<a href="{R}{href}"{cur}>{label}</a>'

    nav = "\n        ".join(nav_link(h, l) for h, l in NAV)
    mnav = "\n    ".join(nav_link(h, l) for h, l in MOBILE_NAV)
    svc_links = "\n            ".join(f'<li><a href="{R}leistungen/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    doc = f'''<!doctype html>
<html lang="de" class="no-js">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="de_DE">
  <meta property="og:site_name" content="Angerer Consulting">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/img/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0c2d4a">
  <link rel="icon" href="{R}assets/img/logo-mark.svg" type="image/svg+xml">
  <link rel="preload" href="{R}assets/fonts/cormorant-garamond.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{R}assets/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{R}assets/css/styles.css?v={VERSION}">
  <script>
    document.documentElement.classList.remove('no-js');
    // Testumgebung nicht in Suchmaschinen aufnehmen. Auf der echten Domain greift das nicht.
    if (/github\\.io$|localhost|127\\.0\\.0\\.1/.test(location.hostname)) {{
      var m = document.createElement('meta'); m.name = 'robots'; m.content = 'noindex, nofollow'; document.head.appendChild(m);
    }}
  </script>
{ld}
</head>
<body>
  {SYMBOLS}
  <a class="skip" href="#inhalt">Zum Inhalt springen</a>

  <div class="strip">Präsent in Oberfranken. Nicht für jeden verfügbar.</div>

  <header class="header" id="top">
    <span class="scroll-progress" aria-hidden="true"></span>
    <div class="wrap header-inner">
      <nav class="nav" aria-label="Hauptnavigation">
        {nav}
      </nav>
      <a class="brand" href="{R or './'}" aria-label="Angerer Consulting, zur Startseite">
        <svg class="brand-mark" aria-hidden="true"><use href="#mark"/></svg>
        <span class="brand-text">
          <span class="brand-name">Bettina Angerer</span>
          <span class="brand-sub">Consulting</span>
        </span>
      </a>
      <a class="btn btn-ghost btn-sm header-cta" href="{R}kontakt/" data-open-wizard>Erstgespräch anfragen</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menü öffnen">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
  <div class="mobile-menu" id="mobile-menu">
    {mnav}
    <a class="btn" href="{R}kontakt/" data-open-wizard>Erstgespräch anfragen</a>
  </div>

  <main id="inhalt">
{body.replace("{R}", R)}
  </main>

  {WIZARD.replace("{R}", R)}
  <footer class="footer">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          <a class="brand" href="{R or './'}" aria-label="Angerer Consulting, zur Startseite">
            <svg class="brand-mark" aria-hidden="true"><use href="#mark"/></svg>
            <span class="brand-text">
              <span class="brand-name">Bettina Angerer</span>
              <span class="brand-sub">Consulting</span>
            </span>
          </a>
          <p class="body-6">Für Ihren Unternehmenserfolg.<br>Für unser Bayreuth.</p>
          <p class="body-6 footer-cert">Zertifizierte Beratung im Beratungsnetzwerk Mittelstand des BVMW.</p>
        </div>
        <div>
          <h2 class="caption-3">Leistungen</h2>
          <ul>
            {svc_links}
          </ul>
        </div>
        <div>
          <h2 class="caption-3">Über</h2>
          <ul>
            <li><a href="{R}ueber-bettina/">Über Bettina Angerer</a></li>
            <li><a href="{R}engagement/">Soziales Engagement</a></li>
            <li><a href="{R}leistungen/">Alle Leistungen</a></li>
          </ul>
        </div>
        <div>
          <h2 class="caption-3">Kontakt</h2>
          <address>
            {ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}<br>
            <a href="tel:{ORG["phone"].replace(" ", "")}">{ORG["phone_display"]}</a><br>
            <a href="mailto:{ORG["email"]}">{ORG["email"]}</a>
          </address>
        </div>
      </div>
      <div class="footer-legal">
        <span>© 2026 Angerer Consulting, Bettina Angerer</span>
        <nav aria-label="Rechtliches">
          <a href="{R}impressum/">Impressum</a>
          <a href="{R}datenschutz/">Datenschutz</a>
          <a href="{R}datenverarbeitung/">Datenverarbeitung</a>
        </nav>
      </div>
    </div>
  </footer>

  <script src="{R}assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
'''
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return url_path


def page_hero(eyebrow, h1, lead, crumbs):
    trail = '<a href="{R}">Startseite</a>' + "".join(
        f'<span aria-hidden="true">/</span><a href="{{R}}{u}">{n}</a>' for u, n in crumbs[:-1]
    ) + f'<span aria-hidden="true">/</span><span aria-current="page">{crumbs[-1][1]}</span>'
    return f'''    <section class="page-hero on-blue">
      <div class="wrap">
        <nav class="crumbs caption-3" aria-label="Brotkrumen">{trail}</nav>
        <p class="eyebrow caption-3">{eyebrow}</p>
        <h1 class="heading-1">{h1}</h1>
        <p class="page-lead body-lg">{lead}</p>
      </div>
    </section>
'''


def final_cta(heading="Sagen Sie uns, wo es hakt.", text="Sechs kurze Fragen, eine nach der anderen. Ihre Antworten gehen direkt an Bettina Angerer."):
    return f'''    <section class="section on-blue final" aria-labelledby="anfrage-title">
      <div class="wrap final-inner reveal">
        <p class="caption-3 final-eyebrow">Erstgespräch</p>
        <h2 class="heading-2" id="anfrage-title">{heading}</h2>
        <p class="body-lg">{text}</p>
        {cta("{R}")}
        <p class="hero-note">Unverbindlich. Sie entscheiden danach, ob es weitergeht.</p>
      </div>
    </section>
'''


SEAL = '<img class="seal" src="{R}assets/img/bvmw-zertifiziert.png" width="324" height="283" loading="lazy" alt="Siegel: Zertifizierte Beratung für mittelständische Unternehmen, Beratungsnetzwerk Mittelstand, BVMW e.V. Bundesverband">'

ORG_SCHEMA = {
    "@context": "https://schema.org", "@type": "ProfessionalService", "@id": f"{SITE}/#organisation",
    "name": "Angerer Consulting", "alternateName": "Bettina Angerer Unternehmensberatung",
    "url": f"{SITE}/", "image": f"{SITE}/assets/img/portrait.jpg", "logo": f"{SITE}/assets/img/logo-mark.svg",
    "telephone": ORG["phone"], "email": ORG["email"],
    "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"],
                "addressLocality": ORG["city"], "addressRegion": "Bayern", "addressCountry": "DE"},
    "areaServed": ["Bayreuth", "Oberfranken", "Deutschland"],
    "founder": {"@id": f"{SITE}/ueber-bettina/#person"},
    "knowsAbout": ["Vertrieb", "Marketing", "Personalentwicklung", "Finanzierung", "Mittelstand"],
}
PERSON_SCHEMA = {
    "@context": "https://schema.org", "@type": "Person", "@id": f"{SITE}/ueber-bettina/#person",
    "name": "Bettina Angerer", "jobTitle": "Unternehmensberaterin", "url": f"{SITE}/ueber-bettina/",
    "image": f"{SITE}/assets/img/portrait.jpg", "worksFor": {"@id": f"{SITE}/#organisation"},
    "address": {"@type": "PostalAddress", "addressLocality": "Bayreuth", "addressCountry": "DE"},
    "memberOf": {"@type": "Organization", "name": "BVMW e.V. Bundesverband mittelständische Wirtschaft"},
}

urls = []

# ================================================================ Startseite
tiles = ""
for s in SERVICES:
    lis = "".join(f"<li><strong>{t}</strong><span>{short}</span></li>" for t, short, _ in s["items"])
    refs = logo_list(s["refs"], "service-refs", "{R}") if s["refs"] else '<p class="service-note">Aus roten Zahlen werden schwarze</p>'
    tiles += f'''
          <article class="service reveal" id="{s["slug"]}">
            <div class="service-top"><span class="num" aria-hidden="true">{s["num"]}</span><span class="tag caption-3">{s["tag"]}</span></div>
            <h3 class="heading-3"><a href="{{R}}leistungen/{s["slug"]}/">{s["name"]}</a></h3>
            <p>{s["lead"]}</p>
            <ul>{lis}</ul>
            {refs}
            <a class="textlink" href="{{R}}leistungen/{s["slug"]}/">Mehr zu {s["name"]} {ARROW}</a>
          </article>
'''
faq_html = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
band = ["Red Bull", "DZ Bank", "Netflix", "Joyn", "ZDF", "ITV Studios", "Miss Germany", "Knabe Malz", "HR", "BR", "WDR", "NDR"]

home = f'''    <section class="hero on-blue" aria-labelledby="hero-title">
      <div class="hero-strand-wrap"><svg class="hero-strand" viewBox="0 0 1100 760" preserveAspectRatio="none" fill="none" aria-hidden="true">
        <g stroke="#D4B678" stroke-width="1" opacity="0.22">
          <path d="M-20 80C220 40 420 140 520 330s220 330 620 380"/>
          <path d="M-20 130C200 100 380 190 480 370s230 300 640 350"/>
          <path d="M-20 30C250 -10 470 90 570 290s210 350 560 400"/>
        </g>
        <path d="M-20 96C210 62 400 160 500 348s222 318 620 366c-380-62-560-190-640-360S180 92 -20 108z" fill="#3AA7E8" opacity="0.5"/>
      </svg></div>
      <div class="wrap hero-inner">
        <h1 id="hero-title"><span class="hero-kicker caption-3">Bettina Angerer · Unternehmensberatung in Bayreuth</span><span class="hero-title heading-1">Dreißig Jahre Mittelstand.<br>Und das Team, das Ihre Kunden heute erreicht.</span></h1>
        <p class="hero-sub body-lg">Sie wissen, dass sich in Ihrem Unternehmen etwas bewegen muss, aber nicht, wo Sie anfangen sollen. Bettina Angerer bringt Sie mit den Menschen zusammen, die Vertrieb, Marketing, Personal und Finanzierung auf den Stand von heute bringen.</p>
        <div class="hero-actions">
          {cta("{R}")}
          <p class="hero-note">Sechs kurze Fragen. Unverbindlich.</p>
        </div>
      </div>
      <div class="wrap">
        <dl class="stats">
          <div class="stat"><dt data-count="30" data-suffix="+">30+</dt><dd>Jahre im Mittelstand</dd></div>
          <div class="stat"><dt data-count="100" data-suffix="+">100+</dt><dd>begleitete Unternehmen</dd></div>
          <div class="stat"><dt data-count="8" data-suffix="">8</dt><dd>Jahre BVMW</dd></div>
        </dl>
      </div>
    </section>

    <section class="refs on-champagne" aria-label="Referenzen des Teams">
      <div class="wrap">
        <p class="refs-label caption-3">Das Team hat gearbeitet für</p>
        <div class="marquee">
          {logo_list(band, "refs-list", "{R}")}
        </div>
      </div>
    </section>

    <section class="section on-blue" id="leistungen" aria-labelledby="leistungen-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Die Leistungen</p>
          <h2 class="heading-2" id="leistungen-title">Vier Felder. Ein Ansprechpartner.</h2>
          <p class="body-lg">Sie sprechen mit Bettina Angerer. Dahinter steht ein Team aus Spezialisten, das jedes dieser Felder täglich bearbeitet. Wählen Sie das Feld, in dem es bei Ihnen gerade hakt.</p>
        </div>
        <div class="services">{tiles}        </div>
        <p class="services-more reveal"><a class="btn btn-ghost" href="{{R}}leistungen/">Alle Leistungen im Überblick {ARROW}</a></p>
      </div>
    </section>

    <section class="section on-champagne on-light" aria-labelledby="problem-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Eine Frage</p>
          <h2 class="heading-2" id="problem-title">Warum wirkt Ihr Marketing heute weniger als vor fünf Jahren?</h2>
          <p class="body-lg">Nicht wegen fehlendem Budget. Wegen eines veränderten Publikums. Drei Beobachtungen, die in der Chefetage selten offen ausgesprochen werden.</p>
        </div>
        <div class="observations">
          <article class="observation reveal"><p class="num" aria-hidden="true">I</p><h3 class="heading-5">Aufmerksamkeit</h3><p>Ihre Anzeige konkurriert nicht mit anderen Anzeigen. Sie konkurriert mit der Story der Tochter auf Instagram. Wer unterbrechen will, verliert.</p></article>
          <article class="observation reveal"><p class="num" aria-hidden="true">II</p><h3 class="heading-5">Vertrauen</h3><p>Bezahlte Botschaften verlieren an Glaubwürdigkeit. Echte Geschichten gewinnen sie. Ihre Kunden wollen sehen, wer Sie sind.</p></article>
          <article class="observation reveal"><p class="num" aria-hidden="true">III</p><h3 class="heading-5">Sichtbarkeit</h3><p>Während die Branche noch über TikTok, Instagram und YouTube diskutiert, holen Mitbewerber dort bereits Ihre Zielkunden ab.</p></article>
        </div>
      </div>
    </section>

    <section class="tagline on-deep" aria-label="Leitsatz">
      <div class="wrap">
        <p data-reveal-words>Zwei Generationen. Eine Mission. <span data-gold>Wer zwischen beiden übersetzt, gewinnt den Markt.</span></p>
      </div>
    </section>

    <section class="section on-light" aria-labelledby="about-title">
      <div class="wrap about">
        <figure class="portrait reveal">
          <img class="portrait-img" src="{{R}}assets/img/portrait.jpg" width="1076" height="1434" alt="Bettina Angerer, Unternehmensberaterin aus Bayreuth" loading="lazy">
        </figure>
        <div class="about-copy reveal">
          <p class="eyebrow caption-3">Über Bettina Angerer</p>
          <h2 class="heading-2" id="about-title">Ich übersetze zwischen Chefetage und der Generation Ihrer Kunden.</h2>
          <p class="body-lg">Ich kenne die Wirtschaft aus allen Perspektiven: aus leitenden Positionen in Marketing und Controlling und seit 2018 als Leiterin der Geschäftsstelle Bayreuth und Nordbayern des BVMW.</p>
          <p>Heute verbinde ich diese Erfahrung mit einem jungen Team, das mit Social Media, Content und neuen Werkzeugen aufgewachsen ist. Beide Welten brauchen einander.</p>
          <div class="cert">
            {SEAL}
            <p><strong>Zertifizierte Beratung für mittelständische Unternehmen.</strong><br>Beratungsnetzwerk Mittelstand, BVMW e.V. Bundesverband.</p>
          </div>
          <a class="textlink" href="{{R}}ueber-bettina/">Mehr über Bettina Angerer {ARROW}</a>
        </div>
      </div>
    </section>

    <section class="section on-blue" id="ablauf" aria-labelledby="ablauf-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Der Ablauf</p>
          <h2 class="heading-2" id="ablauf-title">Drei Schritte bis zum ersten Ergebnis.</h2>
        </div>
        <ol class="process">
          <li class="reveal"><p class="num" aria-hidden="true">I</p><h3 class="heading-5">Anfrage</h3><p>Sie beantworten sechs kurze Fragen, eine nach der anderen. Das Wichtigste: wo es bei Ihnen hakt.</p></li>
          <li class="reveal"><p class="num" aria-hidden="true">II</p><h3 class="heading-5">Erstgespräch</h3><p>Bettina Angerer meldet sich persönlich. Gemeinsam klären Sie, ob und wo wir helfen können.</p></li>
          <li class="reveal"><p class="num" aria-hidden="true">III</p><h3 class="heading-5">Testballon</h3><p>Wir starten klein und messbar. Erst wenn die Zahlen stimmen, wird daraus ein größeres Projekt.</p></li>
        </ol>
      </div>
    </section>

    <section class="section on-champagne on-light" aria-labelledby="faq-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Häufige Fragen</p>
          <h2 class="heading-2" id="faq-title">Bevor Sie anfragen.</h2>
        </div>
        <div class="faq reveal">{faq_html}</div>
      </div>
    </section>

{final_cta()}'''

faq_schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
web_schema = {"@context": "https://schema.org", "@type": "WebSite", "name": "Angerer Consulting", "url": f"{SITE}/", "inLanguage": "de"}
urls.append(page("index.html", "Bettina Angerer | Unternehmensberatung für den Mittelstand in Bayreuth",
                 "Bettina Angerer verbindet dreißig Jahre Mittelstand mit einem jungen Team für Vertrieb, Marketing, Personal und Finanzierung. Zertifizierte Beratung aus Bayreuth.",
                 home, schema=[ORG_SCHEMA, web_schema, faq_schema]))

# ================================================================ Leistungen Übersicht
rows = ""
for s in SERVICES:
    lis = "".join(f"<li><div><h3>{t}</h3><p>{long}</p></div></li>" for t, _, long in s["items"])
    refs = ('<p class="detail-refs-label caption-3">Erfahrung aus der Arbeit für</p>' + logo_list(s["refs"], "detail-refs", "{R}")) if s["refs"] else ""
    rows += f'''
    <section class="section detail {'on-champagne ' if SERVICES.index(s) % 2 else ''}on-light" id="{s["slug"]}" aria-labelledby="{s["slug"]}-title">
      <div class="wrap detail-grid">
        <div class="detail-side reveal">
          <p class="detail-num" aria-hidden="true">{s["num"]}</p>
          <p class="eyebrow caption-3">{s["tag"]}</p>
          <h2 class="heading-2" id="{s["slug"]}-title">{s["name"]}</h2>
          <p class="body-lg">{s["lead"]}</p>
          <p>{s["intro"]}</p>
          {refs}
          <a class="btn btn-dark" href="{{R}}leistungen/{s["slug"]}/">Mehr zu {s["name"]} {ARROW}</a>
        </div>
        <ol class="steps detail-list reveal">{lis}</ol>
      </div>
    </section>
'''
crumbs = [("leistungen/", "Leistungen")]
body = page_hero("Die Leistungen", "Vier Felder, in denen wir Ihr Unternehmen nach vorn bringen.",
                 "Vertrieb, Marketing, Personal und Finanzierung greifen ineinander. Sie müssen nicht alles auf einmal angehen. Wir beginnen dort, wo es bei Ihnen gerade am meisten hakt.", crumbs)
body += f'''    <nav class="jump on-blue" aria-label="Leistungen im Überblick">
      <div class="wrap jump-inner">{"".join(f'<a href="#{s["slug"]}"><span aria-hidden="true">{s["num"]}</span>{s["name"]}</a>' for s in SERVICES)}</div>
    </nav>
''' + rows + final_cta("Welches Feld passt zu Ihnen?", "Sie müssen das nicht allein entscheiden. Beschreiben Sie in einem Satz, wo es hakt, und wir ordnen es gemeinsam ein.")
urls.append(page("leistungen/index.html", "Leistungen: Vertrieb, Marketing, Personal, Finanzierung | Bettina Angerer",
                 "Alle Leistungen von Angerer Consulting im Überblick: Vertrieb, Marketing, Personal und Finanzierung für mittelständische Unternehmen in Bayreuth, Oberfranken und bundesweit.",
                 body, current="leistungen/", crumbs=crumbs))

# ================================================================ Leistung Einzelseiten
for s in SERVICES:
    crumbs = [("leistungen/", "Leistungen"), (f'leistungen/{s["slug"]}/', s["name"])]
    pains = "".join(f'<article class="observation reveal"><p class="num" aria-hidden="true">{"I" * (i + 1)}</p><h3 class="heading-5">{t}</h3><p>{d}</p></article>' for i, (t, d) in enumerate(s["pains"]))
    lis = "".join(f"<li><div><h3>{t}</h3><p>{long}</p></div></li>" for t, _, long in s["items"])
    refs = f'''
    <section class="refs on-champagne" aria-label="Referenzen">
      <div class="wrap">
        <p class="refs-label caption-3">Erfahrung aus der Arbeit für</p>
        {logo_list(s["refs"], "refs-static", "{R}")}
      </div>
    </section>
''' if s["refs"] else ""
    others = "".join(f'<a class="other reveal" href="{{R}}leistungen/{o["slug"]}/"><span class="num" aria-hidden="true">{o["num"]}</span><span class="heading-5">{o["name"]}</span><span class="other-lead">{o["lead"]}</span>{ARROW}</a>' for o in SERVICES if o is not s)
    body = page_hero(s["tag"], f'{s["name"]}: {s["lead"]}', s["intro"], crumbs) + refs + f'''
    <section class="section on-light" aria-labelledby="lage-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Die Ausgangslage</p>
          <h2 class="heading-2" id="lage-title">Kommt Ihnen das bekannt vor?</h2>
        </div>
        <div class="observations">{pains}</div>
      </div>
    </section>

    <section class="section on-champagne on-light" aria-labelledby="was-title">
      <div class="wrap detail-grid">
        <div class="detail-side reveal">
          <p class="eyebrow caption-3">Was wir tun</p>
          <h2 class="heading-2" id="was-title">Unsere Leistungen im Feld {s["name"]}.</h2>
          <p class="body-lg">Jede Leistung können Sie einzeln beauftragen. Meist beginnen wir mit einer und bauen aus, sobald die ersten Ergebnisse da sind.</p>
          {cta("{R}", cls="btn btn-dark")}
        </div>
        <ol class="steps detail-list reveal">{lis}</ol>
      </div>
    </section>

    <section class="section on-blue" aria-labelledby="ablauf-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Der Ablauf</p>
          <h2 class="heading-2" id="ablauf-title">Drei Schritte bis zum ersten Ergebnis.</h2>
        </div>
        <ol class="process">
          <li class="reveal"><p class="num" aria-hidden="true">I</p><h3 class="heading-5">Anfrage</h3><p>Sie beantworten sechs kurze Fragen und beschreiben, wo es hakt.</p></li>
          <li class="reveal"><p class="num" aria-hidden="true">II</p><h3 class="heading-5">Erstgespräch</h3><p>Bettina Angerer meldet sich persönlich und klärt mit Ihnen, was sinnvoll ist.</p></li>
          <li class="reveal"><p class="num" aria-hidden="true">III</p><h3 class="heading-5">Testballon</h3><p>Wir starten klein und messbar. Erst wenn die Zahlen stimmen, wird daraus mehr.</p></li>
        </ol>
      </div>
    </section>

    <section class="section on-light" aria-labelledby="weitere-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Weitere Felder</p>
          <h2 class="heading-2" id="weitere-title">Das greift ineinander.</h2>
        </div>
        <div class="others">{others}</div>
      </div>
    </section>

''' + final_cta()
    svc_schema = {"@context": "https://schema.org", "@type": "Service", "name": f'{s["name"]} für den Mittelstand',
                  "serviceType": s["name"], "description": s["desc"], "provider": {"@id": f"{SITE}/#organisation"},
                  "areaServed": "DE", "url": f'{SITE}/leistungen/{s["slug"]}/',
                  "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["name"],
                                      "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t}} for t, _, _ in s["items"]]}}
    urls.append(page(f'leistungen/{s["slug"]}/index.html', s["title"], s["desc"], body, current="leistungen/", schema=[svc_schema], crumbs=crumbs))

# ================================================================ Über Bettina
crumbs = [("ueber-bettina/", "Über Bettina")]
body = page_hero("Über Bettina Angerer", "Bettina Angerer. Dreißig Jahre Substanz, übersetzt in die Sprache von heute.",
                 "Unternehmensberaterin aus Bayreuth, zertifiziert im Beratungsnetzwerk Mittelstand des BVMW und seit Jahrzehnten im oberfränkischen Mittelstand zu Hause.", crumbs) + f'''
    <section class="section on-light" aria-labelledby="bio-title">
      <div class="wrap about">
        <figure class="portrait reveal">
          <img class="portrait-img" src="{{R}}assets/img/portrait.jpg" width="1076" height="1434" alt="Bettina Angerer, Unternehmensberaterin aus Bayreuth">
        </figure>
        <div class="about-copy reveal">
          <p class="eyebrow caption-3">Der Weg</p>
          <h2 class="heading-2" id="bio-title">Ich kenne die Wirtschaft aus allen Perspektiven.</h2>
          <p class="body-lg">Zunächst war ich in leitenden Positionen in Marketing und Controlling tätig. Seit 2018 leite ich die Geschäftsstelle Bayreuth und Nordbayern des Wirtschaftsverbandes BVMW e.V. DER MITTELSTAND.</p>
          <p>Die Herausforderungen für Unternehmen werden immer vielfältiger. Mit meiner langjährigen Erfahrung und meinem branchenübergreifenden Netzwerk mache ich Sie und Ihr Unternehmen fit für die Zukunft. Mein Grundsatz dabei: Aus roten Zahlen mache ich schwarze. Das ist ein Anspruch, keine Werbung.</p>
          <dl class="facts">
            <div><dt>30+</dt><dd>Jahre im Mittelstand</dd></div>
            <div><dt>100+</dt><dd>begleitete Unternehmen</dd></div>
            <div><dt>8</dt><dd>Jahre BVMW</dd></div>
          </dl>
        </div>
      </div>
    </section>

    <section class="section on-champagne on-light" aria-labelledby="cert-title">
      <div class="wrap cert-block">
        <div class="reveal">{SEAL}</div>
        <div class="reveal">
          <p class="eyebrow caption-3">Zertifizierung</p>
          <h2 class="heading-2" id="cert-title">Zertifizierte Beratung für mittelständische Unternehmen.</h2>
          <p class="body-lg">Bettina Angerer ist zertifizierte Beraterin im Beratungsnetzwerk Mittelstand des BVMW e.V., des Bundesverbands mittelständische Wirtschaft.</p>
          <p>Als Beauftragte von Deutschlands größtem Unternehmernetzwerk öffnet sie Türen, die sonst verschlossen bleiben: zu passenden Dienstleistern, zu Partnern und zu Entscheidern in Wirtschaft und Politik.</p>
        </div>
      </div>
    </section>

    <section class="section on-light" id="prinzip" aria-labelledby="prinzip-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Das Dolmetscher-Prinzip</p>
          <h2 class="heading-2" id="prinzip-title">Ich übersetze in beide Richtungen.</h2>
          <p class="body-lg">Die Chefetage spricht eine andere Sprache als die Generation, die heute Ihre Zielgruppe ist. Beide Welten brauchen einander. Wer übersetzt, gewinnt den Markt.</p>
        </div>
        <div class="bridge two">
          <article class="world reveal">
            <p class="caption-3">I. Die erfahrene Welt</p>
            <h3 class="heading-5">Dreißig Jahre Substanz</h3>
            <ul><li>Chefetage und Strategie</li><li>Finanzen und Verhandlung</li><li>Politik und Netzwerk</li><li>Ehrbarer Kaufmann</li></ul>
          </article>
          <article class="world dark reveal">
            <p class="caption-3">II. Die mediennative Welt</p>
            <h3 class="heading-5">Die Generation Ihrer Kunden</h3>
            <ul><li>TikTok, Instagram, Reels, YouTube</li><li>Creator und Community</li><li>Trend und Tempo</li><li>Authentische Sprache</li></ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section on-champagne on-light" aria-labelledby="auswahl-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Die Auswahl</p>
          <h2 class="heading-2" id="auswahl-title">Was ich nicht jedem anbiete.</h2>
        </div>
        <div class="criteria">
          <article class="reveal">
            <h3 class="heading-5">Mein Geschäftspartner zu sein setzt voraus</h3>
            <ul><li>Klartext über Zahlen und Strukturen</li><li>Tempo statt endloser Diskussionen</li><li>Veränderung, nicht Bestätigung</li></ul>
          </article>
          <article class="reveal">
            <h3 class="heading-5">Unser Mitstreiter für Bayreuth zu sein setzt voraus</h3>
            <ul><li>Verantwortung über das Unternehmen hinaus</li><li>Zeit, Netzwerk und Ressourcen einzubringen</li><li>Anpacken, nicht nur unterzeichnen</li></ul>
          </article>
        </div>
        <p class="closing heading-5 reveal">Wer beides mitbringt, ist bei mir richtig. Alle anderen finden Beratung anderswo.</p>
      </div>
    </section>

''' + final_cta("Lernen wir uns kennen.", "Sechs kurze Fragen, dann meldet sich Bettina Angerer persönlich bei Ihnen.")
urls.append(page("ueber-bettina/index.html", "Über Bettina Angerer | Unternehmensberaterin in Bayreuth",
                 "Bettina Angerer: Unternehmensberaterin aus Bayreuth, zertifiziert im Beratungsnetzwerk Mittelstand des BVMW. Dreißig Jahre Erfahrung in Marketing, Controlling und Mittelstand.",
                 body, current="ueber-bettina/", schema=[PERSON_SCHEMA], crumbs=crumbs))

# ================================================================ Engagement
crumbs = [("engagement/", "Soziales Engagement")]
body = page_hero("Für unser Bayreuth", "Soziales Engagement: anpacken statt nur reden.",
                 "Wer ein Unternehmen führt, lebt in einer Stadt. Und braucht eine, die funktioniert. Deshalb engagiere ich mich seit vielen Jahren ehrenamtlich für Bayreuth und Oberfranken.", crumbs) + '''
    <section class="section on-light" aria-labelledby="selbst-title">
      <div class="wrap civic">
        <div class="civic-copy reveal">
          <p class="eyebrow caption-3">Das Selbstverständnis</p>
          <h2 class="heading-2" id="selbst-title">Bürger und Unternehmer, die sich aktiv am kommunalen Leben beteiligen.</h2>
          <p class="body-lg">Ich gehöre zu dieser Gruppe. Nicht aus Marketing-Kalkül. Seit mehr als dreißig Jahren arbeite und lebe ich in Bayreuth.</p>
          <p>Ich kenne die Unternehmen, die in Oberfranken ihren Standort haben. Ich kenne die Verwaltungen. Und ich kenne die Lücken. Als ehrenamtlicher Zusammenschluss arbeiten wir gemeinsam an konkreten Projekten für unsere Stadt und erweitern uns in ganz Nordbayern.</p>
        </div>
        <div class="reveal">
          <h3 class="caption-3 timeline-title">Was wir bewegt haben</h3>
          <ol class="timeline">
            <li><time>2015</time><span>Beleuchtung für TV-Übertragungen in der Oberfrankenhalle</span></li>
            <li><time>2018</time><span>Museumstag. Bayreuther Kultur sichtbar gemacht</span></li>
            <li><time>2021</time><span>Corona-Kampagne. Infektionsketten durchbrechen</span></li>
            <li><time>2024</time><span>Bürgerstarwahl und Bürgerball. Anerkennung für Engagement</span></li>
            <li><time>2025</time><span>Stern am Bayreuther Weihnachtsbaum</span></li>
            <li><time>2026</time><span>Bürgerstarwahl und Bürgerball sowie die Renovierung des Personendurchganges Dürschnitz und Königsallee</span></li>
          </ol>
        </div>
      </div>
    </section>

    <section class="section on-champagne on-light" aria-labelledby="werte-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Die Werte</p>
          <h2 class="heading-2" id="werte-title">Woran wir uns messen lassen.</h2>
        </div>
        <div class="observations">
          <article class="observation reveal"><p class="num" aria-hidden="true">I</p><h3 class="heading-5">Engagement statt Stillstand</h3><p>Was in der Chefetage im Großen geleistet wird, kann im Kleinen jeder tun. Wir erkennen Handlungsbedarf und setzen gemeinsam Lösungen um.</p></article>
          <article class="observation reveal"><p class="num" aria-hidden="true">II</p><h3 class="heading-5">Konstruktiv und kritisch</h3><p>Wir suchen im Dialog nach besseren Lösungen, bringen unseren Sach- und Fachverstand ein und bleiben im Austausch mit der Verwaltung.</p></article>
          <article class="observation reveal"><p class="num" aria-hidden="true">III</p><h3 class="heading-5">Transparent im Handeln</h3><p>Wir stellen Informationen rechtzeitig und vollständig zur Verfügung. Prozesse und Entscheidungen bleiben nachvollziehbar.</p></article>
        </div>
      </div>
    </section>

    <section class="tagline on-deep" aria-label="Anliegen">
      <div class="wrap">
        <p data-reveal-words>Wir fördern den Dialog zwischen Bürgern und Verwaltung. <span data-gold>Gemeinsam gestalten wir unsere Stadt.</span></p>
      </div>
    </section>

    <section class="section on-light" aria-labelledby="haltung-title">
      <div class="wrap">
        <div class="section-head reveal">
          <p class="eyebrow caption-3">Dieselbe Haltung im Beruf</p>
          <h2 class="heading-2" id="haltung-title">Lösungen liefern. Ergebnisse schaffen.</h2>
          <p class="body-lg">Diese Haltung bringe ich in jedes Beratungsmandat. Keine Berichte, die in Schubladen verschwinden. Unser persönliches Engagement versteht sich als Vorbild: für Bürger, für Unternehmer und für alle, die in dieser Stadt Verantwortung tragen können.</p>
        </div>
        <p class="reveal"><a class="btn btn-dark" href="{R}leistungen/">Zu den Leistungen ''' + ARROW + '''</a></p>
      </div>
    </section>

''' + final_cta("Sie wollen sich für Bayreuth einbringen?", "Schreiben Sie uns über die Anfrage, womit Sie die Stadt voranbringen möchten.")
urls.append(page("engagement/index.html", "Soziales Engagement für Bayreuth | Bettina Angerer",
                 "Bettina Angerer engagiert sich ehrenamtlich für Bayreuth und Oberfranken: Projekte, Werte und Haltung eines Zusammenschlusses von Bürgern und Unternehmern.",
                 body, current="engagement/", crumbs=crumbs))

# ================================================================ Kontakt
crumbs = [("kontakt/", "Kontakt")]
tel = ORG["phone"].replace(" ", "")
body = page_hero("Kontakt", "So erreichen Sie Bettina Angerer.",
                 "Am schnellsten geht es über die Anfrage in sechs kurzen Fragen. Sie können aber auch anrufen oder schreiben.", crumbs) + f'''
    <section class="section on-light" aria-labelledby="kontakt-title">
      <div class="wrap contact">
        <div class="contact-card reveal">
          <p class="eyebrow caption-3">Erstgespräch</p>
          <h2 class="heading-3" id="kontakt-title">Anfrage in sechs Fragen</h2>
          <p>Umsatz, Mitarbeiter, Tätigkeitsbereich, Branche und ein Satz zu Ihrem Anliegen. Danach meldet sich Bettina Angerer persönlich.</p>
          {cta("{R}", cls="btn btn-dark")}
        </div>
        <div class="contact-card reveal">
          <p class="eyebrow caption-3">Direkt</p>
          <h2 class="heading-3">Angerer Consulting</h2>
          <address>
            Bettina Angerer<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}
          </address>
          <ul class="contact-list">
            <li><span class="caption-3">Telefon</span><a href="tel:{tel}">{ORG["phone_display"]}</a></li>
            <li><span class="caption-3">E-Mail</span><a href="mailto:{ORG["email"]}">{ORG["email"]}</a></li>
          </ul>
        </div>
      </div>
    </section>
'''
urls.append(page("kontakt/index.html", "Kontakt | Bettina Angerer, Unternehmensberatung Bayreuth",
                 "Kontakt zu Bettina Angerer, Angerer Consulting: Heinrich-Fickenscher-Str. 5A, 95448 Bayreuth. Erstgespräch in sechs kurzen Fragen anfragen.",
                 body, current="kontakt/", schema=[ORG_SCHEMA], crumbs=crumbs))


# ================================================================ Rechtliches
def legal_page(slug, name, inner, desc):
    crumbs = [(f"{slug}/", name)]
    body = f'''    <section class="section on-light legal-section">
      <div class="wrap legal">
        <nav class="crumbs caption-3" aria-label="Brotkrumen"><a href="{{R}}">Startseite</a><span aria-hidden="true">/</span><span aria-current="page">{name}</span></nav>
{inner}
      </div>
    </section>
'''
    urls.append(page(f"{slug}/index.html", f"{name} | Bettina Angerer", desc, body, crumbs=crumbs))


def esc(t):
    t = html.escape(t, quote=False).replace("­", "")
    t = re.sub(r"(https?://[^\s<]+?)([.,)]?)(\s|$)", r'<a href="\1" rel="noopener">\1</a>\2\3', t)
    return re.sub(r"(?<![\w/@.])(www\.[\w.-]+\.\w+)", r'<a href="https://\1" rel="noopener">\1</a>', t)


legal_page("impressum", "Impressum", f'''        <h1 class="heading-2">Impressum</h1>
        <h2>Angaben gemäß § 5 DDG</h2>
        <p>Bettina Angerer<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}</p>
        <h2>Kontakt</h2>
        <p>Telefon: <a href="tel:{tel}">{ORG["phone_display"]}</a><br>E-Mail: <a href="mailto:{ORG["email"]}">{ORG["email"]}</a></p>
        <h2>Umsatzsteuer-ID</h2>
        <p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br>{ORG["vat"]}</p>
        <h2>Redaktionell verantwortlich</h2>
        <p>Bettina Angerer<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}</p>
        <h2>EU-Streitschlichtung</h2>
        <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" rel="noopener">https://ec.europa.eu/consumers/odr/</a>.<br>Unsere E-Mail-Adresse finden Sie oben im Impressum.</p>
        <h2>Verbraucherstreitbeilegung und Universalschlichtungsstelle</h2>
        <p>Wir nehmen an einem Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teil. Zuständig ist die Universalschlichtungsstelle des Zentrums für Schlichtung e.V., Straßburger Straße 8, 77694 Kehl am Rhein (<a href="https://www.verbraucher-schlichter.de" rel="noopener">https://www.verbraucher-schlichter.de</a>).</p>
        <h2>Bildnachweise</h2>
        <p><span class="placeholder">{{{{Fotograf des Portraits}}}}</span>. Die gezeigten Logos sind Marken der jeweiligen Unternehmen und dienen als Referenz.</p>''',
           "Impressum von Bettina Angerer, Angerer Consulting, Heinrich-Fickenscher-Str. 5A, 95448 Bayreuth.")

# Datenschutz: anwendbare Abschnitte der bisherigen Erklärung, ergänzt um den Stand der neuen Seite.
ds = [l.strip() for l in (ROOT / "content/legal/datenschutz.txt").read_text().split("\n") if l.strip()]
HEAD = re.compile(r"^(\d+)\.(\d+)?\s+(.*)$")


def ds_block(a, b, drop=()):
    out, in_list = [], False
    for i in range(a, b + 1):
        if i in drop:
            continue
        l = ds[i]
        m = HEAD.match(l)
        is_item = bool(m) and not m.group(2) and l.endswith((',', '.', 'sowie'))
        if m and not is_item:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<h3>{esc(m.group(3))}</h3>" if m.group(2) else f"<h2>{esc(m.group(3))}</h2>")
        elif m and is_item:
            if not in_list:
                out.append("<ul>"); in_list = True
            out.append(f"<li>{esc(m.group(3))}</li>")
        else:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<p>{esc(l)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n        ".join(out)


i_rights = next(i for i, l in enumerate(ds) if l.startswith("12. Ihre Rechte"))
i_stand = next(i for i, l in enumerate(ds) if l.startswith("15. Aktualität"))
i_legal = next(i for i, l in enumerate(ds) if l.startswith("5. Rechtsgrundlage"))
i_cookies = next(i for i, l in enumerate(ds) if l.startswith("7. Cookies"))
i_contact = next(i for i, l in enumerate(ds) if l.startswith("8.1 Kontaktaufnahme"))
i_resp = next(i for i, l in enumerate(ds) if l.startswith("2. Verantwortlicher"))
i_defs = next(i for i, l in enumerate(ds) if l.startswith("4. Begriffsbestimmungen"))

legal_page("datenschutz", "Datenschutz", f'''        <h1 class="heading-2">Datenschutzerklärung</h1>
        <p class="legal-note">Diese Fassung übernimmt die weiterhin zutreffenden Abschnitte der bisherigen Erklärung und beschreibt den technischen Stand der neuen Website. Vor dem Livegang muss sie vom Datenschutzbeauftragten geprüft und um die Angaben zum endgültigen Hosting ergänzt werden.</p>
        <h2>Einleitung</h2>
        <p>{esc(ds[2])}</p>
        <p>{esc(ds[4])}</p>
        {ds_block(i_resp, i_defs - 1)}
        {ds_block(i_legal, i_cookies - 1)}
        <h2>Hosting</h2>
        <p><span class="placeholder">{{{{Name und Anschrift des Hosting-Anbieters, Ort der Verarbeitung, Hinweis auf den Vertrag zur Auftragsverarbeitung}}}}</span></p>
        <h2>Cookies, Schriften und eingebundene Dienste</h2>
        <p>Diese Website setzt keine Cookies. Alle Schriften, Bilder und Skripte werden vom eigenen Server ausgeliefert. Es werden keine Inhalte von Drittanbietern wie Kartendienste, Videos oder Schriftbibliotheken eingebunden.</p>
        <h2>Webanalyse</h2>
        <p>Derzeit wird kein Werkzeug zur Webanalyse eingesetzt. <span class="placeholder">{{{{Falls ein Analysewerkzeug eingeführt wird: Anbieter, Zweck, Rechtsgrundlage, Speicherdauer und Widerspruchsmöglichkeit hier ergänzen}}}}</span></p>
        <h2>Kontaktaufnahme und Anfrageformular</h2>
        <p>{esc(ds[i_contact + 1])}</p>
        <p>Das Anfrageformular dieser Website überträgt selbst keine Daten an einen Server. Es bereitet aus Ihren Angaben (Jahresumsatz, Mitarbeiterzahl, Tätigkeitsbereich, Branche, Anliegen, Unternehmen, Name, E-Mail-Adresse und optional Telefonnummer) eine E-Mail in Ihrem eigenen E-Mail-Programm vor, die Sie selbst absenden.</p>
        {ds_block(i_rights, i_stand - 1)}
        <h2>Aktualität und Änderung der Datenschutzerklärung</h2>
        <p>Stand: November 2026.</p>
        <p>{esc(ds[i_stand + 2])}</p>''',
           "Datenschutzerklärung von Bettina Angerer, Angerer Consulting, Bayreuth.")

dv = [l.strip() for l in (ROOT / "content/legal/datenverarbeitung.txt").read_text().split("\n") if l.strip()]
out, in_list, addr = [], False, []
for n, l in enumerate(dv):
    l = l.split("||")[0].strip()
    if n == 0:
        continue
    if l.startswith("- "):
        if not in_list:
            out.append("<ul>"); in_list = True
        out.append(f"<li>{esc(l[2:])}</li>")
        continue
    if in_list:
        out.append("</ul>"); in_list = False
    if l.endswith("?") or l in ("Ihre Rechte als „Betroffene“", "Unser Datenschutzbeauftragter", "Beschwerderecht"):
        out.append(f"<h2>{esc(l)}</h2>")
    elif l:
        out.append(f"<p>{esc(l)}</p>")
legal_page("datenverarbeitung", "Datenverarbeitung",
           '        <h1 class="heading-2">Grundsätze der Datenverarbeitung bei Bettina Angerer</h1>\n        ' + "\n        ".join(out) + "\n        <p>Stand: 01.07.2020</p>",
           "Grundsätze der Datenverarbeitung bei Bettina Angerer: Informationen nach Art. 12 ff. DSGVO.")

# ================================================================ 404, Sitemap, Robots
body404 = '''    <section class="section on-light">
      <div class="wrap legal">
        <p class="eyebrow caption-3">Fehler 404</p>
        <h1 class="heading-2">Diese Seite gibt es nicht.</h1>
        <p class="body-lg">Die Adresse ist falsch geschrieben oder die Seite wurde verschoben. Auf der Startseite finden Sie alle Leistungen und die Anfrage.</p>
        <p style="margin-top:32px"><a class="btn btn-dark" href="/">Zur Startseite</a></p>
      </div>
    </section>
'''
page("404.html", "Seite nicht gefunden | Bettina Angerer", "Diese Seite gibt es nicht.", body404)
# Die Fehlerseite kann in jeder Tiefe ausgeliefert werden.
p404 = ROOT / "404.html"
t = p404.read_text()
# Relative Pfade über ein <base> auflösen: Domainwurzel, auf GitHub Pages der Projektordner.
t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  <script>document.write(\'<base href="\' + (/github\\.io$/.test(location.hostname) ? \'/\' + location.pathname.split(\'/\')[1] + \'/\' : \'/\') + \'">\');</script>', 1)
t = t.replace('href="/">Zur Startseite', 'href="./">Zur Startseite')
t = re.sub(r'\s*<link rel="canonical"[^>]*>', '\n  <meta name="robots" content="noindex">', t)
p404.write_text(t)

sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
prio = {"": "1.0", "leistungen/": "0.9", "ueber-bettina/": "0.8", "kontakt/": "0.7", "engagement/": "0.6"}
for u in urls:
    p = prio.get(u, "0.8" if u.startswith("leistungen/") else "0.3")
    sm += f"  <url><loc>{SITE}/{u}</loc><priority>{p}</priority></url>\n"
(ROOT / "sitemap.xml").write_text(sm + "</urlset>\n")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print("Seiten:", len(urls) + 1)
for u in urls:
    print("  /" + u)
