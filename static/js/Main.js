// Burger menu mobile
const navToggle = document.querySelector('.nav-toggle');
const navLinks  = document.querySelector('.nav-links');
 
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', isOpen);
  });
 
  // Fermer le menu si on clique sur un lien
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
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