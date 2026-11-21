/* Angerer Consulting */
(function () {
  'use strict';

  // Ersatzweg, falls der Versand über den Server nicht klappt (z. B. auf der Testseite bei GitHub
  // oder solange in Vercel kein Postfach eingetragen ist). Dann öffnet sich das E-Mail-Programm mit dieser Empfängeradresse.
  // Für die Testphase laut Absprache; vor dem Livegang auf info@bettina-angerer.de stellen.
  var CONTACT_EMAIL = 'info@oskarjacobsen.de';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;

  /* ---------- Menü auf dem Handy ---------- */
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('mobile-menu');
  function setMenu(open) {
    root.classList.toggle('menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
    document.body.style.overflow = open ? 'hidden' : '';
  }
  if (toggle && menu) {
    toggle.addEventListener('click', function () { setMenu(!root.classList.contains('menu-open')); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });
  }

  /* ---------- Logo-Banner läuft endlos und nahtlos ---------- */
  // Eine Runde = alle Logos einmal. Es werden so viele Runden angehängt, dass immer die ganze
  // Breite gefüllt ist; die Animation verschiebt um genau eine Runde, so ist kein Sprung zu sehen.
  var marquee = document.querySelector('.marquee');
  if (marquee && !reduce) {
    var list = marquee.querySelector('.logos');
    var originals = Array.prototype.slice.call(list.children);
    var setupMarquee = function () {
      Array.prototype.slice.call(list.children).forEach(function (li, i) { if (i >= originals.length) li.remove(); });
      marquee.classList.add('is-running');
      var setWidth = originals.reduce(function (sum, li) { return sum + li.getBoundingClientRect().width; }, 0);
      if (!setWidth) return;
      var copies = Math.ceil(marquee.clientWidth / setWidth) + 1;
      for (var c = 0; c < copies; c++) {
        originals.forEach(function (li) { var k = li.cloneNode(true); k.setAttribute('aria-hidden', 'true'); list.appendChild(k); });
      }
      list.style.setProperty('--set', setWidth + 'px');
      list.style.setProperty('--dur', (setWidth / 45).toFixed(1) + 's');
    };
    setupMarquee();
    window.addEventListener('load', setupMarquee);
    var mqTimer;
    window.addEventListener('resize', function () { clearTimeout(mqTimer); mqTimer = setTimeout(setupMarquee, 200); });
  }

  /* ---------- Scroll-Effekte: nur zwei, beide erzählen etwas ---------- */
  var effects = [];
  var ticking = false;
  function runEffects() { ticking = false; effects.forEach(function (fn) { fn(); }); }
  function requestTick() { if (!ticking) { ticking = true; requestAnimationFrame(runEffects); } }
  window.addEventListener('scroll', requestTick, { passive: true });
  window.addEventListener('resize', requestTick);

  // 1. Rot wird Schwarz: die Ergebniskurve zeichnet sich beim Scrollen von unten nach oben.
  var curve = document.querySelector('[data-curve]');
  if (curve) {
    var red = curve.querySelector('.curve-red');
    var black = curve.querySelector('.curve-black');
    var dot = curve.querySelector('.curve-dot');
    var labelBlack = curve.querySelector('.curve-label-black');
    var lr = red.getTotalLength(), lb = black.getTotalLength();
    var setCurve = function (p) {
      var pr = Math.min(1, p / 0.45), pb = Math.max(0, (p - 0.45) / 0.55);
      red.style.strokeDasharray = lr; red.style.strokeDashoffset = lr * (1 - pr);
      black.style.strokeDasharray = lb; black.style.strokeDashoffset = lb * (1 - pb);
      dot.style.opacity = pb >= 1 ? 1 : 0;
      labelBlack.style.opacity = pb > 0.5 ? 1 : 0;
    };
    if (reduce) { setCurve(1); }
    else {
      effects.push(function () {
        var r = curve.getBoundingClientRect(), vh = window.innerHeight;
        // Beginnt, wenn die Kurve unten ins Bild kommt, fertig, wenn sie in der oberen Hälfte steht.
        setCurve(Math.max(0, Math.min(1, (vh * 0.95 - r.top) / (vh * 0.6))));
      });
    }
  }

  // 2. Die Strähne als Linie: verbindet auf der Startseite die Abschnitte, Punkt für Punkt.
  var main = document.querySelector('.home main');
  if (main && window.matchMedia('(min-width: 1340px)').matches && !reduce) {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('class', 'thread'); svg.setAttribute('aria-hidden', 'true');
    var path = document.createElementNS(NS, 'path');
    svg.appendChild(path);
    main.appendChild(svg);
    var nodes = [], len = 0, ys = [];
    var build = function () {
      var sections = Array.prototype.slice.call(main.querySelectorAll(':scope > section:not(.refs)')).slice(1);
      var mainTop = main.getBoundingClientRect().top + window.scrollY;
      var left = Math.max(0, (window.innerWidth - 1200) / 2 - 20);
      svg.style.left = left + 'px';
      svg.style.height = main.offsetHeight + 'px';
      svg.setAttribute('viewBox', '0 0 64 ' + main.offsetHeight);
      nodes.forEach(function (c) { c.remove(); });
      nodes = []; ys = [];
      var d = '';
      sections.forEach(function (s, i) {
        var y = s.getBoundingClientRect().top + window.scrollY - mainTop + 96;
        var x = i % 2 ? 46 : 16;
        if (i === 0) d = 'M' + x + ' ' + y;
        else {
          var py = ys[i - 1], px = (i - 1) % 2 ? 46 : 16, my = (py + y) / 2;
          d += ' C' + px + ' ' + my + ' ' + x + ' ' + my + ' ' + x + ' ' + y;
        }
        ys.push(y);
        var c = document.createElementNS(NS, 'circle');
        c.setAttribute('cx', x); c.setAttribute('cy', y); c.setAttribute('r', 6);
        svg.appendChild(c); nodes.push(c);
      });
      path.setAttribute('d', d);
      len = path.getTotalLength();
      path.style.strokeDasharray = len;
    };
    build();
    window.addEventListener('resize', function () { build(); requestTick(); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { build(); requestTick(); });
    window.addEventListener('load', function () { build(); requestTick(); });
    effects.push(function () {
      if (!ys.length) return;
      var mainTop = main.getBoundingClientRect().top + window.scrollY;
      var line = window.scrollY + window.innerHeight * 0.6 - mainTop;
      var first = ys[0], last = ys[ys.length - 1];
      var p = Math.max(0, Math.min(1, (line - first) / (last - first)));
      path.style.strokeDashoffset = len * (1 - p);
      nodes.forEach(function (c, i) { c.classList.toggle('on', ys[i] <= line); });
    });
  }
  requestTick();

  /* ---------- Anfrage in Schritten ---------- */
  var dialog = document.getElementById('wizard');
  var form = document.getElementById('enquiry-form');
  if (!dialog || !form) return;

  var steps = Array.prototype.slice.call(form.querySelectorAll('.step'));
  var questions = steps.length - 1; // letzter Schritt ist die Bestätigung
  var doneStep = steps[questions];
  var bar = form.querySelector('.wizard-bar');
  var count = form.querySelector('.wizard-count');
  var foot = form.querySelector('.wizard-foot');
  var backBtn = form.querySelector('[data-back]');
  var nextBtn = form.querySelector('[data-next]');
  var sendError = form.querySelector('.send-error');
  var resultText = document.getElementById('result-text');
  var copyBtn = document.getElementById('copy-btn');
  var current = 0, sending = false;
  document.getElementById('result-mail').textContent = CONTACT_EMAIL;

  function show(i) {
    current = i;
    var done = i === questions;
    steps.forEach(function (st, n) { st.classList.toggle('is-active', n === i); });
    var pct = done ? 100 : Math.round((i / questions) * 100);
    bar.firstElementChild.style.transform = 'scaleX(' + (done ? 1 : Math.max(i / questions, 0.04)) + ')';
    bar.setAttribute('aria-valuenow', String(pct));
    count.textContent = done ? 'Geschafft' : 'Frage ' + (i + 1) + ' von ' + questions;
    backBtn.hidden = i === 0 || done;
    foot.classList.toggle('is-done', done || i === 0);
    nextBtn.firstChild.textContent = done ? 'Schließen ' : (i === questions - 1 ? 'Anfrage senden ' : 'Weiter ');
    var focusEl = done ? doneStep.querySelector(doneStep.dataset.mode === 'sent' ? '.done-sent h2' : '.done-mail h2')
      : (steps[i].dataset.step === 'fields' ? steps[i].querySelector('input, textarea') : steps[i].querySelector('legend'));
    if (focusEl) focusEl.focus({ preventScroll: true });
    form.querySelector('.wizard-body').scrollTop = 0;
  }

  function mark(el, bad) { el.classList.toggle('invalid', bad); return bad; }

  function validateStep(i) {
    var st = steps[i];
    var firstBad = null;
    if (st.dataset.step === 'radio') {
      var bad = !st.querySelector('input:checked');
      if (mark(st, bad)) firstBad = st.querySelector('input');
      return firstBad;
    }
    st.querySelectorAll('.field').forEach(function (f) {
      var input = f.querySelector('input, textarea');
      var v = input.value.trim();
      var bad = input.required ? !v : false;
      if (input.type === 'email' && v) bad = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
      input.setAttribute('aria-invalid', String(bad));
      if (mark(f, bad) && !firstBad) firstBad = input;
    });
    var checkWrap = st.querySelector('[data-check]');
    if (checkWrap) {
      var check = checkWrap.querySelector('input');
      if (mark(checkWrap, !check.checked) && !firstBad) firstBad = check;
    }
    return firstBad;
  }

  function mailText(d) {
    var subject = 'Anfrage Erstgespräch: ' + d.get('firma') + ' [Umsatz ' + d.get('umsatz') + ']';
    var body = [
      'Anfrage über die Website von Angerer Consulting',
      '',
      'Unternehmen: ' + d.get('firma'),
      'Branche: ' + d.get('branche'),
      'Jahresumsatz: ' + d.get('umsatz'),
      'Mitarbeiter: ' + d.get('mitarbeiter'),
      'Tätigkeitsbereich: ' + d.get('gebiet'),
      '',
      'Anliegen:',
      d.get('anliegen'),
      '',
      'Kontakt',
      'Name: ' + d.get('name'),
      'E-Mail: ' + d.get('email'),
      'Telefon: ' + (d.get('telefon') || 'nicht angegeben')
    ].join('\n');
    return { subject: subject, body: body };
  }

  // Ersatzweg: E-Mail-Programm öffnen und den Text zum Kopieren anzeigen.
  function fallbackMail(d) {
    var m = mailText(d);
    resultText.textContent = 'Betreff: ' + m.subject + '\n\n' + m.body;
    doneStep.dataset.mode = 'mail';
    show(questions);
    window.location.href = 'mailto:' + CONTACT_EMAIL + '?subject=' + encodeURIComponent(m.subject) + '&body=' + encodeURIComponent(m.body);
  }

  // Normalfall: Anfrage geht über die Vercel-Funktion api/anfrage direkt als E-Mail an Bettina Angerer.
  function send() {
    if (sending) return;
    var d = new FormData(form);
    sending = true; nextBtn.disabled = true;
    sendError.classList.remove('is-on');
    var ctrl = 'AbortController' in window ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    fetch(form.action, { method: 'POST', body: d, headers: { 'Accept': 'application/json' }, signal: ctrl ? ctrl.signal : undefined })
      .then(function (res) {
        return res.json().catch(function () { return null; }).then(function (json) { return { status: res.status, json: json }; });
      })
      .then(function (r) {
        if (r.json && r.json.ok) { doneStep.dataset.mode = 'sent'; track('Anfrage gesendet'); show(questions); return; }
        if (r.json && r.json.error && r.status === 422) { sendError.textContent = r.json.error; sendError.classList.add('is-on'); return; }
        track('Anfrage Ersatzweg'); fallbackMail(d);
      })
      .catch(function () { track('Anfrage Ersatzweg'); fallbackMail(d); })
      .then(function () { clearTimeout(timer); sending = false; nextBtn.disabled = false; });
  }

  function next() {
    if (current === questions) { dialog.close(); return; }
    var bad = validateStep(current);
    if (bad) { bad.focus(); return; }
    track('Anfrage Schritt', { schritt: current + 1 });
    if (current === questions - 1) send(); else show(current + 1);
  }

  // Messpunkte: greifen nur, wenn später ein Analysewerkzeug eingebunden wird.
  function track(name, props) {
    try {
      if (typeof window.plausible === 'function') window.plausible(name, { props: props || {} });
      if (window._paq && window._paq.push) window._paq.push(['trackEvent', 'Anfrage', name, props && props.schritt ? String(props.schritt) : undefined]);
    } catch (err) {}
  }

  function openWizard() {
    track('Anfrage geöffnet');
    if (root.classList.contains('menu-open')) setMenu(false);
    if (current === questions) { form.reset(); current = 0; delete doneStep.dataset.mode; }
    if (typeof dialog.showModal === 'function') dialog.showModal(); else dialog.setAttribute('open', '');
    root.classList.add('wizard-lock');
    show(current);
  }

  document.addEventListener('click', function (e) {
    var opener = e.target.closest('[data-open-wizard]');
    if (opener) { e.preventDefault(); openWizard(); return; }
    if (e.target.closest('[data-close-wizard]')) dialog.close();
  });
  dialog.addEventListener('click', function (e) { if (e.target === dialog) dialog.close(); });
  dialog.addEventListener('close', function () {
    root.classList.remove('wizard-lock');
    if (current < questions) track('Anfrage abgebrochen', { schritt: current + 1 });
  });

  nextBtn.addEventListener('click', next);
  backBtn.addEventListener('click', function () { if (current > 0) show(current - 1); });

  // Auswahl per Klick oder Tipp geht direkt zur nächsten Frage (nicht bei Tastatur).
  form.addEventListener('click', function (e) {
    if (e.target.matches('.option input') && e.detail > 0) {
      var at = current;
      setTimeout(function () { if (current === at) next(); }, 250);
    }
  });
  ['input', 'change'].forEach(function (ev) {
    form.addEventListener(ev, function (e) {
      var holder = e.target.closest('.invalid');
      if (holder) holder.classList.remove('invalid');
    });
  });
  form.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'BUTTON' && e.target.tagName !== 'A') {
      e.preventDefault(); next();
    }
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); });

  copyBtn.addEventListener('click', function () {
    var text = resultText.textContent;
    var done = function () { copyBtn.textContent = 'Kopiert'; setTimeout(function () { copyBtn.textContent = 'Text kopieren'; }, 2000); };
    if (navigator.clipboard) { navigator.clipboard.writeText(text).then(done, function () {}); }
    else {
      var r = document.createRange(); r.selectNodeContents(resultText);
      var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
      try { document.execCommand('copy'); done(); } catch (err) {}
    }
  });
})();
