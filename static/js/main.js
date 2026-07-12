// Burger menu mobile
const navToggle    = document.querySelector('.nav-toggle');
const navLinks     = document.querySelector('.nav-links');
const navbarForToggle = document.querySelector('.navbar');

if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
    if (navbarForToggle) navbarForToggle.classList.toggle('navbar-menu-open', isOpen);
  });

  // Fermer le menu si on clique sur un lien
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
      if (navbarForToggle) navbarForToggle.classList.remove('navbar-menu-open');
    });
  });
}
// Navbar transparente sur le hero (uniquement sur les pages qui ont un hero)
const navbar = document.querySelector('.navbar');
const hero = document.querySelector('.hero');

if (navbar && hero) {
  const handleScroll = () => {
    if (window.scrollY > 50) {
      navbar.classList.remove('navbar-transparent');
    } else {
      navbar.classList.add('navbar-transparent');
    }
  };

  // Vérifier au chargement de la page
  handleScroll();
  window.addEventListener('scroll', handleScroll);
}

// Lightbox (agrandissement des photos d'album)
const lightbox = document.querySelector('.lightbox');

if (lightbox) {
  const lightboxImg = lightbox.querySelector('.lightbox-img');
  const closeBtn = lightbox.querySelector('.lightbox-close');

  const openLightbox = (src, alt) => {
    lightboxImg.src = src;
    lightboxImg.alt = alt || '';
    lightbox.classList.add('open');
  };

  const closeLightbox = () => {
    lightbox.classList.remove('open');
    lightboxImg.src = '';
  };

  document.querySelectorAll('.lightbox-trigger').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const img = trigger.querySelector('img');
      openLightbox(trigger.href || img.src, img.alt);
    });
  });

  closeBtn.addEventListener('click', closeLightbox);
  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLightbox();
  });
}

// Galerie — accordéon au clic (desktop uniquement ; sur mobile les cartes sont déjà simples)
const galerieContainer = document.querySelector('.galerie-container');

if (galerieContainer) {
  const galerieCards = galerieContainer.querySelectorAll('.galerie-card');
  const isDesktop = () => window.matchMedia('(min-width: 901px)').matches;

  galerieCards.forEach(card => {
    card.addEventListener('click', (e) => {
      if (!isDesktop()) return;
      if (!card.classList.contains('open')) {
        e.preventDefault();
        galerieCards.forEach(c => c.classList.remove('open'));
        card.classList.add('open');
      }
    });
  });

  if (isDesktop() && galerieCards.length) {
    galerieCards[galerieCards.length - 1].classList.add('open');
  }
}

// Carrousel des dernières actualités (accueil)
const newsCarousel = document.querySelector('.news-carousel');

if (newsCarousel) {
  const slides = newsCarousel.querySelectorAll('.news-slide');
  const dots = newsCarousel.querySelectorAll('.news-dot');
  const prevBtn = newsCarousel.querySelector('.news-arrow-prev');
  const nextBtn = newsCarousel.querySelector('.news-arrow-next');
  let current = 0;
  let autoplay;

  const goTo = (index) => {
    slides[current].classList.remove('active');
    dots[current] && dots[current].classList.remove('active');
    current = (index + slides.length) % slides.length;
    slides[current].classList.add('active');
    dots[current] && dots[current].classList.add('active');
  };

  const startAutoplay = () => {
    autoplay = setInterval(() => goTo(current + 1), 6000);
  };
  const stopAutoplay = () => clearInterval(autoplay);

  if (prevBtn) prevBtn.addEventListener('click', () => { goTo(current - 1); stopAutoplay(); startAutoplay(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { goTo(current + 1); stopAutoplay(); startAutoplay(); });
  dots.forEach((dot, i) => {
    dot.addEventListener('click', () => { goTo(i); stopAutoplay(); startAutoplay(); });
  });

  if (slides.length > 1) {
    newsCarousel.addEventListener('mouseenter', stopAutoplay);
    newsCarousel.addEventListener('mouseleave', startAutoplay);
    startAutoplay();
  }
}
