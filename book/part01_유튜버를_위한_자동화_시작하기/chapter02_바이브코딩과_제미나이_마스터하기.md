# Chapter 02: 바이브 코딩과 제미나이 마스터하기

코딩을 배워야 한다고 하면 대부분의 유튜버는 고개를 젓는다. "나는 크리에이터지, 개발자가 아닌데?" 맞는 말이다. 하지만 2025년을 기점으로 세상이 바뀌었다. 이제는 코드를 **직접 작성하지 않아도** 된다. AI에게 원하는 것을 말하면 AI가 코드를 작성해준다. 이것을 **바이브 코딩(Vibe Coding)**이라고 부른다.

이 장에서는 바이브 코딩이 무엇인지, 왜 유튜버에게 제미나이(Gemini)가 최적의 AI인지, 그리고 어떻게 제미나이를 시작하는지를 다룬다.

---

## 바이브 코딩이란?

### 용어의 탄생

**바이브 코딩(Vibe Coding)**이라는 용어는 2025년 2월, 테슬라의 전 AI 수석이자 OpenAI 공동 창립자인 **안드레이 카르파시(Andrej Karpathy)**가 처음 사용했다.

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."
>
> "나는 이것을 '바이브 코딩'이라 부른다. 분위기에 완전히 몸을 맡기고, 코드가 존재한다는 사실조차 잊는 새로운 형태의 코딩이다."

핵심은 이것이다. **코드를 읽거나 이해할 필요 없이, 원하는 결과를 자연어로 설명하면 AI가 코드를 생성**한다. 개발자가 아닌 사람도 프로그래밍의 결과물을 만들어낼 수 있는 시대가 열린 것이다.

### 바이브 코딩의 실제 모습

바이브 코딩이 어떤 것인지, 구글 앱스 스크립트에서의 실제 예를 보자.

**전통적 코딩 방식:**
프로그래밍 언어의 문법을 배우고, API 문서를 읽고, 직접 코드를 작성한다.

```javascript
// 이 코드를 직접 작성하려면 JavaScript 문법,
// Google Apps Script API, YouTube Data API를
// 모두 알아야 한다.
function searchVideos(keyword, maxResults) {
  const apiKey = PropertiesService.getScriptProperties()
    .getProperty('YOUTUBE_API_KEY');
  const url = 'https://www.googleapis.com/youtube/v3/search'
    + '?part=snippet'
    + '&q=' + encodeURIComponent(keyword)
    + '&type=video'
    + '&order=viewCount'
    + '&maxResults=' + maxResults
    + '&key=' + apiKey;
  
  const response = UrlFetchApp.fetch(url);
  const data = JSON.parse(response.getContentText());
  // ... 이하 수십 줄의 코드
}
```

**바이브 코딩 방식:**
AI에게 원하는 것을 설명한다.

```
[제미나이에게 보내는 프롬프트]

구글 앱스 스크립트로 다음 기능을 만들어줘:

1. 스프레드시트 "검색" 시트의 A1 셀에 입력된 키워드로
   유튜브 영상을 검색해줘
2. 최대 50개 결과를 가져와줘
3. 조회수 순으로 정렬해줘
4. 각 영상의 제목, 채널명, 조회수, 좋아요 수, 댓글 수,
   업로드 날짜를 B2 셀부터 아래로 채워줘
5. YouTube Data API 키는 스크립트 속성의
   'YOUTUBE_API_KEY'에 저장되어 있어
6. 기존 데이터는 지우고 새로 채워줘
```

이 프롬프트를 제미나이에게 전달하면, 완전한 코드가 생성된다. 코드를 복사해서 앱스 스크립트 에디터에 붙여넣고 실행하면 끝이다.

### 바이브 코딩 ≠ 노코드

바이브 코딩을 "노코드(No-Code)" 도구와 혼동하면 안 된다. 둘은 근본적으로 다르다.

