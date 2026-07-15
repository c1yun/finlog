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
    const path = location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('nav, .pillnav, .slinks').forEach((navigation) => {
      const chatbotLink = navigation.querySelector('a[href="chatbot.html"]');
      if (!chatbotLink || navigation.querySelector('a[href="team.html"]')) return;
      const teamLink = chatbotLink.cloneNode(false);
      teamLink.href = 'team.html';
      teamLink.textContent = '팀 소개';
      teamLink.classList.remove('on', 'active');
      teamLink.removeAttribute('aria-current');
      teamLink.style.removeProperty('background');
      if (navigation.classList.contains('pillnav')) teamLink.style.color = '#dbe6fb';
      chatbotLink.before(teamLink);
    });
    document.querySelectorAll('.pillnav').forEach((navigation) => {
      navigation.setAttribute('role', 'navigation');
      navigation.setAttribute('aria-label', '주요 페이지');
    });
    document.querySelectorAll('a[href]').forEach((link) => {
      const href = link.getAttribute('href').split('#')[0];
      if (href === path || (path === '' && href === 'index.html')) {
        link.setAttribute('aria-current', 'page');
      }
    });

    const target = document.querySelector('main, #main-content')
      || document.querySelector('.app')
      || document.querySelector('.stage')
      || document.querySelector('.pages')
      || document.querySelector('article')
      || document.querySelector('.page')
      || document.querySelector('header.hero, .hero, section');
    if (target) {
      if (!target.id) target.id = 'main-content';
      if (!target.matches('main')) target.setAttribute('role', 'main');
      target.setAttribute('tabindex', '-1');
      const skip = document.createElement('a');
      skip.className = 'finlog-skip-link';
      skip.href = `#${target.id}`;
      skip.textContent = '본문으로 바로가기';
      document.body.prepend(skip);
    }

    const progress = document.createElement('div');
    progress.className = 'finlog-progress';
    progress.setAttribute('aria-hidden', 'true');
    document.body.append(progress);
    let progressQueued = false;
    const updateProgress = () => {
      const max = document.documentElement.scrollHeight - innerHeight;
      const ratio = max > 0 ? Math.max(0, Math.min(1, scrollY / max)) : 0;
      progress.style.transform = `scaleX(${ratio})`;
      progressQueued = false;
    };
    addEventListener('scroll', () => {
      if (!progressQueued) {
        requestAnimationFrame(updateProgress);
        progressQueued = true;
      }
    }, { passive: true });
    updateProgress();

    document.querySelectorAll('img').forEach((image) => {
      if (image.getAttribute('src') === 'data:,') return;
      image.dataset.finlogImage = '';
      if (!image.decoding) image.decoding = 'async';
      const markLoaded = () => image.classList.add('is-loaded');
      if (image.complete && image.naturalWidth) markLoaded();
      else image.addEventListener('load', markLoaded, { once: true });
      image.addEventListener('error', () => {
        image.classList.add('image-unavailable');
        image.setAttribute('aria-label', `${image.alt || '이미지'}를 불러오지 못했습니다`);
      }, { once: true });
    });

    const hasPageLightbox = document.getElementById('lb');
    const selector = hasPageLightbox
      ? '.pages img, [data-lightbox]'
      : '.pages img, .activity-album img, .gal img, [data-lightbox]';
    const images = [...document.querySelectorAll(selector)].filter((image) => {
      const src = image.getAttribute('src') || '';
      return src && src !== 'data:,' && !image.closest('.finlog-image-viewer');
    });
    if (!images.length) return;

    const viewer = document.createElement('dialog');
    viewer.className = 'finlog-image-viewer';
    viewer.setAttribute('aria-label', '이미지 크게 보기');
    viewer.innerHTML = `
      <div class="finlog-image-viewer__stage">
        <button class="finlog-image-viewer__close" type="button" aria-label="닫기">×</button>
        <button class="finlog-image-viewer__prev" type="button" aria-label="이전 이미지">‹</button>
        <img class="finlog-image-viewer__image" alt="">
        <button class="finlog-image-viewer__next" type="button" aria-label="다음 이미지">›</button>
      </div>
      <div class="finlog-image-viewer__bar">
        <div class="finlog-image-viewer__caption"></div>
        <div class="finlog-image-viewer__count" aria-live="polite"></div>
      </div>`;
    document.body.append(viewer);

    const enlarged = viewer.querySelector('.finlog-image-viewer__image');
    const caption = viewer.querySelector('.finlog-image-viewer__caption');
    const count = viewer.querySelector('.finlog-image-viewer__count');
    const previous = viewer.querySelector('.finlog-image-viewer__prev');
    const next = viewer.querySelector('.finlog-image-viewer__next');
    let current = 0;

    const render = () => {
      const image = images[current];
      enlarged.src = image.currentSrc || image.src;
      enlarged.alt = image.alt || '확대 이미지';
      caption.textContent = image.alt || 'FinLog 이미지';
      count.textContent = `${current + 1} / ${images.length}`;
      previous.hidden = next.hidden = images.length < 2;
    };
    const move = (step) => {
      current = (current + step + images.length) % images.length;
      render();
    };
    const open = (index) => {
      current = index;
      render();
      if (typeof viewer.showModal === 'function') viewer.showModal();
      else viewer.setAttribute('open', '');
    };
    const close = () => {
      if (typeof viewer.close === 'function') viewer.close();
      else viewer.removeAttribute('open');
    };

    images.forEach((image, index) => {
      image.dataset.imageViewer = '';
      image.tabIndex = 0;
      image.setAttribute('role', 'button');
      image.setAttribute('aria-label', `${image.alt || '이미지'} 크게 보기`);
      image.addEventListener('click', () => open(index));
      image.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          open(index);
        }
      });
    });
    viewer.querySelector('.finlog-image-viewer__close').addEventListener('click', close);
    previous.addEventListener('click', () => move(-1));
    next.addEventListener('click', () => move(1));
    viewer.addEventListener('click', (event) => {
      if (event.target === viewer) close();
    });
    viewer.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') move(-1);
      if (event.key === 'ArrowRight') move(1);
    });
  });
})();
