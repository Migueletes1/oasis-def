// accessibility.js - Módulo de Accesibilidad WCAG 2.1
(function() {
    'use strict';

    // Estado de accesibilidad
    const a11yState = {
        fontSize: 100,
        highContrast: false,
        grayscale: false,
        invert: false,
        dyslexia: false,
        highlight: false,
        readingGuide: false,
        noMotion: false
    };

    // Elementos del DOM
    const fab = document.getElementById('a11y-fab');
    const panel = document.getElementById('a11y-panel');
    const overlay = document.getElementById('a11y-overlay');
    const readingGuide = document.getElementById('a11y-reading-guide');

    if (!fab || !panel) return;

    // Cargar estado guardado
    function loadState() {
        const saved = localStorage.getItem('a11y-state');
        if (saved) {
            try {
                Object.assign(a11yState, JSON.parse(saved));
                applyAllSettings();
            } catch (e) {
                console.error('Error loading accessibility state:', e);
            }
        }
    }

    // Guardar estado
    function saveState() {
        localStorage.setItem('a11y-state', JSON.stringify(a11yState));
    }

    // Abrir/cerrar panel
    function togglePanel() {
        const isOpen = panel.classList.contains('open');

        if (isOpen) {
            panel.classList.remove('open');
            overlay.classList.remove('open');
            fab.setAttribute('aria-expanded', 'false');
        } else {
            panel.classList.add('open');
            overlay.classList.add('open');
            fab.setAttribute('aria-expanded', 'true');
        }
    }

    // Cerrar panel
    function closePanel() {
        panel.classList.remove('open');
        overlay.classList.remove('open');
        fab.setAttribute('aria-expanded', 'false');
    }

    // Aplicar tamaño de fuente
    function applyFontSize() {
        document.documentElement.style.fontSize = `${a11yState.fontSize}%`;
        const display = document.getElementById('a11y-font-size-display');
        if (display) {
            display.textContent = `${a11yState.fontSize}%`;
        }
    }

    // Aplicar alto contraste
    function applyHighContrast() {
        if (a11yState.highContrast) {
            document.body.classList.add('high-contrast');
        } else {
            document.body.classList.remove('high-contrast');
        }
        updateToggleButton('a11y-toggle-high-contrast', a11yState.highContrast);
    }

    // Aplicar escala de grises
    function applyGrayscale() {
        if (a11yState.grayscale) {
            document.body.style.filter = 'grayscale(100%)';
        } else {
            document.body.style.filter = '';
        }
        updateToggleButton('a11y-toggle-grayscale', a11yState.grayscale);
    }

    // Aplicar inversión de colores
    function applyInvert() {
        if (a11yState.invert) {
            document.body.classList.add('invert-colors');
        } else {
            document.body.classList.remove('invert-colors');
        }
        updateToggleButton('a11y-toggle-invert', a11yState.invert);
    }

    // Aplicar fuente para dislexia
    function applyDyslexia() {
        if (a11yState.dyslexia) {
            document.body.style.fontFamily = 'OpenDyslexic, Arial, sans-serif';
        } else {
            document.body.style.fontFamily = '';
        }
        updateToggleButton('a11y-toggle-dyslexia', a11yState.dyslexia);
    }

    // Aplicar resaltado de enlaces
    function applyHighlight() {
        if (a11yState.highlight) {
            document.body.classList.add('highlight-links');
        } else {
            document.body.classList.remove('highlight-links');
        }
        updateToggleButton('a11y-toggle-highlight', a11yState.highlight);
    }

    // Aplicar guía de lectura
    function applyReadingGuide() {
        if (a11yState.readingGuide && readingGuide) {
            readingGuide.classList.add('active');
            document.addEventListener('mousemove', updateReadingGuide);
        } else if (readingGuide) {
            readingGuide.classList.remove('active');
            document.removeEventListener('mousemove', updateReadingGuide);
        }
        updateToggleButton('a11y-toggle-reading-guide', a11yState.readingGuide);
    }

    // Actualizar posición de guía de lectura
    function updateReadingGuide(e) {
        if (readingGuide) {
            readingGuide.style.top = `${e.clientY}px`;
        }
    }

    // Aplicar detener animaciones
    function applyNoMotion() {
        if (a11yState.noMotion) {
            document.body.classList.add('no-motion');
            // Emitir evento personalizado para Three.js
            window.dispatchEvent(new CustomEvent('a11y:no-motion', {
                detail: { enabled: true }
            }));
        } else {
            document.body.classList.remove('no-motion');
            window.dispatchEvent(new CustomEvent('a11y:no-motion', {
                detail: { enabled: false }
            }));
        }
        updateToggleButton('a11y-toggle-no-motion', a11yState.noMotion);
    }

    // Actualizar botón de toggle
    function updateToggleButton(buttonId, isActive) {
        const button = document.getElementById(buttonId);
        if (button) {
            if (isActive) {
                button.classList.add('active');
                button.setAttribute('aria-pressed', 'true');
            } else {
                button.classList.remove('active');
                button.setAttribute('aria-pressed', 'false');
            }
        }
    }

    // Aplicar todas las configuraciones
    function applyAllSettings() {
        applyFontSize();
        applyHighContrast();
        applyGrayscale();
        applyInvert();
        applyDyslexia();
        applyHighlight();
        applyReadingGuide();
        applyNoMotion();
    }

    // Resetear todo
    function resetAll() {
        a11yState.fontSize = 100;
        a11yState.highContrast = false;
        a11yState.grayscale = false;
        a11yState.invert = false;
        a11yState.dyslexia = false;
        a11yState.highlight = false;
        a11yState.readingGuide = false;
        a11yState.noMotion = false;

        applyAllSettings();
        saveState();
    }

    // Event Listeners
    fab.addEventListener('click', togglePanel);
    overlay.addEventListener('click', closePanel);

    // Cerrar con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && panel.classList.contains('open')) {
            closePanel();
        }
    });

    // Tamaño de fuente
    const fontDecrease = document.getElementById('a11y-font-decrease');
    const fontIncrease = document.getElementById('a11y-font-increase');

    if (fontDecrease) {
        fontDecrease.addEventListener('click', () => {
            if (a11yState.fontSize > 80) {
                a11yState.fontSize -= 10;
                applyFontSize();
                saveState();
            }
        });
    }

    if (fontIncrease) {
        fontIncrease.addEventListener('click', () => {
            if (a11yState.fontSize < 150) {
                a11yState.fontSize += 10;
                applyFontSize();
                saveState();
            }
        });
    }

    // Toggles
    const toggles = [
        { id: 'a11y-toggle-high-contrast', key: 'highContrast', apply: applyHighContrast },
        { id: 'a11y-toggle-grayscale', key: 'grayscale', apply: applyGrayscale },
        { id: 'a11y-toggle-invert', key: 'invert', apply: applyInvert },
        { id: 'a11y-toggle-dyslexia', key: 'dyslexia', apply: applyDyslexia },
        { id: 'a11y-toggle-highlight', key: 'highlight', apply: applyHighlight },
        { id: 'a11y-toggle-reading-guide', key: 'readingGuide', apply: applyReadingGuide },
        { id: 'a11y-toggle-no-motion', key: 'noMotion', apply: applyNoMotion }
    ];

    toggles.forEach(toggle => {
        const button = document.getElementById(toggle.id);
        if (button) {
            button.addEventListener('click', () => {
                a11yState[toggle.key] = !a11yState[toggle.key];
                toggle.apply();
                saveState();
            });
        }
    });

    // Reset
    const resetButton = document.getElementById('a11y-reset');
    if (resetButton) {
        resetButton.addEventListener('click', () => {
            if (confirm('¿Restablecer todas las opciones de accesibilidad?')) {
                resetAll();
            }
        });
    }

    // Inicializar
    loadState();
})();
