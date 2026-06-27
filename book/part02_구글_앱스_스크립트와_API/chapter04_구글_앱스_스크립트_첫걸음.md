# Chapter 04: 구글 앱스 스크립트 첫걸음

## 4.1 구글 앱스 스크립트의 매력에 퐁당

유튜브 채널을 운영하면서 반복 작업에 지친 적이 있으신가요? 경쟁 채널의 영상 데이터를 매일 수동으로 확인하고, 댓글을 하나하나 읽으며, 업로드 스케줄을 스프레드시트에 손으로 정리하던 시간을 떠올려 보세요. 구글 앱스 스크립트(Google Apps Script)는 이 모든 작업을 자동화할 수 있는 가장 진입장벽이 낮은 프로그래밍 환경입니다.

### 앱스 스크립트가 유튜브 자동화에 완벽한 이유

**첫째, 서버가 필요 없습니다.** 일반적인 프로그래밍에서는 코드를 실행할 서버를 준비해야 합니다. AWS, GCP 같은 클라우드 서비스를 가입하고, 서버를 설정하고, 비용을 지불해야 하죠. 앱스 스크립트는 구글 계정만 있으면 바로 코드를 작성하고 실행할 수 있습니다. 구글의 서버에서 여러분의 코드가 무료로 돌아갑니다.

