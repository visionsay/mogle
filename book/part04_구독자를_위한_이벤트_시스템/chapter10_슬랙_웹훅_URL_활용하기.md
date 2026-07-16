# Chapter 10. 슬랙 웹훅 URL 활용하기

---

## 슬랙(Slack)이 뭔가요?

유튜브 채널을 운영하다 보면 "지금 내 채널에서 무슨 일이 일어나고 있는지"를 실시간으로 알고 싶을 때가 많습니다. 새 영상을 올리면 댓글이 달리고, 구독자 수가 변하고, 조회수가 오르내립니다. 이 모든 상황을 유튜브 스튜디오에 들어가서 하나하나 확인하는 것은 시간 낭비입니다.

슬랙(Slack)은 원래 기업에서 팀 커뮤니케이션을 위해 만들어진 메신저 서비스입니다. 하지만 유튜버인 여러분에게 슬랙이 중요한 이유는 따로 있습니다. 바로 **자동화 연동이 압도적으로 쉽다**는 점입니다.

"카카오톡이나 디스코드를 쓰면 안 되나요?"라고 물으실 수 있습니다. 물론 각각의 장단점이 있지만, 자동화 관점에서 슬랙을 선택하는 명확한 이유가 있습니다.

| 비교 항목 | 슬랙(Slack) | 카카오톡 | 디스코드 |
|-----------|------------|---------|---------|
| 웹훅 설정 난이도 | 매우 쉬움 (3분) | 불가능 (API 미제공) | 보통 (봇 필요) |
| 메시지 서식 | Block Kit (풍부) | 텍스트만 | Embed (보통) |
| 앱스 스크립트 연동 | `UrlFetchApp` 한 줄 | 불가 | 가능하나 복잡 |
| 메시지 전달 안정성 | 99.9% | - | 95%+ |
| 무료 사용 제한 | 90일 이전 메시지 열람 불가 | - | 거의 없음 |
| 채널별 분류 | 완벽 지원 | 제한적 | 지원 |

핵심은 **웹훅(Webhook)**입니다. 슬랙은 URL 하나만 있으면 외부에서 메시지를 보낼 수 있습니다. 구글 앱스 스크립트에서 `UrlFetchApp.fetch()` 한 줄이면 됩니다. 카카오톡은 이런 기능 자체가 없고, 디스코드는 봇을 만들고 토큰을 관리해야 하는 추가 작업이 필요합니다.

이 책에서 만들고 있는 **슈퍼유튜브시트**에 슬랙 알림 기능을 붙이면, 여러분은 스프레드시트를 열지 않아도 채널의 중요한 변화를 실시간으로 알 수 있게 됩니다.

---

## 슬랙 웹훅 URL이란?

### Incoming Webhooks의 개념

웹훅(Webhook)이란 "특정 이벤트가 발생했을 때 지정된 URL로 데이터를 보내는 방식"을 말합니다. 슬랙의 **Incoming Webhooks**는 이 개념을 가장 단순하게 구현한 것입니다.

작동 방식은 놀라울 정도로 간단합니다:

```
[앱스 스크립트] → HTTP POST 요청 → [슬랙 웹훅 URL] → [슬랙 채널에 메시지 표시]
```

일반적인 슬랙 앱을 만들려면 OAuth 인증, 봇 토큰 관리, 스코프 설정 등 복잡한 과정을 거쳐야 합니다. 하지만 Incoming Webhooks를 사용하면 이 모든 과정이 생략됩니다. 우리에게 필요한 것은 딱 하나, **웹훅 URL**뿐입니다.

웹훅 URL은 다음과 같은 형태입니다:

```
https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

이 URL로 JSON 형태의 데이터를 POST로 보내면, 해당 채널에 메시지가 나타납니다. OAuth 토큰도 필요 없고, 사용자 인증도 필요 없습니다. URL 자체가 인증 역할을 합니다.

### 보안 주의사항

웹훅 URL이 곧 인증입니다. 이 URL을 아는 사람은 누구나 해당 채널에 메시지를 보낼 수 있습니다. 따라서 **절대로 코드에 직접 하드코딩하지 마세요.** 이 책에서는 구글 앱스 스크립트의 `PropertiesService`를 사용하여 안전하게 저장하는 방법을 알려드립니다.

---

## 슬랙 웹훅 URL로 할 수 있는 일들

슈퍼유튜브시트와 슬랙을 연결하면 다음과 같은 자동 알림을 구현할 수 있습니다.

### 1. 새 영상 업로드 알림

영상을 업로드하면 슬랙에 자동으로 알림이 옵니다. 영상 제목, 썸네일, 링크가 포함된 카드 형태의 메시지를 받을 수 있습니다. "영상이 제대로 올라갔나?" 하고 유튜브에 다시 들어갈 필요가 없어집니다.

### 2. 댓글 이벤트 당첨자 알림

11장에서 만들 댓글 이벤트 시스템과 연동하면, 새로운 참여자가 폼을 작성할 때마다 실시간 알림을 받을 수 있습니다. 당첨자가 선정되면 당첨 결과도 슬랙으로 바로 확인할 수 있습니다.

### 3. 채널 성과 일일 리포트

매일 정해진 시간에 어제의 채널 성과를 요약해서 보내줍니다. 총 조회수, 신규 구독자, 인기 영상 TOP 3, 새로 달린 댓글 수 등을 한눈에 볼 수 있습니다. 커피 한 잔 마시면서 슬랙 알림만 확인하면 됩니다.

### 4. 구독자 수 마일스톤 알림

구독자 수가 100명, 500명, 1,000명, 10,000명 등 의미 있는 숫자를 달성하면 축하 알림을 보내줍니다. 소소하지만 채널 성장의 기쁨을 놓치지 않을 수 있습니다.

### 5. 경쟁 채널 신규 영상 감지

벤치마킹하는 채널이 새 영상을 올리면 알림을 받을 수 있습니다. 트렌드를 놓치지 않고 빠르게 대응할 수 있는 강력한 기능입니다.

이번 장에서는 이 모든 알림의 기반이 되는 **슬랙 연동 인프라**를 구축합니다. 각각의 구체적인 알림 기능은 이후 장에서 하나씩 구현해 나갈 것입니다.

---

## [바로 실습] 슬랙 계정과 워크스페이스 생성하기

### 1단계: 슬랙 가입

1. 브라우저에서 [https://slack.com](https://slack.com)에 접속합니다.
2. 우측 상단의 **시작하기** 버튼을 클릭합니다.
3. 구글 계정으로 간편 가입하거나, 이메일로 직접 가입합니다.
   - 구글 계정 가입을 추천합니다. 앱스 스크립트에서 사용하는 구글 계정과 동일한 계정을 사용하면 관리가 편합니다.

### 2단계: 워크스페이스 생성

1. 로그인 후 **워크스페이스 생성** 화면이 나타납니다.
2. 워크스페이스 이름을 입력합니다:
   - 추천 이름: `내유튜브알림`, `유튜브자동화`, 또는 여러분의 채널명을 사용하세요.
   - 예: `크리에이터대시보드`
3. "이 워크스페이스는 어떤 팀에서 사용하나요?" 질문에는 **개인 사용**을 선택합니다.
4. 팀원 초대 화면이 나오면 **나중에**를 선택하고 건너뜁니다.

워크스페이스가 생성되면 기본 채널인 `#general`과 `#random`이 자동으로 만들어져 있습니다.

> **팁:** 슬랙 무료 플랜은 90일이 지난 메시지를 열람할 수 없지만, 알림 용도로는 최근 메시지만 중요하므로 무료 플랜으로 충분합니다.

---

## [바로 실습] 채널 만들기

유튜브 자동화 알림을 체계적으로 관리하려면 목적별로 채널을 분리하는 것이 좋습니다.

### 채널 생성 방법

1. 슬랙 좌측 사이드바에서 **채널** 옆의 **+** 버튼을 클릭합니다.
2. **채널 만들기**를 선택합니다.
3. 다음 세 개의 채널을 만듭니다:

#### 채널 1: #영상알림
- **이름:** `영상알림`
- **설명:** 새 영상 업로드, 영상 성과 관련 알림
- **공개/비공개:** 비공개 (본인만 사용하므로)

#### 채널 2: #댓글이벤트
- **이름:** `댓글이벤트`
- **설명:** 구독자 이벤트 참여, 당첨자 선정 알림
- **공개/비공개:** 비공개

#### 채널 3: #채널리포트
- **이름:** `채널리포트`
- **설명:** 일일 채널 성과 요약 리포트
- **공개/비공개:** 비공개

생성이 완료되면 좌측 사이드바에 세 개의 채널이 표시됩니다. 각 채널마다 별도의 웹훅 URL을 연결하면, 알림 종류별로 깔끔하게 분류된 알림 시스템이 완성됩니다.

---

## [바로 실습] 슬랙 웹훅 생성하기

이제 핵심입니다. 슬랙 앱을 만들고 웹훅 URL을 발급받겠습니다.

### 1단계: 슬랙 앱 생성

