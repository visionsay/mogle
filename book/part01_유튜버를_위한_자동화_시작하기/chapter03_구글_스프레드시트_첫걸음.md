# Chapter 03: 구글 스프레드시트 첫걸음

구글 스프레드시트는 대부분의 사람에게 "엑셀의 온라인 버전" 정도로 인식된다. 하지만 슈퍼유튜브시트의 관점에서 구글 스프레드시트는 **자동화 플랫폼**이다. 데이터를 저장하고, 앱스 스크립트로 로직을 실행하고, API와 통신하고, AI와 연동하는 **허브(Hub)**다.

이 장에서는 구글 스프레드시트를 자동화 관점에서 다시 바라보고, 슈퍼유튜브시트를 구축하는 데 필요한 핵심 기능을 익힌다. 기초적인 "셀 클릭하는 법" 같은 내용은 건너뛰고, **코드와 연동되는 실전 기능**에 집중한다.

---

## 구글 스프레드시트를 사용하는 이유 6가지

엑셀이 아닌 구글 스프레드시트를 선택하는 이유는 명확하다. 각각의 이유가 슈퍼유튜브시트의 핵심 기능과 직결된다.

### 이유 1: Apps Script 네이티브 지원

이것이 **가장 결정적인 이유**다. 구글 스프레드시트에는 **Google Apps Script**가 내장되어 있다. 별도의 개발 환경 설치 없이, 스프레드시트 메뉴에서 바로 코드를 작성하고 실행할 수 있다.

```
스프레드시트 → 확장 프로그램 → Apps Script → 코드 작성 → 실행
```

이 한 줄의 워크플로우가 슈퍼유튜브시트의 전부다. 엑셀에서는 VBA(Visual Basic for Applications)를 사용할 수 있지만, 웹 API 호출이나 클라우드 서비스 연동에서 앱스 스크립트에 비할 바가 못 된다.

**앱스 스크립트가 VBA보다 유리한 점:**

| 항목 | Google Apps Script | Excel VBA |
|------|-------------------|-----------|
| 실행 환경 | 클라우드 (서버) | 로컬 PC |
| 외부 API 호출 | `UrlFetchApp.fetch()` 간편 | 복잡한 HTTP 라이브러리 필요 |
| 스케줄 실행 | 트리거(Trigger) 내장 | Windows 작업 스케줄러 필요 |
| Google 서비스 연동 | 네이티브 (Gmail, Calendar 등) | 불가 또는 매우 복잡 |
| 공유/배포 | URL 공유만으로 완료 | 파일 전송 필요 |
| 언어 | JavaScript (ES6+) | VBA (레거시) |

### 이유 2: 무료 클라우드 호스팅

슈퍼유튜브시트의 데이터는 **구글 클라우드에 자동 저장**된다. 별도의 서버나 데이터베이스가 필요 없다.

```
[비용 비교]
─────────────────────────────────────────
구글 스프레드시트: $0/월
AWS EC2 (t3.micro): $8.50/월
Heroku (Basic): $7/월
Firebase (Blaze): 사용량 기반 과금
─────────────────────────────────────────
```

구글 계정당 15GB의 무료 구글 드라이브 용량이 제공되며, 스프레드시트 파일은 구글 드라이브 용량에 포함되지 않는다(구글 자체 형식인 경우). 즉, **데이터 저장 비용이 사실상 $0**이다.

### 이유 3: 실시간 협업

여러 사람이 동시에 같은 스프레드시트를 편집할 수 있다. MCN이나 에이전시에서 여러 채널을 관리하는 경우, 팀원들이 **동시에 대시보드를 확인하고 데이터를 입력**할 수 있다.

```javascript
// 여러 사용자가 공유하는 스프레드시트에서
// 사용자별 입력 영역을 분리하는 패턴
function getUserInputSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const userEmail = Session.getActiveUser().getEmail();
  const sheetName = '입력_' + userEmail.split('@')[0];
  
  let sheet = ss.getSheetByName(sheetName);
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    setupInputTemplate(sheet);
  }
  
  return sheet;
}
```

### 이유 4: API 트리거

앱스 스크립트의 **트리거(Trigger)** 기능은 슈퍼유튜브시트의 자동화 핵심이다. 코드를 특정 시간에, 또는 특정 이벤트 발생 시 **자동으로 실행**할 수 있다.

