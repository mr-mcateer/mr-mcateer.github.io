// js/animations.js

document.addEventListener("DOMContentLoaded", () => {
    // Respect prefers-reduced-motion
    const isReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const isMobile = window.matchMedia("(max-width: 768px)").matches;

    // Intersection Observer for scroll triggers
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // Services cards stagger handled in CSS relying on .animate-in addition
                if (entry.target.classList.contains('service-card') || entry.target.classList.contains('case-card')) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }

                // Approach Section
                if (entry.target.classList.contains('approach-grid')) {
                    const steps = entry.target.querySelectorAll('.step-item');
                    steps.forEach((step, index) => {
                        setTimeout(() => {
                            step.classList.add('animate-in');
                        }, isReducedMotion ? 0 : index * 900); // 900ms stagger for steps sequence
                    });
                    observer.unobserve(entry.target);
                }

                // Flow Diagram
                if (entry.target.classList.contains('approach-visual')) {
                    const flowChildren = entry.target.children[0].children;
                    // Note: flow cascade timing handled by CSS transition-delays
                    Array.from(flowChildren).forEach(child => {
                        child.classList.add('animate-in');
                    });
                    observer.unobserve(entry.target);
                }
            }
        });
    }, { threshold: 0.2, rootMargin: '0px 0px -50px 0px' });

    // Observe Elements
    document.querySelectorAll('.service-card').forEach(el => observer.observe(el));
    document.querySelectorAll('.case-card').forEach(el => observer.observe(el));

    const approachSection = document.querySelector('.approach-grid');
    if (approachSection) observer.observe(approachSection);

    const approachVisual = document.querySelector('.approach-visual');
    if (approachVisual) observer.observe(approachVisual);

    // Typewriter Effect for Hero Headline
    const h1 = document.querySelector('.hero h1');
    if (h1) {
        if (!isMobile && !isReducedMotion) {
            const textLines = ["Your voice, amplified.", "Not replaced."];

            // Rebuild with individual character spans perfectly preserves layout size
            h1.innerHTML = '';
            h1.style.opacity = '1';
            h1.style.visibility = 'visible';

            const cursor = document.createElement('span');
            cursor.className = 'typewriter-cursor active';
            h1.appendChild(cursor);

            let charElements = [];
            textLines.forEach((line, lineIndex) => {
                for (let char of line) {
                    const charSpan = document.createElement('span');
                    charSpan.textContent = char;
                    charSpan.style.opacity = '0';
                    h1.appendChild(charSpan);
                    charElements.push(charSpan);
                }
                if (lineIndex < textLines.length - 1) {
                    h1.appendChild(document.createElement('br'));
                }
            });

            // Delay start by 800ms to allow context and CTA to fade in smoothly first
            setTimeout(() => {
                let i = 0;

                function typeWriter() {
                    if (i < charElements.length) {
                        charElements[i].style.opacity = '1';
                        // Move cursor after the revealed character
                        h1.insertBefore(cursor, charElements[i].nextSibling);

                        // Variable typing speed (fast letters, pause on punctuation)
                        let delay = 60;
                        const char = charElements[i].textContent;
                        if (char === '.' || char === ',') delay = 400;

                        i++;
                        setTimeout(typeWriter, Math.max(delay + (Math.random() * 30 - 15), 20)); // Humanize
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
