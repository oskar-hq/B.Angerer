/* Angerer Consulting */
(function () {
  'use strict';

  // Empfänger der Anfragen. Für die Testphase laut Absprache; später auf Bettinas Adresse ändern.
  var CONTACT_EMAIL = 'info@oskarjakobsen.dk';

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

  /* ---------- Scroll reveals ---------- */
  var reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- Current nav item ---------- */
  var navLinks = document.querySelectorAll('.nav a');
  if ('IntersectionObserver' in window && navLinks.length) {
    var map = {};
    navLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var navIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        navLinks.forEach(function (a) { a.removeAttribute('aria-current'); });
        var link = map[en.target.id];
        if (link) link.setAttribute('aria-current', 'true');
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    document.querySelectorAll('main section[id]').forEach(function (s) { navIo.observe(s); });
  }

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

  /* ---------- Anfrageformular ---------- */
  var form = document.getElementById('enquiry-form');
  if (!form) return;
  var result = document.getElementById('form-result');
  var resultText = document.getElementById('result-text');
  var copyBtn = document.getElementById('copy-btn');
  document.getElementById('result-mail').textContent = CONTACT_EMAIL;

  function mark(el, bad) { el.classList.toggle('invalid', bad); return bad; }

  function validate() {
    var firstBad = null;
    form.querySelectorAll('[data-required]').forEach(function (fs) {
      var bad = !form.querySelector('input[name="' + fs.dataset.required + '"]:checked');
      if (mark(fs, bad) && !firstBad) firstBad = fs.querySelector('input');
    });
    form.querySelectorAll('.field').forEach(function (f) {
      var input = f.querySelector('input, textarea');
      if (!input.required && !input.value) { mark(f, false); return; }
      var bad = !input.value.trim() ||
        (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(input.value.trim()));
      input.setAttribute('aria-invalid', String(bad));
      if (mark(f, bad) && !firstBad) firstBad = input;
    });
    var checkWrap = form.querySelector('[data-check]');
    var check = checkWrap.querySelector('input');
    if (mark(checkWrap, !check.checked) && !firstBad) firstBad = check;
    return firstBad;
  }

  form.addEventListener('input', function (e) {
    var holder = e.target.closest('.invalid');
    if (holder) holder.classList.remove('invalid');
  });
  form.addEventListener('change', function (e) {
    var holder = e.target.closest('.invalid');
    if (holder) holder.classList.remove('invalid');
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = validate();
    if (bad) { bad.focus(); return; }
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
    result.classList.add('show');
    result.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest' });
    window.location.href = 'mailto:' + CONTACT_EMAIL +
      '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });

  copyBtn.addEventListener('click', function () {
    var text = resultText.textContent;
    var done = function () { copyBtn.textContent = 'Kopiert'; setTimeout(function () { copyBtn.textContent = 'Text kopieren'; }, 2000); };
    if (navigator.clipboard) { navigator.clipboard.writeText(text).then(done, function () {}); }
    else {
      var r = document.createRange(); r.selectNodeContents(resultText);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
      try { document.execCommand('copy'); done(); } catch (err) {}
    }
  });
})();
