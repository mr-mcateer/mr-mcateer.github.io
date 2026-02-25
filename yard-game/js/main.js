/* ============================================================
   main.js -- Frisbeam Yard Game
   Scroll reveal, counters, nav, mobile drawer, accordion, cart,
   hero parallax, dismissible announcement bar
   ============================================================ */
(function () {
  'use strict';

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ============================================================
     Scroll Reveal
     ============================================================ */
  var revealElements = document.querySelectorAll('.reveal');

  if (prefersReducedMotion) {
    for (var r = 0; r < revealElements.length; r++) {
      revealElements[r].classList.add('visible');
    }
  } else {
    var heroReveals = document.querySelectorAll('.hero .reveal, .hero.reveal');
    for (var h = 0; h < heroReveals.length; h++) {
      heroReveals[h].classList.add('visible');
    }

    if ('IntersectionObserver' in window) {
      var revealObserver = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) {
            entries[i].target.classList.add('visible');
            revealObserver.unobserve(entries[i].target);
          }
        }
      }, { threshold: 0.08, rootMargin: '0px 0px -20px 0px' });

      for (var v = 0; v < revealElements.length; v++) {
        if (!revealElements[v].classList.contains('visible')) {
          revealObserver.observe(revealElements[v]);
        }
      }
    } else {
      for (var f = 0; f < revealElements.length; f++) {
        revealElements[f].classList.add('visible');
      }
    }
  }

  /* ============================================================
     Counter Animation
     ============================================================ */
  var counters = document.querySelectorAll('[data-counter]');

  function animateCounter(el) {
    var target = parseInt(el.getAttribute('data-counter'), 10) || 0;
    var prefix = el.getAttribute('data-prefix') || '';
    var suffix = el.getAttribute('data-suffix') || '';
    var duration = 2000;
    var start = null;

    if (prefersReducedMotion) {
      el.textContent = prefix + target.toLocaleString() + suffix;
      return;
    }

    function step(timestamp) {
      if (!start) start = timestamp;
      var elapsed = timestamp - start;
      var progress = Math.min(elapsed / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.round(eased * target);
      el.textContent = prefix + current.toLocaleString() + suffix;
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = prefix + target.toLocaleString() + suffix;
      }
    }

    requestAnimationFrame(step);
  }

  if (counters.length > 0 && 'IntersectionObserver' in window) {
    var counterObserver = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          animateCounter(entries[i].target);
          counterObserver.unobserve(entries[i].target);
        }
      }
    }, { threshold: 0.2 });

    for (var c = 0; c < counters.length; c++) {
      counterObserver.observe(counters[c]);
    }
  } else {
    for (var cf = 0; cf < counters.length; cf++) {
      var t = parseInt(counters[cf].getAttribute('data-counter'), 10) || 0;
      var p = counters[cf].getAttribute('data-prefix') || '';
      var s = counters[cf].getAttribute('data-suffix') || '';
      counters[cf].textContent = p + t.toLocaleString() + s;
    }
  }

  /* ============================================================
     Sticky Nav -- add shadow on scroll
     ============================================================ */
  var siteNav = document.querySelector('.site-nav');
  if (siteNav) {
    var navTicking = false;
    window.addEventListener('scroll', function () {
      if (!navTicking) {
        requestAnimationFrame(function () {
          if (window.pageYOffset > 10) {
            siteNav.classList.add('site-nav--scrolled');
          } else {
            siteNav.classList.remove('site-nav--scrolled');
          }
          navTicking = false;
        });
        navTicking = true;
      }
    }, { passive: true });
  }

  /* ============================================================
     Hero Parallax
     ============================================================ */
  var heroBg = document.querySelector('.hero__bg img');
  if (heroBg && !prefersReducedMotion) {
    var parallaxTicking = false;
    window.addEventListener('scroll', function () {
      if (!parallaxTicking) {
        requestAnimationFrame(function () {
          var scrollY = window.pageYOffset;
          if (scrollY < window.innerHeight) {
            heroBg.style.transform = 'translateY(' + (scrollY * 0.3) + 'px) scale(1.1)';
          }
          parallaxTicking = false;
        });
        parallaxTicking = true;
      }
    }, { passive: true });
    heroBg.style.transform = 'scale(1.1)';
  }

  /* ============================================================
     Mobile Navigation
     ============================================================ */
  var hamburger = document.querySelector('.site-nav__hamburger');
  var mobileNav = document.querySelector('.mobile-nav');
  var mobileOverlay = document.querySelector('.mobile-overlay');
  var mobileClose = document.querySelector('.mobile-nav__close');

  function openMobile() {
    if (mobileNav) mobileNav.classList.add('open');
    if (mobileOverlay) mobileOverlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }

  function closeMobile() {
    if (mobileNav) mobileNav.classList.remove('open');
    if (mobileOverlay) mobileOverlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  if (hamburger) hamburger.addEventListener('click', openMobile);
  if (mobileClose) mobileClose.addEventListener('click', closeMobile);
  if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobile);

  /* ============================================================
     Accordion -- one-at-a-time
     ============================================================ */
  var accordions = document.querySelectorAll('.accordion');

  for (var a = 0; a < accordions.length; a++) {
    (function (accordion) {
      var details = accordion.querySelectorAll('details');
      for (var d = 0; d < details.length; d++) {
        details[d].addEventListener('toggle', function () {
          if (!this.open) return;
          var siblings = accordion.querySelectorAll('details');
          var current = this;
          for (var s = 0; s < siblings.length; s++) {
            if (siblings[s] !== current && siblings[s].open) {
              siblings[s].removeAttribute('open');
            }
          }
        });
      }
    })(accordions[a]);
  }

  /* ============================================================
     Cart System (localStorage-backed)
     ============================================================ */
  var cartBtn = document.querySelector('.site-nav__cart');
  var cartDrawer = document.querySelector('.cart-drawer');
  var cartClose = document.querySelector('.cart-drawer__close');
  var cartOverlay = document.querySelector('.cart-overlay');
  var cartItemsEl = document.querySelector('.cart-drawer__items');
  var cartTotalEl = document.querySelector('.cart-drawer__total span:last-child');
  var cartCountEls = document.querySelectorAll('.site-nav__cart-count');

  function getCart() {
    try { return JSON.parse(localStorage.getItem('frisbeam_cart')) || []; }
    catch (e) { return []; }
  }

  function saveCart(cart) {
    localStorage.setItem('frisbeam_cart', JSON.stringify(cart));
  }

  function renderCart() {
    var cart = getCart();
    var total = 0;
    var count = 0;

    if (!cartItemsEl) return;

    if (cart.length === 0) {
      cartItemsEl.innerHTML = '<p class="cart-drawer__empty">Your cart is empty.</p>';
    } else {
      var html = '';
      for (var i = 0; i < cart.length; i++) {
        var item = cart[i];
        total += item.price * item.qty;
        count += item.qty;
        html += '<div class="cart-item" data-index="' + i + '">' +
          '<div class="cart-item__info">' +
            '<div class="cart-item__name">' + item.name + '</div>' +
            '<div class="cart-item__price">$' + item.price + ' x ' + item.qty + '</div>' +
          '</div>' +
          '<button class="cart-item__remove" aria-label="Remove ' + item.name + '">&times;</button>' +
        '</div>';
      }
      cartItemsEl.innerHTML = html;

      var removeBtns = cartItemsEl.querySelectorAll('.cart-item__remove');
      for (var rb = 0; rb < removeBtns.length; rb++) {
        removeBtns[rb].addEventListener('click', function () {
          var idx = parseInt(this.parentElement.getAttribute('data-index'), 10);
          var c = getCart();
          c.splice(idx, 1);
          saveCart(c);
          renderCart();
        });
      }
    }

    if (cartTotalEl) cartTotalEl.textContent = '$' + total.toFixed(2);
    for (var ce = 0; ce < cartCountEls.length; ce++) {
      cartCountEls[ce].textContent = count;
    }
  }

  function addToCart(name, price) {
    var cart = getCart();
    var found = false;
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].name === name) {
        cart[i].qty += 1;
        found = true;
        break;
      }
    }
    if (!found) {
      cart.push({ name: name, price: price, qty: 1 });
    }
    saveCart(cart);
    renderCart();
    openCart();
  }

  function openCart() {
    if (cartDrawer) cartDrawer.classList.add('open');
    if (cartOverlay) cartOverlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }

  function closeCart() {
    if (cartDrawer) cartDrawer.classList.remove('open');
    if (cartOverlay) cartOverlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  if (cartBtn) cartBtn.addEventListener('click', openCart);
  if (cartClose) cartClose.addEventListener('click', closeCart);
  if (cartOverlay) cartOverlay.addEventListener('click', closeCart);

  // Wire up all Add to Cart buttons
  var addBtns = document.querySelectorAll('[data-add-cart]');
  for (var ab = 0; ab < addBtns.length; ab++) {
    addBtns[ab].addEventListener('click', function () {
      var name = this.getAttribute('data-product');
      var price = parseFloat(this.getAttribute('data-price'));
      if (name && price) addToCart(name, price);
    });
  }

  // Render cart on page load
  renderCart();

  /* ============================================================
     Product Gallery -- thumbnail click swap
     ============================================================ */
  var thumbs = document.querySelectorAll('.product-gallery__thumb');
  var mainImg = document.querySelector('.product-gallery__main img');

  for (var th = 0; th < thumbs.length; th++) {
    thumbs[th].addEventListener('click', function () {
      if (mainImg) {
        mainImg.src = this.src;
        mainImg.alt = this.alt;
      }
      for (var at = 0; at < thumbs.length; at++) {
        thumbs[at].classList.remove('active');
      }
      this.classList.add('active');
    });
  }

  /* ============================================================
     Dismissible Announcement Bar
     ============================================================ */
  var announceBar = document.querySelector('.announce-bar');
  if (announceBar) {
    if (localStorage.getItem('frisbeam_announce_dismissed') === '1') {
      announceBar.style.display = 'none';
    } else {
      var closeBtn = announceBar.querySelector('.announce-bar__close');
      if (closeBtn) {
        closeBtn.addEventListener('click', function () {
          announceBar.style.display = 'none';
          localStorage.setItem('frisbeam_announce_dismissed', '1');
        });
      }
    }
  }

})();