| 구분 | 노코드 도구 | 바이브 코딩 |
|------|-----------|-----------|
| 작동 방식 | 미리 만들어진 블록을 조합 | AI가 실제 코드를 생성 |
| 자유도 | 도구가 제공하는 기능으로 제한 | 프로그래밍 언어로 가능한 모든 것 |
| 커스터마이징 | 제한적 | 무한대 |
| 비용 | 대부분 유료 (월 $20~100) | AI 사용료만 (무료 가능) |
| 결과물 | 도구에 종속 | 독립적인 코드 |
| 학습 효과 | 낮음 | 높음 (코드를 점차 이해하게 됨) |

바이브 코딩의 가장 큰 장점은 **자유도**다. 노코드 도구는 만든 사람이 예상한 기능만 제공하지만, 바이브 코딩은 **상상할 수 있는 모든 것**을 구현할 수 있다. YouTube Data API가 제공하는 모든 데이터에 접근할 수 있고, 그 데이터를 원하는 방식으로 가공하고 분석할 수 있다.

---

## 바이브 코딩을 위한 4가지 마음가짐

바이브 코딩이 "AI에게 시키면 끝"이라는 뜻은 아니다. 효과적으로 바이브 코딩을 하려면 올바른 마음가짐이 필요하다.

### 마음가짐 1: 에러는 학습의 기회다

AI가 생성한 코드가 한 번에 완벽하게 작동할 확률은 **약 60~70%**다. 나머지 30~40%는 에러가 발생한다. 이때 패닉에 빠지지 마라.

**에러가 발생했을 때의 바이브 코딩 프로세스:**

```
1단계: 에러 메시지를 복사한다
2단계: AI에게 에러 메시지를 보여주고 수정을 요청한다
3단계: 수정된 코드를 다시 실행한다
4단계: 반복 (보통 2~3회면 해결)
```

**실제 예시:**

```
[에러 발생 시 제미나이에게 보내는 프롬프트]

방금 준 코드를 실행했더니 다음 에러가 발생했어:

"TypeError: Cannot read properties of undefined
(reading 'items')"

에러가 발생한 코드 전체는 이거야:
[코드 전체 붙여넣기]

원인을 분석하고 수정된 코드를 줘.
```

에러를 AI에게 전달하는 것 자체가 **학습**이다. 같은 유형의 에러를 반복적으로 보다 보면 자연스럽게 "아, 이건 API 응답이 비어있을 때 발생하는 에러구나"라는 감이 생긴다. 바이브 코딩을 하면서 **의도치 않게 코딩을 배우게 되는 것**이다.

### 마음가짐 2: 작은 단위로 요청하기

AI에게 한 번에 거대한 시스템을 만들어달라고 하면 실패할 확률이 높다. **작은 기능 단위로 나눠서 요청**하는 것이 핵심이다.

**나쁜 예:**
```
유튜브 채널 분석 시스템을 만들어줘. 키워드 검색, 채널 벤치마킹,
댓글 분석, 트렌드 탐지, 구독자 이벤트 자동화, AI 분석까지
전부 포함해서.
```

**좋은 예:**
```
1번 요청: "유튜브 키워드로 영상을 검색해서 스프레드시트에
          결과를 저장하는 앱스 스크립트를 만들어줘"

2번 요청: "1번에서 만든 코드에 각 영상의 채널 구독자 수도
          함께 가져오는 기능을 추가해줘"

3번 요청: "검색 결과에서 조회수/구독자 비율을 계산하는
          컬럼을 추가해줘"
```

**작은 단위로 나누면 좋은 이유:**
- 각 단계에서 결과를 검증할 수 있다
- 에러가 발생해도 어디서 문제가 생겼는지 바로 알 수 있다
- AI가 더 정확한 코드를 생성한다 (컨텍스트가 명확하므로)
- 나중에 특정 기능만 수정하거나 교체하기 쉽다

### 마음가짐 3: 컨텍스트를 충분히 제공하기

