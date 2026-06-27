# Chapter 09: 댓글 수집 및 분석하기

> 조회수와 좋아요는 영상의 성과를 보여주지만, 댓글은 시청자의 마음을 보여준다. 어떤 부분에 감동했는지, 무엇이 궁금한지, 다음에 어떤 영상을 원하는지—이 모든 정보가 댓글에 담겨 있다. 이번 장에서는 YouTube Data API를 사용해 댓글을 체계적으로 수집하고, 스프레드시트에서 분석하는 시스템을 구축한다.

---

## 9.1 유튜브에서 댓글 가져오는 방법

YouTube Data API에서 댓글을 가져오는 엔드포인트는 두 가지다.

### commentThreads.list

**최상위 댓글(top-level comments)**을 가져오는 API다. 각 댓글 스레드에는 원래 댓글과 대댓글 수 정보가 포함된다.

```
GET https://www.googleapis.com/youtube/v3/commentThreads
  ?part=snippet,replies
  &videoId={VIDEO_ID}
  &maxResults=100
  &order=relevance
  &key={API_KEY}
```

주요 파라미터:

| 파라미터 | 설명 | 비고 |
|---|---|---|
| part | snippet: 댓글 내용, replies: 대댓글 | replies는 최대 5개까지만 반환 |
| videoId | 영상 ID | 필수 |
| maxResults | 한 번에 가져올 수 (1~100) | 기본값 20 |
| order | 정렬 기준 | relevance(인기순) 또는 time(최신순) |
| pageToken | 다음 페이지 토큰 | 페이지네이션용 |
| searchTerms | 검색어 필터 | 특정 단어가 포함된 댓글만 |

### comments.list

**대댓글(replies)**을 가져오는 API다. 특정 댓글의 대댓글을 모두 가져올 때 사용한다.

```
GET https://www.googleapis.com/youtube/v3/comments
  ?part=snippet
  &parentId={COMMENT_ID}
  &maxResults=100
  &key={API_KEY}
```

### 댓글 데이터 구조

API가 반환하는 댓글 데이터의 구조를 이해하는 것이 중요하다.

```
commentThread
├── id: "스레드 ID"
├── snippet
│   ├── videoId: "영상 ID"
│   ├── topLevelComment
│   │   ├── id: "댓글 ID"
│   │   └── snippet
│   │       ├── authorDisplayName: "작성자"
│   │       ├── authorProfileImageUrl: "프로필 이미지"
│   │       ├── authorChannelUrl: "작성자 채널 URL"
│   │       ├── textDisplay: "댓글 내용 (HTML)"
│   │       ├── textOriginal: "댓글 내용 (원본)"
│   │       ├── likeCount: 좋아요 수
│   │       ├── publishedAt: "작성일"
│   │       └── updatedAt: "수정일"
│   └── totalReplyCount: 대댓글 수
└── replies
    └── comments: [대댓글 배열 (최대 5개)]
```

`commentThreads.list`의 `replies` 파트는 **최대 5개의 대댓글만** 포함한다. 대댓글이 5개를 초과하는 경우, `comments.list`를 별도로 호출해야 전체 대댓글을 가져올 수 있다.

### 댓글 수집의 제한사항

1. **댓글이 비활성화된 영상**: 일부 영상은 댓글을 끈 상태다. API 호출 시 403 에러가 발생한다.
2. **삭제되거나 비공개 영상**: 404 에러가 발생한다.
3. **스팸 필터링된 댓글**: API로는 가져올 수 없다.
4. **아동용 콘텐츠**: 아동용으로 설정된 영상은 댓글을 볼 수 없다.

---

## 9.2 할당량 이야기

댓글 수집에서 가장 중요한 것은 **API 할당량 관리**다.

### 비용 계산

| API 호출 | 단위 비용 | 한 번에 가져오는 양 | 설명 |
|---|---|---|---|
| commentThreads.list | 1 unit | 최대 100개 댓글 | 최상위 댓글 |
| comments.list | 1 unit | 최대 100개 대댓글 | 특정 댓글의 대댓글 |

일일 할당량 10,000 unit 기준으로 계산하면:

| 시나리오 | API 호출 수 | 총 비용 | 수집 가능 댓글 수 |
|---|---|---|---|
| 영상 1개, 최상위 댓글만 | 1~10 | 1~10 units | ~1,000개 |
| 영상 1개, 대댓글 포함 | 10~100 | 10~100 units | ~2,000개 |
| 영상 10개, 최상위만 (각 100개) | 10 | 10 units | 1,000개 |
| 영상 100개, 최상위만 (각 100개) | 100 | 100 units | 10,000개 |

**최상위 댓글만 수집하면 매우 효율적이다.** 1 unit으로 최대 100개 댓글을 가져올 수 있으므로, 하루에 최대 **100만 개의 댓글**을 수집할 수 있는 셈이다(이론적으로).

### 할당량 절약 전략

1. **필요한 만큼만 수집한다**: `maxResults`를 적절히 조절한다. 분석에 100개면 충분하다면 1,000개를 가져올 필요 없다.
2. **대댓글은 선택적으로 수집한다**: 대댓글이 많은 인기 댓글만 대댓글을 가져온다.
3. **order=relevance를 활용한다**: 인기순 정렬은 가장 의미 있는 댓글을 먼저 반환하므로, 적은 수로도 유의미한 분석이 가능하다.
4. **이미 수집한 댓글은 건너뛴다**: 댓글 ID를 기록해 두고, 중복 수집을 방지한다.

---

## 9.3 [바로 실습] 첫 댓글 수집하기

가장 기본적인 댓글 수집부터 시작하자. 영상 ID를 입력하면 댓글을 가져와 시트에 기록하는 함수다.