```javascript
// 트리거 종류와 설정 예시
function createAllTriggers() {
  // 1. 시간 기반 트리거: 매일 오전 9시에 트렌드 체크
  ScriptApp.newTrigger('checkDailyTrends')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
  
  // 2. 시간 기반 트리거: 매시간 구독자 수 체크
  ScriptApp.newTrigger('checkSubscriberCount')
    .timeBased()
    .everyHours(1)
    .create();
  
  // 3. 스프레드시트 이벤트 트리거: 셀 편집 시 실행
  ScriptApp.newTrigger('onEditHandler')
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onEdit()
    .create();
  
  // 4. 폼 제출 트리거: 구글 폼 응답 수신 시 실행
  ScriptApp.newTrigger('onFormSubmitHandler')
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onFormSubmit()
    .create();
  
  Logger.log('모든 트리거가 설정되었습니다.');
}
```

**트리거 종류 정리:**

| 트리거 유형 | 설명 | 슈퍼유튜브시트 활용 |
|------------|------|-------------------|
| `onOpen` | 스프레드시트 열 때 | 커스텀 메뉴 생성 |
| `onEdit` | 셀 편집 시 | 키워드 입력 즉시 검색 실행 |
| `onChange` | 구조 변경 시 | 시트 추가/삭제 감지 |
| `onFormSubmit` | 폼 응답 수신 시 | 시청자 설문 자동 처리 |
| `timeBased` | 시간 기반 | 정기 데이터 수집, 트렌드 체크 |

### 이유 5: 설치 불필요

구글 스프레드시트는 **웹 브라우저**만 있으면 된다. 어떤 소프트웨어도 설치할 필요가 없다.

- 노트북에서도, 데스크톱에서도, 심지어 태블릿에서도 접근 가능
- OS에 무관 (Windows, macOS, Linux, ChromeOS)
- 자동 업데이트 (항상 최신 버전)
- 기기 간 완벽한 동기화

이것은 특히 **외부에서 데이터를 확인해야 할 때** 큰 장점이다. 카페에서 노트북을 열고 슈퍼유튜브시트의 트렌드 데이터를 확인하고, 바로 콘텐츠 기획을 시작할 수 있다.

### 이유 6: Google 생태계 통합

구글 스프레드시트는 Google의 전체 서비스 생태계와 **네이티브로 연결**된다.

```
[슈퍼유튜브시트에서 활용하는 Google 서비스 연동]
─────────────────────────────────────────
YouTube Data API  → 영상/채널/댓글 데이터 수집
Gmail            → 트렌드 알림 이메일 발송
Google Calendar  → 업로드 스케줄 관리
Google Drive     → 백업 데이터 저장
Google Forms     → 시청자 피드백 수집
Gemini AI        → 데이터 분석 및 인사이트 도출
Google Slides    → 리포트 자동 생성
─────────────────────────────────────────
```

이 모든 서비스를 **하나의 앱스 스크립트 파일 안에서 호출**할 수 있다. 별도의 인증이나 복잡한 설정 없이, 구글 계정 하나로 전부 연동된다.

---

## 구글 스프레드시트 사용법 알아보기

기본적인 사용법은 건너뛰고, 슈퍼유튜브시트 구축에 필요한 **파워 유저 기능**에 집중한다.

### 이름이 지정된 범위 (Named Ranges)

이름이 지정된 범위(Named Range)는 특정 셀 범위에 **사람이 읽을 수 있는 이름**을 부여하는 기능이다. 앱스 스크립트 코드에서 셀 주소 대신 이름으로 데이터에 접근할 수 있어 코드의 가독성과 유지보수성이 크게 향상된다.

**설정 방법:**
1. 범위를 선택
2. 메뉴: **데이터 → 이름이 지정된 범위**
3. 이름 입력 후 저장

**앱스 스크립트에서의 활용:**

```javascript
// Named Range 없이 (나쁜 예)
function getKeywordBad() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName('검색');
  return sheet.getRange('A1').getValue(); // A1이 뭔지 알 수 없음
}

// Named Range 사용 (좋은 예)
function getKeywordGood() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getRangeByName('검색_키워드').getValue(); // 명확!
}
```

**슈퍼유튜브시트에서 사용할 Named Range 목록:**

| Named Range 이름 | 위치 | 용도 |
|------------------|------|------|
| `검색_키워드` | 검색!A1 | 검색할 키워드 |
| `검색_결과수` | 검색!A2 | 최대 검색 결과 수 |
| `검색_정렬` | 검색!A3 | 정렬 기준 (조회수/날짜/관련성) |
| `채널_ID목록` | 벤치마킹!A2:A | 분석할 채널 ID 목록 |
| `API_쿼터_잔여` | 설정!B1 | 오늘의 남은 API 쿼터 |
| `마지막_실행시간` | 설정!B2 | 마지막 데이터 수집 시간 |