AI는 당신의 상황을 모른다. **구체적인 컨텍스트를 제공할수록 정확한 코드가 나온다**.

**컨텍스트가 부족한 프롬프트:**
```
유튜브 댓글을 가져오는 코드 만들어줘.
```

**컨텍스트가 충분한 프롬프트:**
```
구글 앱스 스크립트(Google Apps Script)로 다음 조건에 맞는
코드를 만들어줘:

환경:
- 구글 스프레드시트에 바인딩된 앱스 스크립트
- YouTube Data API v3 사용
- API 키는 스크립트 속성(Script Properties)의
  'YOUTUBE_API_KEY'에 저장됨

기능:
- '댓글분석' 시트의 A1 셀에 유튜브 영상 ID가 입력되어 있음
  (예: "dQw4w9WgXcQ")
- 해당 영상의 모든 댓글(대댓글 포함)을 수집
- B열: 작성자 이름, C열: 댓글 내용, D열: 좋아요 수,
  E열: 작성일시
- B2 셀부터 데이터를 채움
- 기존 데이터는 삭제하고 새로 채움
- 댓글이 100개 이상이면 페이지네이션 처리

제약사항:
- 앱스 스크립트의 6분 실행 시간 제한을 고려해줘
- API 쿼터를 절약하기 위해 필요한 필드만 요청해줘
```

두 번째 프롬프트가 훨씬 길지만, **AI가 정확한 코드를 생성할 확률이 90% 이상**이다. 처음에는 이런 상세한 프롬프트를 작성하는 것이 번거롭게 느껴질 수 있다. 하지만 이 책의 뒤 챕터에서 제공하는 **프롬프트 템플릿**을 활용하면 쉽게 작성할 수 있다.

### 마음가짐 4: 결과를 검증하는 습관

AI가 생성한 코드가 작동한다고 해서 끝이 아니다. **결과가 정확한지 반드시 검증**해야 한다.

**검증 방법:**

```
1. 소량 테스트: 먼저 3~5개의 소량 데이터로 테스트
2. 수동 대조: API로 가져온 데이터를 유튜브에서 직접 확인
3. 경계값 테스트: 빈 결과, 특수문자, 긴 텍스트 등 예외 상황 확인
4. 쿼터 확인: API 호출 횟수가 예상 범위 내인지 확인
```

**실전 검증 프롬프트:**

```
[검증 요청 프롬프트]

이 코드가 제대로 동작하는지 확인하기 위한 테스트 코드를 만들어줘:

1. 테스트용 영상 ID 3개로 실행해서 결과를 로그에 출력
2. YouTube에서 직접 확인한 값과 비교할 수 있도록
   각 영상의 URL도 함께 로그에 출력
3. API 호출 횟수를 카운트해서 로그에 출력
4. 실행 시간을 측정해서 로그에 출력
```

검증은 귀찮은 작업이지만, **한 번의 검증이 나중에 잘못된 데이터로 인한 수십 시간의 삽질을 방지**한다.

---

## 제미나이 vs 챗GPT vs 클로드 비교

2026년 6월 현재, 코딩 AI의 3대 강자는 **구글 제미나이(Gemini)**, **OpenAI 챗GPT**, **앤트로픽 클로드(Claude)**다. 각각의 특성을 바이브 코딩, 특히 **구글 앱스 스크립트 개발** 관점에서 비교해보자.

### 주요 모델 비교표 (2026년 6월 기준)