```javascript
/**
 * 영상의 댓글을 수집한다 (기본 버전).
 * 
 * @param {string} videoId - YouTube 영상 ID
 * @param {number} maxResults - 최대 수집 수 (1~100, 기본값 100)
 * @return {Array<Object>} 댓글 정보 배열
 */
function getVideoComments(videoId, maxResults) {
  maxResults = Math.min(maxResults || 100, 100);
  var apiKey = getApiKey_();
  
  var url = 'https://www.googleapis.com/youtube/v3/commentThreads'
    + '?part=snippet'
    + '&videoId=' + videoId
    + '&maxResults=' + maxResults
    + '&order=relevance'
    + '&textFormat=plainText'
    + '&key=' + apiKey;
  
  try {
    var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
  } catch (e) {
    // 댓글 비활성화 또는 영상 없음
    Logger.log('댓글 수집 실패 (' + videoId + '): ' + e.message);
    return [];
  }
  
  if (!response.items) return [];
  
  return response.items.map(function(item) {
    var comment = item.snippet.topLevelComment.snippet;
    return {
      commentId: item.snippet.topLevelComment.id,
      author: comment.authorDisplayName,
      authorChannelUrl: comment.authorChannelUrl || '',
      text: comment.textDisplay,
      likes: comment.likeCount,
      publishedAt: comment.publishedAt,
      updatedAt: comment.updatedAt,
      replyCount: item.snippet.totalReplyCount
    };
  });
}

/**
 * 영상 댓글을 시트에 기록한다.
 */
function collectCommentsToSheet() {
  var ui = SpreadsheetApp.getUi();
  
  var videoResult = ui.prompt(
    '댓글 수집',
    '영상 ID 또는 URL을 입력하세요:\n\n예: dQw4w9WgXcQ\n예: https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (videoResult.getSelectedButton() !== ui.Button.OK) return;
  
  var input = videoResult.getResponseText().trim();
  var videoId = extractVideoId_(input);
  
  if (!videoId) {
    ui.alert('올바른 영상 ID 또는 URL을 입력해 주세요.');
    return;
  }
  
  var comments = getVideoComments(videoId, 100);
  
  if (comments.length === 0) {
    ui.alert('댓글을 가져올 수 없습니다.\n댓글이 비활성화되었거나, 영상을 찾을 수 없습니다.');
    return;
  }
  
  // 시트 생성
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = '댓글_' + videoId;
  var sheet = ss.getSheetByName(sheetName);
  if (sheet) {
    sheet.clear();
  } else {
    sheet = ss.insertSheet(sheetName);
  }
  
  // 헤더
  var headers = ['작성자', '댓글 내용', '좋아요', '대댓글 수', '작성일', '댓글 ID'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground('#ea4335');
  headerRange.setFontColor('#ffffff');
  headerRange.setFontWeight('bold');
  headerRange.setHorizontalAlignment('center');
  sheet.setFrozenRows(1);
  
  // 데이터 기록
  var data = comments.map(function(c) {
    return [
      c.author,
      c.text,
      c.likes,
      c.replyCount,
      c.publishedAt.split('T')[0],
      c.commentId
    ];
  });
  
  sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
  
  // 서식
  sheet.setColumnWidth(1, 150);   // 작성자
  sheet.setColumnWidth(2, 500);   // 댓글 내용
  sheet.setColumnWidth(3, 80);    // 좋아요
  sheet.setColumnWidth(4, 90);    // 대댓글 수
  sheet.setColumnWidth(5, 100);   // 작성일
  sheet.setColumnWidth(6, 200);   // 댓글 ID
  
  sheet.getRange(2, 3, data.length, 2).setNumberFormat('#,##0');
  
  // 댓글 내용 줄바꿈 허용
  sheet.getRange(2, 2, data.length, 1).setWrap(true);
  
  ui.alert(comments.length + '개 댓글을 수집했습니다.\n시트: ' + sheetName);
  ss.setActiveSheet(sheet);
}

/**
 * 다양한 형식의 YouTube URL에서 영상 ID를 추출한다.
 * 
 * @param {string} input - 영상 URL 또는 ID
 * @return {string|null} 영상 ID
 */
function extractVideoId_(input) {
  if (!input) return null;
  
  // 이미 영상 ID인 경우 (11자 영숫자+하이픈+언더스코어)
  if (/^[\w-]{11}$/.test(input)) {
    return input;
  }
  
  // youtube.com/watch?v= 형식
  var match = input.match(/[?&]v=([\w-]{11})/);
  if (match) return match[1];
  
  // youtu.be/xxxxx 형식
  match = input.match(/youtu\.be\/([\w-]{11})/);
  if (match) return match[1];
  
  // youtube.com/embed/xxxxx 형식
  match = input.match(/youtube\.com\/embed\/([\w-]{11})/);
  if (match) return match[1];
  
  // youtube.com/shorts/xxxxx 형식
  match = input.match(/youtube\.com\/shorts\/([\w-]{11})/);
  if (match) return match[1];
  
  return null;
}
```

위 코드에서 몇 가지 핵심 포인트를 짚어보자.

1. **`textFormat=plainText`**: HTML 태그가 제거된 순수 텍스트를 받는다. 시트에 기록할 때 깔끔하다.
2. **`order=relevance`**: 좋아요가 많고 답글이 많은 "인기 댓글"이 먼저 온다. 분석에 더 유용하다.
3. **에러 처리**: 댓글이 비활성화된 영상이나 삭제된 영상에 대해 빈 배열을 반환한다.

---

## 9.4 [바로 실습] 더 많은 댓글 가져오기

`commentThreads.list`는 한 번에 최대 100개 댓글만 반환한다. 인기 영상에는 수천, 수만 개의 댓글이 달리므로 **페이지네이션(pagination)**을 구현해야 한다.

