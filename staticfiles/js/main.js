// main.js - Scripts principales del sitio
(function() {
    'use strict';

    // Navegación móvil
    function initMobileMenu() {
        const menuToggle = document.getElementById('mobile-menu-btn') || document.getElementById('mobile-menu-toggle');
        const mobileMenu = document.getElementById('mobile-menu');

        if (menuToggle && mobileMenu) {
            menuToggle.addEventListener('click', () => {
                const isOpen = mobileMenu.classList.toggle('hidden');
                menuToggle.setAttribute('aria-expanded', !isOpen);

                // Cambiar ícono
                const icon = menuToggle.querySelector('i');
                if (icon) {
                    if (isOpen) {
                        icon.classList.remove('fa-bars');
                        icon.classList.add('fa-xmark');
                    } else {
                        icon.classList.remove('fa-xmark');
                        icon.classList.add('fa-bars');
                    }
                }
            });

            // Cerrar menú al hacer clic en un enlace (solo en móvil)
            const mobileLinks = mobileMenu.querySelectorAll('a');
            mobileLinks.forEach(link => {
                link.addEventListener('click', () => {
                    mobileMenu.classList.add('hidden');
                    menuToggle.setAttribute('aria-expanded', 'false');

                    const icon = menuToggle.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fa-xmark');
                        icon.classList.add('fa-bars');
                    }
                });
            });
        }
    }

    // Smooth scroll para enlaces internos
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // Animaciones de entrada en scroll
    function initScrollAnimations() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        document.querySelectorAll('[data-animate]').forEach(el => {
            observer.observe(el);
        });
    }

    // Buscador y Filtros del Bento Grid de Carreras
    function initCarrerasSearch() {
        const searchInput = document.getElementById('search-input');
        const searchCount = document.getElementById('search-count');
        const filterButtons = document.querySelectorAll('.filter-btn');
        const clusterPills = document.querySelectorAll('.cluster-pill');
        const carrerasCards = document.querySelectorAll('.tilt-card[data-cluster]');
        const noResults = document.getElementById('no-results');
        const bentoGrid = document.getElementById('bento-grid');

        if (!searchInput || !carrerasCards.length) return;

        let currentFilter = 'ALL';
        let currentSearch = '';

        // Función para filtrar y mostrar carreras
        function filterCarreras() {
            let visibleCount = 0;

            carrerasCards.forEach(card => {
                const cluster = card.getAttribute('data-cluster');
                const name = card.getAttribute('data-name').toLowerCase();
                const key = card.getAttribute('data-key').toLowerCase();

                // Verificar filtro de cluster
                const matchesFilter = currentFilter === 'ALL' || cluster === currentFilter;

                // Verificar búsqueda (busca en nombre y clave)
                const matchesSearch = currentSearch === '' ||
                                     name.includes(currentSearch) ||
                                     key.includes(currentSearch);

                // Mostrar solo si cumple ambas condiciones
                if (matchesFilter && matchesSearch) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Actualizar contador
            if (searchCount) {
                searchCount.textContent = `${visibleCount} resultado${visibleCount !== 1 ? 's' : ''}`;
            }

            // Mostrar/ocultar mensaje "no results"
            if (noResults && bentoGrid) {
                if (visibleCount === 0) {
                    bentoGrid.style.display = 'none';
                    noResults.classList.remove('hidden');
                } else {
                    bentoGrid.style.display = '';
                    noResults.classList.add('hidden');
                }
            }
        }

        // Event listener para el campo de búsqueda
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                currentSearch = searchInput.value.toLowerCase().trim();
                filterCarreras();
            });
        }

        // Event listeners para botones de filtro
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                currentFilter = button.getAttribute('data-filter');

                // Actualizar estado activo de botones
                filterButtons.forEach(btn => {
                    btn.classList.remove('active', 'bg-oasis-600', 'text-white', 'border-oasis-600');
                    btn.classList.add('bg-white', 'text-dark-600', 'border-dark-200');
                    btn.setAttribute('aria-pressed', 'false');
                });

                button.classList.remove('bg-white', 'text-dark-600', 'border-dark-200');
                button.classList.add('active', 'bg-oasis-600', 'text-white', 'border-oasis-600');
                button.setAttribute('aria-pressed', 'true');

                filterCarreras();
            });
        });

        // Event listeners para cluster pills del hero
        clusterPills.forEach(pill => {
            pill.addEventListener('click', () => {
                const cluster = pill.getAttribute('data-cluster');
                currentFilter = cluster;

                // Scroll a la sección de carreras
                const carrerasSection = document.getElementById('carreras');
                if (carrerasSection) {
                    carrerasSection.scrollIntoView({ behavior: 'smooth' });
                }

                // Esperar un poco para que se complete el scroll
                setTimeout(() => {
                    // Actualizar botón de filtro correspondiente
                    filterButtons.forEach(btn => {
                        if (btn.getAttribute('data-filter') === cluster) {
                            btn.click();
                        }
                    });
                }, 500);
            });
        });
    }

    // Filtros genéricos (para otras secciones)
    function initFilters() {
        const filterButtons = document.querySelectorAll('[data-filter]');
        const items = document.querySelectorAll('[data-category]');

        if (!items.length) return;

        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const filter = button.getAttribute('data-filter');

                // Actualizar estado activo de botones
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Filtrar items
                items.forEach(item => {
                    const category = item.getAttribute('data-category');
                    if (filter === 'all' || category === filter) {
                        item.style.display = '';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // Carrusel de proyectos
    function initCarousel() {
        // Carrusel genérico con data-carousel
        const carousels = document.querySelectorAll('[data-carousel]');

        carousels.forEach(carousel => {
            const prevBtn = carousel.querySelector('[data-carousel-prev]');
            const nextBtn = carousel.querySelector('[data-carousel-next]');
            const container = carousel.querySelector('[data-carousel-container]');

            if (!container) return;

            const scrollAmount = 320; // Ancho de tarjeta + gap

            if (prevBtn) {
                prevBtn.addEventListener('click', () => {
                    container.scrollBy({
                        left: -scrollAmount,
                        behavior: 'smooth'
                    });
                });
            }

            if (nextBtn) {
                nextBtn.addEventListener('click', () => {
                    container.scrollBy({
                        left: scrollAmount,
                        behavior: 'smooth'
                    });
                });
            }
        });

        // Carrusel del index (Talento Pro)
        const carouselTrack = document.getElementById('carousel-track');
        const prevBtn = document.getElementById('carousel-prev');
        const nextBtn = document.getElementById('carousel-next');

        if (carouselTrack && prevBtn && nextBtn) {
            const scrollAmount = 344; // 320px (ancho) + 24px (gap)

            prevBtn.addEventListener('click', () => {
                carouselTrack.scrollBy({
                    left: -scrollAmount,
                    behavior: 'smooth'
                });
            });

            nextBtn.addEventListener('click', () => {
                carouselTrack.scrollBy({
                    left: scrollAmount,
                    behavior: 'smooth'
                });
            });

            // Actualizar estado de botones según posición del scroll
            function updateCarouselButtons() {
                const isAtStart = carouselTrack.scrollLeft <= 10;
                const isAtEnd = carouselTrack.scrollLeft >= carouselTrack.scrollWidth - carouselTrack.clientWidth - 10;

                prevBtn.style.opacity = isAtStart ? '0.3' : '1';
                prevBtn.style.pointerEvents = isAtStart ? 'none' : 'auto';

                nextBtn.style.opacity = isAtEnd ? '0.3' : '1';
                nextBtn.style.pointerEvents = isAtEnd ? 'none' : 'auto';
            }

            carouselTrack.addEventListener('scroll', updateCarouselButtons);
            updateCarouselButtons();
        }
    }

    // Tooltips
    function initTooltips() {
        const tooltipTriggers = document.querySelectorAll('[data-tooltip]');

        tooltipTriggers.forEach(trigger => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = trigger.getAttribute('data-tooltip');
            tooltip.style.display = 'none';
            document.body.appendChild(tooltip);

            trigger.addEventListener('mouseenter', (e) => {
                const rect = trigger.getBoundingClientRect();
                tooltip.style.display = 'block';
                tooltip.style.left = `${rect.left + rect.width / 2}px`;
                tooltip.style.top = `${rect.top - 10}px`;
            });

            trigger.addEventListener('mouseleave', () => {
                tooltip.style.display = 'none';
            });
        });
    }

    // Lazy loading de imágenes
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');

        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.getAttribute('data-src');
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    }

    // Formularios con validación
    function initForms() {
        const forms = document.querySelectorAll('form[data-validate]');

        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                let isValid = true;
                const inputs = form.querySelectorAll('input[required], textarea[required]');

                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        isValid = false;
                        input.classList.add('error');
                    } else {
                        input.classList.remove('error');
                    }
                });

                if (!isValid) {
                    e.preventDefault();
                    alert('Por favor complete todos los campos requeridos');
                }
            });
        });
    }

    // Contador animado
    function initCounters() {
        const counters = document.querySelectorAll('[data-count], [data-counter]');

        const counterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-count') || counter.getAttribute('data-counter'));
                    const duration = 2000;
                    const step = target / (duration / 16);
                    let current = 0;

                    const updateCounter = () => {
                        current += step;
                        if (current < target) {
                            counter.textContent = Math.floor(current);
                            requestAnimationFrame(updateCounter);
                        } else {
                            counter.textContent = target;
                        }
                    };

                    updateCounter();
                    counterObserver.unobserve(counter);
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(counter => counterObserver.observe(counter));
    }

    // Theme toggle (modo oscuro/claro)
    function initThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        const savedTheme = localStorage.getItem('theme') || 'light';

        function applyTheme(theme) {
            if (theme === 'dark') {
                document.body.classList.add('dark-mode');
            } else {
                document.body.classList.remove('dark-mode');
            }
            localStorage.setItem('theme', theme);
        }

        applyTheme(savedTheme);

        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                applyTheme(newTheme);
            });
        }
    }

    // Navbar scroll effect
    function initNavbarScroll() {
        const navbar = document.getElementById('navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;

            // Agregar sombra al navbar cuando se hace scroll
            if (currentScroll > 50) {
                navbar.classList.add('bg-white/95', 'backdrop-blur-xl', 'shadow-lg');
            } else {
                navbar.classList.remove('bg-white/95', 'backdrop-blur-xl', 'shadow-lg');
            }
        });
    }

    // Inicializar todo cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', () => {
        initMobileMenu();
        initSmoothScroll();
        initScrollAnimations();
        initCarrerasSearch();  // Buscador y filtros del Bento Grid
        initFilters();
        initCarousel();
        initTooltips();
        initLazyLoading();
        initForms();
        initCounters();
        initThemeToggle();
        initNavbarScroll();
    });

    // Scroll to top button
    const scrollTopBtn = document.getElementById('scroll-to-top');
    if (scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollTopBtn.style.display = 'block';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });

        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
})();