| 항목 | Gemini 2.5 Pro | Gemini 2.5 Flash | GPT-4.1 | Claude Opus 4 |
|------|---------------|-----------------|---------|--------------|
| **개발사** | Google | Google | OpenAI | Anthropic |
| **컨텍스트 윈도우** | 1M 토큰 | 1M 토큰 | 1M 토큰 | 200K 토큰 |
| **무료 사용** | Google AI Studio | Google AI Studio | 제한적 | 제한적 |
| **API 무료 티어** | Flash 무료 | ✅ 무료 | ❌ | ❌ |
| **Google 생태계 연동** | ★★★★★ 네이티브 | ★★★★★ 네이티브 | ★★☆☆☆ | ★★☆☆☆ |
| **Apps Script 코드 품질** | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| **한국어 이해도** | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| **실시간 검색 연동** | ✅ (Grounding) | ✅ (Grounding) | ✅ (Browsing) | ❌ |
| **월 비용 (API)** | 유료 (Pro) | 무료 (Flash) | $20+/월 | $20+/월 |

### Google 생태계 연동에서의 차이

이것이 **결정적인 차이**다. 구글 앱스 스크립트는 구글의 제품이다. 제미나이 역시 구글의 제품이다. 같은 회사의 제품끼리 **시너지**가 생기는 것은 당연하다.

**제미나이가 Apps Script 코드에서 강한 이유:**

1. **최신 API 반영**: Google의 내부 문서와 최신 API 변경사항이 즉시 반영된다. 다른 AI 모델은 학습 데이터 시점에 따라 구버전 API를 참조할 수 있다.

2. **Google 서비스 간 연동 코드**: Sheets + YouTube + Gmail + Calendar 등 Google 서비스 간 연동 코드를 생성할 때 가장 정확하다.

3. **앱스 스크립트 특유의 제약사항 이해**: 6분 실행 시간 제한, `UrlFetchApp` 사용법, `PropertiesService` 활용법 등 앱스 스크립트만의 특수한 환경을 정확히 이해한다.

**실제 비교 테스트:**

같은 프롬프트("유튜브 영상 댓글을 수집해서 구글 시트에 저장하는 앱스 스크립트")를 세 AI에게 던졌을 때의 차이:

```
[Gemini 2.5 Flash 결과]
- YouTube.CommentThreads.list() 내장 서비스 활용 ✅
- 배치 쓰기(setValues) 사용으로 성능 최적화 ✅
- 페이지네이션 완벽 처리 ✅
- 6분 제한 대비 시간 체크 로직 포함 ✅

[GPT-4.1 결과]
- UrlFetchApp.fetch()로 REST API 직접 호출 ✅
- 배치 쓰기 사용 ✅
- 페이지네이션 처리 ✅
- 6분 제한 미고려 ⚠️

[Claude Opus 4 결과]
- UrlFetchApp.fetch()로 REST API 직접 호출 ✅
- 배치 쓰기 사용 ✅
- 페이지네이션 처리 ✅
- 에러 핸들링 가장 상세 ✅
- 6분 제한 대비 로직 포함 ✅
```

세 모델 모두 작동하는 코드를 생성하지만, **제미나이는 앱스 스크립트의 내장 YouTube 서비스(Advanced Services)를 활용**하는 코드를 생성하는 경향이 있다. 이는 UrlFetchApp으로 REST API를 직접 호출하는 것보다 **코드가 간결하고 쿼터 관리가 용이**하다.

---

## 유튜버가 제미나이를 써야 하는 이유 2가지

### 이유 1: Google 생태계 네이티브 통합

슈퍼유튜브시트의 기술 스택을 보자.

```
[슈퍼유튜브시트 기술 스택]
─────────────────────────────────
구글 스프레드시트  ← Google 제품
앱스 스크립트      ← Google 제품
YouTube Data API  ← Google 제품
Gemini AI         ← Google 제품
─────────────────────────────────
전부 Google 생태계 안에 있다.
```

제미나이는 이 생태계의 **네이티브 시민(native citizen)**이다. 구글 스프레드시트 안에서 직접 제미나이를 호출할 수 있고, 앱스 스크립트에서 Gemini API를 가장 자연스럽게 연동할 수 있다.

**앱스 스크립트에서 Gemini API 호출 예시:**