**둘째, V8 런타임으로 최신 자바스크립트를 지원합니다.** 2020년부터 앱스 스크립트는 V8 런타임을 채택하여 ES6+ 문법을 완벽하게 지원합니다. `const`, `let`, 화살표 함수(`=>`), 템플릿 리터럴(`` ` ``), 구조 분해 할당, `async/await` 등 현대 자바스크립트의 편리한 기능을 모두 사용할 수 있습니다.

**셋째, 구글 서비스와 네이티브로 연결됩니다.** 스프레드시트, 드라이브, Gmail, 캘린더, 유튜브 등 구글의 모든 서비스에 별도의 인증 과정 없이 바로 접근할 수 있습니다. 유튜브 API를 호출하기 위해 복잡한 OAuth 설정을 하지 않아도 됩니다. 앱스 스크립트가 알아서 처리해 줍니다.

**넷째, 트리거(Trigger)로 자동 실행이 가능합니다.** "매일 오전 9시에 경쟁 채널의 신규 영상을 확인해서 스프레드시트에 기록하라"는 식의 자동 실행 스케줄을 설정할 수 있습니다. 시간 기반 트리거, 스프레드시트 편집 트리거, 폼 제출 트리거 등 다양한 자동 실행 조건을 제공합니다.

**다섯째, 웹 앱으로 배포할 수 있습니다.** 작성한 코드를 웹 앱 형태로 배포하면 외부에서 HTTP 요청으로 호출할 수 있습니다. 다른 서비스와의 연동이나 간단한 대시보드 제작도 가능합니다.

### 앱스 스크립트의 실행 제한

무료로 제공되는 만큼 실행에 제한이 있습니다. 2026년 현재 주요 제한 사항은 다음과 같습니다.

| 항목 | 제한 |
|------|------|
| 스크립트 실행 시간 | 6분 (일반 계정) / 30분 (Google Workspace) |
| 일일 트리거 실행 횟수 | 90분 총 실행시간 |
| UrlFetch 호출 | 일 20,000회 |
| 스프레드시트 읽기/쓰기 | 초당 100회 |
| 스크립트 프로젝트 크기 | 프로젝트 전체 소스 코드 합계 5MB |

이 제한은 유튜브 자동화 작업에는 충분한 수준입니다. 하루 수천 개의 영상 데이터를 수집하고 분석하는 데 전혀 문제가 없습니다.

---

## 4.2 스프레드시트에서 앱스 스크립트 열기

### 앱스 스크립트 편집기 접근하기

구글 스프레드시트를 열고 상단 메뉴에서 **확장 프로그램(Extensions) > Apps Script**를 클릭하면 앱스 스크립트 편집기가 새 탭에서 열립니다. 이것이 가장 기본적인 접근 방법이며, 이렇게 열린 스크립트를 **컨테이너 바운드 스크립트(Container-bound Script)**라고 합니다.

### 독립형 스크립트 vs 컨테이너 바운드 스크립트

앱스 스크립트에는 두 가지 유형의 프로젝트가 있습니다.

**컨테이너 바운드 스크립트(Container-bound Script)**는 특정 스프레드시트, 문서, 슬라이드, 또는 폼에 "붙어 있는" 스크립트입니다.
- 스프레드시트의 **확장 프로그램 > Apps Script**에서 생성합니다.
- 해당 스프레드시트에만 직접 접근할 수 있으며, `SpreadsheetApp.getActiveSpreadsheet()`로 현재 스프레드시트를 바로 가져올 수 있습니다.
- 커스텀 메뉴, 사이드바, 다이얼로그 등 UI 요소를 추가할 수 있습니다.
- 이 책에서 주로 사용하는 방식입니다.

**독립형 스크립트(Standalone Script)**는 어떤 파일에도 연결되지 않은 독립적인 스크립트입니다.
- [script.google.com](https://script.google.com)에서 직접 생성합니다.
- 구글 드라이브의 "새로 만들기 > 더보기 > Google Apps Script"로도 생성할 수 있습니다.
- 여러 스프레드시트나 서비스를 동시에 다루는 범용 자동화에 적합합니다.
- 스프레드시트의 `getActiveSpreadsheet()` 대신 `SpreadsheetApp.openById()`나 `SpreadsheetApp.openByUrl()`을 사용해야 합니다.

> **이 책에서는 컨테이너 바운드 스크립트를 사용합니다.** 유튜브 데이터를 스프레드시트에 수집하고 관리하는 것이 핵심이므로, 스프레드시트에 직접 연결된 스크립트가 가장 편리합니다.

### 프로젝트 구조 이해하기

앱스 스크립트 프로젝트는 다음과 같은 구조를 갖습니다.

```
프로젝트명/
├── Code.gs          ← 메인 스크립트 파일
├── Utils.gs         ← 추가 스크립트 파일 (자유롭게 추가 가능)
├── Config.gs        ← 설정 관련 스크립트
├── appsscript.json  ← 매니페스트 파일 (프로젝트 설정)
└── HTML 파일들       ← 사이드바/다이얼로그용 HTML
```

- `.gs` 파일: 자바스크립트 코드를 담는 스크립트 파일입니다. 확장자가 `.gs`이지만 내용은 표준 자바스크립트입니다. 파일을 여러 개로 나누어 관리할 수 있으며, 실행 시 모든 `.gs` 파일이 하나로 합쳐져 실행됩니다.
- `appsscript.json`: 프로젝트의 매니페스트 파일로, 사용할 API 서비스, OAuth 스코프, 런타임 버전 등을 정의합니다. 편집기에서 **프로젝트 설정 > "appsscript.json" 매니페스트 파일을 편집기에 표시** 체크박스를 활성화하면 직접 편집할 수 있습니다.

---

## 4.3 앱스 스크립트 편집기 사용법

### 편집기 주요 기능

**자동완성(Autocomplete)**: 코드를 입력할 때 `Ctrl + Space`를 누르면 사용 가능한 메서드와 속성을 자동으로 제안해 줍니다. `SpreadsheetApp.` 까지 입력하고 잠시 기다리면 사용 가능한 모든 메서드가 목록으로 표시됩니다.

**실행 로그(Execution Log)**: 코드를 실행하면 하단에 실행 로그 패널이 표시됩니다. `console.log()`로 출력한 내용과 에러 메시지를 확인할 수 있습니다. 메뉴의 **실행 기록(Execution log)**에서 과거 실행 기록도 조회할 수 있습니다.

**디버거(Debugger)**: 코드의 특정 줄 왼쪽을 클릭하면 빨간 점(브레이크포인트)이 표시됩니다. **디버그** 버튼을 클릭하면 해당 줄에서 실행이 멈추고, 그 시점의 변수 값을 확인할 수 있습니다. 한 줄씩 실행하며 코드의 동작을 추적할 수 있어 버그를 찾는 데 매우 유용합니다.

**버전 기록(Version History)**: 상단 시계 아이콘을 클릭하면 이전 버전의 코드를 확인하고 복원할 수 있습니다. 코드를 잘못 수정했을 때 이전 상태로 돌아갈 수 있는 안전장치입니다.

### console.log vs Logger.log

앱스 스크립트에는 로그를 출력하는 두 가지 방법이 있습니다.

```javascript
// 2026년 기준 권장 방법: console.log (V8 런타임)
function modernLogging() {
  console.log('일반 로그');
  console.info('정보 로그');
  console.warn('경고 로그');
  console.error('에러 로그');
  
  // 객체도 깔끔하게 출력
  const videoData = { title: '앱스 스크립트 강의', views: 15000 };
  console.log('영상 데이터:', videoData);
  console.log(`조회수: ${videoData.views}회`);  // 템플릿 리터럴 사용
}

// 레거시 방법: Logger.log (Rhino 런타임 시절)
function legacyLogging() {
  Logger.log('이전 방식의 로그');
  Logger.log(Logger.getLog());  // 누적된 로그 확인
}
```

> **2026년 현재 `console.log`를 사용하세요.** V8 런타임에서는 `console.log`가 표준이며, 로그 수준(info, warn, error) 구분이 가능하고, 객체를 구조화된 형태로 출력합니다. `Logger.log`는 이전 Rhino 런타임의 유산으로 아직 동작하지만, 새로 작성하는 코드에서는 사용할 이유가 없습니다.

### clasp CLI로 로컬 개발하기

앱스 스크립트 편집기가 불편하다면 로컬 에디터(VS Code 등)에서 개발할 수 있습니다. `clasp`(Command Line Apps Script Projects)는 구글이 공식 제공하는 CLI 도구입니다.

```bash
# clasp 설치
npm install -g @google/clasp

# 구글 계정 로그인
clasp login

# 기존 앱스 스크립트 프로젝트를 로컬로 가져오기
clasp clone <스크립트_ID>

# 로컬에서 수정 후 앱스 스크립트로 업로드
clasp push

# 앱스 스크립트에서 로컬로 가져오기
clasp pull

# 특정 함수 실행
clasp run myFunction
```

`clasp`를 사용하면 VS Code의 강력한 편집 기능, Git을 통한 버전 관리, 그리고 TypeScript 지원까지 활용할 수 있습니다. 다만 이 책에서는 독자의 접근성을 위해 웹 편집기를 기준으로 설명합니다.

### 편집기 실전 팁

1. **`Ctrl + S`를 자주 누르세요.** 앱스 스크립트 편집기는 자동 저장이 되지만, 저장 후에만 실행이 가능합니다.
2. **함수 이름을 클릭하고 실행 버튼을 누르세요.** 상단의 함수 선택 드롭다운에서 실행할 함수를 선택할 수 있습니다. 테스트용 함수를 `test_`로 시작하게 이름 지으면 관리가 편합니다.
3. **여러 파일로 나누세요.** 코드가 길어지면 기능별로 `.gs` 파일을 나누어 관리하세요. 예를 들어 `YouTube.gs`, `Spreadsheet.gs`, `Utils.gs` 등으로 분리하면 유지보수가 쉬워집니다.

---

## 4.4 바이브 코딩으로 에러 수정하는 방법 3가지

프로그래밍에서 에러는 피할 수 없습니다. 특히 앱스 스크립트를 처음 접하는 분이라면 더욱 그렇죠. 하지만 2026년 현재, AI를 활용하면 대부분의 에러를 빠르게 해결할 수 있습니다. 여기서 소개하는 세 가지 방법은 "바이브 코딩(Vibe Coding)"의 핵심 전략입니다. 코드의 세부 문법을 몰라도, 에러의 맥락을 AI에게 정확하게 전달하면 해결책을 얻을 수 있습니다.

### 방법 1: 에러 메시지 전체를 AI에게 붙여넣기

가장 기본적이면서도 가장 효과적인 방법입니다. 에러가 발생하면 에러 메시지를 무시하지 말고, 전체를 복사하여 AI에게 전달하세요. 이때 중요한 것은 **코드, 에러 메시지, 코드의 목적** 세 가지를 함께 전달하는 것입니다.

**프롬프트 템플릿:**

```
다음 Google Apps Script 코드에서 에러가 발생했습니다.

코드:
function getVideoData() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=VIDEO_ID&key=" + API_KEY;
  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response);
  sheet.getRange(1, 1).setValue(data.items.snippet.title);
}