```javascript
// Named Range를 프로그래밍 방식으로 생성하는 함수
function setupNamedRanges() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  const ranges = [
    { name: '검색_키워드', sheet: '검색', range: 'A1' },
    { name: '검색_결과수', sheet: '검색', range: 'A2' },
    { name: '검색_정렬', sheet: '검색', range: 'A3' },
    { name: '채널_ID목록', sheet: '벤치마킹', range: 'A2:A100' },
    { name: 'API_쿼터_잔여', sheet: '설정', range: 'B1' },
    { name: '마지막_실행시간', sheet: '설정', range: 'B2' }
  ];
  
  for (const r of ranges) {
    const sheet = ss.getSheetByName(r.sheet);
    if (sheet) {
      ss.setNamedRange(r.name, sheet.getRange(r.range));
      Logger.log(`Named Range 설정 완료: ${r.name}`);
    }
  }
}
```

### 데이터 유효성 검사 (Data Validation)

데이터 유효성 검사는 사용자가 **잘못된 데이터를 입력하는 것을 방지**한다. 슈퍼유튜브시트에서 드롭다운 메뉴나 입력 제한을 설정할 때 사용한다.

```javascript
// 데이터 유효성 검사 설정 예시
function setupDataValidation() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('검색');
  
  // 1. 정렬 기준 드롭다운 (A3 셀)
  const sortOptions = SpreadsheetApp.newDataValidation()
    .requireValueInList(
      ['조회수순', '최신순', '관련성순', '평점순'],
      true  // 드롭다운 표시
    )
    .setAllowInvalid(false)  // 목록에 없는 값 입력 불가
    .setHelpText('정렬 기준을 선택하세요')
    .build();
  sheet.getRange('A3').setDataValidation(sortOptions);
  
  // 2. 검색 결과 수 제한 (A2 셀: 1~50)
  const resultCount = SpreadsheetApp.newDataValidation()
    .requireNumberBetween(1, 50)
    .setAllowInvalid(false)
    .setHelpText('1에서 50 사이의 숫자를 입력하세요')
    .build();
  sheet.getRange('A2').setDataValidation(resultCount);
  
  // 3. 날짜 범위 제한 (A4 셀: 오늘 이전 날짜만)
  const dateValidation = SpreadsheetApp.newDataValidation()
    .requireDateOnOrBefore(new Date())
    .setAllowInvalid(false)
    .setHelpText('오늘 이전 날짜를 입력하세요')
    .build();
  sheet.getRange('A4').setDataValidation(dateValidation);
  
  Logger.log('데이터 유효성 검사 설정 완료');
}
```

### 조건부 서식 (Conditional Formatting)

데이터를 시각적으로 한눈에 파악할 수 있게 해주는 기능이다. 앱스 스크립트로 프로그래밍 방식으로 설정하면 **데이터가 갱신될 때마다 자동으로 서식이 적용**된다.

```javascript
// 조건부 서식 설정: 조회수에 따른 색상 그라데이션
function setupConditionalFormatting() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('검색결과');
  
  // 기존 조건부 서식 규칙 초기화
  sheet.clearConditionalFormatRules();
  
  const rules = [];
  
  // 1. 조회수(D열) 색상 스케일: 낮음(흰색) → 높음(진한 녹색)
  const viewCountRule = SpreadsheetApp.newConditionalFormatRule()
    .setGradientMinpoint('#FFFFFF')      // 최솟값: 흰색
    .setGradientMaxpoint('#0B8043')      // 최댓값: 진한 녹색
    .setRanges([sheet.getRange('D2:D500')])
    .build();
  rules.push(viewCountRule);
  
  // 2. 참여율(I열) 기반 하이라이트
  //    참여율 5% 이상: 녹색 배경
  const highEngagement = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberGreaterThanOrEqualTo(5)
    .setBackground('#D9EAD3')
    .setFontColor('#0B8043')
    .setBold(true)
    .setRanges([sheet.getRange('I2:I500')])
    .build();
  rules.push(highEngagement);
  
  //    참여율 1% 미만: 빨간 배경
  const lowEngagement = SpreadsheetApp.newConditionalFormatRule()
    .whenNumberLessThan(1)
    .setBackground('#F4CCCC')
    .setFontColor('#CC0000')
    .setRanges([sheet.getRange('I2:I500')])
    .build();
  rules.push(lowEngagement);
  
  // 3. 업로드 날짜(G열): 최근 7일 이내면 노란 배경
  const recentUpload = SpreadsheetApp.newConditionalFormatRule()
    .whenDateAfter(SpreadsheetApp.RelativeDate.PAST_WEEK)
    .setBackground('#FFF2CC')
    .setRanges([sheet.getRange('G2:G500')])
    .build();
  rules.push(recentUpload);
  
  // 규칙 일괄 적용
  sheet.setConditionalFormatRules(rules);
  Logger.log('조건부 서식 설정 완료: ' + rules.length + '개 규칙');
}
```

