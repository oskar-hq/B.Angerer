// Versand des Anfrageformulars von Angerer Consulting (Vercel-Funktion, Region Frankfurt).
// Die Angaben werden nicht gespeichert, sondern nur als E-Mail über das Postfach von Bettina weitergeleitet.
//
// Benötigte Umgebungsvariablen in Vercel (Settings > Environment Variables):
//   SMTP_HOST, SMTP_PORT (465 oder 587), SMTP_USER, SMTP_PASS  Zugang zum E-Mail-Postfach beim Mail-Anbieter
//   MAIL_TO    Empfänger, z. B. info@bettina-angerer.de
//   MAIL_FROM  Absender, muss zum Postfach gehören, z. B. website@bettina-angerer.de
// Fehlt etwas oder klappt der Versand nicht, fällt das Formular im Browser auf das E-Mail-Programm zurück.
const nodemailer = require('nodemailer');

const FIELDS = { umsatz: 60, mitarbeiter: 60, gebiet: 60, branche: 120, anliegen: 4000, firma: 160, name: 120, email: 160, telefon: 60 };
const REQUIRED = ['umsatz', 'mitarbeiter', 'gebiet', 'branche', 'anliegen', 'firma', 'name', 'email'];

function clean(v, max, multiline) {
  let s = String(v ?? '').replace(/[\r\0]/g, '');
  if (!multiline) s = s.replace(/\s+/g, ' ');
  return s.trim().slice(0, max);
}

async function readForm(req) {
  // Der Browser schickt FormData (multipart). Vercel liefert dafür keinen fertigen Body, also selbst lesen.
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const request = new Request('http://localhost/', { method: 'POST', headers: { 'content-type': req.headers['content-type'] || '' }, body: Buffer.concat(chunks) });
  const fd = await request.formData();
  return Object.fromEntries(fd.entries());
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'Nur POST erlaubt.' });

  let raw;
  try { raw = await readForm(req); } catch { return res.status(400).json({ ok: false }); }

  // Honigtopf: für Menschen unsichtbares Feld. Ist es gefüllt, war es ein Bot.
  if (raw.website) return res.status(200).json({ ok: true });

  const d = {};
  for (const [k, max] of Object.entries(FIELDS)) d[k] = clean(raw[k], max, k === 'anliegen');
  if (REQUIRED.some(k => !d[k])) return res.status(422).json({ ok: false, error: 'Bitte füllen Sie alle Pflichtfelder aus.' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(d.email)) return res.status(422).json({ ok: false, error: 'Bitte prüfen Sie Ihre E-Mail-Adresse.' });
  if (raw.datenschutz !== 'ja') return res.status(422).json({ ok: false, error: 'Bitte stimmen Sie der Datenschutzerklärung zu.' });

  const { SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, MAIL_TO, MAIL_FROM } = process.env;
  if (!SMTP_HOST || !SMTP_USER || !SMTP_PASS || !MAIL_TO) return res.status(503).json({ ok: false });

  const when = new Date().toLocaleString('de-DE', { timeZone: 'Europe/Berlin', dateStyle: 'medium', timeStyle: 'short' });
  const text = [
    'Anfrage über die Website von Angerer Consulting', '',
    'Unternehmen: ' + d.firma, 'Branche: ' + d.branche, 'Jahresumsatz: ' + d.umsatz,
    'Mitarbeiter: ' + d.mitarbeiter, 'Tätigkeitsbereich: ' + d.gebiet, '',
    'Anliegen:', d.anliegen, '',
    'Kontakt', 'Name: ' + d.name, 'E-Mail: ' + d.email, 'Telefon: ' + (d.telefon || 'nicht angegeben'), '',
    'Eingegangen am ' + when + ' Uhr. Einwilligung zur Datenschutzerklärung erteilt.',
  ].join('\n');

  try {
    const port = Number(SMTP_PORT || 465);
    const transport = nodemailer.createTransport({ host: SMTP_HOST, port, secure: port === 465, auth: { user: SMTP_USER, pass: SMTP_PASS } });
    await transport.sendMail({
      from: { name: 'Website Angerer Consulting', address: MAIL_FROM || SMTP_USER },
      to: MAIL_TO,
      replyTo: { name: d.name, address: d.email },
      subject: `Anfrage Erstgespräch: ${d.firma} [Umsatz ${d.umsatz}]`,
      text,
    });
  } catch (err) {
    console.error('Versand fehlgeschlagen:', err.message);
    return res.status(502).json({ ok: false });
  }
  return res.status(200).json({ ok: true });
};
