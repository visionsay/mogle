# Chapter 11. 구독자 댓글 이벤트 자동화하기

---

유튜브 채널을 운영하면서 구독자와의 소통을 강화하는 가장 효과적인 방법 중 하나가 **댓글 이벤트**입니다. "이 영상에 댓글을 남겨주시면 추첨을 통해 기프티콘을 드립니다!" 같은 이벤트는 댓글 수를 폭발적으로 늘리고, 유튜브 알고리즘에서 긍정적인 시그널로 작용합니다.

하지만 수동으로 댓글 이벤트를 운영하면 고통스러운 작업의 연속입니다. 댓글을 하나하나 확인하고, 중복 참여를 걸러내고, 랜덤 추첨을 하고, 당첨자에게 개별적으로 연락하는 과정이 필요합니다. 구독자가 많아질수록 이 작업은 사실상 불가능에 가까워집니다.

이번 장에서는 이 전 과정을 자동화합니다. 구글 폼으로 참여를 받고, 실제 댓글을 자동 수집하여 대조 검증하고, 조건을 충족한 참여자 중에서 랜덤 추첨을 진행하고, 당첨자에게 자동으로 이메일을 발송하고, 모든 과정을 슬랙으로 실시간 모니터링하는 **완전 자동화 댓글 이벤트 시스템**을 만듭니다.

---

## 구글 폼 기본 사용법

구글 폼(Google Forms)은 설문지와 양식을 만드는 구글의 무료 서비스입니다. 유튜브 댓글 이벤트에서 구글 폼을 활용하는 이유는 명확합니다:

### 왜 구글 폼을 사용하는가?

1. **응답이 자동으로 스프레드시트에 기록됩니다.** 구글 폼의 응답은 연결된 구글 스프레드시트에 실시간으로 저장됩니다. 별도의 데이터 수집 코드를 작성할 필요가 없습니다.

2. **폼 제출 트리거를 사용할 수 있습니다.** 누군가 폼을 제출하면 자동으로 앱스 스크립트 함수를 실행할 수 있습니다. 새 참여자가 등록되는 즉시 슬랙 알림을 보내거나, 즉시 댓글 검증을 수행할 수 있습니다.

3. **입력 유효성 검사가 내장되어 있습니다.** 이메일 형식 검증, 필수 항목 체크, URL 형식 검증 등을 코드 없이 설정할 수 있습니다.

4. **앱스 스크립트로 폼 자체를 프로그래밍 방식으로 생성할 수 있습니다.** FormApp 서비스를 사용하면 코드로 폼을 만들고 설정할 수 있어, 이벤트를 반복적으로 진행할 때 매번 수동으로 폼을 만들 필요가 없습니다.

### 구글 폼 + 앱스 스크립트 자동화 흐름

```
[구독자] → 영상에 댓글 작성 → 구글 폼에 참여 정보 입력
                                    ↓
                           [폼 제출 트리거 발동]
                                    ↓
                           슬랙에 새 참여 알림 전송
                                    ↓
                      YouTube API로 실제 댓글 존재 확인
                                    ↓
                           검증 결과를 시트에 기록
                                    ↓
                    이벤트 종료 시 조건 충족자 중 랜덤 추첨
                                    ↓
                         당첨자에게 자동 이메일 발송
                                    ↓
                         슬랙에 당첨 결과 리포트 전송
```

---

## [바로 실습] 구글 폼 자동 생성하기

매번 구글 폼 UI에서 클릭하며 폼을 만드는 대신, 앱스 스크립트로 폼을 자동 생성합니다. 이벤트를 반복적으로 진행할 때 이 함수 하나만 실행하면 됩니다.

```javascript
/**
 * 댓글 이벤트 참여용 구글 폼을 자동 생성합니다.
 * @param {string} [eventTitle] - 이벤트 제목 (선택)
 * @param {string} [videoUrl] - 이벤트 대상 영상 URL (선택)
 * @returns {Object} 생성된 폼 정보 { formUrl, editUrl, formId }
 */
function createEventForm(eventTitle, videoUrl) {
  // 기본값 설정
  eventTitle = eventTitle || '🎉 댓글 이벤트 참여 신청';
  var description = '영상에 댓글을 남기고 이벤트에 참여하세요!\n\n';
  
  if (videoUrl) {
    description += '🎬 이벤트 대상 영상: ' + videoUrl + '\n\n';
  }
  
  description += '참여 방법:\n';
  description += '1. 위 영상에 댓글을 남겨주세요.\n';
  description += '2. 아래 양식을 작성해주세요.\n';
  description += '3. 댓글 확인 후 추첨을 진행합니다.\n\n';
  description += '※ 유튜브 닉네임은 댓글을 작성한 계정의 닉네임과 정확히 일치해야 합니다.';
  
  // 폼 생성
  var form = FormApp.create(eventTitle);
  form.setDescription(description);
  form.setCollectEmail(false);  // 구글 계정 이메일 대신 직접 입력받음
  form.setLimitOneResponsePerUser(false);  // 구글 계정 기반 제한 대신 코드로 중복 체크
  form.setAllowResponseEdits(false);
  
  // 질문 1: 유튜브 닉네임
  form.addTextItem()
    .setTitle('유튜브 닉네임')
    .setHelpText('댓글을 작성한 유튜브 계정의 닉네임을 정확히 입력해주세요.')
    .setRequired(true);
  
  // 질문 2: 이메일 주소
  var emailItem = form.addTextItem()
    .setTitle('이메일 주소')
    .setHelpText('당첨 시 안내를 받을 이메일 주소를 입력해주세요.')
    .setRequired(true);
  
  // 이메일 형식 유효성 검사
  var emailValidation = FormApp.createTextValidation()
    .requireTextIsEmail()
    .build();
  emailItem.setValidation(emailValidation);
  
  // 질문 3: 댓글을 남긴 영상 URL
  var urlItem = form.addTextItem()
    .setTitle('댓글을 남긴 영상 URL')
    .setHelpText('댓글을 작성한 유튜브 영상의 URL을 붙여넣어주세요.')
    .setRequired(true);
  
  // URL 형식 유효성 검사
  var urlValidation = FormApp.createTextValidation()
    .requireTextContains('youtube.com/watch')
    .build();
  urlItem.setValidation(urlValidation);
  
  // 질문 4: 댓글 내용 (선택)
  form.addParagraphTextItem()
    .setTitle('작성한 댓글 내용')
    .setHelpText('작성한 댓글의 내용을 붙여넣어주세요. (확인용, 선택사항)')
    .setRequired(false);
  
  // 제출 확인 메시지
  form.setConfirmationMessage(
    '🎉 참여해 주셔서 감사합니다!\n\n' +
    '댓글 확인 후 결과를 이메일로 안내드리겠습니다.\n' +
    '유튜브 닉네임이 댓글 작성자와 일치해야 참여가 인정됩니다.\n\n' +
    '행운을 빕니다! 🍀'
  );
  
  // 현재 스프레드시트에 응답 시트 연결
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  
  // 폼 정보 로그 출력
  var formUrl = form.getPublishedUrl();
  var editUrl = form.getEditUrl();
  var formId = form.getId();
  
  Logger.log('========================================');
  Logger.log('댓글 이벤트 폼이 생성되었습니다!');
  Logger.log('========================================');
  Logger.log('참여 URL (구독자에게 공유): ' + formUrl);
  Logger.log('편집 URL (관리용): ' + editUrl);
  Logger.log('폼 ID: ' + formId);
  Logger.log('========================================');
  
  // 폼 ID를 PropertiesService에 저장 (나중에 참조용)
  PropertiesService.getScriptProperties().setProperty('CURRENT_EVENT_FORM_ID', formId);
  
  // 폼 생성 알림을 슬랙으로 전송
  var webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_EVENT');
  if (webhookUrl) {
    sendSlackMessage(
      webhookUrl,
      '📋 *새 이벤트 폼이 생성되었습니다*\n\n' +
      '• 이벤트: ' + eventTitle + '\n' +
      '• 참여 URL: ' + formUrl + '\n' +
      (videoUrl ? '• 대상 영상: ' + videoUrl + '\n' : '') +
      '\n구독자에게 위 URL을 공유해주세요!',
      '📝 이벤트 폼 생성'
    );
  }
  
  return {
    formUrl: formUrl,
    editUrl: editUrl,
    formId: formId
  };
}
```