1. 브라우저에서 [https://api.slack.com/apps](https://api.slack.com/apps)에 접속합니다.
2. 우측 상단의 **Create New App** 버튼을 클릭합니다.
3. **From scratch**를 선택합니다.
4. 앱 정보를 입력합니다:
   - **App Name:** `슈퍼유튜브시트 알림봇` (또는 원하는 이름)
   - **Pick a workspace to develop your app in:** 방금 만든 워크스페이스를 선택합니다.
5. **Create App** 버튼을 클릭합니다.

### 2단계: Incoming Webhooks 활성화

1. 앱 설정 페이지의 좌측 메뉴에서 **Incoming Webhooks**를 클릭합니다.
2. 우측 상단의 토글 스위치를 **On**으로 변경합니다.
3. 페이지 하단의 **Add New Webhook to Workspace** 버튼을 클릭합니다.
4. 웹훅을 연결할 채널을 선택합니다:
   - 먼저 `#영상알림` 채널을 선택합니다.
5. **허용** 버튼을 클릭합니다.

### 3단계: 웹훅 URL 확인 및 복사

허용 후 페이지에 웹훅 URL이 생성됩니다:

```
https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

이 URL을 복사해두세요. 나머지 채널(`#댓글이벤트`, `#채널리포트`)에 대해서도 **Add New Webhook to Workspace**를 반복하여 각각의 웹훅 URL을 발급받습니다.

> **중요:** 하나의 슬랙 앱에서 여러 채널에 대한 웹훅을 생성할 수 있습니다. 채널별로 앱을 따로 만들 필요가 없습니다.

### 4단계: 웹훅 URL을 PropertiesService에 저장

웹훅 URL을 코드에 직접 넣으면 보안 위험이 있습니다. 구글 앱스 스크립트의 `PropertiesService`를 사용하여 안전하게 저장합니다.

슈퍼유튜브시트의 앱스 스크립트 편집기를 열고 다음 함수를 실행하세요:

```javascript
/**
 * 슬랙 웹훅 URL을 PropertiesService에 안전하게 저장합니다.
 * 이 함수는 최초 1회만 실행하면 됩니다.
 */
function setupSlackWebhooks() {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  // 각 채널의 웹훅 URL을 여기에 붙여넣으세요
  scriptProperties.setProperties({
    'SLACK_WEBHOOK_VIDEO':   'https://hooks.slack.com/services/여기에/영상알림/웹훅URL',
    'SLACK_WEBHOOK_EVENT':   'https://hooks.slack.com/services/여기에/댓글이벤트/웹훅URL',
    'SLACK_WEBHOOK_REPORT':  'https://hooks.slack.com/services/여기에/채널리포트/웹훅URL'
  });
  
  Logger.log('슬랙 웹훅 URL이 안전하게 저장되었습니다.');
  Logger.log('저장된 키 목록: ' + Object.keys(scriptProperties.getProperties()).join(', '));
}
```

**실행 방법:**

1. 함수 내의 URL 세 개를 실제 발급받은 웹훅 URL로 교체합니다.
2. 함수 선택 드롭다운에서 `setupSlackWebhooks`를 선택합니다.
3. **실행** 버튼을 클릭합니다.
4. 실행 로그에서 "슬랙 웹훅 URL이 안전하게 저장되었습니다." 메시지를 확인합니다.

한번 저장하면 이후에는 코드에서 `PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_VIDEO')` 형태로 불러와서 사용할 수 있습니다. 실제 URL은 코드에 노출되지 않으므로 GitHub 등에 코드를 공유해도 안전합니다.

> **실행 후 꼭 해야 할 일:** `setupSlackWebhooks` 함수 내의 실제 URL 문자열을 코드에서 삭제하거나, 함수 자체를 삭제하세요. PropertiesService에 저장된 값은 함수를 삭제해도 유지됩니다.

---

## [바로 실습] 테스트 메시지 보내기

### 기본 메시지 전송 함수

먼저 슬랙으로 메시지를 보내는 핵심 함수를 만들겠습니다. 이 함수는 이후 모든 알림 기능의 기반이 됩니다.

```javascript
/**
 * 슬랙 채널로 Block Kit 형식의 메시지를 전송합니다.
 * @param {string} webhookUrl - 슬랙 웹훅 URL
 * @param {string} message - 전송할 메시지 (마크다운 지원)
 * @param {string} [headerText] - 헤더 텍스트 (선택)
 */
function sendSlackMessage(webhookUrl, message, headerText) {
  const blocks = [];
  
  // 헤더 블록 (선택적)
  if (headerText) {
    blocks.push({
      type: 'header',
      text: {
        type: 'plain_text',
        text: headerText,
        emoji: true
      }
    });
  }
  
  // 본문 블록
  blocks.push({
    type: 'section',
    text: {
      type: 'mrkdwn',
      text: message
    }
  });
  
  // 구분선
  blocks.push({ type: 'divider' });
  
  // 타임스탬프 컨텍스트
  blocks.push({
    type: 'context',
    elements: [
      {
        type: 'mrkdwn',
        text: `📅 ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })} | 슈퍼유튜브시트`
      }
    ]
  });
  
  const payload = {
    blocks: blocks,
    text: message  // 블록 렌더링이 안 될 때의 폴백 텍스트
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(webhookUrl, options);
  const responseCode = response.getResponseCode();
  
  if (responseCode !== 200) {
    Logger.log('슬랙 메시지 전송 실패: ' + response.getContentText());
    throw new Error('슬랙 메시지 전송 실패 (HTTP ' + responseCode + ')');
  }
  
  Logger.log('슬랙 메시지 전송 성공');
  return true;
}
```

