# 맥 처음 사용자 필수 앱 가이드

## 필수 기본 앱

| 앱 | 용도 | 추천도 |
|---|---|---|
| Rectangle | 창을 좌우/상하 분할하고 단축키로 정렬 | ★★★★★ |
| Raycast | 앱 실행, 계산기, 클립보드 기록, AI 호출 등 만능 런처 | ★★★★★ |
| AltTab | Windows처럼 Alt+Tab으로 창 전환 | ★★★★★ |
| Homebrew | 개발 프로그램을 명령어 한 줄로 설치 | ★★★★★ |
| iTerm2 | 고급 터미널. Claude Code, Git, Python 사용 시 필수 | ★★★★★ |
| Visual Studio Code | 코드 작성, Claude Code 연동 | ★★★★★ |
| LM Studio | 인터넷 없이 AI 모델 실행 | ★★★★☆ |
| Keka | 압축/압축 해제 | ★★★★★ |
| AppCleaner | 앱 삭제 시 찌꺼기까지 제거 | ★★★★★ |
| Shottr | 캡처, 화살표·모자이크·번호 표시 | ★★★★★ |

---

## 강의용 앱

### 화면 필기 (판서)

| 순위 | 앱 | 특징 |
|---|---|---|
| 1순위 | **ScreenBrush** | 화면 위에 바로 필기, 형광펜/화살표/도형/확대 가능. 유튜브 강사들이 가장 많이 사용. ★★★★★ |
| 2순위 | **Presentify** | 화면 판서, 커서 강조, 클릭 효과, 확대. 강의용으로 매우 좋음. |
| 3순위 | **Epic Pen** | Windows에서 유명, 맥 버전도 있음. 필기감이 좋음. |

### 음성으로 타이핑

#### 맥 자체 기능
- 시스템 설정 → 키보드 → 받아쓰기(Dictation) 켜기
- 한글/영어 지원, 자동 구두점, 정확도 높음

#### AI 기반 음성 입력 추천

| 앱 | 특징 | 추천도 |
|---|---|---|
| **MacWhisper** | Whisper AI 사용, 매우 높은 정확도, 회의 녹음 가능, 로컬 실행 가능 | ★★★★★ |
| **Superwhisper** | 단축키 한 번 → 말하면 바로 타이핑. 개발자들이 많이 사용. ChatGPT와 함께 쓰기 좋음. | ★★★★★ |

### 발표 보조 도구

| 앱 | 용도 |
|---|---|
| **Cursor Pro** | 마우스에 원/후광/클릭 효과를 넣어 강의 시 시선 집중 |
| **KeyCastr** | 단축키(⌘+C, ⌘+Shift+P 등)를 화면에 표시. AI 강의 시 매우 유용 |

---

## 강사 추천 세트

강의를 자주 하는 입장에서 가장 추천하는 조합:

| 역할 | 앱 |
|---|---|
| 창 정리 | Rectangle |
| 앱 실행 | Raycast |
| 터미널 | iTerm2 |
| 필기 | ScreenBrush |
| 화면 캡처 | Shottr |
| 음성 입력 | MacWhisper |
| 커서 강조 | Cursor Pro |
| 단축키 표시 | KeyCastr |
| 로컬 AI | LM Studio |
| 개발 및 AI 코딩 | VS Code + Claude Code |

---

## 설치 방법

Homebrew로 자동 설치 가능한 앱은 제공된 스크립트를 사용:

```bash
chmod +x install_mac_apps.sh && ./install_mac_apps.sh
```

App Store 설치 필요:
- ScreenBrush
- Presentify

웹사이트 직접 다운로드:
- MacWhisper: https://goodsnooze.gumroad.com/l/macwhisper
- Superwhisper: https://superwhisper.com
- Epic Pen: https://epicpen.com