### IMPORTDATA / IMPORTXML 함수

스프레드시트 자체의 함수만으로도 외부 데이터를 가져올 수 있다. 앱스 스크립트 없이도 간단한 데이터 수집이 가능하다.

```
=IMPORTDATA("https://example.com/data.csv")
```

**IMPORTXML**은 웹 페이지에서 특정 데이터를 XPath로 추출한다.

```
// 웹 페이지의 특정 요소 추출
=IMPORTXML("https://example.com", "//h1")

// RSS 피드에서 제목 추출
=IMPORTXML("https://example.com/feed.xml", "//item/title")
```

**주의사항:**
- `IMPORTDATA`와 `IMPORTXML`은 **자동 갱신 주기가 불규칙**하다 (보통 1~2시간)
- 안정적인 데이터 수집에는 앱스 스크립트를 사용하는 것이 좋다
- 유튜브 API를 직접 호출하는 것이 더 정확하고 풍부한 데이터를 제공한다

이 함수들은 **빠른 프로토타이핑**이나 **보조 데이터 수집**에 활용하고, 핵심 데이터 수집은 앱스 스크립트로 구현하는 것을 권장한다.

### 커스텀 함수 (Custom Functions)

앱스 스크립트로 만든 함수를 **스프레드시트의 수식처럼** 사용할 수 있다. `=SUM()`이나 `=VLOOKUP()`처럼 `=내함수()`를 셀에 입력하면 된다.

```javascript
/**
 * 유튜브 영상 URL에서 영상 ID를 추출합니다.
 * 스프레드시트에서 =extractVideoId(A1) 형태로 사용
 *
 * @param {string} url 유튜브 영상 URL
 * @return {string} 영상 ID
 * @customfunction
 */
function extractVideoId(url) {
  if (!url) return '';
  
  // 다양한 유튜브 URL 형식 지원
  const patterns = [
    /(?:youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})/,
    /(?:youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /(?:youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
    /(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  
  // URL이 아닌 경우 영상 ID 자체일 수 있음
  if (/^[a-zA-Z0-9_-]{11}$/.test(url)) return url;
  
  return 'INVALID_URL';
}

/**
 * ISO 8601 duration을 "분:초" 형식으로 변환합니다.
 * 스프레드시트에서 =formatDuration("PT12M34S") 형태로 사용
 *
 * @param {string} isoDuration ISO 8601 duration (예: PT1H2M3S)
 * @return {string} "시:분:초" 또는 "분:초" 형식
 * @customfunction
 */
function formatDuration(isoDuration) {
  if (!isoDuration) return '';
  
  const match = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return isoDuration;
  
  const hours = parseInt(match[1] || 0);
  const minutes = parseInt(match[2] || 0);
  const seconds = parseInt(match[3] || 0);
  
  const pad = (n) => String(n).padStart(2, '0');
  
  if (hours > 0) {
    return `${hours}:${pad(minutes)}:${pad(seconds)}`;
  }
  return `${minutes}:${pad(seconds)}`;
}

/**
 * 참여율을 계산합니다. (좋아요 + 댓글) / 조회수 * 100
 *
 * @param {number} likes 좋아요 수
 * @param {number} comments 댓글 수
 * @param {number} views 조회수
 * @return {number} 참여율 (%)
 * @customfunction
 */
function engagementRate(likes, comments, views) {
  if (!views || views === 0) return 0;
  return Math.round(((likes + comments) / views) * 10000) / 100;
}
```

**스프레드시트에서의 사용:**

```
A1: https://www.youtube.com/watch?v=dQw4w9WgXcQ
B1: =extractVideoId(A1)          → "dQw4w9WgXcQ"
C1: =formatDuration("PT12M34S")  → "12:34"
D1: =engagementRate(1500, 200, 50000) → 3.4
```

> **중요**: `@customfunction` JSDoc 태그를 추가하면 스프레드시트에서 함수 자동완성과 도움말이 표시된다. 반드시 붙여주자.

> **제한사항**: 커스텀 함수 안에서는 `SpreadsheetApp`, `UrlFetchApp` 등의 서비스를 호출할 수 없다. 순수한 데이터 변환 로직에만 사용할 수 있다. API 호출이 필요한 기능은 일반 함수로 구현하고 메뉴나 트리거로 실행해야 한다.