```javascript
/**
 * 영상의 댓글을 대량으로 수집한다 (페이지네이션 지원).
 * 
 * @param {string} videoId - YouTube 영상 ID
 * @param {number} targetCount - 목표 수집 수 (기본값 1000)
 * @param {string} order - 정렬 기준 ('relevance' 또는 'time')
 * @return {Array<Object>} 댓글 정보 배열
 */
function getVideoCommentsAll(videoId, targetCount, order) {
  targetCount = targetCount || 1000;
  order = order || 'relevance';
  var apiKey = getApiKey_();
  
  var allComments = [];
  var pageToken = '';
  var pageCount = 0;
  var maxPages = Math.ceil(targetCount / 100);  // 안전 장치
  
  do {
    var url = 'https://www.googleapis.com/youtube/v3/commentThreads'
      + '?part=snippet'
      + '&videoId=' + videoId
      + '&maxResults=100'
      + '&order=' + order
      + '&textFormat=plainText'
      + (pageToken ? '&pageToken=' + pageToken : '')
      + '&key=' + apiKey;
    
    try {
      var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    } catch (e) {
      Logger.log('댓글 수집 중단 (page ' + (pageCount + 1) + '): ' + e.message);
      break;
    }
    
    if (!response.items || response.items.length === 0) break;
    
    response.items.forEach(function(item) {
      var comment = item.snippet.topLevelComment.snippet;
      allComments.push({
        commentId: item.snippet.topLevelComment.id,
        author: comment.authorDisplayName,
        authorChannelUrl: comment.authorChannelUrl || '',
        text: comment.textDisplay,
        likes: comment.likeCount,
        publishedAt: comment.publishedAt,
        updatedAt: comment.updatedAt,
        replyCount: item.snippet.totalReplyCount
      });
    });
    
    pageToken = response.nextPageToken || '';
    pageCount++;
    
    Logger.log('댓글 수집 진행: ' + allComments.length + '개 (페이지 ' + pageCount + ')');
    
    // 목표 수에 도달하면 중단
    if (allComments.length >= targetCount) {
      allComments = allComments.slice(0, targetCount);
      break;
    }
    
    // API 속도 제한 방지 (100ms 대기)
    if (pageToken) {
      Utilities.sleep(100);
    }
    
  } while (pageToken && pageCount < maxPages);
  
  Logger.log('총 ' + allComments.length + '개 댓글 수집 완료 (API ' + pageCount + '회 호출)');
  return allComments;
}

/**
 * 대량 댓글 수집을 실행한다.
 */
function collectManyComments() {
  var ui = SpreadsheetApp.getUi();
  
  // 영상 ID 입력
  var videoResult = ui.prompt(
    '대량 댓글 수집',
    '영상 ID 또는 URL을 입력하세요:',
    ui.ButtonSet.OK_CANCEL
  );
  if (videoResult.getSelectedButton() !== ui.Button.OK) return;
  
  var videoId = extractVideoId_(videoResult.getResponseText().trim());
  if (!videoId) {
    ui.alert('올바른 영상 ID를 입력해 주세요.');
    return;
  }
  
  // 목표 수 입력
  var countResult = ui.prompt(
    '수집 수 설정',
    '몇 개의 댓글을 수집할까요?\n\n' +
    '- 100개: API 1회 호출 (1 unit)\n' +
    '- 500개: API 5회 호출 (5 units)\n' +
    '- 1000개: API 10회 호출 (10 units)\n' +
    '- 5000개: API 50회 호출 (50 units)\n\n' +
    '기본값: 500',
    ui.ButtonSet.OK_CANCEL
  );
  
  var targetCount = 500;
  if (countResult.getSelectedButton() === ui.Button.OK) {
    var parsed = parseInt(countResult.getResponseText());
    if (!isNaN(parsed) && parsed > 0) {
      targetCount = parsed;
    }
  }
  
  // 정렬 방식 선택
  var orderResult = ui.alert(
    '정렬 방식',
    '인기순으로 정렬할까요?\n\n' +
    "[예] 인기순 (좋아요가 많은 댓글 우선)\n" +
    "[아니요] 최신순 (최근 댓글 우선)",
    ui.ButtonSet.YES_NO
  );
  var order = orderResult === ui.Button.YES ? 'relevance' : 'time';
  
  // 수집 시작
  ui.alert('댓글 수집을 시작합니다.\n목표: ' + targetCount + '개\n잠시 기다려 주세요...');
  
  var comments = getVideoCommentsAll(videoId, targetCount, order);
  
  if (comments.length === 0) {
    ui.alert('댓글을 가져올 수 없습니다.');
    return;
  }
  
  // 시트에 기록
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = '댓글_' + videoId + '_' + comments.length;
  var sheet = ss.getSheetByName(sheetName);
  if (sheet) {
    sheet.clear();
  } else {
    sheet = ss.insertSheet(sheetName);
  }
  
  writeCommentsToSheet_(sheet, comments);
  
  ui.alert(comments.length + '개 댓글을 수집했습니다.\n시트: ' + sheetName);
  ss.setActiveSheet(sheet);
}

/**
 * 댓글 데이터를 시트에 기록한다 (공용 함수).
 * 
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet - 대상 시트
 * @param {Array<Object>} comments - 댓글 배열
 */
function writeCommentsToSheet_(sheet, comments) {
  var headers = ['작성자', '댓글 내용', '좋아요', '대댓글 수', '작성일', '수정일', '댓글 ID'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground('#ea4335');
  headerRange.setFontColor('#ffffff');
  headerRange.setFontWeight('bold');
  headerRange.setHorizontalAlignment('center');
  sheet.setFrozenRows(1);
  
  var data = comments.map(function(c) {
    return [
      c.author,
      c.text,
      c.likes,
      c.replyCount,
      c.publishedAt ? c.publishedAt.split('T')[0] : '',
      c.updatedAt ? c.updatedAt.split('T')[0] : '',
      c.commentId
    ];
  });
  
  // 성능을 위해 한 번에 기록
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
  }
  
  // 서식 적용
  sheet.setColumnWidth(1, 150);
  sheet.setColumnWidth(2, 500);
  sheet.setColumnWidth(3, 80);
  sheet.setColumnWidth(4, 90);
  sheet.setColumnWidth(5, 100);
  sheet.setColumnWidth(6, 100);
  sheet.setColumnWidth(7, 200);
  
  sheet.getRange(2, 3, data.length, 2).setNumberFormat('#,##0');
  sheet.getRange(2, 2, data.length, 1).setWrap(true);
}
```

### 실행 시간에 관한 중요한 참고사항

Google Apps Script는 **6분(360초) 실행 시간 제한**이 있다. 댓글 1만 개를 수집하려면 API를 100번 호출해야 하고, 네트워크 지연까지 고려하면 약 30~60초가 소요된다. 일반적인 수집 규모에서는 문제가 되지 않지만, 댓글이 수만 개인 영상을 수집하려면 분할 수집 전략이 필요하다.

