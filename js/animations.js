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


});
