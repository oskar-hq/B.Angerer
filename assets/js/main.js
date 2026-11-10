/* Angerer Consulting */
(function () {
  'use strict';

  // Empfänger der Anfragen. Für die Testphase laut Absprache; später auf Bettinas Adresse ändern.
  var CONTACT_EMAIL = 'info@oskarjacobsen.de';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;

  /* ---------- Mobile menu ---------- */
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

  /* ---------- Scroll reveals, gestaffelt ---------- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      // Elemente, die gleichzeitig ins Bild kommen, erscheinen nacheinander.
      var batch = entries.filter(function (en) { return en.isIntersecting; })
        .sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top || a.boundingClientRect.left - b.boundingClientRect.left; });
      batch.forEach(function (en, i) {
        var el = en.target;
        var delay = reduce ? 0 : Math.min(i * 110, 440);
        el.style.setProperty('--d', delay + 'ms');
        el.classList.add('is-in');
        setTimeout(function () { el.classList.add('is-done'); el.style.removeProperty('--d'); }, delay + 1000);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in', 'is-done'); });
  }

  /* ---------- Zahlen zählen hoch ---------- */
  var counters = document.querySelectorAll('[data-count]');
  if (counters.length && !reduce && 'IntersectionObserver' in window) {
    var easeOut = function (t) { return 1 - Math.pow(1 - t, 4); };
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        cio.unobserve(en.target);
        var el = en.target, end = parseInt(el.dataset.count, 10), suffix = el.dataset.suffix || '';
        var start = null, dur = 1800, wait = 900;
        el.textContent = '0' + suffix;
        var tick = function (ts) {
          if (start === null) start = ts + wait;
          var t = Math.max(0, Math.min(1, (ts - start) / dur));
          el.textContent = Math.round(easeOut(t) * end) + suffix;
          if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  /* ---------- Logoband läuft endlos ---------- */
  var marquee = document.querySelector('.marquee');
  if (marquee) {
    if (reduce) { marquee.classList.add('is-static'); }
    else {
      var list = marquee.querySelector('.refs-list');
      Array.prototype.slice.call(list.children).forEach(function (li) {
        var c = li.cloneNode(true); c.setAttribute('aria-hidden', 'true'); list.appendChild(c);
      });
      marquee.classList.add('is-running');
    }
  }

  /* ---------- Scroll: Header, Fortschritt, Parallaxe ---------- */
  var header = document.querySelector('.header');
  var progress = document.querySelector('.scroll-progress');
  var strand = document.querySelector('.hero-strand-wrap');
  var lastY = window.scrollY, scrollTick = false;
  var onScroll = function () {
    scrollTick = false;
    var y = window.scrollY;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if (progress) progress.style.transform = 'scaleX(' + (max > 0 ? Math.min(1, y / max) : 0) + ')';
    if (header && !root.classList.contains('menu-open')) {
      if (y > 480 && y > lastY + 4) header.classList.add('is-hidden');
      else if (y < lastY - 4 || y <= 480) header.classList.remove('is-hidden');
    }
    if (strand && !reduce && y < window.innerHeight * 1.5) strand.style.transform = 'translate3d(0,' + (y * 0.18).toFixed(1) + 'px,0)';
    lastY = y;
  };
  window.addEventListener('scroll', function () {
    if (!scrollTick) { scrollTick = true; requestAnimationFrame(onScroll); }
  }, { passive: true });
  onScroll();

  /* ---------- Tagline: word by word ---------- */
  var tag = document.querySelector('[data-reveal-words]');
  if (tag) {
    var words = [];
    (function split(node, gold) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var s = document.createElement('span');
            s.className = 'w' + (gold ? ' gold' : '');
            s.textContent = part;
            words.push(s);
            frag.appendChild(s);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          split(child, gold || child.hasAttribute('data-gold'));
        }
      });
    })(tag, false);

    if (reduce) {
      words.forEach(function (w) { w.classList.add('on'); });
    } else {
      var ticking = false;
      var update = function () {
        ticking = false;
        var r = tag.getBoundingClientRect();
        var vh = window.innerHeight;
        // Fortschritt: Start, wenn der Absatz bei 85 % der Höhe ankommt, Ende bei 40 %.
        var p = (vh * 0.85 - r.top) / (vh * 0.45 + r.height * 0.5);
        var n = Math.round(Math.max(0, Math.min(1, p)) * words.length);
        words.forEach(function (w, i) { w.classList.toggle('on', i < n); });
      };
      window.addEventListener('scroll', function () {
        if (!ticking) { ticking = true; requestAnimationFrame(update); }
      }, { passive: true });
      update();
    }
  }

  /* ---------- Anfrage in Schritten ---------- */
  var dialog = document.getElementById('wizard');
  var form = document.getElementById('enquiry-form');
  if (!dialog || !form) return;

  var steps = Array.prototype.slice.call(form.querySelectorAll('.step'));
  var questions = steps.length - 1; // letzter Schritt ist die Bestätigung
  var bar = form.querySelector('.wizard-bar');
  var count = form.querySelector('.wizard-count');
  var foot = form.querySelector('.wizard-foot');
  var backBtn = form.querySelector('[data-back]');
  var nextBtn = form.querySelector('[data-next]');
  var resultText = document.getElementById('result-text');
  var copyBtn = document.getElementById('copy-btn');
  var current = 0;
  document.getElementById('result-mail').textContent = CONTACT_EMAIL;

  function show(i, back) {
    current = i;
    var done = i === questions;
    steps.forEach(function (st, n) {
      st.classList.toggle('is-active', n === i);
      st.classList.toggle('from-back', !!back);
    });
    var pct = done ? 100 : Math.round((i / questions) * 100);
    bar.firstElementChild.style.transform = 'scaleX(' + (done ? 1 : Math.max(i / questions, 0.04)) + ')';
    bar.setAttribute('aria-valuenow', String(pct));
    count.textContent = done ? 'Geschafft' : 'Frage ' + (i + 1) + ' von ' + questions;
    backBtn.hidden = i === 0 || done;
    foot.classList.toggle('is-done', done || i === 0);
    nextBtn.firstChild.textContent = done ? 'Schließen ' : (i === questions - 1 ? 'Anfrage senden ' : 'Weiter ');
    var focusEl = done ? steps[i].querySelector('h2')
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

  function send() {
    var d = new FormData(form);
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
    resultText.textContent = 'Betreff: ' + subject + '\n\n' + body;
    show(questions);
    window.location.href = 'mailto:' + CONTACT_EMAIL +
      '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  }

  function next() {
    if (current === questions) { dialog.close(); return; }
    var bad = validateStep(current);
    if (bad) { bad.focus(); return; }
    track('Anfrage Schritt', { schritt: current + 1 });
    if (current === questions - 1) { track('Anfrage gesendet'); send(); } else show(current + 1);
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
    if (current === questions) { form.reset(); current = 0; }
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
  backBtn.addEventListener('click', function () { if (current > 0) show(current - 1, true); });

  // Auswahl per Klick oder Tipp geht direkt zur nächsten Frage (nicht bei Tastatur).
  form.addEventListener('click', function (e) {
    if (e.target.matches('.option input') && e.detail > 0) {
      var at = current;
      setTimeout(function () { if (current === at) next(); }, 280);
    }
  });
  form.addEventListener('input', function (e) {
    var holder = e.target.closest('.invalid');
    if (holder) holder.classList.remove('invalid');
  });
  form.addEventListener('change', function (e) {
    var holder = e.target.closest('.invalid');
    if (holder) holder.classList.remove('invalid');
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