```javascript
/**
 * 대용량 댓글 수집을 여러 번에 나눠 실행한다.
 * ScriptProperties에 pageToken을 저장하여 이어서 수집한다.
 * 
 * @param {string} videoId - 영상 ID
 * @param {number} batchSize - 한 번에 수집할 수 (기본값 2000)
 */
function collectCommentsInBatches(videoId, batchSize) {
  batchSize = batchSize || 2000;
  var apiKey = getApiKey_();
  var props = PropertiesService.getScriptProperties();
  
  // 이전 수집 상태 확인
  var stateKey = 'COMMENT_BATCH_' + videoId;
  var state = props.getProperty(stateKey);
  var pageToken = '';
  var totalCollected = 0;
  
  if (state) {
    var parsed = JSON.parse(state);
    pageToken = parsed.pageToken;
    totalCollected = parsed.totalCollected;
    Logger.log('이전 수집 이어서 진행: ' + totalCollected + '개 수집 완료 상태');
  }
  
  var comments = [];
  var batchCount = 0;
  var maxBatchCalls = Math.ceil(batchSize / 100);
  
  do {
    var url = 'https://www.googleapis.com/youtube/v3/commentThreads'
      + '?part=snippet'
      + '&videoId=' + videoId
      + '&maxResults=100'
      + '&order=time'
      + '&textFormat=plainText'
      + (pageToken ? '&pageToken=' + pageToken : '')
      + '&key=' + apiKey;
    
    try {
      var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    } catch (e) {
      Logger.log('API 호출 실패: ' + e.message);
      break;
    }
    
    if (!response.items) break;
    
    response.items.forEach(function(item) {
      var c = item.snippet.topLevelComment.snippet;
      comments.push({
        commentId: item.snippet.topLevelComment.id,
        author: c.authorDisplayName,
        authorChannelUrl: c.authorChannelUrl || '',
        text: c.textDisplay,
        likes: c.likeCount,
        publishedAt: c.publishedAt,
        updatedAt: c.updatedAt,
        replyCount: item.snippet.totalReplyCount
      });
    });
    
    pageToken = response.nextPageToken || '';
    batchCount++;
    
    if (batchCount % 10 === 0) {
      Logger.log('배치 진행: ' + comments.length + '개 수집');
    }
    
    Utilities.sleep(100);
    
  } while (pageToken && batchCount < maxBatchCalls);
  
  // 시트에 기록 (기존 데이터 뒤에 추가)
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = '댓글_' + videoId;
  var sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
    writeCommentsToSheet_(sheet, comments);
  } else {
    // 기존 데이터 뒤에 추가
    var lastRow = sheet.getLastRow();
    var data = comments.map(function(c) {
      return [c.author, c.text, c.likes, c.replyCount,
        c.publishedAt ? c.publishedAt.split('T')[0] : '',
        c.updatedAt ? c.updatedAt.split('T')[0] : '',
        c.commentId];
    });
    if (data.length > 0) {
      sheet.getRange(lastRow + 1, 1, data.length, data[0].length).setValues(data);
    }
  }
  
  totalCollected += comments.length;
  
  // 상태 저장
  if (pageToken) {
    props.setProperty(stateKey, JSON.stringify({
      pageToken: pageToken,
      totalCollected: totalCollected
    }));
    Logger.log('배치 수집 완료. 누적: ' + totalCollected + '개. 다음 배치를 실행해 주세요.');
    SpreadsheetApp.getUi().alert(
      '이번 배치: ' + comments.length + '개 수집\n' +
      '누적: ' + totalCollected + '개\n\n' +
      '아직 더 많은 댓글이 있습니다.\n같은 함수를 다시 실행하면 이어서 수집합니다.'
    );
  } else {
    props.deleteProperty(stateKey);
    Logger.log('모든 댓글 수집 완료. 총: ' + totalCollected + '개');
    SpreadsheetApp.getUi().alert('모든 댓글 수집 완료!\n총 ' + totalCollected + '개');
  }
}
```

---

## 9.5 [바로 실습] 대댓글도 함께 가져오기

최상위 댓글만으로는 전체 토론 맥락을 파악하기 어렵다. 대댓글까지 수집하면 시청자들 사이의 대화를 분석할 수 있다.

### 대댓글 수집 함수

```javascript
/**
 * 특정 댓글의 대댓글을 모두 가져온다.
 * 
 * @param {string} commentId - 부모 댓글 ID
 * @return {Array<Object>} 대댓글 배열
 */
function getCommentReplies(commentId) {
  var apiKey = getApiKey_();
  var replies = [];
  var pageToken = '';
  
  do {
    var url = 'https://www.googleapis.com/youtube/v3/comments'
      + '?part=snippet'
      + '&parentId=' + commentId
      + '&maxResults=100'
      + '&textFormat=plainText'
      + (pageToken ? '&pageToken=' + pageToken : '')
      + '&key=' + apiKey;
    
    try {
      var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    } catch (e) {
      Logger.log('대댓글 수집 실패 (' + commentId + '): ' + e.message);
      break;
    }
    
    if (!response.items) break;
    
    response.items.forEach(function(item) {
      replies.push({
        commentId: item.id,
        parentId: commentId,
        author: item.snippet.authorDisplayName,
        authorChannelUrl: item.snippet.authorChannelUrl || '',
        text: item.snippet.textDisplay,
        likes: item.snippet.likeCount,
        publishedAt: item.snippet.publishedAt,
        updatedAt: item.snippet.updatedAt
      });
    });
    
    pageToken = response.nextPageToken || '';
    
    if (pageToken) {
      Utilities.sleep(100);
    }
    
  } while (pageToken);
  
  return replies;
}
```

### 댓글 + 대댓글 통합 수집

```javascript
/**
 * 영상의 댓글과 대댓글을 함께 수집한다.
 * 대댓글이 있는 댓글만 대댓글을 추가로 가져온다.
 * 
 * @param {string} videoId - 영상 ID
 * @param {number} maxTopLevel - 최상위 댓글 최대 수 (기본값 200)
 * @param {number} minRepliesToFetch - 대댓글이 이 수 이상인 댓글만 대댓글 수집 (기본값 1)
 * @return {Array<Object>} 댓글 + 대댓글 배열 (depth 정보 포함)
 */
function getCommentsWithReplies(videoId, maxTopLevel, minRepliesToFetch) {
  maxTopLevel = maxTopLevel || 200;
  minRepliesToFetch = minRepliesToFetch || 1;
  
  // 최상위 댓글 수집
  var topComments = getVideoCommentsAll(videoId, maxTopLevel, 'relevance');
  Logger.log('최상위 댓글 ' + topComments.length + '개 수집');
  
  // 결과 배열 (depth 정보 포함)
  var allComments = [];
  var repliesCollected = 0;
  
  topComments.forEach(function(comment) {
    // 최상위 댓글 추가
    comment.depth = 0;
    comment.parentId = '';
    allComments.push(comment);
    
    // 대댓글이 minRepliesToFetch 이상인 경우만 대댓글 수집
    if (comment.replyCount >= minRepliesToFetch) {
      var replies = getCommentReplies(comment.commentId);
      replies.forEach(function(reply) {
        reply.depth = 1;
        reply.replyCount = 0;
        allComments.push(reply);
      });
      repliesCollected += replies.length;
      
      // API 속도 제한 방지
      Utilities.sleep(100);
    }
  });
  
  Logger.log('총 수집: 최상위 ' + topComments.length + '개 + 대댓글 ' + repliesCollected + '개 = ' + allComments.length + '개');
  return allComments;
}

/**
 * 댓글 + 대댓글을 시트에 트리 구조로 기록한다.
 * 대댓글은 들여쓰기로 구분한다.
 */
function collectCommentsWithRepliesToSheet() {
  var ui = SpreadsheetApp.getUi();
  
  var videoResult = ui.prompt(
    '댓글 + 대댓글 수집',
    '영상 ID 또는 URL을 입력하세요:',
    ui.ButtonSet.OK_CANCEL
  );
  if (videoResult.getSelectedButton() !== ui.Button.OK) return;
  
  var videoId = extractVideoId_(videoResult.getResponseText().trim());
  if (!videoId) {
    ui.alert('올바른 영상 ID를 입력해 주세요.');
    return;
  }
  
  var countResult = ui.prompt(
    '수집 설정',
    '최상위 댓글 몇 개까지 수집할까요? (기본값: 200)\n\n' +
    '대댓글이 있는 댓글은 자동으로 대댓글도 수집합니다.',
    ui.ButtonSet.OK_CANCEL
  );
  
  var maxTopLevel = 200;
  if (countResult.getSelectedButton() === ui.Button.OK) {
    var parsed = parseInt(countResult.getResponseText());
    if (!isNaN(parsed) && parsed > 0) maxTopLevel = parsed;
  }
  
  // 수집
  var allComments = getCommentsWithReplies(videoId, maxTopLevel, 1);
  
  if (allComments.length === 0) {
    ui.alert('댓글을 수집할 수 없습니다.');
    return;
  }
  
  // 시트 생성
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = '댓글트리_' + videoId;
  var sheet = ss.getSheetByName(sheetName);
  if (sheet) {
    sheet.clear();
  } else {
    sheet = ss.insertSheet(sheetName);
  }
  
  // 헤더
  var headers = ['구분', '작성자', '댓글 내용', '좋아요', '대댓글 수', '작성일', '댓글 ID'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground('#ea4335');
  headerRange.setFontColor('#ffffff');
  headerRange.setFontWeight('bold');
  sheet.setFrozenRows(1);
  
  // 데이터 기록 (트리 구조 시각화)
  var data = allComments.map(function(c) {
    var prefix = c.depth === 0 ? '💬' : '  ↳';
    var displayText = c.depth === 1 ? '    ' + c.text : c.text;
    
    return [
      prefix,
      c.author,
      displayText,
      c.likes,
      c.replyCount || 0,
      c.publishedAt ? c.publishedAt.split('T')[0] : '',
      c.commentId
    ];
  });
  
  sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
  
  // 대댓글 행 배경색 구분
  for (var i = 0; i < allComments.length; i++) {
    if (allComments[i].depth === 1) {
      sheet.getRange(i + 2, 1, 1, headers.length).setBackground('#f8f9fa');
    }
  }
  
  // 서식
  sheet.setColumnWidth(1, 50);
  sheet.setColumnWidth(2, 150);
  sheet.setColumnWidth(3, 500);
  sheet.setColumnWidth(4, 80);
  sheet.setColumnWidth(5, 90);
  sheet.setColumnWidth(6, 100);
  sheet.setColumnWidth(7, 200);
  
  sheet.getRange(2, 3, data.length, 1).setWrap(true);
  sheet.getRange(2, 4, data.length, 2).setNumberFormat('#,##0');
  
  var topCount = allComments.filter(function(c) { return c.depth === 0; }).length;
  var replyCount = allComments.length - topCount;
  
  ui.alert(
    '댓글 수집 완료!\n\n' +
    '최상위 댓글: ' + topCount + '개\n' +
    '대댓글: ' + replyCount + '개\n' +
    '합계: ' + allComments.length + '개\n\n' +
    '시트: ' + sheetName
  );
  
  ss.setActiveSheet(sheet);
}
```