에러 메시지:
TypeError: Cannot read properties of undefined (reading 'snippet')
at getVideoData(Code:6:47)

이 코드의 목적: 유튜브 API로 영상 제목을 가져와서 스프레드시트 A1 셀에 입력하는 함수입니다.

에러를 수정해주세요.
```

AI는 이 정보를 바탕으로 `data.items`가 배열이므로 `data.items[0].snippet.title`로 수정해야 한다는 것을 알려줄 것입니다. 추가로 `items`가 빈 배열일 경우의 방어 코드까지 제안해 줍니다.

> **핵심 원칙:** 에러 메시지를 절대 요약하지 마세요. "에러가 나요"라고만 하면 AI도 도움을 줄 수 없습니다. 에러 메시지 전체를 그대로 복사해서 붙여넣으세요.

### 방법 2: 실행 로그 분석 요청하기

에러 메시지만으로 해결이 안 되는 경우, 실행 과정의 로그를 함께 공유하면 AI가 훨씬 정확한 답을 줄 수 있습니다. 이를 위해 코드에 로그를 추가하는 방법을 알아보겠습니다.

**로그를 추가한 디버깅 코드 예시:**

```javascript
function getVideoDataWithLogging() {
  try {
    console.log('=== 함수 실행 시작 ===');
    
    const sheet = SpreadsheetApp.getActiveSheet();
    console.log('시트 이름:', sheet.getName());
    
    const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
    console.log('API 키 존재 여부:', apiKey ? '있음' : '없음');
    console.log('API 키 앞 8자:', apiKey ? apiKey.substring(0, 8) + '...' : 'N/A');
    
    const videoId = 'dQw4w9WgXcQ';
    const url = `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=${videoId}&key=${apiKey}`;
    console.log('요청 URL:', url.replace(apiKey, 'API_KEY_HIDDEN'));
    
    const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    const responseCode = response.getResponseCode();
    console.log('응답 코드:', responseCode);
    
    const responseText = response.getContentText();
    console.log('응답 본문 (앞 500자):', responseText.substring(0, 500));
    
    const data = JSON.parse(responseText);
    console.log('items 개수:', data.items ? data.items.length : '없음');
    
    if (data.items && data.items.length > 0) {
      const title = data.items[0].snippet.title;
      console.log('영상 제목:', title);
      sheet.getRange(1, 1).setValue(title);
      console.log('=== 함수 실행 완료 ===');
    } else {
      console.warn('검색 결과가 없습니다. videoId를 확인하세요:', videoId);
    }
    
  } catch (error) {
    console.error('에러 발생:', error.message);
    console.error('에러 스택:', error.stack);
  }
}
```

이 코드를 실행한 후 **실행 로그** 패널에 표시된 전체 로그를 복사하여 AI에게 전달합니다.

**프롬프트 예시:**

```
다음 Google Apps Script의 실행 로그를 분석해 주세요.