### 폼 생성 실행

앱스 스크립트 편집기에서 다음 함수를 실행합니다:

```javascript
/**
 * 이벤트 폼 생성 실행 함수
 */
function runCreateEventForm() {
  var result = createEventForm(
    '🎉 6월 댓글 이벤트 - 스타벅스 기프티콘 증정!',
    'https://www.youtube.com/watch?v=영상ID를입력하세요'
  );
  
  Logger.log('폼 URL을 영상 설명란이나 고정 댓글에 넣어주세요: ' + result.formUrl);
}
```

실행하면 스프레드시트에 폼 응답 시트가 자동으로 추가됩니다. 시트 이름은 "폼 응답 1" 형태로 생성되는데, 이를 관리하기 쉽게 변경합니다:

```javascript
/**
 * 폼 응답 시트의 이름을 변경합니다.
 */
function renameFormResponseSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  
  // 가장 마지막에 추가된 시트 (폼 응답 시트)를 찾아서 이름 변경
  for (var i = sheets.length - 1; i >= 0; i--) {
    var sheetName = sheets[i].getName();
    if (sheetName.indexOf('폼 응답') === 0 || sheetName.indexOf('Form Responses') === 0) {
      sheets[i].setName('폼 응답');
      Logger.log('시트 이름이 "폼 응답"으로 변경되었습니다.');
      return;
    }
  }
  
  Logger.log('폼 응답 시트를 찾을 수 없습니다.');
}
```

---

## [바로 실습] 댓글 수집 시트 추가하기

이벤트 대상 영상의 모든 댓글을 수집하여 스프레드시트에 저장합니다. YouTube Data API의 `commentThreads.list`를 사용합니다.

```javascript
/**
 * 지정된 영상의 모든 댓글을 수집하여 시트에 저장합니다.
 * @param {string} videoId - 유튜브 영상 ID
 * @returns {number} 수집된 댓글 수
 */
function collectVideoComments(videoId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // '댓글 목록' 시트가 없으면 생성
  var commentSheet = ss.getSheetByName('댓글 목록');
  if (!commentSheet) {
    commentSheet = ss.insertSheet('댓글 목록');
  }
  
  // 시트 초기화 및 헤더 설정
  commentSheet.clear();
  commentSheet.appendRow([
    '작성자 닉네임',
    '채널 ID',
    '댓글 내용',
    '좋아요 수',
    '작성 시간',
    '댓글 ID',
    '프로필 이미지 URL'
  ]);
  
  // 헤더 서식 설정
  var headerRange = commentSheet.getRange(1, 1, 1, 7);
  headerRange.setBackground('#4285F4');
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  
  var allComments = [];
  var nextPageToken = null;
  
  do {
    try {
      var response = YouTube.CommentThreads.list('snippet', {
        videoId: videoId,
        maxResults: 100,
        pageToken: nextPageToken,
        textFormat: 'plainText',
        order: 'time'
      });
      
      if (response.items && response.items.length > 0) {
        response.items.forEach(function(item) {
          var comment = item.snippet.topLevelComment.snippet;
          allComments.push([
            comment.authorDisplayName,
            comment.authorChannelId ? comment.authorChannelId.value : '',
            comment.textDisplay,
            comment.likeCount,
            comment.publishedAt,
            item.snippet.topLevelComment.id,
            comment.authorProfileImageUrl || ''
          ]);
        });
      }
      
      nextPageToken = response.nextPageToken;
      
    } catch (e) {
      Logger.log('댓글 수집 중 에러: ' + e.message);
      // API 할당량 초과 등의 에러 시 수집된 것까지만 저장
      break;
    }
    
    // API 호출 간 짧은 대기 (할당량 보호)
    if (nextPageToken) {
      Utilities.sleep(200);
    }
    
  } while (nextPageToken);
  
  // 수집된 댓글을 시트에 한번에 기록
  if (allComments.length > 0) {
    commentSheet.getRange(2, 1, allComments.length, 7).setValues(allComments);
  }
  
  // 열 너비 자동 조정
  commentSheet.autoResizeColumns(1, 5);
  
  // 수집 정보를 시트 상단에 메모로 추가
  commentSheet.getRange('A1').setNote(
    '영상 ID: ' + videoId + '\n' +
    '수집 시간: ' + new Date().toLocaleString('ko-KR') + '\n' +
    '총 댓글 수: ' + allComments.length
  );
  
  Logger.log('댓글 수집 완료: ' + allComments.length + '개');
  
  // 슬랙 알림
  var webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_EVENT');
  if (webhookUrl) {
    sendSlackMessage(
      webhookUrl,
      '💬 *댓글 수집 완료*\n\n' +
      '• 영상 ID: `' + videoId + '`\n' +
      '• 수집된 댓글: *' + allComments.length + '개*\n' +
      '• 수집 시간: ' + new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }),
      '📥 댓글 수집 리포트'
    );
  }
  
  return allComments.length;
}
```

### 댓글 수집 실행

```javascript
/**
 * 이벤트 대상 영상의 댓글을 수집합니다.
 * videoId에 실제 영상 ID를 넣어주세요.
 */
function runCollectComments() {
  // 영상 URL에서 v= 파라미터 뒤의 값이 영상 ID입니다.
  // 예: https://www.youtube.com/watch?v=dQw4w9WgXcQ → videoId = 'dQw4w9WgXcQ'
  var videoId = '여기에영상ID입력';
  
  var count = collectVideoComments(videoId);
  Logger.log('총 ' + count + '개의 댓글이 수집되었습니다.');
}
```

> **주의:** YouTube Data API를 사용하려면 Part 02에서 설정한 YouTube Data API v3 서비스가 활성화되어 있어야 합니다. 앱스 스크립트 편집기 좌측의 **서비스** 메뉴에서 YouTube Data API가 추가되어 있는지 확인하세요.

### 대량 댓글 처리

인기 영상의 경우 댓글이 수천, 수만 개일 수 있습니다. YouTube Data API의 `commentThreads.list`는 한 번에 최대 100개의 댓글을 반환하며, `pageToken`을 사용하여 다음 페이지를 가져옵니다. 위 코드에서 `do...while` 루프가 모든 페이지를 순회하므로, 댓글 수에 관계없이 전부 수집합니다.