### 테스트 실행

다음 함수를 실행하여 연동이 정상적으로 되었는지 확인합니다:

```javascript
/**
 * 슬랙 웹훅 연동 테스트
 */
function testSlackWebhook() {
  const webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_VIDEO');
  
  if (!webhookUrl) {
    Logger.log('에러: 웹훅 URL이 설정되지 않았습니다. setupSlackWebhooks()를 먼저 실행하세요.');
    return;
  }
  
  sendSlackMessage(
    webhookUrl,
    '✅ *슬랙 연동 테스트 성공!*\n\n슈퍼유튜브시트가 슬랙과 정상적으로 연결되었습니다.\n이제 유튜브 채널의 다양한 알림을 실시간으로 받을 수 있습니다.',
    '🎬 슈퍼유튜브시트 알림'
  );
}
```

`testSlackWebhook`을 실행하면, 슬랙의 `#영상알림` 채널에 테스트 메시지가 나타납니다. 헤더, 본문, 구분선, 타임스탬프가 깔끔하게 정렬된 메시지를 확인할 수 있습니다.

> **문제 해결:** 메시지가 오지 않는다면:
> 1. 웹훅 URL이 정확히 복사되었는지 확인하세요.
> 2. `setupSlackWebhooks()` 실행 후 URL을 제대로 저장했는지 확인하세요.
> 3. 슬랙 앱에서 Incoming Webhooks가 **On** 상태인지 확인하세요.
> 4. 실행 로그에서 에러 메시지를 확인하세요.

---

## Block Kit으로 풍부한 메시지 만들기

슬랙의 Block Kit은 메시지를 구조화된 블록 단위로 구성하는 프레임워크입니다. 단순한 텍스트 메시지가 아니라, 헤더, 이미지, 버튼, 필드 등을 조합하여 시각적으로 우수한 알림을 만들 수 있습니다.

### Block Kit의 주요 블록 타입

```javascript
// 1. Header 블록 - 큰 굵은 텍스트
{ type: 'header', text: { type: 'plain_text', text: '제목', emoji: true } }

// 2. Section 블록 - 본문 텍스트 (마크다운 지원)
{ type: 'section', text: { type: 'mrkdwn', text: '*굵게* _기울임_ ~취소선~' } }

// 3. Section + Fields - 2열 레이아웃
{
  type: 'section',
  fields: [
    { type: 'mrkdwn', text: '*조회수:*\n12,345' },
    { type: 'mrkdwn', text: '*좋아요:*\n890' }
  ]
}

// 4. Image 블록 - 이미지 표시
{ type: 'image', image_url: 'https://...', alt_text: '썸네일' }

// 5. Divider 블록 - 구분선
{ type: 'divider' }

// 6. Context 블록 - 작은 보조 텍스트
{
  type: 'context',
  elements: [{ type: 'mrkdwn', text: '📅 2026-06-27 14:30' }]
}

// 7. Actions 블록 - 버튼
{
  type: 'actions',
  elements: [{
    type: 'button',
    text: { type: 'plain_text', text: '영상 보기', emoji: true },
    url: 'https://youtube.com/watch?v=...',
    style: 'primary'
  }]
}
```

### 영상 카드 형태 메시지 함수

새 영상이 업로드되었을 때 보내는 풍부한 카드 형태의 알림입니다:

```javascript
/**
 * 새 영상 업로드 알림을 카드 형태로 슬랙에 전송합니다.
 * @param {Object} videoInfo - 영상 정보 객체
 * @param {string} videoInfo.title - 영상 제목
 * @param {string} videoInfo.videoId - 유튜브 영상 ID
 * @param {string} videoInfo.thumbnail - 썸네일 URL
 * @param {string} videoInfo.description - 영상 설명 (첫 100자)
 * @param {string} videoInfo.publishedAt - 게시 일시
 * @param {string} videoInfo.duration - 영상 길이
 */
function sendVideoCardNotification(videoInfo) {
  const webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_VIDEO');
  const videoUrl = 'https://www.youtube.com/watch?v=' + videoInfo.videoId;
  
  const payload = {
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: '🎬 새 영상이 업로드되었습니다!',
          emoji: true
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*<${videoUrl}|${videoInfo.title}>*\n\n${videoInfo.description}`
        },
        accessory: {
          type: 'image',
          image_url: videoInfo.thumbnail,
          alt_text: videoInfo.title
        }
      },
      {
        type: 'section',
        fields: [
          {
            type: 'mrkdwn',
            text: `*📅 게시일:*\n${videoInfo.publishedAt}`
          },
          {
            type: 'mrkdwn',
            text: `*⏱️ 영상 길이:*\n${videoInfo.duration}`
          }
        ]
      },
      { type: 'divider' },
      {
        type: 'actions',
        elements: [
          {
            type: 'button',
            text: {
              type: 'plain_text',
              text: '▶️ 영상 보기',
              emoji: true
            },
            url: videoUrl,
            style: 'primary'
          },
          {
            type: 'button',
            text: {
              type: 'plain_text',
              text: '📊 유튜브 스튜디오',
              emoji: true
            },
            url: 'https://studio.youtube.com/video/' + videoInfo.videoId + '/analytics',
          }
        ]
      },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: `📡 슈퍼유튜브시트 자동 알림 | ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}`
          }
        ]
      }
    ],
    text: `새 영상: ${videoInfo.title} - ${videoUrl}`  // 폴백 텍스트
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(webhookUrl, options);
  
  if (response.getResponseCode() !== 200) {
    Logger.log('영상 카드 전송 실패: ' + response.getContentText());
    return false;
  }
  
  Logger.log('영상 카드 전송 성공: ' + videoInfo.title);
  return true;
}
```

### 테스트용 영상 카드 전송

실제 데이터 없이도 카드 형태를 테스트해볼 수 있습니다:

```javascript
/**
 * 영상 카드 알림 테스트
 */
function testVideoCardNotification() {
  sendVideoCardNotification({
    title: '[테스트] 구글 시트로 유튜브 자동화하는 방법',
    videoId: 'dQw4w9WgXcQ',
    thumbnail: 'https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
    description: '구글 스프레드시트와 앱스 스크립트를 활용하여 유튜브 채널을 자동 관리하는 방법을 알아봅니다...',
    publishedAt: '2026-06-27 14:00',
    duration: '15:32'
  });
}
```

이 함수를 실행하면 슬랙에 썸네일 이미지, 영상 제목(클릭 가능한 링크), 게시일, 영상 길이, 그리고 "영상 보기"와 "유튜브 스튜디오" 버튼이 포함된 멋진 카드가 나타납니다.

---

## 채널 성과 리포트 메시지

일일 리포트처럼 여러 항목의 데이터를 보기 좋게 전송하는 함수도 만들어봅시다:

```javascript
/**
 * 채널 일일 성과 리포트를 슬랙으로 전송합니다.
 * @param {Object} report - 리포트 데이터
 * @param {number} report.totalViews - 일일 총 조회수
 * @param {number} report.newSubscribers - 신규 구독자 수
 * @param {number} report.totalSubscribers - 총 구독자 수
 * @param {number} report.newComments - 새 댓글 수
 * @param {Array} report.topVideos - 인기 영상 TOP 3 [{title, views, videoId}]
 */
function sendDailyReport(report) {
  const webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_REPORT');
  
  const today = new Date();
  const dateStr = `${today.getFullYear()}년 ${today.getMonth() + 1}월 ${today.getDate()}일`;
  
  // 구독자 변화 표시
  const subChange = report.newSubscribers >= 0 
    ? `+${report.newSubscribers} 📈` 
    : `${report.newSubscribers} 📉`;
  
  // 인기 영상 목록 생성
  let topVideoText = '';
  if (report.topVideos && report.topVideos.length > 0) {
    topVideoText = report.topVideos.map((v, i) => {
      const medal = ['🥇', '🥈', '🥉'][i] || '▪️';
      const url = `https://www.youtube.com/watch?v=${v.videoId}`;
      return `${medal} <${url}|${v.title}> (${v.views.toLocaleString()}회)`;
    }).join('\n');
  }
  
  const payload = {
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: `📊 ${dateStr} 채널 리포트`,
          emoji: true
        }
      },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: `*👁️ 일일 조회수*\n${report.totalViews.toLocaleString()}회` },
          { type: 'mrkdwn', text: `*👥 총 구독자*\n${report.totalSubscribers.toLocaleString()}명 (${subChange})` },
          { type: 'mrkdwn', text: `*💬 새 댓글*\n${report.newComments.toLocaleString()}개` },
          { type: 'mrkdwn', text: `*📈 일일 시청 시간*\n${report.watchTimeHours || '-'}시간` }
        ]
      },
      { type: 'divider' },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: `*🏆 오늘의 인기 영상 TOP 3*\n\n${topVideoText}`
        }
      },
      { type: 'divider' },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: `📡 슈퍼유튜브시트 자동 리포트 | ${new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })}`
          }
        ]
      }
    ],
    text: `${dateStr} 채널 리포트: 조회수 ${report.totalViews}회, 구독자 ${report.totalSubscribers}명`
  };
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(webhookUrl, options);
  
  if (response.getResponseCode() !== 200) {
    Logger.log('일일 리포트 전송 실패: ' + response.getContentText());
    return false;
  }
  
  Logger.log('일일 리포트 전송 성공');
  return true;
}
```

### 리포트 테스트

```javascript
/**
 * 일일 리포트 전송 테스트
 */
