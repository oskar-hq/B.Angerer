<?php
/*
 * Versand des Anfrageformulars von Bettina Angerer Consulting.
 *
 * Läuft auf jedem üblichen Webhosting mit PHP (z. B. beim bisherigen Hoster der WordPress-Seite).
 * Die Angaben werden nicht gespeichert, sondern nur als E-Mail weitergeleitet.
 * Auf GitHub Pages läuft kein PHP: Dort greift im Browser automatisch der Ersatzweg über das E-Mail-Programm.
 */

// Empfänger und Absender. Die Absenderadresse muss zur Domain gehören, sonst landen Mails im Spam.
const RECIPIENT = 'info@bettina-angerer.de';
const SENDER    = 'website@bettina-angerer.de';
const SUBJECT_PREFIX = 'Anfrage Erstgespräch';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function reply(int $status, array $data): void {
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    reply(405, ['ok' => false, 'error' => 'Nur POST erlaubt.']);
}

// Honigtopf: Dieses Feld ist für Menschen unsichtbar. Ist es gefüllt, war es ein Bot.
if (!empty($_POST['website'])) {
    reply(200, ['ok' => true]);
}

function field(string $name, int $max = 200, bool $multiline = false): string {
    $v = str_replace(["\r", "\0"], '', (string)($_POST[$name] ?? ''));
    if (!$multiline) $v = preg_replace('/\s+/u', ' ', $v);
    return mb_substr(trim($v), 0, $max);
}

$d = [
    'umsatz'      => field('umsatz', 60),
    'mitarbeiter' => field('mitarbeiter', 60),
    'gebiet'      => field('gebiet', 60),
    'branche'     => field('branche', 120),
    'anliegen'    => field('anliegen', 4000, true),
    'firma'       => field('firma', 160),
    'name'        => field('name', 120),
    'email'       => field('email', 160),
    'telefon'     => field('telefon', 60),
];

$missing = [];
foreach (['umsatz', 'mitarbeiter', 'gebiet', 'branche', 'anliegen', 'firma', 'name', 'email'] as $k) {
    if ($d[$k] === '') $missing[] = $k;
}
if ($missing) {
    reply(422, ['ok' => false, 'error' => 'Bitte füllen Sie alle Pflichtfelder aus.']);
}
if (!filter_var($d['email'], FILTER_VALIDATE_EMAIL)) {
    reply(422, ['ok' => false, 'error' => 'Bitte prüfen Sie Ihre E-Mail-Adresse.']);
}
if (($_POST['datenschutz'] ?? '') !== 'ja') {
    reply(422, ['ok' => false, 'error' => 'Bitte stimmen Sie der Datenschutzerklärung zu.']);
}

// Kopfzeilen dürfen keine Zeilenumbrüche enthalten.
$oneLine = fn(string $s) => preg_replace('/[\r\n]+/', ' ', $s);

$subject = SUBJECT_PREFIX . ': ' . $oneLine($d['firma']) . ' [Umsatz ' . $oneLine($d['umsatz']) . ']';
$body = implode("\n", [
    'Anfrage über die Website von Bettina Angerer Consulting',
    '',
    'Unternehmen: ' . $d['firma'],
    'Branche: ' . $d['branche'],
    'Jahresumsatz: ' . $d['umsatz'],
    'Mitarbeiter: ' . $d['mitarbeiter'],
    'Tätigkeitsbereich: ' . $d['gebiet'],
    '',
    'Anliegen:',
    $d['anliegen'],
    '',
    'Kontakt',
    'Name: ' . $d['name'],
    'E-Mail: ' . $d['email'],
    'Telefon: ' . ($d['telefon'] !== '' ? $d['telefon'] : 'nicht angegeben'),
    '',
    'Eingegangen am ' . date('d.m.Y \u\m H:i') . ' Uhr. Einwilligung zur Datenschutzerklärung erteilt.',
]);

$headers = [
    'From: =?UTF-8?B?' . base64_encode('Website Bettina Angerer Consulting') . '?= <' . SENDER . '>',
    'Reply-To: =?UTF-8?B?' . base64_encode($oneLine($d['name'])) . '?= <' . $oneLine($d['email']) . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
];

$ok = mail(
    RECIPIENT,
    '=?UTF-8?B?' . base64_encode($subject) . '?=',
    $body,
    implode("\r\n", $headers),
    '-f' . SENDER
);

if (!$ok) {
    // Browser fällt dann auf das E-Mail-Programm zurück.
    reply(502, ['ok' => false]);
}
reply(200, ['ok' => true]);