---

## 9.6 [바로 실습] 댓글 분석하기

댓글을 수집하는 것 자체로도 가치 있지만, 진짜 인사이트는 **분석**에서 나온다. 별도의 AI 도구 없이도 스프레드시트와 Apps Script만으로 의미 있는 분석이 가능하다.

### 감성 키워드 분석

```javascript
/**
 * 댓글의 감성 키워드를 분석한다.
 * 미리 정의한 긍정/부정 키워드 사전을 기반으로 분류한다.
 * 
 * @param {string} commentSheetName - 댓글 데이터 시트 이름
 */
function analyzeCommentSentiment(commentSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(commentSheetName);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다: ' + commentSheetName);
    return;
  }
  
  // 감성 키워드 사전
  var positiveKeywords = [
    '감사', '고마', '최고', '대박', '좋아', '좋은', '훌륭', '멋지', '멋진',
    '잘했', '잘한', '유익', '도움', '배웠', '배울', '인정', '추천', '완벽',
    '재밌', '재미있', '웃기', '사랑', '응원', '화이팅', '파이팅', '구독',
    '기대', '기다리', 'ㅋㅋ', 'ㅎㅎ', '꿀팁', '정리', '깔끔'
  ];
  
  var negativeKeywords = [
    '별로', '싫', '실망', '아쉬', '부족', '이상한', '틀린', '잘못',
    '짜증', '화나', '지루', '노잼', '광고', '어그로', '낚시', '구라',
    '거짓', '사기', '쓰레기', '최악', 'ㅡㅡ', '그만', '취소', '환불'
  ];
  
  var questionKeywords = [
    '어떻게', '어디서', '왜', '뭐', '무엇', '얼마', '언제',
    '알려', '궁금', '질문', '방법', '하나요', '인가요', '할까요',
    '되나요', '있나요', '없나요', '모르', '?'
  ];
  
  var requestKeywords = [
    '해주세요', '해 주세요', '다뤄', '만들어', '올려', '부탁',
    '다음에', '다음 영상', '시리즈', '콘텐츠', '주제', '요청'
  ];
  
  var data = sheet.getDataRange().getValues();
  var stats = {
    total: 0,
    positive: 0,
    negative: 0,
    question: 0,
    request: 0,
    neutral: 0,
    positiveKeywordCounts: {},
    negativeKeywordCounts: {},
    questionKeywordCounts: {},
    requestKeywordCounts: {}
  };
  
  // 댓글 내용 열 인덱스 찾기 (보통 2번째 열, 인덱스 1)
  var textColIndex = 1;
  for (var h = 0; h < data[0].length; h++) {
    if (data[0][h] === '댓글 내용') {
      textColIndex = h;
      break;
    }
  }
  
  // 각 댓글 분석
  for (var i = 1; i < data.length; i++) {
    var text = String(data[i][textColIndex]).toLowerCase();
    if (!text) continue;
    
    stats.total++;
    
    var isPositive = false, isNegative = false;
    var isQuestion = false, isRequest = false;
    
    // 긍정 키워드 체크
    positiveKeywords.forEach(function(kw) {
      if (text.indexOf(kw) > -1) {
        isPositive = true;
        stats.positiveKeywordCounts[kw] = (stats.positiveKeywordCounts[kw] || 0) + 1;
      }
    });
    
    // 부정 키워드 체크
    negativeKeywords.forEach(function(kw) {
      if (text.indexOf(kw) > -1) {
        isNegative = true;
        stats.negativeKeywordCounts[kw] = (stats.negativeKeywordCounts[kw] || 0) + 1;
      }
    });
    
    // 질문 키워드 체크
    questionKeywords.forEach(function(kw) {
      if (text.indexOf(kw) > -1) {
        isQuestion = true;
        stats.questionKeywordCounts[kw] = (stats.questionKeywordCounts[kw] || 0) + 1;
      }
    });
    
    // 요청 키워드 체크
    requestKeywords.forEach(function(kw) {
      if (text.indexOf(kw) > -1) {
        isRequest = true;
        stats.requestKeywordCounts[kw] = (stats.requestKeywordCounts[kw] || 0) + 1;
      }
    });
    
    // 분류 (중복 가능하지만 대표 1개로)
    if (isPositive && !isNegative) stats.positive++;
    else if (isNegative && !isPositive) stats.negative++;
    else if (isQuestion) stats.question++;
    else if (isRequest) stats.request++;
    else stats.neutral++;
  }
  
  // 결과 시트 작성
  var analysisSheetName = commentSheetName + '_분석';
  var analysisSheet = ss.getSheetByName(analysisSheetName);
  if (analysisSheet) {
    analysisSheet.clear();
  } else {
    analysisSheet = ss.insertSheet(analysisSheetName);
  }
  
  var row = 1;
  
  // 제목
  analysisSheet.getRange(row, 1).setValue('댓글 감성 분석 결과');
  analysisSheet.getRange(row, 1).setFontSize(16).setFontWeight('bold');
  row += 2;
  
  // 요약 통계
  var summary = [
    ['분류', '댓글 수', '비율'],
    ['전체 댓글', stats.total, '100%'],
    ['긍정 댓글', stats.positive, (stats.positive / stats.total * 100).toFixed(1) + '%'],
    ['부정 댓글', stats.negative, (stats.negative / stats.total * 100).toFixed(1) + '%'],
    ['질문 댓글', stats.question, (stats.question / stats.total * 100).toFixed(1) + '%'],
    ['요청 댓글', stats.request, (stats.request / stats.total * 100).toFixed(1) + '%'],
    ['중립/기타', stats.neutral, (stats.neutral / stats.total * 100).toFixed(1) + '%']
  ];
  
  analysisSheet.getRange(row, 1, summary.length, 3).setValues(summary);
  analysisSheet.getRange(row, 1, 1, 3).setBackground('#4285f4').setFontColor('#fff').setFontWeight('bold');
  
  // 긍정 행 색상
  analysisSheet.getRange(row + 2, 1, 1, 3).setBackground('#e6f4ea');
  // 부정 행 색상
  analysisSheet.getRange(row + 3, 1, 1, 3).setBackground('#fce8e6');
  
  row += summary.length + 2;
  
  // 자주 등장하는 키워드 (상위 10개씩)
  var sections = [
    { title: '자주 등장하는 긍정 키워드', data: stats.positiveKeywordCounts, color: '#34a853' },
    { title: '자주 등장하는 부정 키워드', data: stats.negativeKeywordCounts, color: '#ea4335' },
    { title: '자주 등장하는 질문 키워드', data: stats.questionKeywordCounts, color: '#fbbc04' },
    { title: '자주 등장하는 요청 키워드', data: stats.requestKeywordCounts, color: '#4285f4' }
  ];
  
  sections.forEach(function(section) {
    analysisSheet.getRange(row, 1).setValue(section.title);
    analysisSheet.getRange(row, 1, 1, 2).merge().setBackground(section.color)
      .setFontColor('#ffffff').setFontWeight('bold');
    row++;
    
    analysisSheet.getRange(row, 1, 1, 2).setValues([['키워드', '등장 횟수']]);
    analysisSheet.getRange(row, 1, 1, 2).setFontWeight('bold');
    row++;
    
    var sorted = Object.keys(section.data)
      .sort(function(a, b) { return section.data[b] - section.data[a]; })
      .slice(0, 10);
    
    sorted.forEach(function(kw) {
      analysisSheet.getRange(row, 1, 1, 2).setValues([[kw, section.data[kw]]]);
      row++;
    });
    
    row += 1;
  });
  
  // 열 너비
  analysisSheet.setColumnWidth(1, 200);
  analysisSheet.setColumnWidth(2, 120);
  analysisSheet.setColumnWidth(3, 100);
  
  SpreadsheetApp.getUi().alert('댓글 분석이 완료되었습니다.\n시트: ' + analysisSheetName);
  ss.setActiveSheet(analysisSheet);
}
```