function testDailyReport() {
  sendDailyReport({
    totalViews: 15420,
    newSubscribers: 23,
    totalSubscribers: 4567,
    newComments: 89,
    watchTimeHours: 1240,
    topVideos: [
      { title: '초보 유튜버가 꼭 알아야 할 10가지', views: 3210, videoId: 'abc123' },
      { title: '영상 편집 꿀팁 모음', views: 2150, videoId: 'def456' },
      { title: '구독자 1000명 달성 후기', views: 1890, videoId: 'ghi789' }
    ]
  });
}
```

---

## 에러 핸들링과 재시도 로직

실제 운영 환경에서는 네트워크 오류, 슬랙 서버 장애 등으로 메시지 전송이 실패할 수 있습니다. 안정적인 알림 시스템을 위해 재시도 로직을 추가합니다:

```javascript
/**
 * 재시도 로직이 포함된 슬랙 메시지 전송 함수
 * @param {string} webhookUrl - 웹훅 URL
 * @param {Object} payload - 전송할 페이로드
 * @param {number} [maxRetries=3] - 최대 재시도 횟수
 * @returns {boolean} 전송 성공 여부
 */
function sendSlackWithRetry(webhookUrl, payload, maxRetries) {
  maxRetries = maxRetries || 3;
  
  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = UrlFetchApp.fetch(webhookUrl, options);
      const responseCode = response.getResponseCode();
      
      if (responseCode === 200) {
        Logger.log('슬랙 전송 성공 (시도 ' + attempt + '/' + maxRetries + ')');
        return true;
      }
      
      // 429 Too Many Requests - 속도 제한
      if (responseCode === 429) {
        const retryAfter = parseInt(response.getHeaders()['Retry-After'] || '5', 10);
        Logger.log('슬랙 속도 제한. ' + retryAfter + '초 후 재시도...');
        Utilities.sleep(retryAfter * 1000);
        continue;
      }
      
      // 기타 서버 에러 (5xx)
      if (responseCode >= 500) {
        Logger.log('슬랙 서버 에러 (' + responseCode + '). 재시도 ' + attempt + '/' + maxRetries);
        Utilities.sleep(2000 * attempt);  // 점진적 대기
        continue;
      }
      
      // 4xx 에러 (웹훅 URL 오류 등) - 재시도 무의미
      Logger.log('슬랙 전송 실패 (HTTP ' + responseCode + '): ' + response.getContentText());
      return false;
      
    } catch (e) {
      Logger.log('네트워크 에러 (시도 ' + attempt + '/' + maxRetries + '): ' + e.message);
      if (attempt < maxRetries) {
        Utilities.sleep(2000 * attempt);
      }
    }
  }
  
  Logger.log('슬랙 전송 최종 실패: 최대 재시도 횟수 초과');
  return false;
}
```

이 함수는 다음과 같은 상황을 처리합니다:

- **429 (Too Many Requests):** 슬랙의 속도 제한에 걸렸을 때, `Retry-After` 헤더 값만큼 대기 후 재시도합니다.
- **5xx (서버 에러):** 슬랙 서버에 일시적 문제가 있을 때, 점진적으로 대기 시간을 늘려가며 재시도합니다.
- **4xx (클라이언트 에러):** 웹훅 URL이 잘못되었거나 비활성화된 경우로, 재시도해도 의미가 없으므로 즉시 실패를 반환합니다.
- **네트워크 에러:** 인터넷 연결 문제 등으로 요청 자체가 실패한 경우 재시도합니다.

---

## 슬랙 알림 유틸리티 모음

앞서 만든 함수들을 통합하여, 슈퍼유튜브시트 전체에서 공통으로 사용할 슬랙 유틸리티 모듈을 완성합니다:

```javascript
/**
 * ============================================
 * 슬랙 알림 유틸리티 (SlackUtils.gs)
 * 슈퍼유튜브시트 - 슬랙 연동 공통 모듈
 * ============================================
 */