코드의 목적: 유튜브 영상 정보를 가져와서 스프레드시트에 기록

실행 로그:
=== 함수 실행 시작 ===
시트 이름: Sheet1
API 키 존재 여부: 있음
API 키 앞 8자: AIzaSyB2...
요청 URL: https://www.googleapis.com/.../videos?part=snippet,statistics&id=dQw4w9WgXcQ&key=API_KEY_HIDDEN
응답 코드: 403
응답 본문 (앞 500자): {"error":{"code":403,"message":"YouTube Data API v3 has not been used in project 123456 before or it is disabled...","status":"UNAVAILABLE"...}}
에러 발생: Cannot read properties of undefined (reading 'length')

어떤 문제이며, 어떻게 해결하나요?
```

로그를 보면 API 응답 코드가 403이고, API가 활성화되지 않았다는 메시지가 있음을 알 수 있습니다. AI는 구글 클라우드 콘솔에서 YouTube Data API v3를 활성화해야 한다고 안내해 줄 것입니다.

### 방법 3: 단계별 디버깅 요청하기

복잡한 코드에서 에러가 발생하면, AI에게 코드를 작은 단위로 쪼개어 각 단계를 검증하는 테스트 함수를 만들어 달라고 요청하세요.

**프롬프트 예시:**

```
다음 Google Apps Script 함수가 제대로 동작하지 않습니다. 
이 함수를 단계별로 분리하여 각 단계를 독립적으로 테스트할 수 있는 
작은 함수들로 나누어 주세요.

[전체 코드 붙여넣기]
```

AI는 다음과 같이 코드를 분리해 줄 것입니다.

```javascript
// 1단계: 스프레드시트 연결 테스트
function test_step1_spreadsheet() {
  const sheet = SpreadsheetApp.getActiveSheet();
  console.log('시트 연결 성공:', sheet.getName());
  console.log('마지막 행:', sheet.getLastRow());
  console.log('마지막 열:', sheet.getLastColumn());
}

// 2단계: API 키 확인
function test_step2_apiKey() {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  console.log('API 키:', apiKey ? '설정됨 (' + apiKey.length + '자)' : '설정되지 않음');
}

// 3단계: API 호출 테스트
function test_step3_apiCall() {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  const url = `https://www.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key=${apiKey}`;
  
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  console.log('응답 코드:', response.getResponseCode());
  console.log('응답 내용:', response.getContentText().substring(0, 300));
}

