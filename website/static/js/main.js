document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-menu .nav-link');
    const currentPath = window.location.pathname;

    navLinks.forEach(link => {
        // Removing existing active class
        link.classList.remove('active');

        // If the link href matches the current path, add active class
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});