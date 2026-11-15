(function () {
  var navToggle = document.querySelector('.nav-toggle');
  var menu = document.getElementById('menu');
  var themeToggle = document.querySelector('.theme-toggle');
  var themeIcon = document.querySelector('.theme-toggle__icon');
  var storageKey = 'agentic-ai-theme';
  var applicationDialog = document.querySelector('.application-dialog');
  var legalDialog = document.querySelector('.legal-dialog');
  var legalTitle = document.getElementById('legal-dialog-title');
  var legalContent = document.querySelector('.legal-dialog__content');
  var legalStatus = document.querySelector('.legal-dialog__status');

  document.querySelectorAll('[data-legal-document]').forEach(function (link) {
    link.addEventListener('click', function (event) {
      if (!legalDialog) return;

      event.preventDefault();
      legalTitle.textContent = link.textContent.trim();
      legalContent.replaceChildren();
      legalStatus.textContent = 'Loading document…';
      legalDialog.showModal();

      fetch(link.href, { headers: { Accept: 'application/json' } })
        .then(function (response) {
          if (!response.ok) throw new Error('Document request failed with status ' + response.status);
          return response.json();
        })
        .then(function (payload) {
          legalTitle.textContent = payload.title;
          payload.blocks.forEach(function (block) {
            var element = window.document.createElement(block.kind === 'h2' ? 'h3' : 'p');
            element.textContent = block.text;
            legalContent.appendChild(element);
          });
          legalStatus.textContent = 'Last updated ' + new Date(payload.updated_at).toLocaleDateString();
        })
        .catch(function () {
          legalStatus.textContent = 'The document could not be loaded. Please try again later.';
        });
    });
  });

  document.querySelectorAll('[data-close-legal]').forEach(function (button) {
    button.addEventListener('click', function () {
      if (legalDialog) legalDialog.close();
    });
  });

  if (legalDialog) {
    legalDialog.addEventListener('click', function (event) {
      if (event.target === legalDialog) legalDialog.close();
    });
  }

  document.querySelectorAll('[data-open-application]').forEach(function (button) {
    button.addEventListener('click', function () {
      if (applicationDialog) applicationDialog.showModal();
    });
  });

  document.querySelectorAll('[data-close-application]').forEach(function (button) {
    button.addEventListener('click', function () {
      if (applicationDialog) applicationDialog.close();
    });
  });

  if (applicationDialog && applicationDialog.hasAttribute('data-open-on-load')) {
    applicationDialog.showModal();
  }

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    document.body.classList.toggle('theme-dark', isDark);

    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(isDark));
      themeToggle.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }

    if (themeIcon) {
      themeIcon.textContent = isDark ? '🌙' : '☀️';
    }

    try {
      localStorage.setItem(storageKey, theme);
    } catch (error) {}
  }

  if (navToggle && menu) {
    navToggle.addEventListener('click', function () {
      var open = menu.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  function getPreferredTheme() {
    try {
      var savedTheme = localStorage.getItem(storageKey);
      if (savedTheme === 'dark' || savedTheme === 'light') {
        return savedTheme;
      }
    } catch (error) {}

    return 'dark';
  }

  if (themeToggle) {
    applyTheme(getPreferredTheme());

    themeToggle.addEventListener('click', function () {
      var nextTheme = document.body.classList.contains('theme-dark') ? 'light' : 'dark';
      applyTheme(nextTheme);
    });
  }

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('svg.loop').forEach(function (s) { if (s.pauseAnimations) s.pauseAnimations(); });
  }
})();