다만 API 할당량을 주의해야 합니다. YouTube Data API는 하루에 10,000 쿼타 유닛이 제공되며, `commentThreads.list`는 1회 호출당 약 1 유닛을 소비합니다. 댓글 1만 개를 수집하면 100회 API 호출이 필요하므로 100 유닛을 사용합니다. 일반적인 이벤트 영상의 댓글 수준에서는 할당량 걱정이 거의 없습니다.

---

## [바로 실습] 폼 응답과 댓글 대조 확인하기

이벤트의 핵심 검증 단계입니다. 구글 폼으로 제출한 유튜브 닉네임이 실제로 해당 영상에 댓글을 남겼는지 확인합니다. 이 검증을 통해 댓글을 남기지 않고 폼만 제출한 어뷰징을 방지할 수 있습니다.

```javascript
/**
 * 폼 응답의 유튜브 닉네임과 실제 댓글 작성자를 대조 검증합니다.
 * @returns {Object} { verified: [...], unverified: [...], duplicates: [...] }
 */
function verifyParticipants() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var formSheet = ss.getSheetByName('폼 응답');
  var commentSheet = ss.getSheetByName('댓글 목록');
  
  // 시트 존재 여부 확인
  if (!formSheet) {
    Logger.log('에러: "폼 응답" 시트를 찾을 수 없습니다.');
    return null;
  }
  if (!commentSheet) {
    Logger.log('에러: "댓글 목록" 시트를 찾을 수 없습니다. collectVideoComments()를 먼저 실행하세요.');
    return null;
  }
  
  // 폼 응답 데이터 가져오기
  var formData = formSheet.getDataRange().getValues();
  if (formData.length <= 1) {
    Logger.log('폼 응답이 없습니다.');
    return { verified: [], unverified: [], duplicates: [] };
  }
  
  // 헤더 행 확인 후 데이터 파싱
  // 폼 응답 시트 구조: [타임스탬프, 유튜브 닉네임, 이메일 주소, 영상 URL, 댓글 내용(선택)]
  var participants = formData.slice(1).map(function(row, index) {
    return {
      rowIndex: index + 2,  // 시트의 실제 행 번호 (1-indexed, 헤더 제외)
      timestamp: row[0],
      nickname: String(row[1]).trim(),
      email: String(row[2]).trim(),
      videoUrl: String(row[3]).trim(),
      commentText: row[4] ? String(row[4]).trim() : ''
    };
  });
  
  // 댓글 작성자 목록 가져오기
  var commentData = commentSheet.getDataRange().getValues();
  var commentAuthors = {};
  commentData.slice(1).forEach(function(row) {
    var authorName = String(row[0]).trim();
    if (!commentAuthors[authorName]) {
      commentAuthors[authorName] = [];
    }
    commentAuthors[authorName].push({
      content: String(row[2]).trim(),
      likeCount: row[3],
      publishedAt: row[4]
    });
  });
  
  // 중복 참여 체크용 Set
  var seenNicknames = {};
  var verified = [];
  var unverified = [];
  var duplicates = [];
  
  participants.forEach(function(p) {
    // 중복 참여 체크
    if (seenNicknames[p.nickname]) {
      duplicates.push(p);
      return;
    }
    seenNicknames[p.nickname] = true;
    
    // 댓글 존재 여부 확인
    if (commentAuthors[p.nickname]) {
      p.verified = true;
      p.matchedComments = commentAuthors[p.nickname];
      verified.push(p);
    } else {
      p.verified = false;
      unverified.push(p);
    }
  });
  
  // 검증 결과 시트 생성
  writeVerificationResults(ss, verified, unverified, duplicates);
  
  Logger.log('========================================');
  Logger.log('검증 결과:');
  Logger.log('  검증 통과: ' + verified.length + '명');
  Logger.log('  검증 실패: ' + unverified.length + '명');
  Logger.log('  중복 참여: ' + duplicates.length + '명');
  Logger.log('========================================');
  
  return {
    verified: verified,
    unverified: unverified,
    duplicates: duplicates
  };
}

/**
 * 검증 결과를 별도 시트에 기록합니다.
 */
function writeVerificationResults(ss, verified, unverified, duplicates) {
  // '검증 결과' 시트가 없으면 생성
  var resultSheet = ss.getSheetByName('검증 결과');
  if (!resultSheet) {
    resultSheet = ss.insertSheet('검증 결과');
  }
  resultSheet.clear();
  
  // 헤더
  resultSheet.appendRow(['상태', '닉네임', '이메일', '영상 URL', '검증 시간', '비고']);
  
  var headerRange = resultSheet.getRange(1, 1, 1, 6);
  headerRange.setBackground('#34A853');
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  
  var allRows = [];
  
  // 검증 통과
  verified.forEach(function(p) {
    allRows.push([
      '✅ 통과',
      p.nickname,
      p.email,
      p.videoUrl,
      new Date().toLocaleString('ko-KR'),
      '댓글 ' + p.matchedComments.length + '개 확인'
    ]);
  });
  
  // 검증 실패
  unverified.forEach(function(p) {
    allRows.push([
      '❌ 실패',
      p.nickname,
      p.email,
      p.videoUrl,
      new Date().toLocaleString('ko-KR'),
      '댓글을 찾을 수 없음'
    ]);
  });
  
  // 중복 참여
  duplicates.forEach(function(p) {
    allRows.push([
      '⚠️ 중복',
      p.nickname,
      p.email,
      p.videoUrl,
      new Date().toLocaleString('ko-KR'),
      '중복 참여'
    ]);
  });
  
  if (allRows.length > 0) {
    resultSheet.getRange(2, 1, allRows.length, 6).setValues(allRows);
  }
  
  // 조건부 서식: 상태별 배경색
  var dataRange = resultSheet.getRange(2, 1, allRows.length, 6);
  
  // 통과: 연한 초록
  var rulePass = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('통과')
    .setBackground('#E6F4EA')
    .setRanges([dataRange])
    .build();
  
  // 실패: 연한 빨강
  var ruleFail = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('실패')
    .setBackground('#FCE8E6')
    .setRanges([dataRange])
    .build();
  
  // 중복: 연한 노랑
  var ruleDup = SpreadsheetApp.newConditionalFormatRule()
    .whenTextContains('중복')
    .setBackground('#FEF7E0')
    .setRanges([dataRange])
    .build();
  
  resultSheet.setConditionalFormatRules([rulePass, ruleFail, ruleDup]);
  resultSheet.autoResizeColumns(1, 6);
}
```

### 닉네임 매칭의 함정과 개선

유튜브 닉네임 매칭에는 몇 가지 주의할 점이 있습니다:

1. **대소문자:** 유튜브 닉네임은 대소문자를 구분합니다. 사용자가 폼에 입력할 때 대소문자가 다를 수 있습니다.
2. **공백:** 닉네임 앞뒤에 공백이 들어갈 수 있습니다.
3. **특수문자:** 유튜브 닉네임에는 이모지나 특수문자가 포함될 수 있습니다.

이 문제를 해결하기 위한 개선된 매칭 함수:

```javascript
/**
 * 닉네임을 정규화하여 비교합니다.
 * 대소문자 무시, 앞뒤 공백 제거, 연속 공백 단일 공백으로 변환
 * @param {string} name - 닉네임
 * @returns {string} 정규화된 닉네임
 */
function normalizeNickname(name) {
  return String(name)
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');  // 연속 공백을 단일 공백으로
}

/**
 * 개선된 닉네임 매칭 - 유사도 기반
 * 정확히 일치하지 않더라도 유사한 닉네임을 찾아줍니다.
 * @param {string} formNickname - 폼에 입력된 닉네임
 * @param {Object} commentAuthors - 댓글 작성자 맵
 * @returns {Object|null} 매칭된 작성자 정보 또는 null
 */
function findMatchingAuthor(formNickname, commentAuthors) {
  var normalizedForm = normalizeNickname(formNickname);
  
  // 1차: 정규화된 닉네임으로 정확히 매칭
  var authorNames = Object.keys(commentAuthors);
  for (var i = 0; i < authorNames.length; i++) {
    if (normalizeNickname(authorNames[i]) === normalizedForm) {
      return {
        originalName: authorNames[i],
        comments: commentAuthors[authorNames[i]],
        matchType: 'exact'
      };
    }
  }
  
  // 2차: 포함 관계 확인 (닉네임이 서로 포함되는 경우)
  for (var j = 0; j < authorNames.length; j++) {
    var normalizedAuthor = normalizeNickname(authorNames[j]);
    if (normalizedAuthor.indexOf(normalizedForm) !== -1 || 
        normalizedForm.indexOf(normalizedAuthor) !== -1) {
      return {
        originalName: authorNames[j],
        comments: commentAuthors[authorNames[j]],
        matchType: 'partial'
      };
    }
  }
  
  return null;
}
```

> **팁:** 이벤트 공지에 "폼에 입력하는 유튜브 닉네임은 댓글을 작성한 계정의 닉네임과 **정확히** 같아야 합니다"라고 명시하면 매칭 정확도가 크게 올라갑니다.

---

## [바로 실습] 조건 충족 시 자동 메일 발송하기

검증을 통과한 참여자 중에서 당첨자를 선정하고, 자동으로 축하 이메일을 발송합니다.

### 당첨자 랜덤 추첨

```javascript
/**
 * 검증을 통과한 참여자 중에서 랜덤으로 당첨자를 선정합니다.
 * @param {number} winnerCount - 당첨자 수
 * @returns {Array} 당첨자 목록
 */
function selectWinners(winnerCount) {
  var result = verifyParticipants();
  
  if (!result || result.verified.length === 0) {
    Logger.log('검증을 통과한 참여자가 없습니다.');
    return [];
  }
  
  winnerCount = winnerCount || 3;  // 기본 3명
  
  // 검증 통과자 수가 당첨자 수보다 적은 경우
  if (result.verified.length <= winnerCount) {
    Logger.log('검증 통과자(' + result.verified.length + '명)가 당첨자 수(' + winnerCount + '명) 이하이므로 전원 당첨 처리합니다.');
    return result.verified;
  }
  
  // Fisher-Yates 셔플 알고리즘으로 랜덤 추첨
  var pool = result.verified.slice();  // 배열 복사
  
  for (var i = pool.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var temp = pool[i];
    pool[i] = pool[j];
    pool[j] = temp;
  }
  
  var winners = pool.slice(0, winnerCount);
  
  Logger.log('========================================');
  Logger.log('🎉 당첨자 발표!');
  Logger.log('========================================');
  winners.forEach(function(w, idx) {
    Logger.log((idx + 1) + '등: ' + w.nickname + ' (' + w.email + ')');
  });
  Logger.log('========================================');
  
  // 당첨 결과를 시트에 기록
  writeWinnerResults(winners);
  
  return winners;
}

/**
 * 당첨 결과를 별도 시트에 기록합니다.
 */
function writeWinnerResults(winners) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var winnerSheet = ss.getSheetByName('당첨자 목록');
  if (!winnerSheet) {
    winnerSheet = ss.insertSheet('당첨자 목록');
  }
  winnerSheet.clear();
  
  // 헤더
  winnerSheet.appendRow(['순번', '닉네임', '이메일', '영상 URL', '추첨 일시', '메일 발송 여부']);
  
  var headerRange = winnerSheet.getRange(1, 1, 1, 6);
  headerRange.setBackground('#FBBC04');
  headerRange.setFontWeight('bold');
  
  var rows = winners.map(function(w, idx) {
    return [
      idx + 1,
      w.nickname,
      w.email,
      w.videoUrl,
      new Date().toLocaleString('ko-KR'),
      '미발송'
    ];
  });
  
  if (rows.length > 0) {
    winnerSheet.getRange(2, 1, rows.length, 6).setValues(rows);
  }
  
  winnerSheet.autoResizeColumns(1, 6);
}
```

### 당첨 이메일 발송

```javascript
/**
 * 당첨자에게 축하 이메일을 발송합니다.
 * @param {string} email - 당첨자 이메일
 * @param {string} nickname - 당첨자 닉네임
 * @param {string} [channelName] - 채널명 (선택)
 * @param {string} [prizeDescription] - 경품 설명 (선택)
 * @param {string} [claimUrl] - 경품 수령 링크 (선택)
 */
function sendWinnerEmail(email, nickname, channelName, prizeDescription, claimUrl) {
  channelName = channelName || '슈퍼유튜브시트 채널';
  prizeDescription = prizeDescription || '댓글 이벤트 경품';
  claimUrl = claimUrl || '#';
  
  var htmlBody = '<!DOCTYPE html>' +
    '<html>' +
    '<head><meta charset="UTF-8"></head>' +
    '<body style="margin: 0; padding: 0; background-color: #f5f5f5;">' +
    '<div style="font-family: \'Noto Sans KR\', \'Apple SD Gothic Neo\', \'Malgun Gothic\', sans-serif; max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">' +
    
    // 헤더 영역
    '<div style="background: linear-gradient(135deg, #FF0000, #CC0000); padding: 40px 30px; text-align: center;">' +
    '<h1 style="color: white; margin: 0; font-size: 28px;">&#127881; 축하합니다!</h1>' +
    '<p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">댓글 이벤트 당첨 안내</p>' +
    '</div>' +
    
    // 본문 영역
    '<div style="padding: 30px;">' +
    '<p style="font-size: 16px; color: #333; line-height: 1.6;">' +
    '안녕하세요, <strong>' + nickname + '</strong>님!</p>' +
    
    '<p style="font-size: 16px; color: #333; line-height: 1.6;">' +
    '<strong>' + channelName + '</strong>의 댓글 이벤트에 당첨되셨습니다!</p>' +
    
    '<div style="background: #FFF3E0; border-left: 4px solid #FF9800; padding: 15px 20px; margin: 20px 0; border-radius: 0 8px 8px 0;">' +
    '<p style="margin: 0; font-size: 14px; color: #E65100;"><strong>&#127873; 경품:</strong> ' + prizeDescription + '</p>' +
    '</div>' +
    
    '<p style="font-size: 16px; color: #333; line-height: 1.6;">' +
    '아래 버튼을 클릭하여 경품을 수령해 주세요.</p>' +
    
    // 버튼
    '<div style="text-align: center; margin: 30px 0;">' +
    '<a href="' + claimUrl + '" style="display: inline-block; background: linear-gradient(135deg, #FF0000, #CC0000); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold; box-shadow: 0 2px 8px rgba(255,0,0,0.3);">&#127873; 경품 수령하기</a>' +
    '</div>' +
    
    '<p style="font-size: 14px; color: #666; line-height: 1.6;">' +
    '경품 수령 관련 문의사항은 유튜브 채널의 커뮤니티 탭이나 댓글로 남겨주세요.</p>' +
    '</div>' +
    
    // 푸터
    '<div style="background: #f9f9f9; padding: 20px 30px; text-align: center; border-top: 1px solid #eee;">' +
    '<p style="margin: 0; font-size: 12px; color: #999;">' +
    '본 메일은 ' + channelName + '의 댓글 이벤트 당첨 안내 메일입니다.</p>' +
    '<p style="margin: 5px 0 0 0; font-size: 12px; color: #999;">' +
    '발송일: ' + new Date().toLocaleString('ko-KR') + '</p>' +
    '</div>' +
    
    '</div>' +
    '</body>' +
    '</html>';
  
  // 이메일 발송
  try {
    GmailApp.sendEmail(
      email,
      '[' + channelName + '] &#127881; 댓글 이벤트 당첨을 축하드립니다!',
      // 플레인 텍스트 폴백
      nickname + '님, ' + channelName + '의 댓글 이벤트에 당첨되셨습니다! ' +
      '경품: ' + prizeDescription + '. 경품 수령: ' + claimUrl,
      {
        htmlBody: htmlBody,
        name: channelName
      }
    );
    
    Logger.log('당첨 이메일 발송 완료: ' + email + ' (' + nickname + ')');
    return true;
    
  } catch (e) {
    Logger.log('이메일 발송 실패 (' + email + '): ' + e.message);
    return false;
  }
}
```