// 4단계: JSON 파싱 테스트
function test_step4_parsing() {
  const sampleJson = '{"items":[{"snippet":{"title":"테스트 영상"}}]}';
  const data = JSON.parse(sampleJson);
  console.log('파싱 결과:', data.items[0].snippet.title);
}
```

각 함수를 하나씩 실행하면서 어느 단계에서 문제가 발생하는지 확인할 수 있습니다. 문제가 발견된 단계만 AI에게 다시 질문하면 됩니다.

---

## 4.5 실전 코드 예제

이제 실제로 동작하는 코드를 작성해 보겠습니다. 아래의 코드들은 모두 앱스 스크립트 편집기에 붙여넣기 하여 바로 실행할 수 있습니다.

### 예제 1: Hello World - 커스텀 메뉴와 사이드바

스프레드시트에 나만의 메뉴를 추가하고, 사이드바를 표시하는 기본 예제입니다.

```javascript
/**
 * 스프레드시트가 열릴 때 자동으로 실행되는 함수
 * 커스텀 메뉴를 추가합니다.
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🎬 유튜브 도구')
    .addItem('인사하기', 'showGreeting')
    .addItem('사이드바 열기', 'showSidebar')
    .addSeparator()
    .addItem('현재 시간 입력', 'insertCurrentTime')
    .addToUi();
}

/**
 * 알림 대화상자를 표시합니다.
 */
function showGreeting() {
  const ui = SpreadsheetApp.getUi();
  ui.alert('환영합니다!', '유튜브 자동화의 세계에 오신 것을 환영합니다! 🎉', ui.ButtonSet.OK);
}

/**
 * 사이드바를 표시합니다.
 */