```javascript
function callGemini(prompt) {
  const apiKey = PropertiesService.getScriptProperties()
    .getProperty('GEMINI_API_KEY');
  
  const url = 'https://generativelanguage.googleapis.com/v1beta/models/'
    + 'gemini-2.5-flash:generateContent?key=' + apiKey;
  
  const payload = {
    contents: [{
      parts: [{
        text: prompt
      }]
    }],
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 2048
    }
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  
  return data.candidates[0].content.parts[0].text;
}
```

이 코드 하나로 **앱스 스크립트 안에서 AI 분석이 가능**해진다. 수집한 유튜브 데이터를 제미나이에게 전달하고, 분석 결과를 다시 스프레드시트에 기록하는 것이 **하나의 환경 안에서 완결**된다.

### 이유 2: 무료 티어의 관대함

2026년 6월 기준, 각 AI 서비스의 무료 사용 범위를 비교해보자.

```
[무료 사용 비교]
─────────────────────────────────────────
Gemini (Google AI Studio):
  - Gemini 2.5 Flash: 무료 (분당 요청 제한 있음)
  - 일일 무료 요청: 충분한 수준
  - API 키 발급: 무료, 즉시 가능
  - 추가 비용 없이 Grounding(실시간 검색) 사용 가능

ChatGPT:
  - GPT-4.1 API: 유료 ($2/1M input tokens)
  - 무료 티어: GPT-4o-mini 제한적 무료
  - 웹 인터페이스: 무료 사용 가능하지만 API 접근 제한

Claude:
  - Opus 4 API: 유료 ($15/1M input tokens)
  - 무료 티어: claude.ai에서 제한적 무료
  - API: 무료 크레딧 소진 후 유료
─────────────────────────────────────────
```

슈퍼유튜브시트에서 AI 분석을 사용할 때마다 API 비용이 발생한다면, "무료로 유튜브 분석 시스템을 만든다"는 취지가 무색해진다. **Gemini 2.5 Flash의 무료 티어**는 개인 유튜버가 사용하기에 충분한 수준이다.

물론 대량의 데이터를 분석하거나 빈번하게 호출하면 무료 한도를 초과할 수 있다. 그때도 Gemini 2.5 Flash의 유료 요금은 다른 모델 대비 **압도적으로 저렴**하다.

---

## 제미나이만이 알려줄 수 있는 것 3가지

### 1. Grounding을 통한 실시간 YouTube 데이터 인사이트

제미나이의 **Grounding with Google Search** 기능은 다른 AI에 없는 고유한 강점이다. AI가 답변을 생성할 때 **실시간 구글 검색 결과를 참조**할 수 있다.

**활용 예시:**

```
[프롬프트 - Grounding 활용]

다음 유튜브 채널의 최근 트렌드를 분석해줘.
구글 검색을 활용해서 최신 정보를 포함해줘.

채널 카테고리: 한국 IT/코딩 교육
분석 기간: 최근 1개월

다음 항목을 분석해줘:
1. 현재 가장 핫한 주제 3가지
2. 각 주제의 경쟁 강도 (상/중/하)
3. 소형 채널이 진입 가능한 틈새 주제
4. 추천 영상 제목 3개
```

Grounding이 활성화된 제미나이는 이 프롬프트에 대해 **오늘 시점의 실시간 트렌드를 반영한 답변**을 제공한다. GPT나 Claude는 학습 데이터 시점까지의 정보만 활용할 수 있지만, 제미나이는 **지금 이 순간의 검색 트렌드**를 참조한다.

### 2. Google Workspace 애드온 생태계

제미나이는 구글 워크스페이스(Google Workspace)와의 통합이 점점 깊어지고 있다. 2026년 현재, 구글 스프레드시트 안에서 **사이드바로 제미나이를 호출**할 수 있으며, 이를 앱스 스크립트로 커스터마이징할 수 있다.

