#!/usr/bin/env python3
"""Baut die statische Website von Bettina Angerer Consulting.

Aufruf:  python3 build.py
Erzeugt alle HTML-Seiten, sitemap.xml und robots.txt im Projektordner.
Inhalte stehen in diesem Skript, wiederkehrende Teile in partials/.
Alles, was sich ein- und ausblenden lässt, steht im Block SCHALTER direkt hier unten.
"""
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://www.bettina-angerer.de"
VERSION = "20"

# ================================================================ SCHALTER
# Team von Marvin Angerer als eigenes Versprechen zeigen (Hero, Leistungen).
# Erst auf True stellen, wenn Bettina und Marvin das freigegeben haben.
SHOW_TEAM = False

# Kundenlogos zeigen. Erst nach Freigabe auf True stellen und unten bei
# CLIENT_LOGOS eintragen, welche Logos gezeigt werden dürfen.
SHOW_CLIENT_LOGOS = False
CLIENT_LOGOS = []  # z. B. ["Red Bull", "DZ Bank"]; Dateien liegen in assets/img/logos/

# Siegel „Zertifizierte Beratung“ des BVMW. Gültig mindestens bis Ende 2027.
# Auf False stellen, wenn es nicht verlängert wird: dann verschwindet es überall.
SHOW_BVMW_SEAL = True

# Kennzahlen im Hero. Die Netzwerkzahl ersetzen, sobald Bettina sie nennt.
STATS = [
    ("30+", "Jahre im und für den Mittelstand"),
    ("Hunderte", "Unternehmerinnen und Unternehmer in meinem Netzwerk"),
]

# Fallbeispiele. Solange die Liste leer ist, erscheint der Abschnitt nicht.
# Jedes Beispiel: {"titel", "branche", "ausgang", "vorgehen", "ergebnis", "zahl" (optional)}
CASES = []

# Kurzes Video von Bettina im Über-mich-Teil, z. B. "assets/video/bettina.mp4"
# (selbst gehostet, kein YouTube). None = kein Video.
VIDEO = None
VIDEO_POSTER = "assets/img/portrait.jpg"

# Marvin Angerer. Text und Foto kommen von Bettina und Marvin; bis dahin ein neutraler Satz.
MARVIN = {
    "photo": None,  # z. B. "assets/img/marvin.jpg" (Hochformat 3:4)
    "text": [
        "Marvin Angerer ist mein Partner bei Bettina Angerer Consulting. Sein Schwerpunkt sind Vertrieb, Social Media und Content: Er sorgt dafür, dass Ihr Unternehmen die Menschen erreicht, die heute Ihre Kunden sind.",
    ],
}

ORG = {
    "name": "Bettina Angerer Consulting",
    "person": "Bettina Angerer",
    "partner": "Marvin Angerer",
    "street": "Heinrich-Fickenscher-Str. 5A",
    "zip": "95448",
    "city": "Bayreuth",
    "phone": "+49 172 8640338",
    "phone_display": "+49 (0) 172 / 86 40 338",
    "email": "info@bettina-angerer.de",
    "vat": "DE298988354",
}
NAME = ORG["name"]
CLAIM = "Strategische Unternehmensberatung für den Mittelstand"

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


def logo_list(names, R="{R}"):
    out = []
    for n in names:
        if n in LOGOS:
            f, ar, k = LOGOS[n]
            u = f"{R}assets/img/logos/{f}"
            out.append(f'<li><span class="logo" role="img" aria-label="{n}" style="-webkit-mask-image:url({u});mask-image:url({u});aspect-ratio:{ar};--k:{k}"></span></li>')
        else:
            out.append(f'<li><span class="logo-text">{n}</span></li>')
    return '<ul class="logos" aria-label="Referenzen">' + "".join(out) + "</ul>"


def client_logos(label="Marvin Angerer und sein Team haben gearbeitet für"):
    if not (SHOW_CLIENT_LOGOS and CLIENT_LOGOS):
        return ""
    return f'''
    <section class="refs" aria-label="Referenzen">
      <div class="wrap">
        <p class="refs-label">{label}</p>
        {logo_list(CLIENT_LOGOS)}
      </div>
    </section>
'''


ARROW = '<svg class="arrow" width="16" height="16" aria-hidden="true"><use href="#arrow"/></svg>'
STRAND = '<svg class="strand-divider" aria-hidden="true" preserveAspectRatio="none"><use href="#strand"/></svg>'
TEL = ORG["phone"].replace(" ", "")


def cta(label="Erstgespräch anfragen", cls="btn"):
    return f'<a class="{cls}" href="{{R}}kontakt/" data-open-wizard>{label} {ARROW}</a>'


def seal_block(cls="cert"):
    """Siegel des BVMW. Ein Schalter blendet es überall aus."""
    if not SHOW_BVMW_SEAL:
        return ""
    return f'''<div class="{cls}">
            <img class="seal" src="{{R}}assets/img/bvmw-zertifiziert.png" width="324" height="283" loading="lazy" alt="Siegel: Zertifizierte Beratung für mittelständische Unternehmen, Beratungsnetzwerk Mittelstand">
            <p>Zertifizierte Beratung für mittelständische Unternehmen im Beratungsnetzwerk Mittelstand.</p>
          </div>'''