function showSidebar() {
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        body { font-family: Arial, sans-serif; padding: 16px; }
        h2 { color: #1a73e8; }
        .info-box { 
          background: #e8f0fe; 
          border-radius: 8px; 
          padding: 12px; 
          margin: 8px 0; 
        }
        button {
          background: #1a73e8;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 12px;
        }
        button:hover { background: #1557b0; }
      </style>
    </head>
    <body>
      <h2>유튜브 도구</h2>
      <div class="info-box">
        <p><strong>현재 시트:</strong> <span id="sheetName">로딩 중...</span></p>
        <p><strong>데이터 행 수:</strong> <span id="rowCount">로딩 중...</span></p>
      </div>
      <button onclick="google.script.run.insertCurrentTime()">현재 시간 입력</button>
      <button onclick="google.script.host.close()">닫기</button>
      <script>
        google.script.run.withSuccessHandler(function(info) {
          document.getElementById('sheetName').textContent = info.sheetName;
          document.getElementById('rowCount').textContent = info.rowCount;
        }).getSheetInfo();
      </script>
    </body>
    </html>
  `;
  
  const html = HtmlService.createHtmlOutput(htmlContent)
    .setTitle('유튜브 도구')
    .setWidth(300);
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * 사이드바에 표시할 시트 정보를 반환합니다.
 */
function getSheetInfo() {
  const sheet = SpreadsheetApp.getActiveSheet();
  return {
    sheetName: sheet.getName(),
    rowCount: sheet.getLastRow()
  };
}

/**
 * 현재 선택된 셀에 현재 시간을 입력합니다.
 */
function insertCurrentTime() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const cell = sheet.getActiveCell();
  cell.setValue(new Date());
  cell.setNumberFormat('yyyy-MM-dd HH:mm:ss');
}
```

> **실행 방법:** 코드를 붙여넣고 저장한 후, 스프레드시트를 새로고침하세요. 상단에 "유튜브 도구" 메뉴가 나타납니다. 처음 실행할 때 구글 계정 권한 승인이 필요합니다.

### 예제 2: 스프레드시트 데이터 읽기/쓰기

스프레드시트의 데이터를 읽고 쓰는 핵심 패턴입니다. 유튜브 데이터를 스프레드시트에 저장할 때 이 패턴을 기반으로 합니다.

```javascript
/**
 * 스프레드시트 데이터 읽기 - 다양한 방법
 */
function readSpreadsheetData() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  
  // 1. 단일 셀 읽기
  const cellValue = sheet.getRange('A1').getValue();
  console.log('A1 셀 값:', cellValue);
  
  // 2. 범위로 읽기 (2D 배열로 반환)
  const rangeValues = sheet.getRange('A1:C3').getValues();
  console.log('A1:C3 데이터:', rangeValues);
  // 결과: [['제목', '조회수', '좋아요'], ['영상1', 1000, 50], ['영상2', 2000, 100]]
  
  // 3. 데이터가 있는 전체 범위 읽기
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  if (lastRow > 0 && lastCol > 0) {
    const allData = sheet.getRange(1, 1, lastRow, lastCol).getValues();
    console.log(`전체 데이터: ${lastRow}행 x ${lastCol}열`);
    
    // 헤더와 데이터 분리
    const headers = allData[0];
    const dataRows = allData.slice(1);
    console.log('헤더:', headers);
    console.log('데이터 행 수:', dataRows.length);
  }
}

/**
 * 스프레드시트 데이터 쓰기 - 다양한 방법
 */
function writeSpreadsheetData() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  
  // 1. 단일 셀 쓰기
  sheet.getRange('A1').setValue('유튜브 영상 데이터');
  
  // 2. 헤더 행 쓰기 (한 번에 여러 셀)
  const headers = [['영상 제목', '채널명', '조회수', '좋아요', '수집일']];
  sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
  
  // 3. 여러 행 한 번에 쓰기 (성능 최적화의 핵심!)
  const videoData = [
    ['앱스 스크립트 입문', '코딩채널', 15000, 320, new Date()],
    ['유튜브 API 활용', '개발자TV', 8500, 210, new Date()],
    ['자동화 실전편', '테크톡', 22000, 580, new Date()]
  ];
  
  // 데이터를 마지막 행 다음에 추가
  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, videoData.length, videoData[0].length).setValues(videoData);
  
  console.log(`${videoData.length}개의 영상 데이터를 ${startRow}행부터 기록했습니다.`);
  
  // 4. 서식 적용
  // 헤더 행 스타일링
  const headerRange = sheet.getRange(1, 1, 1, headers[0].length);
  headerRange.setFontWeight('bold');
  headerRange.setBackground('#4285f4');
  headerRange.setFontColor('#ffffff');
  
  // 열 너비 자동 조정
  for (let col = 1; col <= headers[0].length; col++) {
    sheet.autoResizeColumn(col);
  }
}

/**
 * 기존 데이터 업데이트 - 특정 조건으로 찾아서 수정
 */
function updateExistingData() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  const data = sheet.getDataRange().getValues();
  
  // 헤더에서 '영상 제목' 열 인덱스 찾기
  const headers = data[0];
  const titleCol = headers.indexOf('영상 제목');
  const viewsCol = headers.indexOf('조회수');
  
  if (titleCol === -1 || viewsCol === -1) {
    console.error('필요한 열을 찾을 수 없습니다.');
    return;
  }
  
  // '앱스 스크립트 입문' 영상의 조회수 업데이트
  for (let i = 1; i < data.length; i++) {
    if (data[i][titleCol] === '앱스 스크립트 입문') {
      sheet.getRange(i + 1, viewsCol + 1).setValue(16500);  // 행/열은 1부터 시작
      console.log(`${i + 1}행의 조회수를 업데이트했습니다.`);
      break;
    }
  }
}
```

> **성능 팁:** `getValue()`/`setValue()`를 반복문 안에서 셀 하나씩 호출하면 매우 느립니다. 반드시 `getValues()`/`setValues()`로 범위 단위로 읽고 쓰세요. 100행의 데이터를 쓸 때 셀 단위로 쓰면 수십 초가 걸리지만, 범위 단위로 한 번에 쓰면 1초 이내에 끝납니다.

### 예제 3: UrlFetchApp으로 HTTP 요청 보내기

외부 API를 호출하는 핵심 도구인 `UrlFetchApp`의 사용법입니다.

```javascript
/**
 * GET 요청 - 유튜브 API 호출 예시
 */
function fetchYouTubeData() {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  const videoId = 'dQw4w9WgXcQ';
  
  const url = `https://www.googleapis.com/youtube/v3/videos`
    + `?part=snippet,statistics`
    + `&id=${videoId}`
    + `&key=${apiKey}`;
  
  const options = {
    method: 'get',
    muteHttpExceptions: true,  // HTTP 에러 시에도 예외를 발생시키지 않음
    headers: {
      'Accept': 'application/json'
    }
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const responseCode = response.getResponseCode();
  
  if (responseCode === 200) {
    const data = JSON.parse(response.getContentText());
    console.log('영상 제목:', data.items[0].snippet.title);
    console.log('조회수:', data.items[0].statistics.viewCount);
    return data;
  } else {
    console.error(`API 에러 (${responseCode}):`, response.getContentText());
    return null;
  }
}

/**
 * POST 요청 - 외부 서비스에 데이터 전송 예시
 */
function sendDataToWebhook() {
  const webhookUrl = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL';
  
  const payload = {
    text: '유튜브 데이터 수집이 완료되었습니다!',
    blocks: [
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*유튜브 일일 리포트*\n수집된 영상: 50건\n총 조회수: 1,250,000회'
        }
      }
    ]
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(webhookUrl, options);
  console.log('전송 결과:', response.getResponseCode());
}

/**
 * 여러 URL을 한꺼번에 호출하기 (fetchAll - 병렬 처리)
 */
function fetchMultipleUrls() {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  const videoIds = ['dQw4w9WgXcQ', 'jNQXAC9IVRw', '9bZkp7q19f0'];
  
  // 각 영상에 대한 요청 객체 배열 생성
  const requests = videoIds.map(id => ({
    url: `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=${id}&key=${apiKey}`,
    method: 'get',
    muteHttpExceptions: true
  }));
  
  // 모든 요청을 병렬로 실행 (순차 실행보다 훨씬 빠름!)
  const responses = UrlFetchApp.fetchAll(requests);
  
  responses.forEach((response, index) => {
    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());
      if (data.items && data.items.length > 0) {
        console.log(`영상 ${index + 1}: ${data.items[0].snippet.title}`);
      }
    }
  });
}
```

> **중요:** `muteHttpExceptions: true` 옵션을 반드시 사용하세요. 이 옵션이 없으면 HTTP 4xx, 5xx 응답 시 스크립트가 즉시 중단됩니다. 이 옵션을 켜면 에러 응답도 정상적으로 받아서 처리할 수 있습니다.

### 예제 4: 에러 처리 패턴

안정적인 자동화를 위한 에러 처리 패턴입니다.

```javascript
/**
 * 체계적인 에러 처리 패턴
 * 유튜브 데이터를 안전하게 수집하는 함수
 */