### 미당첨자 감사 이메일 (선택)

이벤트에 참여했지만 당첨되지 않은 분들에게 감사 이메일을 보내는 것도 채널 브랜딩에 좋습니다:

```javascript
/**
 * 미당첨 참여자에게 감사 이메일을 발송합니다.
 * @param {string} email - 참여자 이메일
 * @param {string} nickname - 참여자 닉네임
 * @param {string} [channelName] - 채널명
 */
function sendThankYouEmail(email, nickname, channelName) {
  channelName = channelName || '슈퍼유튜브시트 채널';
  
  var htmlBody = '<!DOCTYPE html>' +
    '<html>' +
    '<head><meta charset="UTF-8"></head>' +
    '<body style="margin: 0; padding: 0; background-color: #f5f5f5;">' +
    '<div style="font-family: \'Noto Sans KR\', \'Apple SD Gothic Neo\', \'Malgun Gothic\', sans-serif; max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">' +
    
    '<div style="background: linear-gradient(135deg, #4285F4, #3367D6); padding: 40px 30px; text-align: center;">' +
    '<h1 style="color: white; margin: 0; font-size: 24px;">참여해 주셔서 감사합니다!</h1>' +
    '</div>' +
    
    '<div style="padding: 30px;">' +
    '<p style="font-size: 16px; color: #333; line-height: 1.6;">' +
    '안녕하세요, <strong>' + nickname + '</strong>님!</p>' +
    '<p style="font-size: 16px; color: #333; line-height: 1.6;">' +
    '이번 이벤트에 참여해 주셔서 진심으로 감사드립니다. 아쉽게도 이번에는 당첨되지 않으셨지만, ' +
    '다음 이벤트에서는 꼭 좋은 소식을 전해드리겠습니다!</p>' +
    '<p style="font-size: 16px; color: #333; line-height: 1.6;">' +
    '채널을 구독하고 알림을 켜두시면 다음 이벤트 소식을 빠르게 받으실 수 있습니다. &#128276;</p>' +
    '</div>' +
    
    '<div style="background: #f9f9f9; padding: 20px 30px; text-align: center; border-top: 1px solid #eee;">' +
    '<p style="margin: 0; font-size: 12px; color: #999;">' + channelName + '</p>' +
    '</div>' +
    
    '</div>' +
    '</body>' +
    '</html>';
  
  try {
    GmailApp.sendEmail(
      email,
      '[' + channelName + '] 이벤트 참여 감사드립니다!',
      nickname + '님, 이벤트에 참여해 주셔서 감사합니다. 다음 이벤트에도 많은 관심 부탁드립니다!',
      {
        htmlBody: htmlBody,
        name: channelName
      }
    );
    
    Logger.log('감사 이메일 발송 완료: ' + email);
    return true;
  } catch (e) {
    Logger.log('감사 이메일 발송 실패 (' + email + '): ' + e.message);
    return false;
  }
}
```

> **GmailApp 사용 시 주의사항:**
> - GmailApp은 하루 최대 100명에게 이메일을 발송할 수 있습니다 (무료 구글 계정 기준).
> - Google Workspace 계정은 하루 1,500명까지 가능합니다.
> - 대량 발송 시 스팸으로 분류되지 않도록 발송 간격을 두는 것이 좋습니다.

---

## [바로 실습] 전체 프로세스 자동화하기

지금까지 만든 개별 함수들을 하나의 워크플로우로 통합합니다. 이 함수 하나를 실행하면 댓글 수집부터 당첨자 이메일 발송까지 전 과정이 자동으로 진행됩니다.

