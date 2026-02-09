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
        noMotion: false,
        lineSpacing: false,
        letterSpacing: false,
        bigCursor: false,
        focusMode: false,
        saturate: false
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

    // Aplicar espaciado de líneas
    function applyLineSpacing() {
        if (a11yState.lineSpacing) {
            document.body.classList.add('line-spacing');
        } else {
            document.body.classList.remove('line-spacing');
        }
        updateToggleButton('a11y-toggle-line-spacing', a11yState.lineSpacing);
    }

    // Aplicar espaciado de letras
    function applyLetterSpacing() {
        if (a11yState.letterSpacing) {
            document.body.classList.add('letter-spacing');
        } else {
            document.body.classList.remove('letter-spacing');
        }
        updateToggleButton('a11y-toggle-letter-spacing', a11yState.letterSpacing);
    }

    // Aplicar cursor grande
    function applyBigCursor() {
        if (a11yState.bigCursor) {
            document.body.classList.add('big-cursor');
        } else {
            document.body.classList.remove('big-cursor');
        }
        updateToggleButton('a11y-toggle-big-cursor', a11yState.bigCursor);
    }

    // Aplicar modo de enfoque
    function applyFocusMode() {
        if (a11yState.focusMode) {
            document.body.classList.add('focus-mode');
        } else {
            document.body.classList.remove('focus-mode');
        }
        updateToggleButton('a11y-toggle-focus-mode', a11yState.focusMode);
    }

    // Aplicar saturación
    function applySaturate() {
        if (a11yState.saturate) {
            document.body.classList.add('saturate');
        } else {
            document.body.classList.remove('saturate');
        }
        updateToggleButton('a11y-toggle-saturate', a11yState.saturate);
    }

    // Actualizar botón de toggle
    function updateToggleButton(checkboxId, isActive) {
        const checkbox = document.getElementById(checkboxId);
        if (checkbox) {
            checkbox.checked = isActive;
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
        applyLineSpacing();
        applyLetterSpacing();
        applyBigCursor();
        applyFocusMode();
        applySaturate();
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
        a11yState.lineSpacing = false;
        a11yState.letterSpacing = false;
        a11yState.bigCursor = false;
        a11yState.focusMode = false;
        a11yState.saturate = false;

        applyAllSettings();
        saveState();
    }

    // Actualizar badge del FAB
    function updateFabBadge() {
        const activeCount = Object.values(a11yState).filter(v => v === true).length;
        let badge = fab.querySelector('.a11y-active-badge');

        if (activeCount > 0) {
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'a11y-active-badge';
                fab.appendChild(badge);
            }
        } else {
            if (badge) {
                badge.remove();
            }
        }
    }

    // Event Listeners
    fab.addEventListener('click', togglePanel);
    overlay.addEventListener('click', closePanel);

    // Botón de cerrar en el panel
    const closeBtn = document.getElementById('a11y-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closePanel);
    }

    // Cerrar con ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && panel.classList.contains('open')) {
            closePanel();
        }
    });

    // Atajos de teclado
    document.addEventListener('keydown', (e) => {
        // Alt + A: Abrir/cerrar panel
        if (e.altKey && e.key === 'a') {
            e.preventDefault();
            togglePanel();
        }

        // Alt + 1: Toggle alto contraste
        if (e.altKey && e.key === '1') {
            e.preventDefault();
            a11yState.highContrast = !a11yState.highContrast;
            applyHighContrast();
            saveState();
            updateFabBadge();
        }

        // Alt + 2: Toggle escala de grises
        if (e.altKey && e.key === '2') {
            e.preventDefault();
            a11yState.grayscale = !a11yState.grayscale;
            applyGrayscale();
            saveState();
            updateFabBadge();
        }

        // Alt + +: Aumentar tamaño de fuente
        if (e.altKey && e.key === '+') {
            e.preventDefault();
            if (a11yState.fontSize < 150) {
                a11yState.fontSize += 10;
                applyFontSize();
                saveState();
            }
        }

        // Alt + -: Reducir tamaño de fuente
        if (e.altKey && e.key === '-') {
            e.preventDefault();
            if (a11yState.fontSize > 80) {
                a11yState.fontSize -= 10;
                applyFontSize();
                saveState();
            }
        }

        // Alt + 0: Reset todo
        if (e.altKey && e.key === '0') {
            e.preventDefault();
            if (confirm('¿Restablecer todas las opciones de accesibilidad?')) {
                resetAll();
                updateFabBadge();
            }
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
        { id: 'a11y-toggle-no-motion', key: 'noMotion', apply: applyNoMotion },
        { id: 'a11y-toggle-line-spacing', key: 'lineSpacing', apply: applyLineSpacing },
        { id: 'a11y-toggle-letter-spacing', key: 'letterSpacing', apply: applyLetterSpacing },
        { id: 'a11y-toggle-big-cursor', key: 'bigCursor', apply: applyBigCursor },
        { id: 'a11y-toggle-focus-mode', key: 'focusMode', apply: applyFocusMode },
        { id: 'a11y-toggle-saturate', key: 'saturate', apply: applySaturate }
    ];

    toggles.forEach(toggle => {
        const checkbox = document.getElementById(toggle.id);
        if (checkbox) {
            checkbox.addEventListener('change', () => {
                a11yState[toggle.key] = checkbox.checked;
                toggle.apply();
                saveState();
                updateFabBadge();
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
    updateFabBadge();

    // Mostrar tooltip de atajos al cargar (solo primera vez)
    if (!localStorage.getItem('a11y-shortcuts-shown')) {
        setTimeout(() => {
            const tooltip = document.createElement('div');
            tooltip.className = 'a11y-shortcuts-tooltip';
            tooltip.innerHTML = `
                <div style="position: fixed; bottom: 100px; right: 24px; background: #047857; color: white; padding: 16px 20px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); z-index: 999; max-width: 280px; animation: slideInRight 0.5s;">
                    <div style="font-weight: 700; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                        <i class="fa-solid fa-keyboard"></i>
                        Atajos de Teclado
                    </div>
                    <div style="font-size: 0.875rem; opacity: 0.95; line-height: 1.6;">
                        <div><kbd style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; font-family: monospace;">Alt + A</kbd> Abrir/Cerrar</div>
                        <div><kbd style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; font-family: monospace;">Alt + +/-</kbd> Tamaño</div>
                        <div><kbd style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 4px; font-family: monospace;">Alt + 0</kbd> Resetear</div>
                    </div>
                    <button onclick="this.parentElement.remove()" style="position: absolute; top: 8px; right: 8px; background: none; border: none; color: white; cursor: pointer; opacity: 0.7; font-size: 1.25rem;">×</button>
                </div>
            `;
            document.body.appendChild(tooltip);

            setTimeout(() => {
                tooltip.remove();
            }, 8000);

            localStorage.setItem('a11y-shortcuts-shown', 'true');
        }, 2000);
    }
})();