### 활발한 댓글 작성자 분석

어떤 시청자가 가장 활발하게 참여하는지 파악하면, 충성 팬을 식별할 수 있다.

```javascript
/**
 * 가장 활발한 댓글 작성자를 분석한다.
 * 
 * @param {string} commentSheetName - 댓글 데이터 시트 이름
 */
function analyzeTopCommenters(commentSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(commentSheetName);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다.');
    return;
  }
  
  var data = sheet.getDataRange().getValues();
  
  // 작성자 열 인덱스 찾기
  var authorColIndex = 0;
  var likesColIndex = 2;
  for (var h = 0; h < data[0].length; h++) {
    if (data[0][h] === '작성자') authorColIndex = h;
    if (data[0][h] === '좋아요') likesColIndex = h;
  }
  
  // 작성자별 통계 집계
  var authorStats = {};
  
  for (var i = 1; i < data.length; i++) {
    var author = String(data[i][authorColIndex]);
    var likes = Number(data[i][likesColIndex]) || 0;
    
    if (!author) continue;
    
    if (!authorStats[author]) {
      authorStats[author] = { count: 0, totalLikes: 0 };
    }
    authorStats[author].count++;
    authorStats[author].totalLikes += likes;
  }
  
  // 댓글 수 기준 상위 20명 정렬
  var topAuthors = Object.keys(authorStats)
    .map(function(name) {
      return {
        name: name,
        count: authorStats[name].count,
        totalLikes: authorStats[name].totalLikes,
        avgLikes: (authorStats[name].totalLikes / authorStats[name].count).toFixed(1)
      };
    })
    .sort(function(a, b) { return b.count - a.count; })
    .slice(0, 20);
  
  // 결과 시트
  var resultSheetName = commentSheetName + '_작성자분석';
  var resultSheet = ss.getSheetByName(resultSheetName);
  if (resultSheet) {
    resultSheet.clear();
  } else {
    resultSheet = ss.insertSheet(resultSheetName);
  }
  
  // 헤더
  var headers = [['순위', '작성자', '댓글 수', '받은 좋아요 합계', '평균 좋아요']];
  resultSheet.getRange(1, 1, 1, 5).setValues(headers);
  resultSheet.getRange(1, 1, 1, 5)
    .setBackground('#673ab7')
    .setFontColor('#ffffff')
    .setFontWeight('bold');
  
  // 데이터
  var tableData = topAuthors.map(function(a, idx) {
    return [idx + 1, a.name, a.count, a.totalLikes, a.avgLikes];
  });
  
  if (tableData.length > 0) {
    resultSheet.getRange(2, 1, tableData.length, 5).setValues(tableData);
    resultSheet.getRange(2, 3, tableData.length, 3).setNumberFormat('#,##0');
  }
  
  // 열 너비
  resultSheet.setColumnWidth(1, 60);
  resultSheet.setColumnWidth(2, 200);
  resultSheet.setColumnWidth(3, 100);
  resultSheet.setColumnWidth(4, 140);
  resultSheet.setColumnWidth(5, 110);
  
  SpreadsheetApp.getUi().alert('활발한 댓글 작성자 Top 20\n시트: ' + resultSheetName);
  ss.setActiveSheet(resultSheet);
}
```

