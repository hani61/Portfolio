/* hanylockedin.com — site behaviour. No dependencies, no build step. */
(function () {
  'use strict';

  /* ==========================================================================
     CONFIG
     Paste your form endpoint here (Formspree, Web3Forms, Basin, a Worker…).
     While it is empty the forms run in demo mode: they validate, show the
     loading state, then redirect to the thank-you page with a clear notice
     that nothing was delivered. Nothing is ever silently "sent".
     Remember to also allow the endpoint in the Content-Security-Policy
     connect-src / form-action of each page.
     ========================================================================== */
  var FORM_ENDPOINT = '';

  var CONTACT_EMAIL = 'hello@hanylockedin.com';
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/;
  var URL_RE = /^https?:\/\/[^\s/]+\.[^\s]{2,}$/i;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  /* -------------------------------------------------------------------------
     Sanitising. Values are only ever written back with textContent, never
     as HTML, and control characters are stripped before anything is sent.
     ------------------------------------------------------------------------- */
  function clean(value, max) {
    return String(value == null ? '' : value)
      .replace(/[\u0000-\u001F\u007F]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .slice(0, max || 2000);
  }

  function isEmail(value) { return EMAIL_RE.test(value); }

  /* -------------------------------------------------------------------------
     Footer year
     ------------------------------------------------------------------------- */
  $$('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* -------------------------------------------------------------------------
     Navigation: scrolled state, mobile menu, page transition progress
     ------------------------------------------------------------------------- */
  var nav = $('#siteNav');
  var toggle = $('#navToggle');
  var menu = $('#navMenu');
  var stickyCta = $('#stickyCta');
  var progress = $('#navProgress');

  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (nav) nav.classList.toggle('is-scrolled', y > 12);
    if (stickyCta) stickyCta.classList.toggle('is-visible', y > 380);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  function setMenu(open) {
    if (!menu || !toggle) return;
    menu.hidden = !open;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      setMenu(menu.hidden);
    });
    $$('a', menu).forEach(function (link) {
      link.addEventListener('click', function () { setMenu(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) {
        setMenu(false);
        toggle.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth >= 900 && !menu.hidden) setMenu(false);
    });
  }

  // Thin orange bar during navigation so a click always feels acknowledged.
  function startProgress() {
    if (!progress) return;
    progress.classList.add('is-loading');
    progress.style.width = '72%';
  }
  function endProgress() {
    if (!progress) return;
    progress.style.width = '100%';
    window.setTimeout(function () {
      progress.classList.remove('is-loading');
      progress.style.width = '0';
    }, 240);
  }
  endProgress();

  document.addEventListener('click', function (e) {
    var link = e.target && e.target.closest ? e.target.closest('a') : null;
    if (!link) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    if (link.target === '_blank' || link.hasAttribute('download')) return;
    var href = link.getAttribute('href');
    if (!href || href.charAt(0) === '#' || /^(mailto|tel|sms|javascript):/i.test(href)) return;
    var url;
    try { url = new URL(link.href, window.location.href); } catch (err) { return; }
    if (url.origin !== window.location.origin) return;
    if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) return;
    startProgress();
    // Fail-safe: if the navigation never happens (blocked, download), reset.
    window.setTimeout(function () {
      if (progress) { progress.classList.remove('is-loading'); progress.style.width = '0'; }
    }, 8000);
  });

  window.addEventListener('pageshow', endProgress);

  /* -------------------------------------------------------------------------
     Reveal on scroll (degrades to visible without IntersectionObserver)
     ------------------------------------------------------------------------- */
  var revealables = $$('.reveal');
  if (!('IntersectionObserver' in window) || reduceMotion) {
    revealables.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var siblings = Array.prototype.slice.call(el.parentNode.children).filter(function (c) {
          return c.classList.contains('reveal');
        });
        var index = Math.max(0, siblings.indexOf(el));
        el.style.transitionDelay = Math.min(index * 70, 280) + 'ms';
        el.classList.add('is-in');
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* -------------------------------------------------------------------------
     Cookie banner — dismissible, does not block content, remembers the choice
     ------------------------------------------------------------------------- */
  var banner = $('#cookieBanner');
  var CONSENT_KEY = 'hany.consent.v1';

  function readConsent() {
    try { return window.localStorage.getItem(CONSENT_KEY); } catch (err) { return null; }
  }
  function writeConsent(value) {
    try { window.localStorage.setItem(CONSENT_KEY, value); } catch (err) { /* private mode */ }
  }
  function hideBanner() {
    if (!banner) return;
    banner.classList.add('is-hiding');
    window.setTimeout(function () { banner.hidden = true; }, 300);
  }

  if (banner && !readConsent()) {
    window.setTimeout(function () { banner.hidden = false; }, 1100);
  }
  $$('#cookieAccept, #cookieDismiss').forEach(function (btn) {
    btn.addEventListener('click', function () {
      writeConsent(btn.id === 'cookieAccept' ? 'all' : 'essential');
      hideBanner();
    });
  });

  /* -------------------------------------------------------------------------
     Forms
     ------------------------------------------------------------------------- */
  var MESSAGES = {
    name: 'Add your name so I know who I’m replying to.',
    email: 'I need an email address to reply to.',
    service: 'Pick the closest option — even if you’re not sure.',
    message: 'Tell me what’s not working. One or two lines is enough.',
    consent: 'Please tick the box so I’m allowed to reply.',
    shortName: 'That looks a little short — at least 2 characters.',
    shortMessage: 'A little more detail helps: at least 20 characters.',
    badEmail: 'That email looks incomplete — check for a typo, like name@business.com.',
    badUrl: 'Websites start with https:// — or leave it empty if you don’t have one.'
  };

  function fieldValue(field) {
    if (field.type === 'checkbox') return field.checked;
    return clean(field.value, field.getAttribute('maxlength') ? Number(field.getAttribute('maxlength')) : 2000);
  }

  function validateField(field) {
    var value = fieldValue(field);
    var minLength = Number(field.getAttribute('minlength') || 0);

    if (field.type === 'checkbox') {
      return value ? '' : MESSAGES[field.name] || MESSAGES.consent;
    }
    if (!value) {
      return MESSAGES[field.name] || 'This field is needed.';
    }
    if (field.type === 'email' && !isEmail(value)) return MESSAGES.badEmail;
    if (field.type === 'url' && !URL_RE.test(value)) return MESSAGES.badUrl;
    if (minLength && value.length < minLength) {
      return field.name === 'message' ? MESSAGES.shortMessage : MESSAGES.shortName;
    }
    return '';
  }

  function setFieldError(field, message) {
    var target = document.getElementById(field.id + '-error');
    if (message) {
      field.setAttribute('aria-invalid', 'true');
      if (target) target.textContent = message;
    } else {
      field.removeAttribute('aria-invalid');
      if (target) target.textContent = '';
    }
  }

  function setStatus(statusEl, tone, message) {
    if (!statusEl) return;
    if (!message) {
      statusEl.hidden = true;
      statusEl.textContent = '';
      return;
    }
    statusEl.hidden = false;
    statusEl.setAttribute('data-tone', tone);
    statusEl.textContent = message;
  }

  function setLoading(form, loading) {
    var button = $('[data-submit]', form);
    var label = $('[data-submit-label]', form);
    var spinner = $('[data-spinner]', form);
    if (button) {
      button.disabled = loading;
      button.setAttribute('aria-busy', loading ? 'true' : 'false');
    }
    if (spinner) spinner.hidden = !loading;
    if (label) {
      if (!label.dataset.idleLabel) label.dataset.idleLabel = label.textContent;
      label.textContent = loading ? 'Sending…' : label.dataset.idleLabel;
    }
  }

  function wireForm(form) {
    var fields = $$('input, select, textarea', form).filter(function (f) {
      return !f.closest('.honeypot') && f.type !== 'hidden';
    });
    var statusEl = $('[data-form-status]', form);
    var submitButton = $('[data-submit]', form);
    var mode = form.getAttribute('data-mode') || 'inline';
    var formName = form.getAttribute('data-form-name') || 'form';

    // Clear errors as the visitor fixes them — never re-validate mid-typing.
    fields.forEach(function (field) {
      field.addEventListener('blur', function () {
        if (field.type === 'checkbox') return;
        setFieldError(field, validateField(field));
      });
      field.addEventListener('input', function () {
        if (field.getAttribute('aria-invalid') === 'true' && !validateField(field)) {
          setFieldError(field, '');
        }
      });
      field.addEventListener('change', function () {
        if (field.getAttribute('aria-invalid') === 'true' && !validateField(field)) {
          setFieldError(field, '');
        }
      });
    });

    // Live character counter
    var counterTarget = $('[data-count-for]', form.parentNode) || $('[data-count-for]');
    if (counterTarget) {
      var source = document.getElementById(counterTarget.getAttribute('data-count-for'));
      if (source) {
        var updateCount = function () { counterTarget.textContent = String(source.value.length); };
        source.addEventListener('input', updateCount);
        updateCount();
      }
    }

    form.addEventListener('submit', function (event) {
      event.preventDefault();
      setStatus(statusEl, '', '');

      var firstInvalid = null;
      fields.forEach(function (field) {
        if (field.required || field.type === 'url' || field.type === 'email') {
          var message = validateField(field);
          setFieldError(field, message);
          if (message && !firstInvalid) firstInvalid = field;
        }
      });

      if (firstInvalid) {
        setStatus(statusEl, 'error', 'Almost there — check the highlighted field' +
          (firstInvalid.id ? ' above.' : '.'));
        firstInvalid.focus();
        firstInvalid.scrollIntoView({ block: 'center', behavior: reduceMotion ? 'auto' : 'smooth' });
        return;
      }

      // Bots fill hidden fields. Accept silently, send nothing.
      var honey = $('.honeypot input', form);
      if (honey && clean(honey.value)) {
        setStatus(statusEl, 'success', 'Thanks — that’s in.');
        return;
      }

      var payload = { form: formName, page: window.location.pathname, submittedAt: new Date().toISOString() };
      fields.forEach(function (field) {
        if (field.type === 'checkbox') {
          payload[field.name] = !!field.checked;
        } else if (field.name) {
          var value = fieldValue(field);
          payload[field.name] = field.type === 'email' ? value.toLowerCase() : value;
        }
      });

      setLoading(form, true);
      if (submitButton) submitButton.setAttribute('aria-busy', 'true');

      var finish = function (delivered) {
        setLoading(form, false);
        if (mode === 'redirect') {
          var params = new URLSearchParams({ type: formName });
          if (!delivered) params.set('demo', '1');
          window.location.assign('/thank-you.html?' + params.toString());
          return;
        }
        var panel = $('[data-lead-success]', form.parentNode);
        if (panel) {
          form.classList.add('hidden');
          panel.classList.remove('hidden');
          panel.setAttribute('tabindex', '-1');
          panel.focus();
          var download = form.getAttribute('data-success-download');
          if (download) {
            var link = $('a[download]', panel);
            if (link) link.href = download;
          }
          setStatus(statusEl, '', '');
        } else {
          setStatus(statusEl, 'success', 'Got it — I’ll reply within 24 hours.');
          form.reset();
        }
      };

      // No endpoint configured: honest demo mode, clearly labelled downstream.
      if (!FORM_ENDPOINT) {
        window.setTimeout(function () { finish(false); }, reduceMotion ? 250 : 850);
        return;
      }

      var controller = new AbortController();
      var timer = window.setTimeout(function () { controller.abort(); }, 15000);

      fetch(FORM_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      }).then(function (response) {
        window.clearTimeout(timer);
        if (response.ok) {
          finish(true);
          return;
        }
        var message;
        if (response.status === 422) {
          message = 'The form service rejected one of the fields. Check your email address and try again.';
        } else if (response.status === 429) {
          message = 'Too many attempts from this connection. Wait a minute, or DM “SITE” on Instagram.';
        } else if (response.status >= 500) {
          message = 'The form service is down (error ' + response.status + '). Your message wasn’t sent — email ' + CONTACT_EMAIL + ' and I’ll reply from there.';
        } else {
          message = 'The form didn’t go through (error ' + response.status + '). Try again, or email ' + CONTACT_EMAIL + '.';
        }
        setStatus(statusEl, 'error', message);
        setLoading(form, false);
      }).catch(function (error) {
        window.clearTimeout(timer);
        var message = error && error.name === 'AbortError'
          ? 'That took too long, so I stopped waiting. Check your connection and try again — or DM “SITE” on Instagram.'
          : 'Couldn’t reach the form service. Check your connection and try again, or email ' + CONTACT_EMAIL + '.';
        setStatus(statusEl, 'error', message);
        setLoading(form, false);
      });
    });
  }

  $$('form[data-form-name]').forEach(wireForm);

  /* -------------------------------------------------------------------------
     Page-specific touches
     ------------------------------------------------------------------------- */
  var params = new URLSearchParams(window.location.search);

  // Pre-select the service from /contact.html?service=wordpress
  var serviceParam = params.get('service');
  var serviceSelect = $('#service');
  if (serviceParam && serviceSelect) {
    var match = $$('option', serviceSelect).some(function (opt) {
      if (opt.value === serviceParam) { serviceSelect.value = serviceParam; return true; }
      return false;
    });
    if (match) serviceSelect.setAttribute('data-prefilled', 'true');
  }

  // /thank-you.html?type=playbook&demo=1
  var downloadPanel = $('#downloadPanel');
  if (downloadPanel && params.get('type') === 'playbook') downloadPanel.hidden = false;
  var demoNotice = $('#demoNotice');
  if (demoNotice && params.get('demo') === '1') demoNotice.hidden = false;

  // No-JS fallback message for forms
  $$('noscript').forEach(function () { /* noop: kept for clarity */ });
})();