function safeYouTubeDataCollection() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('수집결과');
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('실행로그');
  
  try {
    // 1. 사전 조건 확인
    if (!sheet) {
      throw new Error('수집결과 시트가 없습니다. "수집결과" 이름의 시트를 만들어주세요.');
    }
    
    const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
    if (!apiKey) {
      throw new Error('API 키가 설정되지 않았습니다. setApiKey() 함수를 먼저 실행하세요.');
    }
    
    // 2. API 호출
    const videoId = 'dQw4w9WgXcQ';
    const url = `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=${videoId}&key=${apiKey}`;
    
    let response;
    try {
      response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    } catch (fetchError) {
      throw new Error(`네트워크 에러: ${fetchError.message}`);
    }
    
    // 3. 응답 코드 확인
    const responseCode = response.getResponseCode();
    if (responseCode === 403) {
      const errorBody = JSON.parse(response.getContentText());
      const reason = errorBody.error?.errors?.[0]?.reason || '알 수 없음';
      
      if (reason === 'quotaExceeded') {
        throw new Error('일일 API 할당량을 초과했습니다. 내일 다시 시도하세요.');
      } else if (reason === 'forbidden') {
        throw new Error('API 키에 YouTube Data API 권한이 없습니다.');
      }
      throw new Error(`API 접근 거부 (${reason}): ${response.getContentText()}`);
    }
    
    if (responseCode !== 200) {
      throw new Error(`API 에러 (HTTP ${responseCode}): ${response.getContentText()}`);
    }
    
    // 4. 데이터 파싱
    const data = JSON.parse(response.getContentText());
    
    if (!data.items || data.items.length === 0) {
      console.warn(`영상을 찾을 수 없습니다: ${videoId}`);
      logExecution(logSheet, '경고', `영상 없음: ${videoId}`);
      return;
    }
    
    // 5. 스프레드시트에 기록
    const video = data.items[0];
    const rowData = [
      video.id,
      video.snippet.title,
      video.snippet.channelTitle,
      parseInt(video.statistics.viewCount || '0'),
      parseInt(video.statistics.likeCount || '0'),
      parseInt(video.statistics.commentCount || '0'),
      new Date()
    ];
    
    sheet.appendRow(rowData);
    logExecution(logSheet, '성공', `영상 수집 완료: ${video.snippet.title}`);
    console.log('데이터 수집 완료:', video.snippet.title);
    
  } catch (error) {
    // 6. 에러 기록
    console.error('에러 발생:', error.message);
    logExecution(logSheet, '에러', error.message);
    
    // 7. 이메일 알림 (선택사항)
    // MailApp.sendEmail('your@email.com', '유튜브 수집 에러', error.message);
  }
}

/**
 * 실행 로그를 시트에 기록하는 헬퍼 함수
 */
function logExecution(logSheet, status, message) {
  if (!logSheet) {
    console.warn('로그 시트가 없어 로그를 기록하지 않습니다.');
    return;
  }
  logSheet.appendRow([new Date(), status, message]);
}

/**
 * 재시도 로직이 포함된 API 호출 함수
 */
