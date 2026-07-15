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

    if (!body.classList.contains('standalone-chatbot')) {
      const commandEntries = [
        { label: '핀로그 소개', detail: '프로젝트 목표와 핵심 성과', href: 'index.html#about', keys: '홈 소개 성과 목표' },
        { label: '전공 간 협업 모델', detail: '전공자와 비전공자의 교차 검토', href: 'index.html#collab', keys: '협업 팀 번역 검토' },
        { label: 'AI 검증 보조 체계', detail: '자료 탐색·반론·문장 점검 원칙', href: 'index.html#ai', keys: '인공지능 ai 프롬프트 검증' },
        { label: '금융·시사 21개 주제', detail: '분석 주제 전체 목록', href: 'index.html#topics', keys: '이슈 금융 시사 토론' },
        { label: '산출물 아카이브', detail: '보고서·카드뉴스·챗봇·웹', href: 'index.html#works', keys: '포트폴리오 결과물' },
        { label: '기술 구현 증거', detail: '검색·데이터·이미지·자동 검사', href: 'index.html#technology', keys: '기술 개발 코드 품질 접근성' },
        { label: '팀과 개인 기여', detail: '협업 구조와 담당 범위', href: 'index.html#team', keys: '정시윤 역할 기여 팀' },
        { label: '금융 챗봇', detail: '108개 용어·63개 FAQ', href: 'chatbot.html', keys: '검색 질문 지식베이스' },
        { label: '용어 번역과정', detail: '전문 개념과 비전공자 해설 비교', href: 'translator.html', keys: '번역 설명 경제용어' },
        { label: '카드뉴스', detail: '24세트·168장 에디토리얼', href: 'cards.html', keys: '이미지 인스타 아카이브' },
        { label: '활동 보고서', detail: '통합 기록 95쪽', href: 'report.html', keys: 'pdf 보고서 문서' },
        { label: '최종 발표자료', detail: '발표 슬라이드 22장', href: 'deck.html', keys: 'ppt deck 발표' },
        { label: '디지털 금융 포럼', detail: '스테이블코인·CBDC 현장 리포트', href: 'forum.html', keys: '포럼 현장 토큰증권' },
        { label: '금융 분석 노트', detail: '원화 스테이블코인 개인 분석', href: 'insight.html', keys: '칼럼 인사이트 정시윤' },
        { label: '출처·검증 원장', detail: '공식 출처와 기준일 확인', href: 'sources.html', keys: '근거 팩트 출처 날짜 법령' }
      ];

      const command = document.createElement('dialog');
      command.className = 'lab-command';
      command.setAttribute('aria-label', '핀로그 전체 아카이브 검색');
      command.innerHTML = `
        <div class="lab-command__head">
          <span>SEARCH</span>
          <input type="search" aria-label="전체 아카이브 검색어" placeholder="콘텐츠·기술·근거 자료 검색">
          <button class="lab-command__close" type="button" aria-label="검색 닫기">×</button>
        </div>
        <div class="lab-command__meta"><span>FINLOG ARCHIVE</span><span class="lab-command__count"></span></div>
        <div class="lab-command__results" aria-live="polite"></div>`;
      document.body.appendChild(command);

      const commandInput = command.querySelector('input');
      const commandResults = command.querySelector('.lab-command__results');
      const commandCount = command.querySelector('.lab-command__count');

      const renderCommands = () => {
        const query = commandInput.value.trim().toLocaleLowerCase('ko');
        const matches = commandEntries.filter((entry) => {
          const haystack = `${entry.label} ${entry.detail} ${entry.keys}`.toLocaleLowerCase('ko');
          return !query || query.split(/\s+/).every((term) => haystack.includes(term));
        });
        commandCount.textContent = `${matches.length} RESULTS`;
        commandResults.innerHTML = matches.length
          ? matches.map((entry, index) => `
              <a class="lab-command__result" href="${entry.href}">
                <i>${String(index + 1).padStart(2, '0')}</i>
                <span><b>${entry.label}</b><small>${entry.detail}</small></span>
                <span>OPEN ↗</span>
              </a>`).join('')
          : '<div class="lab-command__empty">일치하는 항목이 없습니다.</div>';
      };

      const openCommand = () => {
        renderCommands();
        if (command.open) {
          commandInput.focus();
          return;
        }
        if (typeof command.showModal === 'function') command.showModal();
        else command.setAttribute('open', '');
        requestAnimationFrame(() => commandInput.focus());
      };
      const closeCommand = () => {
        if (typeof command.close === 'function') command.close();
        else command.removeAttribute('open');
      };

      const commandTrigger = document.createElement('button');
      commandTrigger.type = 'button';
      commandTrigger.className = 'lab-command-trigger';
      commandTrigger.setAttribute('aria-label', '전체 아카이브 검색 열기');
      commandTrigger.innerHTML = '<span>⌕</span> SEARCH <kbd>CTRL K</kbd>';
      document.body.appendChild(commandTrigger);

      commandTrigger.addEventListener('click', openCommand);
      document.querySelectorAll('[data-command-palette]').forEach((button) => button.addEventListener('click', openCommand));
      command.querySelector('.lab-command__close').addEventListener('click', closeCommand);
      command.addEventListener('click', (event) => {
        if (event.target === command) closeCommand();
      });
      commandInput.addEventListener('input', renderCommands);
      commandResults.addEventListener('click', (event) => {
        if (event.target.closest('a')) closeCommand();
      });
      commandInput.addEventListener('keydown', (event) => {
        if (event.key === 'ArrowDown') {
          event.preventDefault();
          commandResults.querySelector('a')?.focus();
        }
        if (event.key === 'Enter') {
          const first = commandResults.querySelector('a');
          if (first) {
            event.preventDefault();
            first.click();
          }
        }
      });
      document.addEventListener('keydown', (event) => {
        const editing = /INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName || '');
        if ((event.ctrlKey || event.metaKey) && event.key.toLocaleLowerCase() === 'k') {
          event.preventDefault();
          openCommand();
        } else if (event.key === '/' && !editing && !command.open) {
          event.preventDefault();
          openCommand();
        }
      });
    }

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