```javascript
// 스프레드시트 사이드바에서 Gemini 분석을 실행하는 코드
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('슈퍼유튜브시트')
    .addItem('AI 분석 실행', 'runAIAnalysis')
    .addItem('트렌드 리포트', 'generateTrendReport')
    .addItem('댓글 감성 분석', 'analyzeSentiment')
    .addToUi();
}

function runAIAnalysis() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = sheet.getDataRange().getValues();
  
  // 데이터를 Gemini에게 전달할 형태로 가공
  const summary = formatDataForAI(data);
  
  // Gemini API 호출
  const analysis = callGemini(
    '다음 유튜브 영상 데이터를 분석하고 인사이트를 도출해줘:\n\n'
    + summary
    + '\n\n분석 항목: 성과 패턴, 개선점, 다음 콘텐츠 추천'
  );
  
  // 결과를 새 시트에 기록
  writeAnalysisResult(analysis);
}
```

### 3. 멀티모달 분석 역량

제미나이의 멀티모달 기능은 **썸네일 분석**에서 진가를 발한다.

```
[프롬프트 - 썸네일 분석]

이 유튜브 썸네일 이미지를 분석해줘:
[이미지 첨부]

다음 항목을 평가해줘:
1. 텍스트 가독성 (1~10점)
2. 색상 대비 효과 (1~10점)
3. 감정 유발력 (1~10점)
4. 클릭 유도 요소 분석
5. 개선 제안 3가지
6. 비슷한 주제의 고성과 썸네일과 비교했을 때의 차이점
```

앱스 스크립트에서 YouTube Data API로 가져온 썸네일 URL을 제미나이에게 전달하고, **썸네일의 효과를 자동으로 분석**할 수 있다. 이것은 2026년 현재 어떤 유료 유튜브 도구에서도 제공하지 않는 기능이다.

---

## 제미나이 무료 가입하기

제미나이를 실제로 사용하기 위한 설정을 단계별로 진행해보자. 슈퍼유튜브시트에서 가장 많이 사용할 **Gemini 2.5 Flash**의 무료 API 키를 발급받는 것이 목표다.

### 단계 1: Google AI Studio 접속

1. 브라우저에서 **https://aistudio.google.com** 접속
2. 구글 계정으로 로그인 (유튜브 채널과 같은 계정 권장)
3. 서비스 약관 동의

> **팁**: 유튜브 채널과 같은 구글 계정을 사용하면 나중에 YouTube Data API 설정 시 편리하다.

### 단계 2: API 키 발급

1. Google AI Studio 좌측 메뉴에서 **"Get API Key"** 클릭
2. **"Create API Key"** 버튼 클릭
3. 프로젝트 선택 (기존 GCP 프로젝트가 있으면 선택, 없으면 새로 생성)
4. 생성된 API 키를 **안전한 곳에 복사해서 저장**

```
⚠️ API 키 보안 주의사항:
- API 키를 코드에 직접 하드코딩하지 말 것
- 앱스 스크립트에서는 반드시 PropertiesService를 사용할 것
- API 키를 GitHub 등 공개 저장소에 올리지 말 것
- 주기적으로 API 키를 갱신할 것
```

### 단계 3: API 키 테스트

Google AI Studio에서 바로 테스트할 수 있다.

1. Google AI Studio 메인 화면에서 **"Create new prompt"** 클릭
2. 모델을 **"Gemini 2.5 Flash"**로 선택
3. 다음 테스트 프롬프트 입력:

```
구글 앱스 스크립트로 현재 스프레드시트의 A1 셀에
"Hello, 슈퍼유튜브시트!"를 입력하는 코드를 작성해줘.
```

4. 응답이 정상적으로 오면 API 키가 정상 작동하는 것이다.

### 단계 4: 앱스 스크립트에 API 키 저장

발급받은 API 키를 앱스 스크립트에서 안전하게 사용하기 위해 **스크립트 속성(Script Properties)**에 저장한다.

