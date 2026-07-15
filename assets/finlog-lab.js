(() => {
  'use strict';

  const onReady = (callback) => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', callback, { once: true });
    } else {
      callback();
    }
  };

  onReady(() => {
    const body = document.body;
    if (!body.classList.contains('finlog-lab')) return;

    body.classList.add('lab-is-ready');

    document.querySelectorAll('table').forEach((table) => {
      if (table.parentElement?.classList.contains('table-shell')) return;
      const shell = document.createElement('div');
      shell.className = 'table-shell';
      table.parentNode.insertBefore(shell, table);
      shell.appendChild(table);
    });

    const backTop = document.createElement('button');
    backTop.className = 'lab-backtop';
    backTop.type = 'button';
    backTop.setAttribute('aria-label', '페이지 맨 위로 이동');
    backTop.textContent = '↑';
    document.body.appendChild(backTop);

    const updateBackTop = () => {
      backTop.classList.toggle('is-visible', window.scrollY > 720);
    };
    updateBackTop();
    window.addEventListener('scroll', updateBackTop, { passive: true });
    backTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    const page = body.dataset.finlogPage;
    if (page === 'index' && 'IntersectionObserver' in window) {
      const sections = [...document.querySelectorAll('section[id]')];
      const hashLinks = [...document.querySelectorAll('nav a[href^="#"]')];
      const linkById = new Map(hashLinks.map((link) => [link.hash.slice(1), link]));

      const sectionObserver = new IntersectionObserver((entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        hashLinks.forEach((link) => link.removeAttribute('aria-current'));
        linkById.get(visible.target.id)?.setAttribute('aria-current', 'location');
      }, { rootMargin: '-22% 0px -62%', threshold: [0, .2, .55] });

      sections.forEach((section) => sectionObserver.observe(section));
    }
  });
})();