### 인기 댓글 Top 10 (좋아요 순)

```javascript
/**
 * 좋아요를 가장 많이 받은 댓글 Top 10을 정리한다.
 * 
 * @param {string} commentSheetName - 댓글 데이터 시트 이름
 */
function getTopLikedComments(commentSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(commentSheetName);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다.');
    return;
  }
  
  var data = sheet.getDataRange().getValues();
  
  // 열 인덱스 찾기
  var authorIdx = 0, textIdx = 1, likesIdx = 2, dateIdx = 4;
  for (var h = 0; h < data[0].length; h++) {
    if (data[0][h] === '작성자') authorIdx = h;
    if (data[0][h] === '댓글 내용') textIdx = h;
    if (data[0][h] === '좋아요') likesIdx = h;
    if (data[0][h] === '작성일') dateIdx = h;
  }
  
  // 좋아요 기준 정렬
  var comments = [];
  for (var i = 1; i < data.length; i++) {
    comments.push({
      author: data[i][authorIdx],
      text: data[i][textIdx],
      likes: Number(data[i][likesIdx]) || 0,
      date: data[i][dateIdx]
    });
  }
  
  comments.sort(function(a, b) { return b.likes - a.likes; });
  var top10 = comments.slice(0, 10);
  
  // 결과 시트
  var resultSheetName = commentSheetName + '_인기댓글';
  var resultSheet = ss.getSheetByName(resultSheetName);
  if (resultSheet) {
    resultSheet.clear();
  } else {
    resultSheet = ss.insertSheet(resultSheetName);
  }
  
  // 제목
  resultSheet.getRange(1, 1).setValue('인기 댓글 Top 10 (좋아요 순)');
  resultSheet.getRange(1, 1, 1, 4).merge().setFontSize(14).setFontWeight('bold')
    .setBackground('#1a73e8').setFontColor('#ffffff');
  
  // 헤더
  resultSheet.getRange(2, 1, 1, 4).setValues([['순위', '작성자', '댓글 내용', '좋아요']]);
  resultSheet.getRange(2, 1, 1, 4).setFontWeight('bold').setBackground('#f1f3f4');
  
  // 데이터
  var tableData = top10.map(function(c, idx) {
    return [idx + 1, c.author, c.text, c.likes];
  });
  
  if (tableData.length > 0) {
    resultSheet.getRange(3, 1, tableData.length, 4).setValues(tableData);
    resultSheet.getRange(3, 4, tableData.length, 1).setNumberFormat('#,##0');
    resultSheet.getRange(3, 3, tableData.length, 1).setWrap(true);
  }
  
  // 열 너비
  resultSheet.setColumnWidth(1, 60);
  resultSheet.setColumnWidth(2, 180);
  resultSheet.setColumnWidth(3, 500);
  resultSheet.setColumnWidth(4, 100);
  
  SpreadsheetApp.getUi().alert('인기 댓글 Top 10을 정리했습니다.\n시트: ' + resultSheetName);
  ss.setActiveSheet(resultSheet);
}
```

### 댓글 시간대 분석

댓글이 언제 달리는지 분석하면, 시청자의 활동 패턴을 파악할 수 있다.

```javascript
/**
 * 댓글의 시간대별 분포를 분석한다.
 * 
 * @param {string} commentSheetName - 댓글 데이터 시트 이름
 */
function analyzeCommentTimeline(commentSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(commentSheetName);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다.');
    return;
  }
  
  var data = sheet.getDataRange().getValues();
  
  // 작성일 열 인덱스 찾기
  var dateColIndex = 4;
  for (var h = 0; h < data[0].length; h++) {
    if (data[0][h] === '작성일') {
      dateColIndex = h;
      break;
    }
  }
  
  // 날짜별 댓글 수 집계
  var dailyCounts = {};
  var totalDays = 0;
  
  for (var i = 1; i < data.length; i++) {
    var dateStr = String(data[i][dateColIndex]);
    if (!dateStr || dateStr === 'undefined') continue;
    
    // YYYY-MM-DD 형식으로 정규화
    var dateKey = dateStr.substring(0, 10);
    dailyCounts[dateKey] = (dailyCounts[dateKey] || 0) + 1;
  }
  
  // 날짜 정렬
  var sortedDates = Object.keys(dailyCounts).sort();
  
  if (sortedDates.length === 0) {
    SpreadsheetApp.getUi().alert('분석할 날짜 데이터가 없습니다.');
    return;
  }
  
  // 결과 시트
  var resultSheetName = commentSheetName + '_시간분석';
  var resultSheet = ss.getSheetByName(resultSheetName);
  if (resultSheet) {
    resultSheet.clear();
  } else {
    resultSheet = ss.insertSheet(resultSheetName);
  }
  
  var row = 1;
  
  // 제목
  resultSheet.getRange(row, 1).setValue('댓글 시간대 분석');
  resultSheet.getRange(row, 1).setFontSize(16).setFontWeight('bold');
  row += 2;
  
  // 요약 통계
  var totalComments = data.length - 1;
  var firstDate = sortedDates[0];
  var lastDate = sortedDates[sortedDates.length - 1];
  var daySpan = Math.ceil(
    (new Date(lastDate) - new Date(firstDate)) / (1000 * 60 * 60 * 24)
  ) + 1;
  
  var summaryData = [
    ['총 댓글 수', totalComments],
    ['첫 댓글 날짜', firstDate],
    ['마지막 댓글 날짜', lastDate],
    ['기간 (일)', daySpan],
    ['일 평균 댓글', (totalComments / daySpan).toFixed(1)]
  ];
  
  resultSheet.getRange(row, 1, summaryData.length, 2).setValues(summaryData);
  row += summaryData.length + 2;
  
  // 업로드 후 경과일별 댓글 수 (첫 7일)
  resultSheet.getRange(row, 1).setValue('영상 업로드 후 댓글 추이');
  resultSheet.getRange(row, 1, 1, 2).merge().setFontWeight('bold').setBackground('#e8f0fe');
  row++;
  
  resultSheet.getRange(row, 1, 1, 2).setValues([['날짜', '댓글 수']]).setFontWeight('bold');
  row++;
  
  // 처음 날짜 기준 7일간의 댓글 수
  var earlyDates = sortedDates.slice(0, Math.min(14, sortedDates.length));
  earlyDates.forEach(function(d) {
    resultSheet.getRange(row, 1, 1, 2).setValues([[d, dailyCounts[d]]]);
    row++;
  });
  
  if (sortedDates.length > 14) {
    resultSheet.getRange(row, 1, 1, 2).setValues([['... (이후 생략)', '']]);
    row++;
  }
  
  row += 1;
  
  // 가장 댓글이 많은 날
  resultSheet.getRange(row, 1).setValue('댓글이 가장 많은 날 Top 5');
  resultSheet.getRange(row, 1, 1, 2).merge().setFontWeight('bold').setBackground('#e8f0fe');
  row++;
  
  var topDays = sortedDates
    .sort(function(a, b) { return dailyCounts[b] - dailyCounts[a]; })
    .slice(0, 5);
  
  topDays.forEach(function(d, idx) {
    resultSheet.getRange(row, 1, 1, 2).setValues([[d, dailyCounts[d]]]);
    row++;
  });
  
  // 열 너비
  resultSheet.setColumnWidth(1, 200);
  resultSheet.setColumnWidth(2, 120);
  
  SpreadsheetApp.getUi().alert('댓글 시간대 분석이 완료되었습니다.\n시트: ' + resultSheetName);
  ss.setActiveSheet(resultSheet);
}
```