```javascript
/**
 * 댓글 이벤트 전체 프로세스를 자동 실행합니다.
 * 
 * 프로세스:
 * 1. 대상 영상의 최신 댓글 수집
 * 2. 폼 응답과 댓글 작성자 대조 검증
 * 3. 검증 통과자 중 랜덤 당첨자 선정
 * 4. 당첨자에게 축하 이메일 발송
 * 5. 미당첨자에게 감사 이메일 발송 (선택)
 * 6. 결과를 시트에 기록
 * 7. 슬랙으로 최종 리포트 전송
 * 
 * @param {Object} config - 이벤트 설정
 * @param {string} config.videoId - 대상 영상 ID
 * @param {number} config.winnerCount - 당첨자 수
 * @param {string} config.channelName - 채널명
 * @param {string} config.prizeDescription - 경품 설명
 * @param {string} config.claimUrl - 경품 수령 링크
 * @param {boolean} config.sendThankYou - 미당첨자 감사 메일 발송 여부
 */
function runFullEventProcess(config) {
  var startTime = new Date();
  Logger.log('========================================');
  Logger.log('댓글 이벤트 자동화 프로세스 시작');
  Logger.log('시작 시간: ' + startTime.toLocaleString('ko-KR'));
  Logger.log('========================================');
  
  var processLog = [];
  
  try {
    // ─────────────────────────────────────────
    // Step 1: 최신 댓글 수집
    // ─────────────────────────────────────────
    Logger.log('\n📥 Step 1: 댓글 수집 중...');
    var commentCount = collectVideoComments(config.videoId);
    processLog.push('댓글 수집: ' + commentCount + '개');
    Logger.log('댓글 수집 완료: ' + commentCount + '개');
    
    // ─────────────────────────────────────────
    // Step 2: 폼 응답 검증
    // ─────────────────────────────────────────
    Logger.log('\n🔍 Step 2: 참여자 검증 중...');
    var verificationResult = verifyParticipants();
    
    if (!verificationResult) {
      throw new Error('참여자 검증 실패: 폼 응답 또는 댓글 목록 시트를 확인하세요.');
    }
    
    processLog.push('검증 통과: ' + verificationResult.verified.length + '명');
    processLog.push('검증 실패: ' + verificationResult.unverified.length + '명');
    processLog.push('중복 참여: ' + verificationResult.duplicates.length + '명');
    Logger.log('검증 완료 - 통과: ' + verificationResult.verified.length + '명');
    
    if (verificationResult.verified.length === 0) {
      throw new Error('검증을 통과한 참여자가 없습니다.');
    }
    
    // ─────────────────────────────────────────
    // Step 3: 당첨자 랜덤 추첨
    // ─────────────────────────────────────────
    Logger.log('\n🎲 Step 3: 당첨자 추첨 중...');
    var winnerCount = config.winnerCount || 3;
    
    // Fisher-Yates 셔플
    var pool = verificationResult.verified.slice();
    for (var i = pool.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = pool[i];
      pool[i] = pool[j];
      pool[j] = temp;
    }
    
    var winners = pool.slice(0, winnerCount);
    var nonWinners = pool.slice(winnerCount);
    
    processLog.push('당첨자: ' + winners.length + '명 선정');
    
    // 당첨 결과 시트 기록
    writeWinnerResults(winners);
    
    Logger.log('당첨자 ' + winners.length + '명 선정 완료');
    winners.forEach(function(w, idx) {
      Logger.log('  ' + (idx + 1) + '등: ' + w.nickname);
    });
    
    // ─────────────────────────────────────────
    // Step 4: 당첨자 이메일 발송
    // ─────────────────────────────────────────
    Logger.log('\n📧 Step 4: 당첨 이메일 발송 중...');
    var emailSuccessCount = 0;
    var emailFailCount = 0;
    
    winners.forEach(function(winner, idx) {
      var success = sendWinnerEmail(
        winner.email,
        winner.nickname,
        config.channelName,
        config.prizeDescription,
        config.claimUrl
      );
      
      if (success) {
        emailSuccessCount++;
        // 당첨자 목록 시트에서 메일 발송 상태 업데이트
        var ss = SpreadsheetApp.getActiveSpreadsheet();
        var winnerSheet = ss.getSheetByName('당첨자 목록');
        if (winnerSheet) {
          winnerSheet.getRange(idx + 2, 6).setValue('✅ 발송 완료');
        }
      } else {
        emailFailCount++;
      }
      
      // 이메일 간 1초 대기 (스팸 방지)
      Utilities.sleep(1000);
    });
    
    processLog.push('당첨 이메일: 성공 ' + emailSuccessCount + ', 실패 ' + emailFailCount);
    
    // ─────────────────────────────────────────
    // Step 5: 미당첨자 감사 이메일 (선택)
    // ─────────────────────────────────────────
    if (config.sendThankYou && nonWinners.length > 0) {
      Logger.log('\n💌 Step 5: 감사 이메일 발송 중...');
      var thankYouCount = 0;
      
      nonWinners.forEach(function(participant) {
        var success = sendThankYouEmail(
          participant.email,
          participant.nickname,
          config.channelName
        );
        if (success) thankYouCount++;
        
        Utilities.sleep(1000);  // 스팸 방지 대기
      });
      
      processLog.push('감사 이메일: ' + thankYouCount + '/' + nonWinners.length + '명 발송');
    }
    
    // ─────────────────────────────────────────
    // Step 6: 실행 로그 시트에 기록
    // ─────────────────────────────────────────
    Logger.log('\n📝 Step 6: 실행 로그 기록 중...');
    writeProcessLog(config, processLog, startTime);
    
    // ─────────────────────────────────────────
    // Step 7: 슬랙으로 최종 리포트 전송
    // ─────────────────────────────────────────
    Logger.log('\n📣 Step 7: 슬랙 리포트 전송 중...');
    sendEventResultToSlack(config, verificationResult, winners, processLog, startTime);
    
    Logger.log('\n========================================');
    Logger.log('댓글 이벤트 자동화 프로세스 완료!');
    Logger.log('소요 시간: ' + ((new Date() - startTime) / 1000).toFixed(1) + '초');
    Logger.log('========================================');
    
  } catch (e) {
    Logger.log('\n❌ 프로세스 에러: ' + e.message);
    Logger.log('스택: ' + e.stack);
    
    // 에러 발생 시 슬랙으로 알림
    var webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_EVENT');
    if (webhookUrl) {
      sendSlackMessage(
        webhookUrl,
        '❌ *댓글 이벤트 프로세스 에러*\n\n' +
        '• 에러: `' + e.message + '`\n' +
        '• 시간: ' + new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' }) + '\n' +
        '• 진행 상태:\n' + processLog.map(function(l) { return '  - ' + l; }).join('\n'),
        '🚨 이벤트 시스템 에러'
      );
    }
  }
}

/**
 * 프로세스 실행 로그를 시트에 기록합니다.
 */
function writeProcessLog(config, processLog, startTime) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var logSheet = ss.getSheetByName('실행 로그');
  if (!logSheet) {
    logSheet = ss.insertSheet('실행 로그');
    logSheet.appendRow(['실행 일시', '영상 ID', '당첨자 수', '소요 시간(초)', '상세 로그']);
    var headerRange = logSheet.getRange(1, 1, 1, 5);
    headerRange.setBackground('#666666');
    headerRange.setFontColor('#FFFFFF');
    headerRange.setFontWeight('bold');
  }
  
  var endTime = new Date();
  var duration = ((endTime - startTime) / 1000).toFixed(1);
  
  logSheet.appendRow([
    endTime.toLocaleString('ko-KR'),
    config.videoId,
    config.winnerCount || 3,
    duration,
    processLog.join(' | ')
  ]);
}

/**
 * 이벤트 결과를 슬랙에 리포트 형태로 전송합니다.
 */
function sendEventResultToSlack(config, verificationResult, winners, processLog, startTime) {
  var webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_EVENT');
  if (!webhookUrl) return;
  
  var endTime = new Date();
  var duration = ((endTime - startTime) / 1000).toFixed(1);
  
  // 당첨자 목록 텍스트 생성
  var winnerList = winners.map(function(w, idx) {
    var medal = ['🥇', '🥈', '🥉'][idx] || '🏅';
    return medal + ' ' + w.nickname;
  }).join('\n');
  
  var payload = {
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: '🎉 댓글 이벤트 추첨 완료!',
          emoji: true
        }
      },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: '*📋 총 참여자*\n' + (verificationResult.verified.length + verificationResult.unverified.length + verificationResult.duplicates.length) + '명' },
          { type: 'mrkdwn', text: '*✅ 검증 통과*\n' + verificationResult.verified.length + '명' },
          { type: 'mrkdwn', text: '*❌ 검증 실패*\n' + verificationResult.unverified.length + '명' },
          { type: 'mrkdwn', text: '*⚠️ 중복 참여*\n' + verificationResult.duplicates.length + '명' }
        ]
      },
      { type: 'divider' },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*🏆 당첨자*\n\n' + winnerList
        }
      },
      { type: 'divider' },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: '*🎁 경품*\n' + (config.prizeDescription || '-') },
          { type: 'mrkdwn', text: '*⏱️ 소요 시간*\n' + duration + '초' }
        ]
      },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: '📡 슈퍼유튜브시트 이벤트 시스템 | ' + endTime.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
          }
        ]
      }
    ],
    text: '댓글 이벤트 추첨 완료 - 당첨자 ' + winners.length + '명'
  };
  
  sendSlackWithRetry(webhookUrl, payload);
}
```