---

## 셀, 행, 열 이해하기

기본 개념은 건너뛰고, 앱스 스크립트와 연동할 때 반드시 알아야 하는 **기술적 세부사항**에 집중한다.

### A1 표기법 vs R1C1 표기법

앱스 스크립트에서 셀을 참조하는 두 가지 방식이 있다.

**A1 표기법** — 가장 일반적인 방식:
```javascript
// 단일 셀
sheet.getRange('A1')        // A열 1행
sheet.getRange('C5')        // C열 5행

// 범위
sheet.getRange('A1:D10')    // A1부터 D10까지
sheet.getRange('A:A')       // A열 전체
sheet.getRange('3:3')       // 3행 전체
```

**R1C1 표기법** — 행/열 번호를 숫자로 지정:
```javascript
// getRange(행, 열)
sheet.getRange(1, 1)        // = A1 (1행, 1열)
sheet.getRange(5, 3)        // = C5 (5행, 3열)

// getRange(행, 열, 행수, 열수)
sheet.getRange(1, 1, 10, 4) // = A1:D10 (1행1열부터 10행4열)
sheet.getRange(2, 2, 1, 5)  // = B2:F2 (2행2열부터 1행5열)
```

**어느 것을 사용해야 하는가?**

```javascript
// ❌ 하드코딩된 A1 표기법 - 열이 추가되면 깨짐
const views = sheet.getRange('D2:D100').getValues();

// ✅ 변수를 사용한 R1C1 표기법 - 유연함
const VIEW_COL = 4;  // D열
const START_ROW = 2;
const lastRow = sheet.getLastRow();
const views = sheet.getRange(START_ROW, VIEW_COL, lastRow - 1, 1)
  .getValues();
```

**실전 팁**: 열 번호를 상수로 정의해두면 나중에 열 순서가 바뀌어도 상수값만 수정하면 된다.

```javascript
// 열 매핑 상수 정의
const COLS = {
  VIDEO_ID: 1,     // A열
  TITLE: 2,        // B열
  CHANNEL: 3,      // C열
  VIEWS: 4,        // D열
  LIKES: 5,        // E열
  COMMENTS: 6,     // F열
  UPLOAD_DATE: 7,  // G열
  DURATION: 8,     // H열
  ENGAGEMENT: 9    // I열
};

// 사용
const title = sheet.getRange(row, COLS.TITLE).getValue();
const views = sheet.getRange(row, COLS.VIEWS).getValue();
```

### getRange 패턴 완전 정리

앱스 스크립트에서 가장 자주 사용하는 `getRange` 메서드의 모든 패턴을 정리한다.

```javascript
const sheet = SpreadsheetApp.getActiveSpreadsheet()
  .getSheetByName('검색결과');

// ── 읽기 패턴 ──

// 1. 단일 셀 값 읽기
const keyword = sheet.getRange('A1').getValue();

// 2. 범위의 모든 값 읽기 (2D 배열로 반환)
const allData = sheet.getRange('A2:I100').getValues();
// allData[0][0] = A2의 값
// allData[0][1] = B2의 값
// allData[1][0] = A3의 값

// 3. 데이터가 있는 마지막 행까지만 읽기
const lastRow = sheet.getLastRow();
const data = sheet.getRange(2, 1, lastRow - 1, 9).getValues();

// 4. 데이터 범위 자동 감지
const dataRange = sheet.getDataRange();  // 데이터가 있는 전체 범위
const allValues = dataRange.getValues();

// ── 쓰기 패턴 ──

// 5. 단일 셀에 값 쓰기
sheet.getRange('A1').setValue('검색 완료');

// 6. 범위에 2D 배열 쓰기 (★ 가장 중요한 패턴)
const outputData = [
  ['제목1', '채널1', 10000, 500],
  ['제목2', '채널2', 20000, 800],
  ['제목3', '채널3', 15000, 600]
];
sheet.getRange(2, 1, outputData.length, outputData[0].length)
  .setValues(outputData);

// 7. 행 추가 (마지막 행 뒤에)
sheet.appendRow(['새 데이터', '채널명', 5000, 200]);
```

### 배치 연산의 중요성

앱스 스크립트에서 **성능을 결정짓는 핵심 개념**이다. 셀 하나하나를 읽고 쓰면 극도로 느리다.

