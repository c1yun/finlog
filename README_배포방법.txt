[핀로그 통합 웹사이트 — GitHub Pages 배포 방법] (Claude 생성)

구성: index.html(포트폴리오·메인) / chatbot.html(금융챗봇 v3, 용어 108개)
      / forum.html(디지털금융포럼 웹 리포트) / translator.html(금융번역기)
모두 자기완결형(외부 CDN 없음)이라 폴더째 올리면 끝.

배포 순서(약 5분):
1. github.com 로그인 → New repository → 이름: finlog (Public)
2. 'uploading an existing file' 클릭 → 이 폴더의 파일 5개(.nojekyll 포함) 드래그 → Commit
3. Settings → Pages → Branch: main / (root) → Save
4. 1~2분 후 https://c1yun-stack.github.io/finlog/ 접속 확인

* 기존 finlog-chatbot 저장소도 Settings → Pages만 켜면 챗봇 단독 주소가 생깁니다.
* 공개(Public) 저장소 = 전 세계 공개입니다. 팀원 실명 등 공개 범위를 올리기 전에 확인하세요.