# ---------------------------------------------------------------- Leistungen
# Reihenfolge = Gewichtung. Strategie zuerst, Social Media ist ein Teil, nicht das Ganze.
SERVICES = [
    {
        "slug": "strategie", "name": "Strategie und Sanierung",
        "lead": "Ich finde die Stellen, an denen in Ihrem Unternehmen Geld verloren geht oder liegen bleibt.",
        "intro": "Wenn die Zahlen nicht stimmen, liegt das selten an einer einzigen Ursache. Ich schaue mir jede Abteilung an, vom Einkauf über Personal und Vertrieb bis zur Buchhaltung, und sage Ihnen offen, was ich sehe. Daraus entsteht ein Plan, der sich in Ihren Zahlen zeigt.",
        "pains": [
            ("Der Umsatz stimmt, der Gewinn nicht", "Es wird viel gearbeitet und verkauft, aber am Jahresende bleibt zu wenig übrig."),
            ("Kosten laufen weiter, der Nutzen nicht", "Verträge, Abläufe und Ausgaben, die irgendwann sinnvoll waren, laufen einfach weiter."),
            ("Die Nachfolge ist offen", "Der Generationswechsel steht an, aber es gibt noch keinen Plan, wie das Unternehmen übergeben wird."),
            ("Für Neues fehlt das Geld", "Investitionen scheitern am Etat, und Förderprogramme bleiben ungenutzt, weil niemand Zeit für den Antrag hat."),
        ],
        "items": [
            ("Unternehmensanalyse", "Zahlen, Strukturen und Abläufe, klar und ehrlich bewertet.",
             "Ich gehe mit Ihnen durch jede Abteilung und lasse mir zeigen, wie dort gearbeitet wird. Am Ende steht eine schriftliche Einschätzung: wo Ihr Unternehmen Geld verliert, wo es Geld liegen lässt und was Sie zuerst angehen sollten."),
            ("Restrukturierung und Turnaround", "Begleitung, bis die Zahlen wieder schwarz sind.",
             "Wenn es eng wird, braucht es Entscheidungen, die im Alltag gern aufgeschoben werden. Ich bereite sie mit Ihnen vor, spreche mit Banken und Partnern und bleibe dabei, bis die Maßnahmen greifen."),
            ("Prozessoptimierung", "Einkauf, Personal, Vertrieb, Marketing und Finanzen.",
             "Viele Abläufe sind über Jahre gewachsen und kosten mehr Zeit, als sie müssten. Wir räumen sie gemeinsam auf, Abteilung für Abteilung, ohne den laufenden Betrieb zu stören."),
            ("Unternehmensnachfolge", "Die Übergabe planen, bevor sie drängt.",
             "Ob Familie, Führungskräfte oder ein externer Käufer: Eine Nachfolge braucht Jahre Vorlauf. Ich helfe Ihnen, das Unternehmen übergabefähig zu machen, und begleite die Gespräche zwischen den Generationen."),
            ("Finanzierung und Förderung", "Fördermittel abrufen und Vorhaben sauber budgetieren.",
             "Für Digitalisierung, Weiterbildung und Beratung gibt es Förderprogramme. Ich prüfe, welche für Sie in Frage kommen, und lege für jedes Vorhaben Budget, Meilensteine und Kennzahlen fest. So wissen Sie jederzeit, was es kostet und was es bringt."),
        ],
        "title": f"Strategie, Sanierung und Nachfolge | {NAME}",
        "desc": "Unternehmensanalyse, Restrukturierung, Prozessoptimierung, Nachfolge und Förderung: Bettina Angerer bringt mittelständische Unternehmen zurück in die schwarzen Zahlen.",
    },
    {
        "slug": "netzwerk", "name": "Netzwerk und Politik",
        "lead": "Ich bringe Sie mit den Menschen zusammen, die Ihr Vorhaben voranbringen.",
        "intro": "In mehr als dreißig Jahren ist ein Netzwerk gewachsen, das von Unternehmerinnen und Unternehmern über Verbände bis in die Politik reicht, von der Kommune über Landtag und Bundestag bis nach Brüssel. Wo Ihr Unternehmen jemanden braucht, den ich nicht ersetzen kann, stelle ich den Kontakt her.",
        "pains": [
            ("Der passende Partner fehlt", "Sie suchen einen Lieferanten, einen Kooperationspartner oder einen Spezialisten, kennen aber niemanden, dem Sie vertrauen."),
            ("Ein Vorhaben steckt fest", "Genehmigungen, Förderzusagen oder Gespräche mit Behörden kommen nicht voran, weil der richtige Ansprechpartner fehlt."),
        ],
        "items": [
            ("Unternehmen verbinden", "Kooperationen, Kunden und Partner aus meinem Netzwerk.",
             "Ich kenne viele Unternehmen persönlich und weiß, wer was kann. Wenn zwei zueinander passen, bringe ich sie an einen Tisch. Das gilt für Kooperationen ebenso wie für neue Kunden oder Lieferanten."),
            ("Kontakte in die Politik", "Von der Kommune bis zur EU.",
             "Ich weiß, wer in Rathaus, Landtag, Bundestag und in Brüssel für welches Thema zuständig ist. Ich helfe Ihnen, Ihr Anliegen dort vorzubringen, wo darüber entschieden wird."),
            ("Internationale Kontakte", "Mittelstandsnetzwerke in vielen Ländern.",
             "Über die Mittelstandsarbeit der letzten Jahre habe ich Kontakte in zahlreiche Länder. Wenn Sie einen neuen Markt prüfen, finde ich Ansprechpartner, die ihn kennen."),
            ("Spezialisten auf Empfehlung", "Wo ich nicht selbst helfe, nenne ich jemanden, der es kann.",
             "Steuerfragen, Recht, Technik: Manche Aufgaben gehören in andere Hände. Ich empfehle Ihnen nur Menschen, mit denen ich selbst gute Erfahrungen gemacht habe."),
        ],
        "title": f"Netzwerk und politische Kontakte für den Mittelstand | {NAME}",
        "desc": "Bettina Angerer verbindet Unternehmen miteinander und öffnet Türen von der Kommune über Landtag und Bundestag bis nach Brüssel.",
    },
    {
        "slug": "coaching", "name": "Coaching für Unternehmer",
        "lead": "Ich bilde Unternehmerinnen und Unternehmer darin aus, ihr Haus strategisch zu führen.",
        "intro": "Viele Inhaber sind hervorragend in ihrem Fach und stecken trotzdem jeden Tag im operativen Geschäft fest. Im Coaching arbeiten wir daran, dass Sie Ihr Unternehmen von oben sehen: mit klaren Zahlen, klaren Prioritäten und Entscheidungen, die Sie auch vor Ihrem Team vertreten können.",
        "pains": [
            ("Keine Zeit für Strategie", "Das Tagesgeschäft frisst die Woche. Für die Frage, wohin das Unternehmen in fünf Jahren soll, bleibt nichts übrig."),
            ("Allein mit den großen Entscheidungen", "Mit dem Team können Sie nicht über alles sprechen, mit der Familie wollen Sie es nicht. Es fehlt ein Gegenüber, das offen widerspricht."),
        ],
        "items": [
            ("Strategische Unternehmensführung", "Ein Programm, das Sie Schritt für Schritt aufbauen.",
             "Wir arbeiten an Ihren eigenen Zahlen und Fragen: Wie lese ich meine Auswertungen richtig, woran erkenne ich früh, dass etwas schiefläuft, und wie setze ich Prioritäten, die das Team mitträgt?"),
            ("Sparring auf Augenhöhe", "Vertraulich, direkt und regelmäßig.",
             "In festen Abständen sprechen wir über das, was Sie gerade beschäftigt. Ich sage Ihnen, was ich sehe, auch wenn es unbequem ist. Was Sie daraus machen, entscheiden Sie."),
            ("Führung im Generationswechsel", "Wenn erfahrene Führung auf ein junges Team trifft.",
             "Ältere und jüngere Mitarbeiter haben oft unterschiedliche Vorstellungen von Arbeit. Ich vermittle zwischen beiden Seiten, damit das Wissen der einen und der Schwung der anderen dem Unternehmen zugutekommen."),
            ("Weiterbildung für Ihr Team", "Workshops vor Ort, an echten Aufgaben.",
             "Praktiker aus meinem Netzwerk schulen Ihre Mitarbeiter direkt bei Ihnen im Haus. So bleibt das Wissen im Unternehmen und wird sofort angewendet."),
        ],
        "title": f"Coaching und Ausbildung in strategischer Unternehmensführung | {NAME}",
        "desc": "Coaching, Sparring und Ausbildung für Inhaberinnen und Inhaber, die ihr Unternehmen strategisch führen wollen. Bettina Angerer Consulting.",
    },
    {
        "slug": "vertrieb", "name": "Vertrieb", "partner": True,
        "lead": "Neue Kunden gewinnen, ohne Ihre Mannschaft von den bestehenden abzuziehen.",
        "intro": "Viele Mittelständler leben von Empfehlungen und Stammkunden. Das trägt lange, wächst aber nicht von allein. Gemeinsam mit meinem Partner Marvin Angerer baue ich Ihnen einen zweiten Weg zu neuen Kunden auf: planbar, messbar und so, dass Ihr Team dabei entlastet wird.",
        "pains": [
            ("Empfehlungen reichen nicht mehr", "Der Auftragseingang hängt an wenigen Kontakten. Fällt einer weg, fehlt Umsatz."),
            ("Kaltakquise bleibt liegen", "Niemand im Team hat Zeit, täglich fremde Menschen anzuschreiben und nachzufassen."),
            ("Neue Märkte sind ein Risiko", "Sie vermuten Potenzial in einer neuen Zielgruppe, wollen dafür aber nicht gleich Personal umschichten."),
        ],
        "items": [
            ("Akquise über LinkedIn und Instagram", "Ihre Zielkunden finden und persönlich ansprechen.",
             "Ein System sucht nach Menschen, die zu Ihrer Zielgruppe passen, und prüft vorab deren Unternehmen. Jede Nachricht geht einzeln und persönlich raus, wer nicht antwortet, wird zur richtigen Zeit erinnert. Der tägliche Aufwand liegt bei rund zehn Minuten, und Sie sehen schwarz auf weiß, welche Ansprache funktioniert."),
            ("Testballon für neue Zielgruppen", "Erst im kleinen Versuch prüfen, ob sich ein Weg lohnt.",
             "Bevor Sie Mitarbeiter und Budget auf einen neuen Markt ansetzen, testen wir ihn: eine klar umrissene Zielgruppe, eine begrenzte Laufzeit, messbare Antworten. Danach entscheiden Sie anhand von Zahlen."),
            ("Vertriebsstrategie", "Ein klarer Plan, wer wen wann anspricht.",
             "Wir ordnen Ihre Vertriebsrichtungen: Fachkunden, Endkunden, Großkunden. Für jede legen wir fest, welche Ansprache passt, welche Kanäle sich lohnen und woran Sie Erfolg erkennen."),
        ] + ([
            ("Betreuung großer Kunden", "Erfahrung aus der Arbeit mit Konzernen und Sendern.",
             "Große Kunden haben eigene Abläufe, Einkaufsregeln und Erwartungen. Marvin Angerer und sein Team kennen diese Welt aus der täglichen Arbeit und begleiten Sie von der ersten Anfrage bis zur laufenden Zusammenarbeit."),
        ] if SHOW_TEAM else []),
        "title": f"Vertrieb und Neukundengewinnung | {NAME}",
        "desc": "Neue Kunden gewinnen mit Akquise über LinkedIn und Instagram, Testläufen für neue Zielgruppen und einer klaren Vertriebsstrategie.",
    },
    {
        "slug": "marketing", "name": "Marketing und Social Media", "partner": True,
        "lead": "Inhalte, die Ihre Kunden dort erreichen, wo sie heute sind.",
        "intro": "Klassische Werbung verliert an Wirkung, weil sich Ihr Publikum verändert hat. Was heute trägt, sind Inhalte, die Menschen freiwillig ansehen: geplant, verlässlich produziert und messbar. Hier arbeite ich eng mit meinem Partner Marvin Angerer zusammen, der diese Welt aus dem Alltag kennt.",
        "pains": [
            ("Anzeigen verpuffen", "Was vor fünf Jahren noch getragen hat, bringt heute kaum Rückmeldung."),
            ("Kein Gesicht nach außen", "Ihre Kunden wollen sehen, wer hinter dem Unternehmen steht. Im Netz finden sie wenig."),
            ("Social Media bleibt liegen", "Das Thema steht auf jeder Liste, aber niemand im Haus hat Zeit oder Erfahrung dafür."),
            ("Die Generationen verstehen sich nicht", "Die Chefetage und die Zielgruppe sprechen unterschiedliche Sprachen. Das kostet Reichweite und Vertrauen."),
        ],
        "items": [
            ("Content-Strategie", "Was Sie zeigen, wem und wo.",
             "Wir klären, welche Themen Ihr Unternehmen glaubwürdig besetzen kann, auf welchen Plattformen Ihre Kunden unterwegs sind und in welchem Rhythmus Inhalte erscheinen. Das Ergebnis ist ein Redaktionsplan, den Sie verstehen und freigeben."),
            ("Content-Produktion", "Dreh, Schnitt, Grafik und Text aus einer Hand.",
             "Sie stellen Ihr Wissen und Ihre Menschen vor die Kamera, um alles Weitere kümmern wir uns und liefern fertige Beiträge, die zur jeweiligen Plattform passen."),
            ("Personal Branding", "Ihr Auftritt als Unternehmerin oder Unternehmer.",
             "Menschen kaufen von Menschen. Wir entwickeln Ihren persönlichen Auftritt: Positionierung, Bildsprache und Profile. So werden Sie sichtbar, ohne sich zu verbiegen."),
            ("Zusammenarbeit mit Creatorn", "Die richtigen Gesichter für Ihr Produkt.",
             "Wenn es schneller gehen soll, erreichen Sie über Creator Menschen, die Ihrer Marke sonst nicht begegnen würden. Wir wählen passende Partner aus, verhandeln und begleiten die Zusammenarbeit."),
        ] + ([
            ("Produktdesign", "Verpackung und Auftritt, die im Regal und im Bild funktionieren.",
             "Vom Getränkekühlschrank bis zur Verpackung: Marvin Angerer und sein Team gestalten Produkte so, dass sie im Handel auffallen und auf Fotos und Videos gut aussehen."),
        ] if SHOW_TEAM else []),
        "title": f"Marketing und Social Media für den Mittelstand | {NAME}",
        "desc": "Content-Strategie, Content-Produktion, Personal Branding und Creator-Kooperationen für mittelständische Unternehmen, gemeinsam mit Marvin Angerer.",
    },
]