```javascript
// ❌ 느린 방법: 셀을 하나씩 읽고 쓰기 (100행 → 약 30초)
function slowMethod() {
  const sheet = SpreadsheetApp.getActiveSheet();
  for (let i = 1; i <= 100; i++) {
    const value = sheet.getRange(i, 1).getValue();   // API 호출 1
    sheet.getRange(i, 2).setValue(value * 2);         // API 호출 2
    // 100행 × 2회 = 200번의 API 호출
  }
}

// ✅ 빠른 방법: 배치로 읽고 쓰기 (100행 → 약 1초)
function fastMethod() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const values = sheet.getRange(1, 1, 100, 1).getValues();  // API 호출 1
  
  const results = values.map(row => [row[0] * 2]);
  
  sheet.getRange(1, 2, 100, 1).setValues(results);          // API 호출 2
  // 총 2번의 API 호출
}
```

**속도 차이: 약 30배**. 슈퍼유튜브시트에서 수백 개의 영상 데이터를 처리할 때 이 차이는 **6분 실행 시간 제한 이내에 완료하느냐 마느냐**를 결정한다.

**배치 연산 원칙:**

```
1. 읽기: getValues()로 한 번에 읽기 → 메모리에서 처리 → setValues()로 한 번에 쓰기
2. 절대 금지: 루프 안에서 getValue()/setValue() 호출
3. SpreadsheetApp.flush(): 버퍼에 쌓인 쓰기 작업을 즉시 실행 (필요한 경우에만)
```

### 데이터 타입 주의사항

스프레드시트에서 읽어온 데이터의 타입이 예상과 다를 수 있다.

```javascript
function checkDataTypes() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const values = sheet.getRange('A1:A5').getValues();
  
  // 스프레드시트 셀 값과 JavaScript 타입 매핑
  // 숫자 셀    → number    (예: 12345)
  // 텍스트 셀  → string    (예: "안녕하세요")
  // 날짜 셀    → Date 객체 (예: Date object)
  // 빈 셀      → ''        (빈 문자열)
  // 체크박스    → boolean   (true/false)
  // 수식 셀    → 수식의 결과값 (수식 자체가 아님)
  
  for (const [value] of values) {
    Logger.log(`값: ${value}, 타입: ${typeof value}`);
  }
}
```

**자주 발생하는 문제:**

```javascript
// 문제: 숫자처럼 보이지만 문자열인 경우
const viewCount = sheet.getRange('D2').getValue();
// viewCount가 "10,000" (쉼표 포함 문자열)일 수 있음

// 해결: 숫자로 변환
const viewCountNum = Number(String(viewCount).replace(/,/g, ''));

// 문제: 날짜 비교
const uploadDate = sheet.getRange('G2').getValue(); // Date 객체
const sevenDaysAgo = new Date();
sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

if (uploadDate > sevenDaysAgo) {
  Logger.log('최근 7일 이내 업로드');
}
```

---

## 시트 탭 알아보기

슈퍼유튜브시트는 **여러 개의 시트 탭**으로 구성된다. 각 시트가 고유한 역할을 담당하며, 앱스 스크립트가 이 시트들을 자동으로 관리한다.

### 슈퍼유튜브시트의 시트 구조

```
[슈퍼유튜브시트 시트 탭 구성]
─────────────────────────────────────────
📋 대시보드      → 핵심 지표 요약 (읽기 전용)
🔍 키워드검색    → 키워드 기반 영상 검색 결과
📊 채널벤치마킹  → 경쟁 채널 비교 데이터
💬 댓글분석      → 댓글 수집 및 감성 분석 결과
📈 트렌드        → 트렌드 탐지 데이터
🎯 구독자추적    → 구독자 수 변화 기록
🤖 AI분석        → Gemini AI 분석 결과
⚙️ 설정          → API 키, 설정값, 쿼터 관리
📝 로그          → 실행 로그 기록
─────────────────────────────────────────
```

### 시트 프로그래밍 방식 관리

앱스 스크립트로 시트를 생성, 삭제, 이름 변경하는 방법을 알아보자.