/** 웹훅 키 상수 */
var SLACK_KEYS = {
  VIDEO:  'SLACK_WEBHOOK_VIDEO',
  EVENT:  'SLACK_WEBHOOK_EVENT',
  REPORT: 'SLACK_WEBHOOK_REPORT'
};

/**
 * 지정된 키에 해당하는 슬랙 웹훅 URL을 반환합니다.
 * @param {string} key - SLACK_KEYS의 값
 * @returns {string|null} 웹훅 URL
 */
function getSlackWebhookUrl(key) {
  var url = PropertiesService.getScriptProperties().getProperty(key);
  if (!url) {
    Logger.log('경고: 슬랙 웹훅 URL이 설정되지 않았습니다. 키: ' + key);
  }
  return url;
}

/**
 * 간단한 텍스트 알림을 슬랙에 전송합니다.
 * @param {string} channelKey - SLACK_KEYS 값 (VIDEO, EVENT, REPORT)
 * @param {string} text - 메시지 텍스트
 * @param {string} [header] - 헤더 (선택)
 */
function notifySlack(channelKey, text, header) {
  var url = getSlackWebhookUrl(channelKey);
  if (!url) return false;
  
  return sendSlackMessage(url, text, header);
}

/**
 * 구독자 수 마일스톤 알림을 전송합니다.
 * @param {number} currentSubs - 현재 구독자 수
 * @param {number} milestone - 달성한 마일스톤 (예: 1000, 5000, 10000)
 */
function sendMilestoneNotification(currentSubs, milestone) {
  var webhookUrl = getSlackWebhookUrl(SLACK_KEYS.VIDEO);
  if (!webhookUrl) return false;
  
  var milestoneText = milestone.toLocaleString();
  
  var payload = {
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: '🎉🎊 구독자 ' + milestoneText + '명 달성!',
          emoji: true
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '축하합니다! 채널 구독자가 *' + milestoneText + '명*을 돌파했습니다!\n\n' +
                '현재 구독자 수: *' + currentSubs.toLocaleString() + '명*\n\n' +
                '꾸준히 성장하고 있는 채널, 앞으로도 화이팅입니다! 💪'
        }
      },
      { type: 'divider' },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: '📡 슈퍼유튜브시트 마일스톤 알림 | ' + new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
          }
        ]
      }
    ],
    text: '구독자 ' + milestoneText + '명 달성!'
  };
  
  return sendSlackWithRetry(webhookUrl, payload);
}

/**
 * 경쟁 채널 신규 영상 감지 알림을 전송합니다.
 * @param {string} channelName - 경쟁 채널명
 * @param {string} videoTitle - 영상 제목
 * @param {string} videoUrl - 영상 URL
 */
function sendCompetitorVideoAlert(channelName, videoTitle, videoUrl) {
  var webhookUrl = getSlackWebhookUrl(SLACK_KEYS.VIDEO);
  if (!webhookUrl) return false;
  
  var payload = {
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: '🔍 경쟁 채널 새 영상 감지',
          emoji: true
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*채널:* ' + channelName + '\n*영상:* <' + videoUrl + '|' + videoTitle + '>'
        }
      },
      {
        type: 'actions',
        elements: [
          {
            type: 'button',
            text: { type: 'plain_text', text: '영상 확인하기', emoji: true },
            url: videoUrl,
            style: 'primary'
          }
        ]
      },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: '📡 슈퍼유튜브시트 경쟁 채널 모니터링 | ' + new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
          }
        ]
      }
    ],
    text: channelName + ' 새 영상: ' + videoTitle
  };
  
  return sendSlackWithRetry(webhookUrl, payload);
}
```

---

## 슬랙 메시지 디자인 팁

### 마크다운 문법

슬랙의 마크다운은 일반 마크다운과 약간 다릅니다:

| 서식 | 슬랙 문법 | 일반 마크다운 |
|------|-----------|-------------|
| 굵게 | `*텍스트*` | `**텍스트**` |
| 기울임 | `_텍스트_` | `*텍스트*` |
| 취소선 | `~텍스트~` | `~~텍스트~~` |
| 코드 | `` `텍스트` `` | `` `텍스트` `` |
| 코드 블록 | ` ```텍스트``` ` | ` ```텍스트``` ` |
| 링크 | `<URL\|표시텍스트>` | `[표시텍스트](URL)` |
| 목록 | `• 항목` 또는 `1. 항목` | `- 항목` 또는 `1. 항목` |
| 인용 | `> 텍스트` | `> 텍스트` |

### Block Kit Builder 활용

슬랙은 메시지 레이아웃을 시각적으로 설계할 수 있는 도구를 제공합니다:

1. [Block Kit Builder](https://app.slack.com/block-kit-builder)에 접속합니다.
2. 좌측에서 블록을 드래그하여 배치합니다.
3. 미리보기로 결과를 확인합니다.
4. 우측의 JSON을 복사하여 앱스 스크립트의 `payload.blocks`에 붙여넣습니다.

복잡한 레이아웃을 만들 때는 코드로 직접 작성하는 것보다 Block Kit Builder에서 먼저 디자인하고 코드를 가져오는 것이 훨씬 효율적입니다.

### 이모지 활용 가이드

슬랙의 이모지를 활용하면 메시지의 가독성이 크게 향상됩니다. 유튜브 자동화에서 자주 사용할 이모지를 정리합니다:

```
📊 리포트/통계      🎬 영상 관련       👥 구독자 관련
📈 증가/성장        🆕 새 영상         🎉 축하/이벤트
📉 감소             ▶️ 재생            🏆 랭킹/순위
💬 댓글             🔔 알림            ⚠️ 경고/주의
✅ 완료/성공        ❌ 실패            📅 날짜/일정
👁️ 조회수           ❤️ 좋아요          🔍 모니터링/검색
```

---

## 트리거를 이용한 자동 알림 설정

지금까지 만든 함수들을 수동으로 실행하는 것이 아니라, 시간 기반 트리거로 자동 실행되도록 설정합니다:

```javascript
/**
 * 슬랙 알림 관련 트리거를 설정합니다.
 * 이 함수는 최초 1회만 실행하면 됩니다.
 */