FAQ = [
    ("Arbeiten Sie nur in Bayern?", "Nein. Mein Sitz ist in Bayreuth, ich arbeite aber für Unternehmen in ganz Deutschland, in Österreich und in der Schweiz. Gespräche führe ich vor Ort oder per Video, je nachdem, was die Aufgabe verlangt."),
    ("Was passiert nach meiner Anfrage?", "Ich lese jede Anfrage selbst und rufe Sie für ein Erstgespräch an. Wenn ich nicht die Richtige für Ihr Anliegen bin, sage ich Ihnen das offen und nenne Ihnen jemanden aus meinem Netzwerk, der besser passt."),
    ("Was ist ein Testballon?", "Ein kleiner, zeitlich begrenzter erster Schritt, dessen Ergebnis sich messen lässt. Zum Beispiel sprechen wir eine neue Zielgruppe an und zählen, wie viele antworten, oder wir prüfen eine Abteilung, bevor wir das ganze Unternehmen umbauen. Erst wenn die Zahlen stimmen, wird daraus ein größeres Projekt."),
    ("Welche Rolle hat Marvin Angerer?", "Marvin Angerer ist mein Partner bei Bettina Angerer Consulting. Sein Schwerpunkt sind Vertrieb, Social Media und Content. Ihre erste Ansprechpartnerin bin ich. Wenn es um seine Themen geht, ist er von Anfang an mit dabei."),
    ("Muss ich mich mit Social Media auskennen?", "Nein. Sie sagen, was Sie erreichen wollen, wir übersetzen das in Maßnahmen und erklären jeden Schritt in klarer Sprache."),
]

NAV = [("leistungen/", "Leistungen"), ("ueber-mich/", "Über mich"), ("kontakt/", "Kontakt")]

# Ablauf: gilt auf Start- und Leistungsseiten gleich.
PROCESS = [
    ("Anfrage", "Sie beantworten sechs kurze Fragen. Das Wichtigste ist ein Satz dazu, wo es bei Ihnen hakt."),
    ("Mein Anruf", "Ich rufe Sie persönlich an. Wenn es um Vertrieb oder Social Media geht, ist mein Partner Marvin Angerer gleich mit dabei."),
    ("Testballon", "Wir beginnen mit einem kleinen, messbaren Schritt. So sehen Sie früh, ob der Weg trägt."),
    ("Ihre Entscheidung", "Erst wenn die Zahlen stimmen, sprechen wir über ein größeres Projekt. Ob es weitergeht, entscheiden Sie."),
]


