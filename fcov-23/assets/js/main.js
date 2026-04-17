/* ==========================================================
   FCoV-23 — Main JS
   Theme toggle · Mobile nav · Scroll effects · Reveal
   ========================================================== */

(function () {
  'use strict';

  /* ---- Theme ---- */
  const STORAGE_KEY = 'fcov23-theme';
  const root = document.documentElement;

  function getPreferred() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    const btn = document.querySelector('.theme-toggle');
    if (btn) btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }

  // Init theme without flash (inline script sets it before paint, this is the fallback)
  const saved = localStorage.getItem(STORAGE_KEY);
  applyTheme(saved || getPreferred());

  document.addEventListener('DOMContentLoaded', function () {

    /* ---- Theme toggle ---- */
    const toggleBtn = document.querySelector('.theme-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function () {
        applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
      });
    }

    /* ---- Mobile nav ---- */
    const hamburger = document.querySelector('.nav-hamburger');
    const navLinks  = document.querySelector('.nav-links');
    if (hamburger && navLinks) {
      hamburger.addEventListener('click', function () {
        const open = hamburger.getAttribute('aria-expanded') === 'true';
        hamburger.setAttribute('aria-expanded', String(!open));
        navLinks.classList.toggle('open', !open);
      });
      // Close on link click
      navLinks.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () {
          hamburger.setAttribute('aria-expanded', 'false');
          navLinks.classList.remove('open');
        });
      });
    }

    /* ---- Nav scroll state ---- */
    var nav = document.querySelector('.site-nav');
    if (nav) {
      function onScroll() {
        nav.classList.toggle('scrolled', window.scrollY > 20);
      }
      window.addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }

    /* ---- Active page link ---- */
    var path = window.location.pathname.replace(/\/$/, '') || '/index';
    document.querySelectorAll('.nav-links a').forEach(function (a) {
      var href = a.getAttribute('href').replace(/\/$/, '') || '/index';
      if (path === href || (path === '' && href === '/index') || (path.endsWith('/index.html') && href === '/index')) {
        a.setAttribute('aria-current', 'page');
      }
    });

    /* ---- Reveal on scroll ---- */
    var reveals = document.querySelectorAll('.reveal');
    if (reveals.length > 0 && 'IntersectionObserver' in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
      reveals.forEach(function (el) { observer.observe(el); });
    } else {
      reveals.forEach(function (el) { el.classList.add('visible'); });
    }

    /* ---- Contact form ---- */
    var form = document.querySelector('.contact-form');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var data = new FormData(form);
        var btn  = form.querySelector('[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Sending…';
        var mailto = 'mailto:info@fcov23.org'
          + '?subject=' + encodeURIComponent(data.get('subject') || 'Contact from website')
          + '&body=' + encodeURIComponent(
              'From: ' + data.get('name') + ' <' + data.get('email') + '>\n\n' + data.get('message')
            );
        window.location.href = mailto;
        setTimeout(function () {
          btn.disabled = false;
          btn.textContent = 'Send Message';
        }, 2000);
      });
    }

  });

})();