```javascript
// 이 함수를 한 번만 실행해서 API 키를 저장한다
function setApiKeys() {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  // Gemini API 키 저장
  scriptProperties.setProperty(
    'GEMINI_API_KEY',
    '여기에_발급받은_API_키_입력'
  );
  
  Logger.log('API 키가 저장되었습니다.');
  
  // 저장 확인
  const saved = scriptProperties.getProperty('GEMINI_API_KEY');
  Logger.log('저장된 키 앞 10자: ' + saved.substring(0, 10) + '...');
}
```

**실행 방법:**
1. 구글 스프레드시트에서 **확장 프로그램 → Apps Script** 클릭
2. 위 코드를 에디터에 붙여넣기
3. `'여기에_발급받은_API_키_입력'` 부분을 실제 API 키로 교체
4. **실행** 버튼 클릭
5. 구글 계정 권한 승인
6. 실행 로그에서 "API 키가 저장되었습니다" 확인
7. **코드에서 API 키 문자열을 삭제** (보안을 위해)

### 단계 5: Gemini API 동작 확인

API 키가 앱스 스크립트에서 제대로 작동하는지 확인하는 테스트 함수를 실행한다.

```javascript
function testGeminiAPI() {
  const apiKey = PropertiesService.getScriptProperties()
    .getProperty('GEMINI_API_KEY');
  
  if (!apiKey) {
    Logger.log('❌ API 키가 설정되지 않았습니다. setApiKeys()를 먼저 실행하세요.');
    return;
  }
  
  const url = 'https://generativelanguage.googleapis.com/v1beta/models/'
    + 'gemini-2.5-flash:generateContent?key=' + apiKey;
  
  const payload = {
    contents: [{
      parts: [{
        text: '구글 앱스 스크립트에서 현재 날짜와 시간을 스프레드시트 A1 셀에 입력하는 코드를 작성해줘. 코드만 출력해줘.'
      }]
    }],
    generationConfig: {
      temperature: 0.2,
      maxOutputTokens: 1024
    }
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  try {
    const response = UrlFetchApp.fetch(url, options);
    const statusCode = response.getResponseCode();
    
    if (statusCode === 200) {
      const data = JSON.parse(response.getContentText());
      const generatedText = data.candidates[0].content.parts[0].text;
      Logger.log('✅ Gemini API 연동 성공!');
      Logger.log('생성된 코드:\n' + generatedText);
    } else {
      Logger.log('❌ API 오류 (상태 코드: ' + statusCode + ')');
      Logger.log('응답: ' + response.getContentText());
    }
  } catch (error) {
    Logger.log('❌ 요청 실패: ' + error.message);
  }
}
```

이 함수를 실행해서 "Gemini API 연동 성공!" 메시지가 나오면 모든 준비가 완료된 것이다.

---

## 프롬프트 엔지니어링: Apps Script 코드를 잘 뽑아내는 기술

바이브 코딩의 핵심은 결국 **프롬프트**다. 같은 AI라도 프롬프트를 어떻게 작성하느냐에 따라 결과물의 품질이 천차만별이다. 구글 앱스 스크립트 코드 생성에 특화된 프롬프트 엔지니어링 기법을 알아보자.

### 기법 1: 역할 지정 (Role Setting)

```
[프롬프트 템플릿]

너는 구글 앱스 스크립트(Google Apps Script) 전문 개발자야.
다음 조건을 반드시 지켜서 코드를 작성해줘:

1. 앱스 스크립트 V8 런타임 사용
2. const, let 사용 (var 사용 금지)
3. 화살표 함수 사용
4. JSDoc 주석으로 함수 설명 포함
5. 에러 핸들링(try-catch) 포함
6. Logger.log()로 실행 과정 로깅 포함

[여기에 구체적인 요청 작성]
```

### 기법 2: 출력 형식 지정 (Output Format)