def process_html():
    lis = "".join(f'<li><span class="step-no">{i + 1}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(PROCESS))
    return f'<ol class="process">{lis}</ol>'


# ---------------------------------------------------------------- Rahmen
def page(path, title, desc, body, current="", schema=None, crumbs=None, extra_head="", body_cls=""):
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
    mnav = "\n    ".join(nav_link(h, l) for h, l in [("", "Startseite")] + NAV)
    svc_links = "\n            ".join(f'<li><a href="{R}leistungen/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    brand = f'''<a class="brand" href="{R or './'}" aria-label="{NAME}, zur Startseite">
        <svg class="brand-mark" aria-hidden="true"><use href="#mark"/></svg>
        <span class="brand-text"><span class="brand-name">Bettina Angerer</span> <span class="brand-sub">Consulting</span></span>
      </a>'''
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
  <meta property="og:site_name" content="{NAME}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE}/assets/img/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0c2d4a">
  <link rel="icon" href="{R}assets/img/logo-mark.svg" type="image/svg+xml">
  <link rel="preload" href="{R}assets/fonts/source-serif-4.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{R}assets/fonts/libre-franklin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{R}assets/css/styles.css?v={VERSION}">
  <script>
    document.documentElement.classList.remove('no-js');
    // Testumgebung nicht in Suchmaschinen aufnehmen. Auf www.bettina-angerer.de greift das nicht, dort ist die Seite indexierbar.
    if (/github\\.io$|localhost|127\\.0\\.0\\.1/.test(location.hostname)) {{
      var m = document.createElement('meta'); m.name = 'robots'; m.content = 'noindex, nofollow'; document.head.appendChild(m);
    }}
  </script>
{extra_head}{ld}
</head>
<body{f' class="{body_cls}"' if body_cls else ''}>
  {SYMBOLS}
  <a class="skip" href="#inhalt">Zum Inhalt springen</a>

  <div class="strip">Strategische Beratung für den Mittelstand im DACH-Raum. Ausgewählte Mandate.</div>

  <header class="header" id="top">
    <div class="wrap header-inner">
      {brand}
      <nav class="nav" aria-label="Hauptnavigation">
        {nav}
      </nav>
      <a class="btn btn-sm header-cta" href="{R}kontakt/" data-open-wizard>Erstgespräch anfragen</a>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menü öffnen">
        <span></span><span></span>
      </button>
    </div>
  </header>
  <div class="mobile-menu" id="mobile-menu">
    {mnav}
    <a class="btn" href="{R}kontakt/" data-open-wizard>Erstgespräch anfragen {ARROW}</a>
    <a class="mobile-tel" href="tel:{TEL}">{ORG["phone_display"]}</a>
  </div>

  <main id="inhalt">
{body.replace("{R}", R)}
  </main>

  {WIZARD.replace("{R}", R)}
  <footer class="footer">
    <div class="wrap">
      <div class="footer-grid">
        <div>
          {brand}
          <p class="footer-claim">{CLAIM}</p>
        </div>
        <div>
          <h2 class="footer-h">Leistungen</h2>
          <ul>
            {svc_links}
          </ul>
        </div>
        <div>
          <h2 class="footer-h">Kontakt</h2>
          <address>
            {ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}<br>
            <a href="tel:{TEL}">{ORG["phone_display"]}</a><br>
            <a href="mailto:{ORG["email"]}">{ORG["email"]}</a>
          </address>
        </div>
      </div>
      <div class="footer-legal">
        <span>© 2026 {NAME}</span>
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


def page_hero(h1, lead, crumbs, extra=""):
    trail = '<a href="{R}">Startseite</a>' + "".join(
        f'<span aria-hidden="true">/</span><a href="{{R}}{u}">{n}</a>' for u, n in crumbs[:-1]
    ) + f'<span aria-hidden="true">/</span><span aria-current="page">{crumbs[-1][1]}</span>'
    return f'''    <section class="page-hero">
      <div class="wrap">
        <nav class="crumbs" aria-label="Brotkrumen">{trail}</nav>
        <h1>{h1}</h1>
        <p class="lead">{lead}</p>{extra}
      </div>
      {STRAND}
    </section>
'''


def final_cta(heading="Erzählen Sie mir, wo es hakt.", text="Sechs kurze Fragen, eine nach der anderen. Ich lese jede Anfrage persönlich und melde mich bei Ihnen."):
    return f'''    <section class="section final on-navy" aria-labelledby="anfrage-title">
      <div class="wrap final-inner">
        <h2 id="anfrage-title">{heading}</h2>
        <p class="lead">{text}</p>
        <div class="final-actions">
          {cta()}
          <a class="textlink on-dark" href="tel:{TEL}">Oder rufen Sie mich an: {ORG["phone_display"]}</a>
        </div>
      </div>
    </section>
'''


def marvin_card(heading_tag="h3"):
    photo = (f'<img src="{{R}}{MARVIN["photo"]}" width="600" height="800" loading="lazy" alt="Marvin Angerer, Partner bei {NAME}">'
             if MARVIN["photo"] else '<span class="initials" aria-hidden="true">MA</span>')
    text = "".join(f"<p>{t}</p>" for t in MARVIN["text"])
    return f'''<article class="partner">
          <figure class="partner-photo{' is-placeholder' if not MARVIN['photo'] else ''}">{photo}</figure>
          <div>
            <p class="partner-role">Mein Partner</p>
            <{heading_tag} class="partner-name">Marvin Angerer</{heading_tag}>
            {text}
          </div>
        </article>'''


def cases_section():
    if not CASES:
        return ""
    items = ""
    for c in CASES:
        zahl = f'<p class="case-figure">{c["zahl"]}</p>' if c.get("zahl") else ""
        items += f'''
          <article class="case">
            <p class="case-meta">{c["branche"]}</p>
            <h3>{c["titel"]}</h3>
            <dl>
              <dt>Ausgangslage</dt><dd>{c["ausgang"]}</dd>
              <dt>Was wir gemacht haben</dt><dd>{c["vorgehen"]}</dd>
              <dt>Ergebnis</dt><dd>{c["ergebnis"]}</dd>
            </dl>{zahl}
          </article>'''
    return f'''
    <section class="section" aria-labelledby="praxis-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="praxis-title">Aus der Praxis</h2>
          <p class="lead">Einige Unternehmen, die ich begleitet habe. Namen nenne ich nur, wenn die Inhaber zugestimmt haben.</p>
        </div>
        <div class="cases">{items}
        </div>
      </div>
    </section>
'''


ORG_SCHEMA = {
    "@context": "https://schema.org", "@type": "ProfessionalService", "@id": f"{SITE}/#organisation",
    "name": NAME, "description": CLAIM,
    "url": f"{SITE}/", "image": f"{SITE}/assets/img/portrait.jpg", "logo": f"{SITE}/assets/img/logo-mark.svg",
    "telephone": ORG["phone"], "email": ORG["email"],
    "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"],
                "addressLocality": ORG["city"], "addressCountry": "DE"},
    "areaServed": [{"@type": "Country", "name": n} for n in ("Deutschland", "Österreich", "Schweiz")],
    "founder": {"@id": f"{SITE}/ueber-mich/#person"},
    "member": [{"@id": f"{SITE}/ueber-mich/#person"}, {"@type": "Person", "name": ORG["partner"], "jobTitle": "Partner"}],
    "knowsAbout": ["Unternehmensberatung", "Sanierung", "Restrukturierung", "Unternehmensnachfolge", "Strategische Unternehmensführung", "Coaching", "Vertrieb", "Social Media", "Mittelstand"],
}
PERSON_SCHEMA = {
    "@context": "https://schema.org", "@type": "Person", "@id": f"{SITE}/ueber-mich/#person",
    "name": "Bettina Angerer", "jobTitle": "Unternehmensberaterin", "url": f"{SITE}/ueber-mich/",
    "image": f"{SITE}/assets/img/portrait.jpg", "worksFor": {"@id": f"{SITE}/#organisation"},
}

urls = []

# ================================================================ Startseite
stats = "".join(f'<div class="stat"><dt>{n}</dt><dd>{l}</dd></div>' for n, l in STATS)
svc_rows = "".join(f'''
          <li>
            <a href="{{R}}leistungen/{s["slug"]}/">
              <h3>{s["name"]}</h3>
              <p>{s["lead"]}{' <span class="with">Gemeinsam mit Marvin Angerer.</span>' if s.get("partner") else ''}</p>
              {ARROW}
            </a>
          </li>''' for s in SERVICES)
faq_html = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)

if SHOW_TEAM:
    hero_sub = "Ich berate Inhaberinnen und Inhaber mittelständischer Unternehmen in Deutschland, Österreich und der Schweiz. Ich finde die Stellen, an denen Geld verloren geht, und bringe Sie mit den Menschen zusammen, die Sie weiterbringen. Für Vertrieb und Social Media arbeite ich mit meinem Partner Marvin Angerer und seinem Team, das Ihre Kunden dort erreicht, wo sie heute sind."
else:
    hero_sub = "Ich berate Inhaberinnen und Inhaber mittelständischer Unternehmen in Deutschland, Österreich und der Schweiz. Ich schaue mir jede Abteilung an, vom Vertrieb bis zur Buchhaltung, finde die Stellen, an denen Geld verloren geht, und bringe Sie mit den Menschen zusammen, die Sie weiterbringen."

# Die Kurve ist schematisch: keine echten Werte, nur das Bild von Rot nach Schwarz.
curve = '''<figure class="curve" data-curve>
            <svg viewBox="0 0 640 260" role="img" aria-label="Schematische Kurve eines Betriebsergebnisses, die aus dem roten Bereich unter der Nulllinie in den schwarzen Bereich darüber steigt">
              <line class="curve-zero" x1="0" y1="150" x2="640" y2="150"/>
              <text class="curve-axis" x="636" y="142" text-anchor="end">0</text>
              <path class="curve-line curve-red" d="M8 196C60 206 104 236 160 226S236 182 268 150"/>
              <path class="curve-line curve-black" d="M268 150C300 118 340 112 396 98S500 70 540 52 610 26 632 20"/>
              <circle class="curve-dot" cx="632" cy="20" r="6"/>
              <text class="curve-label curve-label-red" x="20" y="246">rote Zahlen</text>
              <text class="curve-label curve-label-black" x="420" y="118">schwarze Zahlen</text>
            </svg>
            <figcaption>Betriebsergebnis, schematisch</figcaption>
          </figure>'''

home = f'''    <section class="hero" aria-labelledby="hero-title">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <p class="hero-kicker">{NAME}</p>
          <h1 id="hero-title">Aus <span class="red">roten Zahlen</span> mache ich <span class="black u">schwarze</span>.</h1>
          <p class="lead">{hero_sub}</p>
          <div class="hero-actions">
            {cta()}
            <a class="textlink" href="tel:{TEL}">{ORG["phone_display"]}</a>
          </div>
          <dl class="stats">{stats}</dl>
        </div>
        <figure class="hero-portrait">
          <img src="{{R}}assets/img/portrait.jpg" width="1076" height="1434" alt="Bettina Angerer, Unternehmensberaterin, mit ihrer blauen Haarsträhne" fetchpriority="high">
          <figcaption>Bettina Angerer</figcaption>
        </figure>
      </div>
    </section>
{client_logos()}
    <section class="section measure" aria-labelledby="mass-title">
      <div class="wrap measure-grid">
        <div>
          <h2 id="mass-title">Gute Ideen sind nur dann etwas wert, wenn sie sich in den Zahlen zeigen.</h2>
          <p class="lead">Das habe ich in leitenden Positionen in Marketing und Controlling gelernt, und daran messe ich meine Arbeit bis heute.</p>
          <p>Ich verkaufe niemandem ein großes Projekt, bevor die Zahlen stimmen. Deshalb beginnt fast jede Zusammenarbeit mit einem Testballon: ein kleiner, messbarer Schritt, an dem Sie sehen, ob der Weg trägt.</p>
        </div>
        {curve}
      </div>
    </section>

    <section class="section on-navy" id="leistungen" aria-labelledby="leistungen-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="leistungen-title">Wobei ich Sie unterstütze</h2>
          <p class="lead">Der größte Teil meiner Arbeit dreht sich um Zahlen, Strukturen und Menschen. Vertrieb und Social Media gehören dazu, dort arbeite ich eng mit meinem Partner Marvin Angerer zusammen.</p>
        </div>
        <ul class="svc-list">{svc_rows}
        </ul>
      </div>
    </section>

    <section class="section fit" aria-labelledby="fit-title">
      <div class="wrap fit-grid">
        <h2 id="fit-title">Für wen ich arbeite</h2>
        <div class="fit-copy">
          <p class="lead">Ich arbeite mit Inhaberinnen und Inhabern, die selbst entscheiden und bereit sind, etwas zu verändern, auch wenn es unbequem wird. Wer nur eine Bestätigung für den bisherigen Weg sucht, ist bei mir falsch.</p>
          <p>Ich sitze selbst mit am Tisch, deshalb begleite ich nur wenige Unternehmen gleichzeitig. Jede Anfrage lese ich persönlich, und wenn ich nicht helfen kann, sage ich das offen und nenne Ihnen jemanden aus meinem Netzwerk, der besser passt.</p>
        </div>
      </div>
    </section>
{cases_section()}
    <section class="section on-paper" aria-labelledby="about-title">
      <div class="wrap about-teaser">
        <div class="about-copy">
          <h2 id="about-title">Seit über dreißig Jahren im und für den Mittelstand</h2>
          <p class="lead">In dieser Zeit habe ich mit Hunderten Unternehmerinnen und Unternehmern gesprochen, über Nachfolge, Fachkräfte, Finanzierung und darüber, wie man Kunden heute überhaupt noch erreicht.</p>
          <p>Daraus ist ein Netzwerk entstanden, das von der Kommune über Landtag und Bundestag bis nach Brüssel reicht. Heute nutze ich es für die Unternehmen, die ich berate.</p>
          {seal_block()}
          <a class="textlink" href="{{R}}ueber-mich/">Mehr über mich {ARROW}</a>
        </div>
        {marvin_card()}
      </div>
    </section>

    <section class="saying on-deep" aria-label="Leitsatz">
      <div class="wrap">
        <p>Wer zwischen den Generationen vermittelt, <span class="u">gewinnt den Markt.</span></p>
      </div>
    </section>

    <section class="section" id="ablauf" aria-labelledby="ablauf-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="ablauf-title">So beginnt eine Zusammenarbeit</h2>
        </div>
        {process_html()}
      </div>
    </section>

    <section class="section on-paper" aria-labelledby="faq-title">
      <div class="wrap faq-grid">
        <h2 id="faq-title">Häufige Fragen</h2>
        <div class="faq">{faq_html}</div>
      </div>
    </section>

{final_cta()}'''

faq_schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
web_schema = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": f"{SITE}/", "inLanguage": "de"}
urls.append(page("index.html", f"{NAME} | {CLAIM}",
                 "Bettina Angerer berät Inhaberinnen und Inhaber mittelständischer Unternehmen im DACH-Raum: Strategie und Sanierung, Netzwerk und Politik, Coaching, Vertrieb und Social Media. Aus roten Zahlen werden schwarze.",
                 home, schema=[ORG_SCHEMA, web_schema, faq_schema], body_cls="home"))

# ================================================================ Leistungen Übersicht
rows = ""
for n, s in enumerate(SERVICES):
    lis = "".join(f"<li><h3>{t}</h3><p>{long}</p></li>" for t, _, long in s["items"])
    rows += f'''
    <section class="section detail{' on-paper' if n % 2 else ''}" id="{s["slug"]}" aria-labelledby="{s["slug"]}-title">
      <div class="wrap detail-grid">
        <div class="detail-side">
          <h2 id="{s["slug"]}-title">{s["name"]}</h2>
          <p class="lead">{s["lead"]}</p>
          <p>{s["intro"]}</p>
          <a class="btn btn-outline" href="{{R}}leistungen/{s["slug"]}/">Mehr zu {s["name"]} {ARROW}</a>
        </div>
        <ul class="item-list">{lis}</ul>
      </div>
    </section>
'''
crumbs = [("leistungen/", "Leistungen")]
body = page_hero("Wobei ich Sie unterstütze",
                 "Sie müssen nicht alles auf einmal angehen. Wir beginnen dort, wo es bei Ihnen gerade am meisten kostet, und arbeiten uns von dort aus weiter.", crumbs)
body += f'''    <nav class="jump" aria-label="Leistungen im Überblick">
      <div class="wrap jump-inner">{"".join(f'<a href="#{s["slug"]}">{s["name"]}</a>' for s in SERVICES)}</div>
    </nav>
''' + rows + final_cta("Welches Feld passt zu Ihnen?", "Sie müssen das nicht allein entscheiden. Beschreiben Sie in einem Satz, wo es hakt, und ich ordne es mit Ihnen ein.")
urls.append(page("leistungen/index.html", f"Leistungen | {NAME}",
                 "Strategie und Sanierung, Netzwerk und Politik, Coaching für Unternehmer, Vertrieb sowie Marketing und Social Media: alle Leistungen von Bettina Angerer Consulting im Überblick.",
                 body, current="leistungen/", crumbs=crumbs))

# ================================================================ Leistung Einzelseiten
for s in SERVICES:
    crumbs = [("leistungen/", "Leistungen"), (f'leistungen/{s["slug"]}/', s["name"])]
    pains = "".join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in s["pains"])
    lis = "".join(f"<li><h3>{t}</h3><p>{long}</p></li>" for t, _, long in s["items"])
    others = "".join(f'<li><a href="{{R}}leistungen/{o["slug"]}/"><h3>{o["name"]}</h3><p>{o["lead"]}</p>{ARROW}</a></li>' for o in SERVICES if o is not s)
    who = (f'''
    <section class="section on-paper" aria-labelledby="wer-title">
      <div class="wrap who">
        <div>
          <h2 id="wer-title">Wer mit am Tisch sitzt</h2>
          <p class="lead">Ihre erste Ansprechpartnerin bin ich. In diesem Feld ist mein Partner Marvin Angerer von Anfang an dabei.</p>
        </div>
        {marvin_card()}
      </div>
    </section>
''' if s.get("partner") else "")
    body = page_hero(s["lead"], s["intro"], crumbs) + client_logos() + f'''
    <section class="section" aria-labelledby="lage-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="lage-title">Kommt Ihnen das bekannt vor?</h2>
        </div>
        <ul class="pains">{pains}</ul>
      </div>
    </section>

    <section class="section on-paper" aria-labelledby="was-title">
      <div class="wrap detail-grid">
        <div class="detail-side">
          <h2 id="was-title">Was ich in diesem Feld für Sie tue</h2>
          <p class="lead">Jede Leistung können Sie einzeln beauftragen. Meist beginnen wir mit einer und bauen aus, sobald die ersten Ergebnisse da sind.</p>
          {cta(cls="btn")}
        </div>
        <ul class="item-list">{lis}</ul>
      </div>
    </section>
{who}
    <section class="section" aria-labelledby="ablauf-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="ablauf-title">So beginnt eine Zusammenarbeit</h2>
        </div>
        {process_html()}
      </div>
    </section>

    <section class="section on-paper" aria-labelledby="weitere-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="weitere-title">Das greift ineinander</h2>
        </div>
        <ul class="others">{others}</ul>
      </div>
    </section>

''' + final_cta()
    svc_schema = {"@context": "https://schema.org", "@type": "Service", "name": s["name"],
                  "serviceType": s["name"], "description": s["desc"], "provider": {"@id": f"{SITE}/#organisation"},
                  "areaServed": ["DE", "AT", "CH"], "url": f'{SITE}/leistungen/{s["slug"]}/',
                  "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["name"],
                                      "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": t}} for t, _, _ in s["items"]]}}
    urls.append(page(f'leistungen/{s["slug"]}/index.html', s["title"], s["desc"], body, current="leistungen/", schema=[svc_schema], crumbs=crumbs))

# ================================================================ Über mich
crumbs = [("ueber-mich/", "Über mich")]
video = (f'''
          <figure class="video">
            <video controls preload="none" playsinline poster="{{R}}{VIDEO_POSTER}" src="{{R}}{VIDEO}"></video>
            <figcaption>Bettina Angerer stellt sich vor</figcaption>
          </figure>''' if VIDEO else "")
body = page_hero("Ich mache aus roten Zahlen schwarze.",
                 "Unternehmensberaterin, Netzwerkerin und Coach für Inhaberinnen und Inhaber im Mittelstand. Daran messe ich meine Arbeit.", crumbs) + f'''
    <section class="section" aria-labelledby="bio-title">
      <div class="wrap bio">
        <figure class="bio-portrait">
          <img src="{{R}}assets/img/portrait.jpg" width="1076" height="1434" alt="Bettina Angerer, Unternehmensberaterin, mit ihrer blauen Haarsträhne">
        </figure>
        <div class="bio-copy">
          <h2 id="bio-title" class="sr-only">Mein Weg</h2>
          <p class="lead">Seit über dreißig Jahren arbeite ich im und für den Mittelstand. Angefangen habe ich in leitenden Positionen in Marketing und Controlling. Dort habe ich gelernt, dass gute Ideen nur dann etwas wert sind, wenn sie sich am Ende in den Zahlen zeigen. Daran messe ich meine Arbeit bis heute.</p>
          <p>Acht Jahre lang habe ich die Mittelstandsarbeit des BVMW in Nordbayern geleitet. In dieser Zeit habe ich mit Hunderten Unternehmerinnen und Unternehmern gesprochen, über Nachfolge, Fachkräfte, Finanzierung und über die Frage, wie man Kunden heute überhaupt noch erreicht. Aus dieser Zeit ist ein Netzwerk entstanden, das von der Kommune über Landtag und Bundestag bis nach Brüssel reicht. Mit der Region bleibe ich zudem über meine Ehrenämter verbunden.</p>
          <p>Seit Januar 2026 arbeite ich mit Bettina Angerer Consulting für Unternehmen im gesamten DACH-Raum, zusammen mit meinem Partner Marvin Angerer. Ich schaue mir jede Abteilung an, vom Vertrieb bis zur Buchhaltung, und suche die Stellen, an denen Geld verloren geht oder liegen bleibt. Wo ein Unternehmen jemanden braucht, den ich nicht ersetzen kann, bringe ich die richtigen Leute aus meinem Netzwerk zusammen. Unternehmerinnen und Unternehmer, die ihr Haus strategisch führen wollen, coache ich und bilde sie aus.</p>
          <p>Ich halte mich an das Leitbild des Ehrbaren Kaufmanns. Für mich heißt das: Ich sage offen, was ich sehe, auch wenn es unbequem ist. Und ich verkaufe niemandem ein Projekt, das er nicht braucht.</p>
          <p class="strand-note">Die blaue Haarsträhne fällt beim ersten Treffen fast allen auf. Oft fängt das Gespräch genau damit an, und das ist mir recht.</p>{video}
          {seal_block()}
        </div>
      </div>
    </section>

    <section class="section on-paper" aria-labelledby="partner-title">
      <div class="wrap who">
        <div>
          <h2 id="partner-title">Wir arbeiten zu zweit</h2>
          <p class="lead">Ich bin Ihre erste Ansprechpartnerin. Wenn es um Vertrieb, Social Media oder Content geht, ist Marvin Angerer von Anfang an dabei.</p>
        </div>
        {marvin_card("h3")}
      </div>
    </section>

    <section class="section" id="prinzip" aria-labelledby="prinzip-title">
      <div class="wrap">
        <div class="section-head">
          <h2 id="prinzip-title">Ich übersetze in beide Richtungen</h2>
          <p class="lead">Die Chefetage spricht eine andere Sprache als die Generation, die heute Ihre Kunden stellt. Ich vermittle in die Welt der Entscheider, Marvin Angerer in die Welt der neuen Medien.</p>
        </div>
        <div class="bridge">
          <article class="world">
            <h3>Die Welt der Entscheider</h3>
            <p>Strategie und Zahlen, Verhandlungen mit Banken und Partnern, Politik und Netzwerk, die Haltung des Ehrbaren Kaufmanns.</p>
          </article>
          <article class="world dark">
            <h3>Die Welt Ihrer Kunden</h3>
            <p>LinkedIn, Instagram, YouTube und TikTok, Creator und Community, ein anderes Tempo und eine andere Sprache.</p>
          </article>
        </div>
        <p class="bridge-saying">Beide Welten brauchen <span class="u">einander.</span></p>
      </div>
    </section>

''' + final_cta("Lernen wir uns kennen.", "Sechs kurze Fragen, dann rufe ich Sie persönlich an.")
urls.append(page("ueber-mich/index.html", f"Über mich: Bettina Angerer | {NAME}",
                 "Bettina Angerer: über dreißig Jahre im und für den Mittelstand, zuerst in Marketing und Controlling, heute mit Bettina Angerer Consulting im gesamten DACH-Raum.",
                 body, current="ueber-mich/", schema=[PERSON_SCHEMA], crumbs=crumbs))

# ================================================================ Kontakt
crumbs = [("kontakt/", "Kontakt")]
body = page_hero("So erreichen Sie mich",
                 "Am schnellsten geht es über die Anfrage in sechs kurzen Fragen. Sie können mich aber auch direkt anrufen oder mir schreiben.", crumbs) + f'''
    <section class="section" aria-labelledby="kontakt-title">
      <div class="wrap contact">
        <div class="contact-card">
          <h2 id="kontakt-title">Anfrage in sechs Fragen</h2>
          <p>Umsatz, Unternehmensgröße, Tätigkeitsbereich, Branche und ein Satz zu Ihrem Anliegen. Ich lese jede Anfrage selbst und rufe Sie an.</p>
          {cta()}
        </div>
        <div class="contact-card">
          <h2>{NAME}</h2>
          <address>
            Bettina Angerer<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}
          </address>
          <ul class="contact-list">
            <li><span>Telefon</span><a href="tel:{TEL}">{ORG["phone_display"]}</a></li>
            <li><span>E-Mail</span><a href="mailto:{ORG["email"]}">{ORG["email"]}</a></li>
          </ul>
        </div>
      </div>
    </section>
'''
urls.append(page("kontakt/index.html", f"Kontakt | {NAME}",
                 f"Kontakt zu Bettina Angerer, {NAME}: {ORG['street']}, {ORG['zip']} {ORG['city']}. Erstgespräch in sechs kurzen Fragen anfragen.",
                 body, current="kontakt/", schema=[ORG_SCHEMA], crumbs=crumbs))


# ================================================================ Rechtliches
def legal_page(slug, name, inner, desc):
    crumbs = [(f"{slug}/", name)]
    body = f'''    <section class="section legal-section">
      <div class="wrap legal">
        <nav class="crumbs" aria-label="Brotkrumen"><a href="{{R}}">Startseite</a><span aria-hidden="true">/</span><span aria-current="page">{name}</span></nav>
{inner}
      </div>
    </section>
'''
    urls.append(page(f"{slug}/index.html", f"{name} | {NAME}", desc, body, crumbs=crumbs))


def esc(t):
    t = html.escape(t, quote=False).replace("­", "")
    t = re.sub(r"(https?://[^\s<“”„\"]+?)([.,)]?)(\s|$)", r'<a href="\1" rel="noopener">\1</a>\2\3', t)
    return re.sub(r"(?<![\w/@.])(www\.[\w.-]+\.\w+)", r'<a href="https://\1" rel="noopener">\1</a>', t)


legal_page("impressum", "Impressum", f'''        <h1>Impressum</h1>
        <p class="legal-note">Die Angaben werden für die neue Firmierung noch überarbeitet. Bitte vor dem Livegang Rechtsform und vertretungsberechtigte Personen prüfen.</p>
        <h2>Angaben gemäß § 5 DDG</h2>
        <p>{NAME}<br><span class="placeholder">{{{{Rechtsform und vertretungsberechtigte Personen}}}}</span><br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}</p>
        <h2>Kontakt</h2>
        <p>Telefon: <a href="tel:{TEL}">{ORG["phone_display"]}</a><br>E-Mail: <a href="mailto:{ORG["email"]}">{ORG["email"]}</a></p>
        <h2>Umsatzsteuer-ID</h2>
        <p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br>{ORG["vat"]}</p>
        <h2>Redaktionell verantwortlich</h2>
        <p>Bettina Angerer<br>{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}</p>
        <h2>EU-Streitschlichtung</h2>
        <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" rel="noopener">https://ec.europa.eu/consumers/odr/</a>.<br>Unsere E-Mail-Adresse finden Sie oben im Impressum.</p>
        <h2>Verbraucherstreitbeilegung und Universalschlichtungsstelle</h2>
        <p>Wir nehmen an einem Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teil. Zuständig ist die Universalschlichtungsstelle des Zentrums für Schlichtung e.V., Straßburger Straße 8, 77694 Kehl am Rhein (<a href="https://www.verbraucher-schlichter.de" rel="noopener">https://www.verbraucher-schlichter.de</a>).</p>
        <h2>Bildnachweise</h2>
        <p>Portrait: Bettina Angerer.{' Die gezeigten Logos sind Marken der jeweiligen Unternehmen und dienen als Referenz.' if SHOW_CLIENT_LOGOS and CLIENT_LOGOS else ''}</p>''',
           f"Impressum von {NAME}, {ORG['street']}, {ORG['zip']} {ORG['city']}.")

# Datenschutz: anwendbare Abschnitte der bisherigen Erklärung, ergänzt um den Stand der neuen Seite.
ds = [l.strip() for l in (ROOT / "content/legal/datenschutz.txt").read_text().split("\n") if l.strip()]
# In der alten Vorlage stand noch ein Platzhalter des Textgenerators.
ds = [l.replace("für die „Mustermandant“ geltenden", "für uns geltenden") for l in ds]
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

legal_page("datenschutz", "Datenschutz", f'''        <h1>Datenschutzerklärung</h1>
        <p class="legal-note">Diese Fassung übernimmt die weiterhin zutreffenden Abschnitte der bisherigen Erklärung und beschreibt den technischen Stand der neuen Website. Vor dem Livegang wird sie für die neue Firmierung überarbeitet, vom Datenschutzbeauftragten geprüft und um die Angaben zum endgültigen Hosting ergänzt.</p>
        <h2>Einleitung</h2>
        <p>{esc(ds[2])}</p>
        <p>{esc(ds[4])}</p>
        {ds_block(i_resp, i_defs - 1)}
        {ds_block(i_legal, i_cookies - 1)}
        <h2>Hosting</h2>
        <p><span class="placeholder">{{{{Name und Anschrift des Hosting-Anbieters, Ort der Verarbeitung, Hinweis auf den Vertrag zur Auftragsverarbeitung}}}}</span></p>
        <p>Beim Aufruf der Website verarbeitet der Server des Hosting-Anbieters technisch notwendige Daten wie Ihre IP-Adresse, Datum und Uhrzeit des Abrufs und die aufgerufene Adresse. <span class="placeholder">{{{{Speicherdauer der Server-Logdateien beim Hoster erfragen}}}}</span></p>
        <h2>Cookies, Schriften und eingebundene Dienste</h2>
        <p>Diese Website setzt keine Cookies und speichert nichts in Ihrem Browser. Schriften (Source Serif 4 und Libre Franklin), Bilder und Skripte werden ausschließlich vom eigenen Server ausgeliefert. Es werden keine Inhalte von Drittanbietern eingebunden, also keine Schriftbibliotheken wie Google Fonts, keine Kartendienste, keine Videoplattformen und keine Social-Media-Plugins.</p>
        <h2>Webanalyse</h2>
        <p>Derzeit wird kein Werkzeug zur Webanalyse eingesetzt. <span class="placeholder">{{{{Falls ein Analysewerkzeug eingeführt wird: Anbieter, Zweck, Rechtsgrundlage, Speicherdauer und Widerspruchsmöglichkeit hier ergänzen}}}}</span></p>
        <h2>Kontaktaufnahme und Anfrageformular</h2>
        <p>{esc(ds[i_contact + 1])}</p>
        <p>Wenn Sie das Anfrageformular nutzen, werden Ihre Angaben (Jahresumsatz, Unternehmensgröße, Tätigkeitsbereich, Branche, Anliegen, Unternehmen, Name, E-Mail-Adresse und optional Telefonnummer) verschlüsselt an unseren Webserver übertragen und von dort per E-Mail an {ORG["email"]} weitergeleitet. Die Daten werden auf dem Webserver nicht gespeichert und ausschließlich zur Bearbeitung Ihrer Anfrage verwendet. Rechtsgrundlage ist Art. 6 Abs. 1 lit. b DS-GVO (Anbahnung eines Vertrags) sowie Ihre Einwilligung nach Art. 6 Abs. 1 lit. a DS-GVO.</p>
        <p>Ist der Versand über den Server nicht möglich, bereitet das Formular stattdessen eine E-Mail in Ihrem eigenen E-Mail-Programm vor, die Sie selbst absenden.</p>
        {ds_block(i_rights, i_stand - 1)}
        <h2>Aktualität und Änderung der Datenschutzerklärung</h2>
        <p>Stand: November 2026.</p>
        <p>{esc(ds[i_stand + 2])}</p>''',
           f"Datenschutzerklärung von {NAME}, Bayreuth.")

dv = [l.strip() for l in (ROOT / "content/legal/datenverarbeitung.txt").read_text().split("\n") if l.strip()]
out, in_list = [], False
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
           f'        <h1>Grundsätze der Datenverarbeitung bei {NAME}</h1>\n        ' + "\n        ".join(out) + "\n        <p>Stand: 01.07.2020</p>",
           f"Grundsätze der Datenverarbeitung bei {NAME}: Informationen nach Art. 12 ff. DSGVO.")

# ================================================================ Logo-Varianten (nur zur Abstimmung, nicht verlinkt)
lv = (ROOT / "partials/logo-varianten.html").read_text()
page("logo-varianten/index.html", f"Logo-Varianten zur Abstimmung | {NAME}", "Entwürfe zur Abstimmung.", lv,
     extra_head='  <meta name="robots" content="noindex, nofollow">\n')

# ================================================================ 404, Sitemap, Robots
body404 = '''    <section class="section">
      <div class="wrap legal">
        <h1>Diese Seite gibt es nicht.</h1>
        <p class="lead">Die Adresse ist falsch geschrieben oder die Seite wurde verschoben. Auf der Startseite finden Sie alle Leistungen und die Anfrage.</p>
        <p style="margin-top:32px"><a class="btn" href="/">Zur Startseite</a></p>
      </div>
    </section>
'''
page("404.html", f"Seite nicht gefunden | {NAME}", "Diese Seite gibt es nicht.", body404)
# Die Fehlerseite kann in jeder Tiefe ausgeliefert werden.
p404 = ROOT / "404.html"
t = p404.read_text()
# Relative Pfade über ein <base> auflösen: Domainwurzel, auf GitHub Pages der Projektordner.
t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  <script>document.write(\'<base href="\' + (/github\\.io$/.test(location.hostname) ? \'/\' + location.pathname.split(\'/\')[1] + \'/\' : \'/\') + \'">\');</script>', 1)
t = t.replace('href="/">Zur Startseite', 'href="./">Zur Startseite')
t = re.sub(r'\s*<link rel="canonical"[^>]*>', '\n  <meta name="robots" content="noindex">', t)
p404.write_text(t)

# Seiten, die es nicht mehr gibt, aus früheren Entwürfen entfernen.
for old in ("engagement", "ueber-bettina", "leistungen/personal", "leistungen/finanzierung"):
    shutil.rmtree(ROOT / old, ignore_errors=True)

sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
prio = {"": "1.0", "leistungen/": "0.9", "ueber-mich/": "0.8", "kontakt/": "0.7"}
for u in urls:
    p = prio.get(u, "0.8" if u.startswith("leistungen/") else "0.3")
    sm += f"  <url><loc>{SITE}/{u}</loc><priority>{p}</priority></url>\n"
(ROOT / "sitemap.xml").write_text(sm + "</urlset>\n")
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
print("Seiten:", len(urls) + 1)
for u in urls:
    print("  /" + u)