### 전체 프로세스 실행

```javascript
/**
 * 댓글 이벤트 전체 프로세스를 실행합니다.
 * videoId, 경품 정보 등을 실제 값으로 변경한 후 실행하세요.
 */
function runMyEvent() {
  runFullEventProcess({
    videoId: '여기에영상ID입력',          // 이벤트 대상 영상 ID
    winnerCount: 3,                      // 당첨자 수
    channelName: '내 채널 이름',          // 채널명
    prizeDescription: '스타벅스 아메리카노 기프티콘',  // 경품 설명
    claimUrl: 'https://수령링크.com',     // 경품 수령 링크
    sendThankYou: true                   // 미당첨자 감사 메일 발송 여부
  });
}
```

> **실행 전 체크리스트:**
> 1. `createEventForm()`으로 폼을 생성하고 구독자에게 공유했는지 확인
> 2. 충분한 참여 기간이 지났는지 확인
> 3. `videoId`를 실제 영상 ID로 변경했는지 확인
> 4. 경품 정보와 수령 링크를 준비했는지 확인
> 5. GmailApp 사용을 위한 권한을 승인했는지 확인

---

## [바로 실습] 슬랙으로 실시간 알림 받기

지금까지는 이벤트 종료 후 일괄 처리하는 방식이었습니다. 이번에는 **실시간 알림** 시스템을 구축합니다. 구독자가 폼을 제출할 때마다 슬랙에 알림이 오도록 설정합니다.

### 폼 제출 트리거 설정

```javascript
/**
 * 폼 제출 시 자동 실행되는 트리거를 설정합니다.
 * 이 함수는 최초 1회만 실행하면 됩니다.
 */
function setupFormSubmitTrigger() {
  // 기존 폼 제출 트리거 제거 (중복 방지)
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'onFormSubmit') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 스프레드시트의 폼 제출 이벤트에 트리거 연결
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(SpreadsheetApp.getActiveSpreadsheet())
    .onFormSubmit()
    .create();
  
  Logger.log('폼 제출 트리거가 설정되었습니다.');
  Logger.log('이제 구독자가 폼을 제출할 때마다 onFormSubmit 함수가 자동 실행됩니다.');
}
```

### 폼 제출 시 슬랙 알림

```javascript
/**
 * 폼 제출 시 자동 실행되는 함수
 * @param {Object} e - 폼 제출 이벤트 객체
 */
function onFormSubmit(e) {
  try {
    var responses = e.namedValues;
    var webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_EVENT');
    
    if (!webhookUrl) {
      Logger.log('슬랙 웹훅 URL이 설정되지 않았습니다.');
      return;
    }
    
    // 참여자 정보 추출
    var nickname = responses['유튜브 닉네임'] ? responses['유튜브 닉네임'][0] : '알 수 없음';
    var email = responses['이메일 주소'] ? responses['이메일 주소'][0] : '알 수 없음';
    var videoUrl = responses['댓글을 남긴 영상 URL'] ? responses['댓글을 남긴 영상 URL'][0] : '알 수 없음';
    
    // 현재까지의 총 참여자 수 계산
    var formSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('폼 응답');
    var totalParticipants = formSheet ? formSheet.getLastRow() - 1 : 1;
    
    // 슬랙 알림 전송
    var payload = {
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: '📝 새 이벤트 참여!',
            emoji: true
          }
        },
        {
          type: 'section',
          fields: [
            { type: 'mrkdwn', text: '*👤 닉네임*\n' + nickname },
            { type: 'mrkdwn', text: '*📊 누적 참여자*\n' + totalParticipants + '명' }
          ]
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: '*🎬 영상:* ' + videoUrl
          }
        },
        {
          type: 'context',
          elements: [
            {
              type: 'mrkdwn',
              text: '📡 실시간 이벤트 알림 | ' + new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
            }
          ]
        }
      ],
      text: '새 이벤트 참여: ' + nickname + ' (누적 ' + totalParticipants + '명)'
    };
    
    sendSlackWithRetry(webhookUrl, payload);
    
  } catch (error) {
    Logger.log('폼 제출 알림 에러: ' + error.message);
  }
}
```

### 일일 이벤트 현황 요약 리포트

매일 정해진 시간에 이벤트 참여 현황을 요약 리포트로 발송합니다:

```javascript
/**
 * 이벤트 참여 현황 일일 요약 리포트를 슬랙으로 전송합니다.
 */
function sendEventDailySummary() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var formSheet = ss.getSheetByName('폼 응답');
  
  if (!formSheet || formSheet.getLastRow() <= 1) {
    Logger.log('폼 응답 데이터가 없습니다.');
    return;
  }
  
  var formData = formSheet.getDataRange().getValues();
  var allParticipants = formData.slice(1);
  var totalCount = allParticipants.length;
  
  // 오늘 참여자 수 계산
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  
  var todayCount = 0;
  allParticipants.forEach(function(row) {
    var timestamp = new Date(row[0]);
    if (timestamp >= today) {
      todayCount++;
    }
  });
  
  // 고유 닉네임 수 (중복 제거)
  var uniqueNicknames = {};
  allParticipants.forEach(function(row) {
    var nickname = String(row[1]).trim();
    uniqueNicknames[nickname] = true;
  });
  var uniqueCount = Object.keys(uniqueNicknames).length;
  
  // 중복 참여 수
  var duplicateCount = totalCount - uniqueCount;
  
  // 최근 5명의 참여자
  var recentParticipants = allParticipants.slice(-5).reverse().map(function(row) {
    return '• ' + String(row[1]).trim() + ' (' + new Date(row[0]).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul', hour: '2-digit', minute: '2-digit' }) + ')';
  }).join('\n');
  
  var webhookUrl = PropertiesService.getScriptProperties().getProperty('SLACK_WEBHOOK_EVENT');
  if (!webhookUrl) return;
  
  var dateStr = today.getFullYear() + '년 ' + (today.getMonth() + 1) + '월 ' + today.getDate() + '일';
  
  var payload = {
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: '📊 이벤트 일일 현황 리포트',
          emoji: true
        }
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*' + dateStr + ' 기준*'
        }
      },
      {
        type: 'section',
        fields: [
          { type: 'mrkdwn', text: '*📋 총 참여*\n' + totalCount + '건' },
          { type: 'mrkdwn', text: '*👤 고유 참여자*\n' + uniqueCount + '명' },
          { type: 'mrkdwn', text: '*📅 오늘 참여*\n' + todayCount + '건' },
          { type: 'mrkdwn', text: '*⚠️ 중복 참여*\n' + duplicateCount + '건' }
        ]
      },
      { type: 'divider' },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*🕐 최근 참여자*\n\n' + recentParticipants
        }
      },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: '📡 슈퍼유튜브시트 이벤트 리포트 | ' + new Date().toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
          }
        ]
      }
    ],
    text: '이벤트 일일 현황: 총 ' + totalCount + '건, 오늘 ' + todayCount + '건'
  };
  
  sendSlackWithRetry(webhookUrl, payload);
  Logger.log('이벤트 일일 요약 리포트 전송 완료');
}

/**
 * 일일 요약 리포트 트리거를 설정합니다.
 */
function setupDailySummaryTrigger() {
  // 기존 트리거 제거
  var triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'sendEventDailySummary') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // 매일 저녁 8시에 요약 리포트 전송
  ScriptApp.newTrigger('sendEventDailySummary')
    .timeBased()
    .everyDays(1)
    .atHour(20)
    .create();
  
  Logger.log('일일 요약 리포트 트리거 설정 완료 (매일 저녁 8시)');
}
```