```
[프롬프트 템플릿]

다음 기능을 하는 앱스 스크립트 코드를 작성해줘.

기능: [기능 설명]

출력 형식:
1. 완성된 코드를 코드 블록으로 제공
2. 코드 아래에 "사용법" 섹션 추가
   - 어떤 시트/셀에 데이터를 입력해야 하는지
   - 어떤 순서로 함수를 실행해야 하는지
3. "주의사항" 섹션 추가
   - API 쿼터 관련 주의사항
   - 실행 시간 제한 관련 주의사항
```

### 기법 3: 반복 개선 (Iterative Refinement)

한 번의 프롬프트로 완벽한 코드를 기대하지 마라. **대화를 통해 점진적으로 개선**하는 것이 바이브 코딩의 핵심이다.

```
[1차 프롬프트]
유튜브 키워드 검색 결과를 스프레드시트에 저장하는
앱스 스크립트를 만들어줘.

[2차 프롬프트 - 기능 추가]
잘 됐어! 이제 여기에 각 영상의 채널 구독자 수도
함께 가져오도록 수정해줘.

[3차 프롬프트 - 최적화]
잘 작동하는데, API 호출이 너무 많아.
영상 ID를 배치로 묶어서 한 번에 조회하도록 최적화해줘.

[4차 프롬프트 - 에러 처리]
가끔 에러가 나는데, 삭제된 영상이나 비공개 영상을
건너뛰도록 에러 처리를 추가해줘.

[5차 프롬프트 - UI 개선]
마지막으로 실행 중에 진행률을 토스트 메시지로
보여주는 기능을 추가해줘.
```

이런 반복 과정을 통해 **점점 완성도 높은 코드**가 만들어진다. 그리고 이 과정에서 **당신도 앱스 스크립트에 대한 이해가 깊어진다**. 이것이 바이브 코딩의 숨겨진 가치다.

### 실전 프롬프트 예제: 유튜브 영상 분석 함수

실제로 제미나이에게 보낼 수 있는, 바로 사용 가능한 프롬프트를 하나 제공한다.

```
너는 구글 앱스 스크립트 전문 개발자야.

다음 기능을 하는 함수를 만들어줘:

함수명: analyzeYouTubeVideos

입력:
- '분석' 시트의 A2:A 범위에 유튜브 영상 URL 또는 영상 ID가
  여러 개 입력되어 있음

처리:
1. 각 영상 ID에 대해 YouTube Data API v3의 videos.list 엔드포인트를
   호출해서 snippet, statistics, contentDetails 파트를 가져옴
2. 영상 ID는 최대 50개씩 배치로 묶어서 API를 호출해서 쿼터를 절약함
3. URL이 입력된 경우 영상 ID를 추출하는 로직 포함

출력 (B2 셀부터):
- B열: 영상 제목
- C열: 채널명
- D열: 조회수 (숫자 형식)
- E열: 좋아요 수
- F열: 댓글 수
- G열: 업로드 날짜 (YYYY-MM-DD 형식)
- H열: 영상 길이 (분:초 형식, ISO 8601 파싱)
- I열: 참여율 (좋아요+댓글)/조회수 * 100, 소수점 2자리)
- 첫 번째 행(1행)에 헤더를 자동으로 입력

환경:
- YouTube Data API 키: PropertiesService.getScriptProperties()
  .getProperty('YOUTUBE_API_KEY')
- 기존 B:I 열 데이터는 삭제 후 새로 작성
- V8 런타임, const/let 사용

제약사항:
- 앱스 스크립트 6분 실행 시간 제한 대비
- 빈 셀이나 잘못된 URL은 건너뛰기
- 에러 발생 시 해당 행에 에러 메시지 표시
- 실행 중 토스트 메시지로 진행률 표시
```

이 프롬프트를 제미나이에게 전달하면 **즉시 사용 가능한 완전한 코드**가 생성된다. 이것이 바이브 코딩의 위력이다.

다음 장에서는 이 모든 것의 기반이 되는 **구글 스프레드시트**의 핵심 기능을 알아본다. 스프레드시트를 단순한 표 도구가 아닌 **자동화 플랫폼**으로 활용하는 방법을 배울 것이다.