```javascript
// 슈퍼유튜브시트 초기 설정: 모든 시트를 자동으로 생성
function initializeSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  const sheetConfigs = [
    {
      name: '대시보드',
      headers: ['항목', '값', '변화', '업데이트 시간'],
      color: '#4285F4',  // 파란색
      protected: true
    },
    {
      name: '키워드검색',
      headers: ['영상ID', '제목', '채널명', '조회수', '좋아요',
                '댓글수', '업로드일', '길이', '참여율'],
      color: '#0F9D58',  // 녹색
      protected: false
    },
    {
      name: '채널벤치마킹',
      headers: ['채널ID', '채널명', '구독자수', '총영상수',
                '총조회수', '최근30일영상수', '평균조회수'],
      color: '#F4B400',  // 노란색
      protected: false
    },
    {
      name: '댓글분석',
      headers: ['영상ID', '작성자', '댓글내용', '좋아요수',
                '작성일시', '감성', '키워드'],
      color: '#DB4437',  // 빨간색
      protected: false
    },
    {
      name: '설정',
      headers: ['항목', '값', '설명'],
      color: '#757575',  // 회색
      protected: true
    },
    {
      name: '로그',
      headers: ['시간', '함수명', '상태', '메시지'],
      color: '#9E9E9E',  // 연한 회색
      protected: true
    }
  ];
  
  for (const config of sheetConfigs) {
    let sheet = ss.getSheetByName(config.name);
    
    // 시트가 없으면 생성
    if (!sheet) {
      sheet = ss.insertSheet(config.name);
      Logger.log(`시트 생성: ${config.name}`);
    }
    
    // 헤더 설정
    if (config.headers.length > 0) {
      const headerRange = sheet.getRange(1, 1, 1, config.headers.length);
      headerRange.setValues([config.headers]);
      headerRange.setFontWeight('bold');
      headerRange.setBackground('#E8EAED');
      headerRange.setHorizontalAlignment('center');
    }
    
    // 탭 색상 설정
    sheet.setTabColor(config.color);
    
    // 열 너비 자동 조정
    for (let i = 1; i <= config.headers.length; i++) {
      sheet.autoResizeColumn(i);
    }
    
    // 첫 행 고정 (스크롤 시 헤더 유지)
    sheet.setFrozenRows(1);
  }
  
  // 기본 "Sheet1" 시트 삭제 (있는 경우)
  const defaultSheet = ss.getSheetByName('Sheet1');
  if (defaultSheet && ss.getSheets().length > 1) {
    ss.deleteSheet(defaultSheet);
  }
  
  // 대시보드를 첫 번째 탭으로 이동
  const dashboard = ss.getSheetByName('대시보드');
  if (dashboard) {
    ss.setActiveSheet(dashboard);
    ss.moveActiveSheet(1);
  }
  
  Logger.log('슈퍼유튜브시트 초기 설정 완료!');
  SpreadsheetApp.getUi().alert('슈퍼유튜브시트 초기 설정이 완료되었습니다!');
}
```

### 시트 보호 (Sheet Protection)

설정 시트나 대시보드처럼 **사용자가 실수로 수정하면 안 되는 시트**를 보호하는 방법이다.

```javascript
// 시트 보호 설정
function protectSheets() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const currentUser = Session.getEffectiveUser();
  
  // 보호할 시트 목록
  const protectedSheetNames = ['대시보드', '설정', '로그'];
  
  for (const sheetName of protectedSheetNames) {
    const sheet = ss.getSheetByName(sheetName);
    if (!sheet) continue;
    
    // 기존 보호 제거
    const protections = sheet.getProtections(
      SpreadsheetApp.ProtectionType.SHEET
    );
    for (const p of protections) {
      if (p.canEdit()) p.remove();
    }
    
    // 새 보호 설정
    const protection = sheet.protect()
      .setDescription(`${sheetName} - 자동 관리 시트 (수정 금지)`);
    
    // 스크립트 실행자만 편집 가능
    protection.addEditor(currentUser);
    protection.removeEditors(
      protection.getEditors()
        .filter(editor => editor.getEmail() !== currentUser.getEmail())
    );
    
    // 경고 메시지만 표시 (완전 잠금이 아닌 경고)
    protection.setWarningOnly(true);
    
    Logger.log(`시트 보호 설정 완료: ${sheetName}`);
  }
}
```

### 특정 범위만 보호하기

시트 전체가 아닌 **특정 범위만 보호**할 수도 있다. 예를 들어, 키워드검색 시트에서 입력 영역(A1:A3)은 편집 가능하고 결과 영역(B:I)은 보호하는 식이다.

```javascript
// 범위 보호: 결과 영역만 보호하고 입력 영역은 허용
function protectResultArea() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('키워드검색');
  
  // 결과 영역 보호
  const resultRange = sheet.getRange('B1:I500');
  const protection = resultRange.protect()
    .setDescription('검색 결과 영역 - 자동 생성 데이터');
  
  // 편집 불가 설정 (경고만 표시)
  protection.setWarningOnly(true);
  
  Logger.log('결과 영역 보호 설정 완료');
}
```

### 시트 관리 유틸리티 함수

실무에서 자주 사용하는 시트 관리 함수들을 모아보자.

