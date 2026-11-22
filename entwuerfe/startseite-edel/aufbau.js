// DOM-Umbau für den Entwurf „edel“ (Logo-Muster, Hinweis, Zahlen-Umzug). Als Vorlage, nicht eingebunden.
function aufbau(lead, bridge, rows, gap) {
      document.querySelector('.hero .lead').textContent = lead;
      document.querySelector('.refs-bridge').textContent = bridge;
      const hint = document.createElement('p'); hint.className = 'va-hint';
      hint.textContent = 'Im Hintergrund: Kunden, für die das Team um Marvin Angerer produziert hat.';
      document.querySelector('.hero-actions').after(hint);
      // Zahlen aus dem Hero zu „Zweimal Angerer“ verschieben
      const st = document.querySelector('.hero .stats');
      const dl = document.createElement('dl'); dl.className = 'va-stats'; dl.innerHTML = st.innerHTML;
      document.querySelector('.about-copy .lead').after(dl);
      // Logo-Muster
      const src = [...document.querySelectorAll('.refs .logos > li')].slice(0, 12).map(li => li.innerHTML);
      const lp = document.createElement('div'); lp.className = 'lp'; lp.style.setProperty('--lp-gap', gap + 'px');
      for (let r = 0; r < rows; r++) {
        const row = document.createElement('div'); row.className = 'lp-row';
        const start = (r * 5) % src.length; const seq = [...src.slice(start), ...src.slice(0, start)];
        row.innerHTML = seq.concat(seq).join(''); row.style.transform = `translateX(${r % 2 ? -260 : -40}px)`;
        lp.appendChild(row);
      }
      document.querySelector('.hero').prepend(lp);
    }
