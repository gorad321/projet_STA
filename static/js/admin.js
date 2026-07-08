// Menu burger admin (mobile)
const adminNavToggle = document.querySelector('.admin-nav-toggle');
const adminNav = document.querySelector('.admin-nav');

if (adminNavToggle && adminNav) {
  adminNavToggle.addEventListener('click', () => {
    const isOpen = adminNav.classList.toggle('open');
    adminNavToggle.setAttribute('aria-expanded', isOpen);
  });

  adminNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      adminNav.classList.remove('open');
      adminNavToggle.setAttribute('aria-expanded', 'false');
    });
  });
}