---

## 9.7 메뉴 통합

댓글 관련 기능을 메뉴에 추가한다. 앞 장의 `onOpen` 함수를 확장한다.

```javascript
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  
  ui.createMenu('슈퍼유튜브시트')
    .addSubMenu(ui.createMenu('벤치마킹')
      .addItem('키워드로 채널 검색', 'showChannelSearchDialog')
      .addItem('벤치마킹 채널 등록', 'showAddBenchmarkDialog')
      .addSeparator()
      .addItem('선택 채널 영상 수집', 'collectSelectedChannelVideos')
      .addItem('전체 채널 영상 수집', 'collectAllBenchmarkChannels')
      .addSeparator()
      .addItem('업로드 패턴 분석', 'showUploadPatternAnalysis')
      .addItem('인기 영상 Top 10', 'showTop10Analysis')
    )
    .addSubMenu(ui.createMenu('댓글 분석')
      .addItem('댓글 수집 (기본)', 'collectCommentsToSheet')
      .addItem('대량 댓글 수집', 'collectManyComments')
      .addItem('댓글 + 대댓글 수집', 'collectCommentsWithRepliesToSheet')
      .addSeparator()
      .addItem('감성 키워드 분석', 'showCommentAnalysis')
      .addItem('활발한 작성자 분석', 'showTopCommentersAnalysis')
      .addItem('인기 댓글 Top 10', 'showTopLikedCommentsAnalysis')
      .addItem('댓글 시간대 분석', 'showCommentTimelineAnalysis')
    )
    .addToUi();
}

/**
 * 댓글 분석 실행 헬퍼: 댓글 시트를 선택하고 분석 함수를 실행한다.
 */
function showCommentAnalysis() {
  runCommentAnalysisFunction_('감성 키워드 분석', analyzeCommentSentiment);
}

function showTopCommentersAnalysis() {
  runCommentAnalysisFunction_('활발한 작성자 분석', analyzeTopCommenters);
}

function showTopLikedCommentsAnalysis() {
  runCommentAnalysisFunction_('인기 댓글 Top 10', getTopLikedComments);
}

function showCommentTimelineAnalysis() {
  runCommentAnalysisFunction_('댓글 시간대 분석', analyzeCommentTimeline);
}

/**
 * 댓글 분석 함수를 실행하기 위한 공용 래퍼.
 * 댓글 시트를 선택하는 대화상자를 표시한 뒤, 지정된 분석 함수를 호출한다.
 * 
 * @param {string} title - 대화상자 제목
 * @param {Function} analysisFunction - 실행할 분석 함수
 */
function runCommentAnalysisFunction_(title, analysisFunction) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  var commentSheets = sheets.map(function(s) { return s.getName(); })
    .filter(function(name) {
      return name.indexOf('댓글') > -1 && name.indexOf('분석') === -1
        && name.indexOf('작성자') === -1 && name.indexOf('인기') === -1
        && name.indexOf('시간') === -1;
    });
  
  if (commentSheets.length === 0) {
    SpreadsheetApp.getUi().alert('댓글 데이터 시트가 없습니다.\n먼저 댓글을 수집해 주세요.');
    return;
  }
  
  var ui = SpreadsheetApp.getUi();
  var result = ui.prompt(
    title,
    '분석할 댓글 시트 이름을 입력하세요:\n\n' + commentSheets.join('\n'),
    ui.ButtonSet.OK_CANCEL
  );
  
  if (result.getSelectedButton() === ui.Button.OK) {
    var sheetName = result.getResponseText().trim();
    if (sheetName) {
      analysisFunction(sheetName);
    }
  }
}
```

---

## 정리

이번 장에서 구현한 기능을 정리한다.

| 기능 | 함수명 | API 비용 |
|---|---|---|
| 기본 댓글 수집 (100개) | `getVideoComments()` | 1 unit |
| 대량 댓글 수집 (페이지네이션) | `getVideoCommentsAll()` | 1 unit / 100개 |
| 배치 댓글 수집 (6분 제한 대응) | `collectCommentsInBatches()` | 1 unit / 100개 |
| 대댓글 수집 | `getCommentReplies()` | 1 unit / 100개 |
| 댓글 + 대댓글 통합 수집 | `getCommentsWithReplies()` | 가변 |
| 감성 키워드 분석 | `analyzeCommentSentiment()` | 0 units |
| 활발한 작성자 분석 | `analyzeTopCommenters()` | 0 units |
| 인기 댓글 Top 10 | `getTopLikedComments()` | 0 units |
| 댓글 시간대 분석 | `analyzeCommentTimeline()` | 0 units |

핵심 포인트:

1. **`commentThreads.list`는 1 unit으로 100개 댓글을 가져오므로 매우 경제적이다.** 일일 할당량 10,000 unit으로 이론상 100만 개의 댓글을 수집할 수 있다.
2. **대댓글은 `comments.list`로 별도 수집해야 한다.** `commentThreads.list`의 `replies` 파트는 최대 5개만 반환한다.
3. **감성 분석은 키워드 사전 방식으로도 충분히 유용하다.** 별도 AI API 없이 한국어 댓글의 톤을 대략적으로 파악할 수 있다.
4. **6분 실행 시간 제한에 대비하여 배치 수집 패턴을 구현했다.** `ScriptProperties`에 상태를 저장하고 이어서 수집하는 방식이다.

다음 장에서는 수집한 채널 데이터와 댓글 데이터를 종합하여, 대시보드를 만들고 정기적으로 자동 업데이트하는 시스템을 구축한다.