---

## 전체 트리거 통합 설정

이벤트 시스템에 필요한 모든 트리거를 한 번에 설정하는 함수입니다:

```javascript
/**
 * 댓글 이벤트 시스템의 모든 트리거를 한번에 설정합니다.
 * 이벤트 시작 시 1회 실행하세요.
 */
function setupAllEventTriggers() {
  // 1. 폼 제출 실시간 알림
  setupFormSubmitTrigger();
  
  // 2. 일일 요약 리포트
  setupDailySummaryTrigger();
  
  Logger.log('========================================');
  Logger.log('모든 이벤트 트리거가 설정되었습니다.');
  Logger.log('========================================');
  Logger.log('1. 폼 제출 알림: 폼 제출 시 즉시 슬랙 알림');
  Logger.log('2. 일일 요약: 매일 저녁 8시 슬랙 리포트');
  Logger.log('========================================');
}

/**
 * 모든 이벤트 관련 트리거를 제거합니다.
 * 이벤트 종료 시 실행하세요.
 */
function removeAllEventTriggers() {
  var eventFunctions = ['onFormSubmit', 'sendEventDailySummary'];
  var triggers = ScriptApp.getProjectTriggers();
  var removed = 0;
  
  triggers.forEach(function(trigger) {
    if (eventFunctions.indexOf(trigger.getHandlerFunction()) !== -1) {
      ScriptApp.deleteTrigger(trigger);
      removed++;
    }
  });
  
  Logger.log('이벤트 트리거 ' + removed + '개가 제거되었습니다.');
}
```

---

## 이벤트 운영 워크플로우 정리

실제 이벤트를 운영할 때의 순서를 정리합니다:

### 이벤트 시작 단계

```
1. createEventForm() 실행 → 폼 생성
2. renameFormResponseSheet() 실행 → 시트 이름 정리
3. setupAllEventTriggers() 실행 → 트리거 설정
4. 영상 설명란/고정댓글에 폼 URL 게시
5. 이벤트 공지 및 참여 기간 안내
```

### 이벤트 진행 중

```
- 실시간: 폼 제출 시 슬랙 알림 자동 수신
- 매일 저녁 8시: 일일 참여 현황 요약 리포트 수신
- 필요 시: 중간 댓글 수집(collectVideoComments) 실행하여 참여 상태 모니터링
```

### 이벤트 종료 단계

```
1. runMyEvent() 실행 → 전체 프로세스 자동 실행
   (댓글 수집 → 검증 → 추첨 → 이메일 발송 → 슬랙 리포트)
2. removeAllEventTriggers() 실행 → 트리거 해제
3. 당첨 결과를 영상 고정댓글/커뮤니티 탭에 공지
```

---

## 시트 구조 요약

이번 장에서 생성/사용되는 시트 목록입니다:

| 시트 이름 | 용도 | 생성 시점 |
|-----------|------|----------|
| 폼 응답 | 구글 폼 응답 자동 기록 | createEventForm() 실행 시 |
| 댓글 목록 | 영상 댓글 수집 결과 | collectVideoComments() 실행 시 |
| 검증 결과 | 닉네임 대조 검증 결과 | verifyParticipants() 실행 시 |
| 당첨자 목록 | 추첨된 당첨자 정보 | selectWinners() 실행 시 |
| 실행 로그 | 프로세스 실행 이력 | runFullEventProcess() 실행 시 |

---

## 보안 및 개인정보 처리

이벤트 시스템에서 참여자의 이메일 주소를 수집하고 처리하므로 개인정보 보호에 주의해야 합니다.

### 필수 조치사항

1. **구글 폼에 개인정보 수집 동의 항목을 추가하세요.**
```javascript
// createEventForm() 함수에 다음을 추가할 수 있습니다:
form.addCheckboxItem()
  .setTitle('개인정보 수집 및 이용 동의')
  .setHelpText('이벤트 운영을 위해 닉네임, 이메일 주소를 수집합니다. 수집된 정보는 이벤트 종료 후 30일 이내에 파기됩니다.')
  .setChoices([
    form.addCheckboxItem().createChoice('동의합니다')
  ])
  .setRequired(true);
```

2. **이벤트 종료 후 개인정보를 삭제하세요.**
```javascript
/**
 * 이벤트 종료 후 개인정보가 포함된 시트를 정리합니다.
 * 이벤트 완전 종료 후 실행하세요.
 */
function cleanupEventData() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetsToClean = ['폼 응답', '검증 결과', '당첨자 목록'];
  
  sheetsToClean.forEach(function(sheetName) {
    var sheet = ss.getSheetByName(sheetName);
    if (sheet) {
      // 이메일 열의 데이터를 마스킹 처리
      var data = sheet.getDataRange().getValues();
      // 실제 구현 시 이메일 열 번호에 맞게 조정
      Logger.log(sheetName + ' 시트에 ' + (data.length - 1) + '행의 데이터가 있습니다.');
    }
  });
  
  Logger.log('개인정보 정리 작업을 수행하기 전에 당첨자 경품 수령이 완료되었는지 확인하세요.');
}
```

3. **스프레드시트 공유 설정을 확인하세요.** 이벤트 데이터가 포함된 스프레드시트는 **본인만 액세스 가능**하도록 공유 설정을 제한하세요.

---

## 마무리: 댓글 이벤트 자동화 체크리스트

| 항목 | 완료 여부 |
|------|----------|
| 이벤트 폼 자동 생성 함수 완성 | ☐ |
| 댓글 수집 함수 완성 (YouTube API 연동) | ☐ |
| 폼 응답-댓글 대조 검증 함수 완성 | ☐ |
| 당첨자 랜덤 추첨 함수 완성 | ☐ |
| 당첨자 이메일 발송 함수 완성 | ☐ |
| 전체 프로세스 통합 함수 완성 | ☐ |
| 폼 제출 실시간 슬랙 알림 설정 | ☐ |
| 일일 요약 리포트 트리거 설정 | ☐ |
| 개인정보 수집 동의 항목 추가 | ☐ |

이번 장에서 완성한 시스템은 **단순한 추첨 도구가 아닙니다.** 참여 접수, 자격 검증, 공정한 추첨, 결과 통보, 실시간 모니터링까지 댓글 이벤트의 전체 라이프사이클을 자동화한 시스템입니다.

이벤트를 여러 번 진행할수록 이 시스템의 가치는 더욱 커집니다. 첫 이벤트 때는 코드를 설정하는 시간이 필요하지만, 두 번째 이벤트부터는 `createEventForm()`과 `runMyEvent()`만 실행하면 됩니다. 이벤트가 반복될수록 절약되는 시간은 기하급수적으로 늘어납니다.

다음 Part 05에서는 노트북LM을 활용하여 유튜브 콘텐츠 기획과 분석을 한 단계 더 발전시키는 방법을 알아보겠습니다.
