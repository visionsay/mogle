# AI 전자책 출간 워크플로우 — HyperFrames 프로모 영상

책(전자책) 출간을 **강의/홍보 콘텐츠**로 만드는 AI 워크플로우의 레퍼런스 프로젝트입니다.
주제는 **"Claude로 4주 만에 교보문고·예스24에서 팔리는 전자책 출판하기"**이며, 그 과정을
소개하는 **상업적 이용 가능 퀄리티의 모션그래픽 프로모 영상**을 HyperFrames로 직접 렌더링합니다.

> 결과물: `out/promo.mp4` — 1920×1080 · 30fps · 약 36초

![preview](docs/frames/frame-14s.png)

---

## 1. 전체 아이디어 — 책을 강의/영상으로

| 단계 | 도구 | 하는 일 |
| --- | --- | --- |
| ① 기획·대본 | ChatGPT / Claude | 주제·목차·강의 대본(스크립트) 작성 |
| ② 영상 제작 | **Claude/Codex + HyperFrames** | 대본을 HTML 컴포지션으로 만들어 MP4로 렌더링 |
| ③ 출간/배포 | 교보문고·예스24·리디 / 유튜브·릴스 | 전자책 등록 + 홍보 영상 배포 |

이 저장소는 ②번 단계를 실제로 구현한 예시입니다. 사람이 프롬프트로 지시하면 AI 에이전트가
HTML/CSS/JS를 작성하고, 헤드리스 브라우저로 캡처해 영상을 만듭니다.

---

## 2. HyperFrames 란?

[HyperFrames](https://hyperframes.heygen.com/)는 HeyGen이 공개한 **오픈소스(Apache-2.0)
HTML → 영상 렌더링 프레임워크**입니다.

- **작동 방식**: HTML/CSS/JS로 타임라인을 작성 → 헤드리스 Chrome이 프레임 단위로 스크린샷 →
  FFmpeg가 MP4로 인코딩. (10초·30fps = 정확히 300프레임, 결정론적)
- **에이전트 친화적**: Claude Code·Cursor·Gemini CLI 등이 이미 잘 다루는 HTML로 영상을 만듭니다.
- **강점**: 텍스트·데이터·모션그래픽 중심의 설명형/숏폼 영상에 특히 강합니다.
- 참고: [GitHub](https://github.com/heygen-com/hyperframes) ·
  [해설(MindStudio)](https://www.mindstudio.ai/blog/what-is-hyperframes-html-video-renderer-ai-agents)

---

## 3. 빠른 시작

### 사전 요구사항
- **Node.js 22+**
- **FFmpeg** (`apt install ffmpeg` / `brew install ffmpeg`)
- 헤드리스 Chrome — 최초 1회 `npx hyperframes browser ensure`

### 명령어
```bash
npm run dev      # 브라우저 실시간 프리뷰 (long-running)
npm run check    # lint + validate + inspect
npm run render   # MP4 렌더링
```
또는 직접:
```bash
npx hyperframes render --quality high --fps 30 --output out/promo.mp4
```

렌더 옵션: `-q draft|standard|high`, `-f 24|30|60`, `-w 1-8`(워커), `--gpu`, `-o`(출력 경로).

---

## 4. 영상 구성 (스토리보드)

전부 `index.html` 한 파일에 담긴 단일 컴포지션이며, GSAP 타임라인 하나로 제어합니다.

| # | 씬 | 시간 | 내용 |
| --- | --- | --- | --- |
| A | 콜드 오픈 | 0–5s | "지식이 책이 되는 가장 빠른 길." — 키네틱 타이포 인트로 |
| B | 약속 | 5–11s | "아이디어는 누구나, 출간은 소수만" → "이제 단 4주면 충분" |
| C | 4주 프로세스 | 11–25.5s | Week 01~04 카드 + 진행 타임라인 (기획→집필→편집→출간) |
| D | 데이터 증명 | 25.5–30.5s | 카운터 애니메이션: 4주 · 3대 서점 · 100% 내 저작권 |
| E | CTA / 아웃트로 | 30.5–36s | "첫 문장을 시작하세요." + 브랜드 로고 시머 (엔드카드 홀드) |

전체에 필름 그레인 + 비네팅 오버레이를 깔아 편집 디자인 톤을 유지합니다.

**BGM**: 경쾌한 4-on-the-floor 그루브 위에, **텍스트가 등장하는 정확한 순간(히어로·4주 카드·
데이터·CTA)마다 멜로디 액센트가 떨어지도록** 비트를 맞춘 100% 오리지널 트랙입니다.
`tools/make_bgm.py`로 절차적으로 생성(결정론적)하고 -16 LUFS로 라우드니스 정규화했습니다.

---

## 5. 라이선스 — 상업적 이용 가능

이 영상은 **상업적 사용에 안전하도록** 외부 저작물 없이 구성했습니다.

- **Pretendard** 폰트 — SIL Open Font License 1.1 (상업 사용 가능) · `assets/fonts/`에 로컬 내장
- **GSAP 3** — 무료(상업 사용 가능) · `assets/lib/`에 로컬 내장
- **BGM** — `tools/make_bgm.py`로 직접 합성한 100% 오리지널 트랙 (`assets/audio/bgm.mp3`)
- 디자인·카피·모션 — 100% 오리지널, 제3자 음원/이미지 미사용

> 내레이션(TTS)을 추가하려면 HyperFrames의 `/hyperframes-media` 스킬(Kokoro TTS)을 쓰고,
> BGM을 바꾸려면 `tools/make_bgm.py`의 히트포인트/코드 진행을 수정해 재생성하세요.
> 외부 음원을 쓸 경우 반드시 **로열티 프리/상업 라이선스**만 사용하세요.

---

## 6. 프로젝트 구조
```
index.html              # 메인 컴포지션 (루트 타임라인)
assets/fonts/           # Pretendard 가변 폰트 (woff2)
assets/lib/             # GSAP (vendored)
assets/audio/           # 오리지널 BGM (bgm.mp3)
tools/make_bgm.py       # BGM 생성기 (절차적, 결정론적)
out/promo.mp4           # 렌더링 결과물
docs/frames/            # 대표 프레임 미리보기 PNG
meta.json               # 프로젝트 메타데이터
hyperframes.json        # HyperFrames 설정
CLAUDE.md / AGENTS.md   # 에이전트용 제작 가이드
```

---

## 7. 직접 수정하기 (AI 에이전트에게 요청 예시)

> "/hyperframes 를 사용해서 Scene C의 4주 카드 문구를 내 책 목차에 맞게 바꾸고,
> 아웃트로 브랜드명을 'OOO 출판'으로 변경한 뒤 high 품질로 렌더링해줘."

`index.html`의 텍스트만 바꿔도 다른 책/강의용 영상으로 재활용할 수 있습니다.