function fetchWithRetry(url, options = {}, maxRetries = 3) {
  const defaultOptions = {
    muteHttpExceptions: true,
    ...options
  };
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = UrlFetchApp.fetch(url, defaultOptions);
      const code = response.getResponseCode();
      
      // 성공 또는 클라이언트 에러 (재시도 불필요)
      if (code < 500) {
        return response;
      }
      
      // 서버 에러 (재시도 가능)
      console.warn(`서버 에러 (${code}), 재시도 ${attempt}/${maxRetries}`);
      
      if (attempt < maxRetries) {
        // 지수 백오프: 1초, 2초, 4초...
        const waitTime = Math.pow(2, attempt - 1) * 1000;
        Utilities.sleep(waitTime);
      }
      
    } catch (error) {
      console.error(`네트워크 에러 (시도 ${attempt}/${maxRetries}):`, error.message);
      
      if (attempt === maxRetries) {
        throw new Error(`${maxRetries}회 재시도 후에도 실패: ${error.message}`);
      }
      
      Utilities.sleep(Math.pow(2, attempt - 1) * 1000);
    }
  }
}
```

### 예제 5: PropertiesService로 API 키 안전하게 저장하기

API 키를 코드에 직접 하드코딩하면 보안 위험이 있습니다. `PropertiesService`를 사용하여 안전하게 관리하는 방법을 알아보겠습니다.

```javascript
/**
 * API 키를 PropertiesService에 저장합니다.
 * 이 함수를 한 번만 실행하면 됩니다.
 * 실행 후에는 코드에서 API 키를 삭제하세요!
 */
function setApiKey() {
  // 아래 값을 실제 API 키로 변경한 후 한 번 실행하세요
  const apiKey = 'YOUR_YOUTUBE_API_KEY_HERE';
  
  PropertiesService.getScriptProperties().setProperty('YOUTUBE_API_KEY', apiKey);
  console.log('API 키가 안전하게 저장되었습니다.');
  console.log('이제 이 함수의 API 키 값을 코드에서 삭제하세요!');
}

/**
 * 여러 설정값을 한꺼번에 저장합니다.
 */
function setAllConfig() {
  const config = {
    'YOUTUBE_API_KEY': 'YOUR_API_KEY',
    'DEFAULT_SHEET_NAME': '유튜브데이터',
    'MAX_RESULTS': '50',
    'NOTIFICATION_EMAIL': 'your@email.com'
  };
  
  PropertiesService.getScriptProperties().setProperties(config);
  console.log('모든 설정이 저장되었습니다.');
}

/**
 * 저장된 설정값을 읽어옵니다.
 */
function getConfig(key) {
  const value = PropertiesService.getScriptProperties().getProperty(key);
  if (!value) {
    console.warn(`설정값 '${key}'이(가) 없습니다. setAllConfig()을 먼저 실행하세요.`);
  }
  return value;
}

/**
 * 현재 저장된 모든 설정을 확인합니다.
 * (디버깅용 - API 키의 전체 값은 로그에 출력하지 않습니다)
 */
function listAllConfig() {
  const props = PropertiesService.getScriptProperties().getProperties();
  
  for (const [key, value] of Object.entries(props)) {
    // API 키는 앞부분만 표시
    if (key.includes('KEY') || key.includes('SECRET')) {
      console.log(`${key}: ${value.substring(0, 8)}...`);
    } else {
      console.log(`${key}: ${value}`);
    }
  }
}

/**
 * 특정 설정값을 삭제합니다.
 */
function deleteConfig(key) {
  PropertiesService.getScriptProperties().deleteProperty(key);
  console.log(`설정값 '${key}'이(가) 삭제되었습니다.`);
}
```

> **PropertiesService의 세 가지 유형:**
> - `getScriptProperties()`: 스크립트에 저장. 해당 스크립트의 모든 실행에서 공유. API 키 저장에 적합.
> - `getUserProperties()`: 사용자별로 저장. 같은 스크립트라도 사용자마다 다른 값 유지.
> - `getDocumentProperties()`: 문서(스프레드시트)에 저장. 해당 문서에 연결된 스크립트에서만 접근 가능.
>
> API 키는 `getScriptProperties()`에 저장하는 것이 가장 적합합니다.

---

## 4.6 이 장의 핵심 정리

이 장에서 배운 내용을 정리하겠습니다.

| 항목 | 핵심 내용 |
|------|-----------|
| 앱스 스크립트 특징 | V8 런타임, 서버 불필요, 구글 서비스 네이티브 연결 |
| 스크립트 유형 | 컨테이너 바운드(이 책에서 사용) vs 독립형 |
| 로그 출력 | `console.log` 사용 (Logger.log는 레거시) |
| 에러 해결 | 에러 메시지 전체 + 코드 + 목적을 AI에게 전달 |
| HTTP 요청 | `UrlFetchApp.fetch()` + `muteHttpExceptions: true` |
| 데이터 읽기/쓰기 | 반드시 범위 단위(`getValues`/`setValues`)로 처리 |
| API 키 관리 | `PropertiesService.getScriptProperties()` 사용 |
| 에러 처리 | try-catch + 상세 로그 + 재시도 로직 |

다음 장에서는 이 기초 위에 유튜브 API를 본격적으로 활용하는 방법을 배워보겠습니다.