```javascript
/**
 * 시트의 데이터를 모두 삭제합니다 (헤더는 유지).
 * @param {string} sheetName 시트 이름
 */
function clearSheetData(sheetName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName(sheetName);
  
  if (!sheet) {
    Logger.log(`시트를 찾을 수 없음: ${sheetName}`);
    return;
  }
  
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    // 2행부터 마지막 행까지 삭제 (헤더인 1행은 유지)
    sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clearContent();
    Logger.log(`${sheetName} 시트 데이터 삭제 완료 (${lastRow - 1}행)`);
  }
}

/**
 * 시트에 로그를 기록합니다.
 * @param {string} functionName 함수명
 * @param {string} status 상태 (성공/실패/경고)
 * @param {string} message 메시지
 */
function writeLog(functionName, status, message) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName('로그');
  
  if (!sheet) return;
  
  sheet.appendRow([
    new Date(),
    functionName,
    status,
    message
  ]);
  
  // 로그가 1000행을 초과하면 오래된 로그 삭제
  const lastRow = sheet.getLastRow();
  if (lastRow > 1000) {
    sheet.deleteRows(2, lastRow - 500);  // 최근 500개만 유지
  }
}

/**
 * 시트 존재 여부를 확인하고 없으면 생성합니다.
 * @param {string} sheetName 시트 이름
 * @param {string[]} headers 헤더 배열
 * @return {GoogleAppsScript.Spreadsheet.Sheet} 시트 객체
 */
function getOrCreateSheet(sheetName, headers) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    if (headers && headers.length > 0) {
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
      sheet.getRange(1, 1, 1, headers.length)
        .setFontWeight('bold')
        .setBackground('#E8EAED');
      sheet.setFrozenRows(1);
    }
    Logger.log(`시트 생성 완료: ${sheetName}`);
  }
  
  return sheet;
}

/**
 * 시트의 데이터를 2D 배열에서 객체 배열로 변환합니다.
 * 헤더를 키로 사용하여 각 행을 객체로 변환합니다.
 * @param {string} sheetName 시트 이름
 * @return {Object[]} 객체 배열
 */
function sheetToObjects(sheetName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName(sheetName);
  
  if (!sheet || sheet.getLastRow() < 2) return [];
  
  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  
  return data.slice(1)
    .filter(row => row.some(cell => cell !== ''))  // 빈 행 제거
    .map(row => {
      const obj = {};
      headers.forEach((header, index) => {
        obj[header] = row[index];
      });
      return obj;
    });
}
```

**`sheetToObjects` 사용 예시:**

```javascript
// 키워드검색 시트의 데이터를 객체 배열로 가져오기
const videos = sheetToObjects('키워드검색');

// 조회수 10,000 이상인 영상만 필터링
const popularVideos = videos.filter(v => v['조회수'] >= 10000);

// 참여율 기준 정렬
const sortedByEngagement = videos.sort(
  (a, b) => b['참여율'] - a['참여율']
);

// 채널별 영상 수 집계
const channelCounts = {};
for (const video of videos) {
  const channel = video['채널명'];
  channelCounts[channel] = (channelCounts[channel] || 0) + 1;
}
```

이 유틸리티 함수들은 앞으로 슈퍼유튜브시트의 모든 기능에서 **반복적으로 사용**된다. 한 번 만들어두면 계속 재사용할 수 있다.

---

## 정리: 다음 단계를 위한 준비

이 장에서 다룬 내용을 정리하면 다음과 같다.

```
[Chapter 03 핵심 정리]
─────────────────────────────────────────
✅ 구글 스프레드시트 = 자동화 플랫폼
✅ Named Range로 코드 가독성 향상
✅ 데이터 유효성 검사로 입력 오류 방지
✅ 조건부 서식으로 데이터 시각화
✅ 커스텀 함수로 수식 확장
✅ A1 표기법 vs R1C1 표기법 이해
✅ 배치 연산으로 성능 최적화 (getValues/setValues)
✅ 시트 프로그래밍 방식 관리 (생성/삭제/보호)
✅ 유틸리티 함수 라이브러리 구축
─────────────────────────────────────────
```

Part 01의 세 장을 통해 우리는 다음을 준비했다.

1. **슈퍼유튜브시트가 무엇인지, 왜 필요한지** 이해했다 (Chapter 01)
2. **바이브 코딩과 제미나이**를 사용할 준비를 마쳤다 (Chapter 02)
3. **구글 스프레드시트**를 자동화 플랫폼으로 활용하는 기반을 갖추었다 (Chapter 03)

다음 Part 02에서는 본격적으로 **구글 앱스 스크립트**를 다루고, **YouTube Data API**를 연동하는 방법을 배운다. 슈퍼유튜브시트의 핵심 엔진을 직접 만드는 과정이 시작된다.