function setupSlackTriggers() {
  // 기존 슬랙 관련 트리거 제거
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    var funcName = trigger.getHandlerFunction();
    if (funcName === 'scheduledDailyReport' || funcName === 'checkSubscriberMilestone') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 매일 아침 9시에 일일 리포트 전송
  ScriptApp.newTrigger('scheduledDailyReport')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
  
  // 6시간마다 구독자 마일스톤 체크
  ScriptApp.newTrigger('checkSubscriberMilestone')
    .timeBased()
    .everyHours(6)
    .create();
  
  Logger.log('슬랙 알림 트리거가 설정되었습니다.');
  Logger.log('- 일일 리포트: 매일 오전 9시');
  Logger.log('- 마일스톤 체크: 6시간마다');
}

/**
 * 트리거에 의해 자동 실행되는 일일 리포트 함수
 */
function scheduledDailyReport() {
  try {
    // 여기에 YouTube Data API에서 데이터를 가져오는 코드를 연결합니다.
    // Part 03에서 만든 함수들을 활용하세요.
    var report = collectDailyStats();  // Part 03에서 구현한 함수
    sendDailyReport(report);
  } catch (e) {
    Logger.log('일일 리포트 생성 실패: ' + e.message);
    // 에러 발생 시에도 알림
    notifySlack(SLACK_KEYS.REPORT, '⚠️ *일일 리포트 생성 실패*\n에러: ' + e.message, '🚨 시스템 경고');
  }
}
```

---

## 마무리: 슬랙 연동 체크리스트

이번 장에서 완성한 내용을 정리합니다:

| 항목 | 완료 여부 확인 |
|------|-------------|
| 슬랙 워크스페이스 생성 | ☐ |
| #영상알림 채널 생성 | ☐ |
| #댓글이벤트 채널 생성 | ☐ |
| #채널리포트 채널 생성 | ☐ |
| 슬랙 앱 생성 및 Incoming Webhooks 활성화 | ☐ |
| 3개 채널에 웹훅 URL 발급 | ☐ |
| PropertiesService에 웹훅 URL 저장 | ☐ |
| 테스트 메시지 전송 성공 | ☐ |
| 영상 카드 알림 테스트 성공 | ☐ |
| 일일 리포트 테스트 성공 | ☐ |

이 장에서 구축한 슬랙 알림 인프라는 단순한 메시지 전송 기능이 아닙니다. 재시도 로직, 에러 핸들링, 채널별 분류, Block Kit을 활용한 풍부한 메시지 포맷까지 갖춘 **프로덕션 수준의 알림 시스템**입니다.

다음 11장에서는 이 슬랙 알림 시스템을 활용하여 **구독자 댓글 이벤트 자동화**를 구현합니다. 구글 폼으로 참여를 받고, 댓글을 대조 확인하고, 당첨자를 선정하고, 메일을 발송하고, 그 모든 과정을 슬랙으로 실시간 모니터링하는 완전 자동화 시스템을 만들어보겠습니다.
