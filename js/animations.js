// js/animations.js

document.addEventListener("DOMContentLoaded", function () {
    var isReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var isMobile = window.matchMedia("(max-width: 768px)").matches;

    // ===== Intersection Observer for scroll triggers =====
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;

            // Service cards and case cards: stagger handled in CSS
            if (entry.target.classList.contains('service-card') ||
                entry.target.classList.contains('case-card') ||
                entry.target.classList.contains('case-card--featured')) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }

            // Approach cards: stagger via CSS --card-index
            if (entry.target.classList.contains('approach-card')) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2, rootMargin: '0px 0px -50px 0px' });

    // Observe all animatable elements
    document.querySelectorAll('.service-card').forEach(function (el) { observer.observe(el); });
    document.querySelectorAll('.case-card').forEach(function (el) { observer.observe(el); });
    document.querySelectorAll('.approach-card').forEach(function (el) { observer.observe(el); });

    var featuredCard = document.querySelector('.case-card--featured');
    if (featuredCard) observer.observe(featuredCard);

    // ===== Glow card mouse tracking =====
    if (!isMobile && !isReducedMotion) {
        document.querySelectorAll('.glow-card').forEach(function (card) {
            card.addEventListener('mousemove', function (e) {
                var rect = card.getBoundingClientRect();
                card.style.setProperty('--mouse-x', (e.clientX - rect.left) + 'px');
                card.style.setProperty('--mouse-y', (e.clientY - rect.top) + 'px');
            });
        });
    }

    // ===== Typewriter Effect for Hero Headline =====
    var h1 = document.querySelector('.hero h1');
    if (h1) {
        if (!isMobile && !isReducedMotion) {
            var textLines = ["Your voice, amplified.", "Not replaced."];

            h1.innerHTML = '';
            h1.style.opacity = '1';
            h1.style.visibility = 'visible';

            var cursor = document.createElement('span');
            cursor.className = 'typewriter-cursor active';
            h1.appendChild(cursor);

            var charElements = [];
            textLines.forEach(function (line, lineIndex) {
                for (var c = 0; c < line.length; c++) {
                    var charSpan = document.createElement('span');
                    charSpan.textContent = line[c];
                    charSpan.style.opacity = '0';
                    h1.appendChild(charSpan);
                    charElements.push(charSpan);
                }
                if (lineIndex < textLines.length - 1) {
                    h1.appendChild(document.createElement('br'));
                }
            });

            setTimeout(function () {
                var i = 0;

                function typeWriter() {
                    if (i < charElements.length) {
                        charElements[i].style.opacity = '1';
                        h1.insertBefore(cursor, charElements[i].nextSibling);

                        var delay = 60;
                        var char = charElements[i].textContent;
                        if (char === '.' || char === ',') delay = 400;

                        i++;
                        setTimeout(typeWriter, Math.max(delay + (Math.random() * 30 - 15), 20));
                    }
                }
                typeWriter();
            }, 800);
        } else {
            h1.style.opacity = '1';
            h1.style.visibility = 'visible';
            h1.style.animation = 'hero-fade-up 0.5s ease-out 0.8s forwards';
        }
    }
});
