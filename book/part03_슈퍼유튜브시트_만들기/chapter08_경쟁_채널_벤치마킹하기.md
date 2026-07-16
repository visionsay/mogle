# Chapter 08: 경쟁 채널 벤치마킹하기

> "적을 알고 나를 알면 백전불태." 유튜브에서도 마찬가지다. 경쟁 채널이 어떤 전략으로 성장하고 있는지 데이터로 파악할 수 있다면, 우리 채널의 방향을 잡는 데 결정적인 단서가 된다. 이번 장에서는 Google Sheets와 YouTube Data API를 활용해 경쟁 채널의 모든 데이터를 체계적으로 수집하고 분석하는 시스템을 구축한다.

---

## 8.1 채널 분석 기능 이해하기

벤치마킹이라는 말을 들으면 거창하게 느껴질 수 있지만, 핵심은 단순하다. **경쟁 채널의 공개 데이터를 수집하고, 패턴을 발견하고, 우리 채널에 적용할 인사이트를 뽑아내는 것**이다.

YouTube Data API를 통해 수집할 수 있는 채널 데이터는 다음과 같다.

| 데이터 항목 | API 엔드포인트 | part 파라미터 |
|---|---|---|
| 구독자 수 | channels.list | statistics |
| 총 조회수 | channels.list | statistics |
| 총 영상 수 | channels.list | statistics |
| 채널 설명, 키워드 | channels.list | snippet, brandingSettings |
| 업로드 재생목록 ID | channels.list | contentDetails |
| 개별 영상 목록 | playlistItems.list | contentDetails |
| 영상별 조회수, 좋아요, 댓글 수 | videos.list | statistics |
| 영상 길이, 태그, 카테고리 | videos.list | contentDetails, snippet |

이 데이터들을 조합하면 다음과 같은 분석이 가능하다.

- **업로드 빈도**: 주당/월당 몇 개의 영상을 올리는가?
- **평균 조회수**: 최근 영상의 평균 퍼포먼스는 어떤가?
- **참여율(Engagement Rate)**: (좋아요 + 댓글) / 조회수 비율
- **인기 콘텐츠 패턴**: 어떤 제목, 길이, 카테고리의 영상이 잘 되는가?
- **성장 추세**: 최근 영상과 과거 영상의 퍼포먼스 차이
- **최적 업로드 시간**: 어떤 요일, 시간대에 영상을 올리는가?

이 모든 것을 수작업으로 하려면 며칠이 걸리겠지만, 우리는 Apps Script로 몇 분 만에 처리할 것이다.

### 할당량 계산

벤치마킹 과정에서 소모되는 API 할당량을 미리 계산해 보자.

| 작업 | API 호출 | 단위 비용 | 영상 500개 채널 기준 |
|---|---|---|---|
| 채널 정보 조회 | channels.list | 1 unit | 1 unit |
| 영상 ID 목록 수집 | playlistItems.list | 1 unit/50개 | 10 units |
| 영상 상세 정보 수집 | videos.list | 1 unit/50개 | 10 units |
| **합계** | | | **21 units** |

영상 500개짜리 채널 하나를 완전히 분석하는 데 약 21 unit이면 된다. 일일 할당량 10,000 unit 기준으로 **하루에 400개 이상의 채널**을 분석할 수 있는 셈이다. search.list를 사용하면 호출당 100 unit이 소모되므로, 채널 검색은 최소한으로 하고 나머지는 playlistItems.list 전략을 사용하는 것이 핵심이다.

---

## 8.2 [바로 실습] 키워드로 채널 검색하기

경쟁 채널을 분석하려면 먼저 어떤 채널이 있는지 찾아야 한다. YouTube Data API의 `search.list`를 사용하면 키워드로 채널을 검색할 수 있다.

> **주의**: `search.list`는 호출당 **100 unit**을 소모한다. 일일 할당량 10,000 unit 기준으로 하루에 100번만 호출 가능하다. 채널 검색은 필요할 때만 신중하게 사용하자.

### 기본 채널 검색 함수

```javascript
/**
 * 키워드로 YouTube 채널을 검색한다.
 * search.list 호출 1회 = 100 unit 소모
 * 
 * @param {string} keyword - 검색 키워드
 * @param {number} maxResults - 최대 결과 수 (1~50, 기본값 10)
 * @return {Array<Object>} 채널 정보 배열
 */
function searchChannels(keyword, maxResults) {
  maxResults = maxResults || 10;
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  if (!apiKey) {
    throw new Error('YOUTUBE_API_KEY가 설정되지 않았습니다. 스크립트 속성에서 API 키를 등록해 주세요.');
  }
  
  // Step 1: search.list로 채널 ID 목록 가져오기 (100 units)
  const searchUrl = 'https://www.googleapis.com/youtube/v3/search'
    + '?part=snippet'
    + '&q=' + encodeURIComponent(keyword)
    + '&type=channel'
    + '&maxResults=' + maxResults
    + '&key=' + apiKey;
  
  const searchResponse = JSON.parse(UrlFetchApp.fetch(searchUrl).getContentText());
  
  if (!searchResponse.items || searchResponse.items.length === 0) {
    Logger.log('검색 결과가 없습니다: ' + keyword);
    return [];
  }
  
  // Step 2: 검색된 채널 ID로 상세 정보 가져오기 (1 unit)
  const channelIds = searchResponse.items.map(function(item) {
    return item.snippet.channelId;
  }).join(',');
  
  const channelUrl = 'https://www.googleapis.com/youtube/v3/channels'
    + '?part=snippet,statistics,brandingSettings'
    + '&id=' + channelIds
    + '&key=' + apiKey;
  
  const channelResponse = JSON.parse(UrlFetchApp.fetch(channelUrl).getContentText());
  
  // Step 3: 결과 가공
  var results = channelResponse.items.map(function(ch) {
    var stats = ch.statistics;
    var subscriberCount = stats.hiddenSubscriberCount ? '비공개' : Number(stats.subscriberCount);
    var viewCount = Number(stats.viewCount);
    var videoCount = Number(stats.videoCount);
    var avgViews = videoCount > 0 ? Math.round(viewCount / videoCount) : 0;
    
    return {
      channelId: ch.id,
      title: ch.snippet.title,
      description: ch.snippet.description,
      customUrl: ch.snippet.customUrl || '',
      thumbnail: ch.snippet.thumbnails.medium.url,
      subscriberCount: subscriberCount,
      viewCount: viewCount,
      videoCount: videoCount,
      avgViewsPerVideo: avgViews,
      publishedAt: ch.snippet.publishedAt,
      country: ch.snippet.country || '미설정',
      keywords: ch.brandingSettings && ch.brandingSettings.channel
        ? ch.brandingSettings.channel.keywords || ''
        : ''
    };
  });
  
  return results;
}
```

### 검색 결과를 시트에 출력하기

```javascript
/**
 * 키워드로 채널을 검색하고 결과를 시트에 출력한다.
 * 
 * @param {string} keyword - 검색 키워드
 * @param {number} maxResults - 최대 결과 수
 */
function searchChannelsToSheet(keyword, maxResults) {
  keyword = keyword || '요리 유튜버';
  maxResults = maxResults || 10;
  
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = '채널검색_' + keyword;
  var sheet = ss.getSheetByName(sheetName);
  
  if (!sheet) {
    sheet = ss.insertSheet(sheetName);
  } else {
    sheet.clear();
  }
  
  // 헤더 작성
  var headers = [
    '썸네일', '채널명', '구독자 수', '총 조회수', '영상 수',
    '영상당 평균 조회수', '채널 개설일', '국가', '채널 ID', '채널 URL'
  ];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  
  // 헤더 스타일 적용
  var headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setBackground('#1a73e8');
  headerRange.setFontColor('#ffffff');
  headerRange.setFontWeight('bold');
  headerRange.setHorizontalAlignment('center');
  
  // 검색 실행
  var channels = searchChannels(keyword, maxResults);
  
  if (channels.length === 0) {
    SpreadsheetApp.getUi().alert('검색 결과가 없습니다.');
    return;
  }
  
  // 데이터 작성
  var data = channels.map(function(ch) {
    return [
      '=IMAGE("' + ch.thumbnail + '")',
      ch.title,
      ch.subscriberCount,
      ch.viewCount,
      ch.videoCount,
      ch.avgViewsPerVideo,
      ch.publishedAt.split('T')[0],
      ch.country,
      ch.channelId,
      ch.customUrl ? 'https://www.youtube.com/' + ch.customUrl : ''
    ];
  });
  
  sheet.getRange(2, 1, data.length, data[0].length).setValues(data);
  
  // 숫자 서식 적용
  sheet.getRange(2, 3, data.length, 4).setNumberFormat('#,##0');
  
  // 열 너비 조정
  sheet.setColumnWidth(1, 120);  // 썸네일
  sheet.setColumnWidth(2, 200);  // 채널명
  sheet.setColumnWidth(3, 120);  // 구독자
  sheet.setColumnWidth(4, 130);  // 총 조회수
  
  // 행 높이 조정 (썸네일 표시)
  for (var i = 2; i <= data.length + 1; i++) {
    sheet.setRowHeight(i, 68);
  }
  
  Logger.log(channels.length + '개 채널을 검색했습니다.');
  SpreadsheetApp.getUi().alert(channels.length + '개 채널을 찾았습니다.');
}
```

### 메뉴에서 검색 실행하기

사용자가 메뉴에서 편리하게 검색할 수 있도록 대화상자를 추가한다.

```javascript
/**
 * 채널 검색 대화상자를 표시한다.
 */
function showChannelSearchDialog() {
  var ui = SpreadsheetApp.getUi();
  
  var keywordResult = ui.prompt(
    '채널 검색',
    '검색할 키워드를 입력하세요:',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (keywordResult.getSelectedButton() !== ui.Button.OK) return;
  var keyword = keywordResult.getResponseText().trim();
  if (!keyword) {
    ui.alert('키워드를 입력해 주세요.');
    return;
  }
  
  var countResult = ui.prompt(
    '검색 결과 수',
    '최대 몇 개의 채널을 검색할까요? (1~50, 기본값: 10)\n※ search.list 1회 호출 = 100 unit 소모',
    ui.ButtonSet.OK_CANCEL
  );
  
  var maxResults = 10;
  if (countResult.getSelectedButton() === ui.Button.OK) {
    var parsed = parseInt(countResult.getResponseText());
    if (!isNaN(parsed) && parsed >= 1 && parsed <= 50) {
      maxResults = parsed;
    }
  }
  
  searchChannelsToSheet(keyword, maxResults);
}
```

---

## 8.3 [바로 실습] 벤치마킹 채널 등록하기

채널 검색을 통해 관심 채널을 발견했다면, 이제 "벤치마킹" 시트에 등록하여 지속적으로 추적할 수 있게 만들자. 사용자는 채널 URL을 그대로 붙여넣기만 하면 된다.

### 채널 URL 파싱

YouTube 채널 URL은 여러 형식이 존재한다. 모든 형식을 처리해야 사용자 편의성이 높아진다.

```javascript
/**
 * 다양한 형식의 YouTube 채널 URL에서 채널 ID를 추출한다.
 * 
 * 지원하는 형식:
 * - https://www.youtube.com/channel/UCxxxxxx
 * - https://www.youtube.com/@handle
 * - https://www.youtube.com/c/customname
 * - https://youtube.com/@handle
 * - 채널 ID 직접 입력 (UC로 시작하는 24자)
 * 
 * @param {string} input - 채널 URL 또는 채널 ID
 * @return {string|null} 채널 ID 또는 null
 */
function parseChannelUrl(input) {
  var apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  input = input.trim();
  
  // Case 1: 이미 채널 ID인 경우 (UC로 시작, 24자)
  if (/^UC[\w-]{22}$/.test(input)) {
    return input;
  }
  
  // Case 2: /channel/UCxxxxxx 형식
  var channelMatch = input.match(/youtube\.com\/channel\/(UC[\w-]{22})/);
  if (channelMatch) {
    return channelMatch[1];
  }
  
  // Case 3: /@handle 형식
  var handleMatch = input.match(/youtube\.com\/@([\w.-]+)/);
  if (handleMatch) {
    return resolveHandleToChannelId_(handleMatch[1], apiKey);
  }
  
  // Case 4: /c/customname 형식
  var customMatch = input.match(/youtube\.com\/c\/([\w.-]+)/);
  if (customMatch) {
    return resolveCustomUrlToChannelId_(customMatch[1], apiKey);
  }
  
  // Case 5: /user/username 형식 (레거시)
  var userMatch = input.match(/youtube\.com\/user\/([\w.-]+)/);
  if (userMatch) {
    return resolveUsernameToChannelId_(userMatch[1], apiKey);
  }
  
  // Case 6: @handle만 입력한 경우 (URL 없이)
  if (/^@[\w.-]+$/.test(input)) {
    return resolveHandleToChannelId_(input.substring(1), apiKey);
  }
  
  Logger.log('인식할 수 없는 URL 형식: ' + input);
  return null;
}

/**
 * @handle을 채널 ID로 변환한다.
 * channels.list의 forHandle 파라미터를 사용한다.
 */
function resolveHandleToChannelId_(handle, apiKey) {
  var url = 'https://www.googleapis.com/youtube/v3/channels'
    + '?part=id'
    + '&forHandle=' + encodeURIComponent(handle)
    + '&key=' + apiKey;
  
  try {
    var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    if (response.items && response.items.length > 0) {
      return response.items[0].id;
    }
  } catch (e) {
    Logger.log('Handle 조회 실패: ' + handle + ', 에러: ' + e.message);
  }
  return null;
}

/**
 * 커스텀 URL을 채널 ID로 변환한다.
 * search.list를 사용한다 (100 unit 소모).
 */
function resolveCustomUrlToChannelId_(customName, apiKey) {
  var url = 'https://www.googleapis.com/youtube/v3/search'
    + '?part=snippet'
    + '&q=' + encodeURIComponent(customName)
    + '&type=channel'
    + '&maxResults=1'
    + '&key=' + apiKey;
  
  try {
    var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    if (response.items && response.items.length > 0) {
      return response.items[0].snippet.channelId;
    }
  } catch (e) {
    Logger.log('커스텀 URL 조회 실패: ' + customName);
  }
  return null;
}

/**
 * 레거시 username을 채널 ID로 변환한다.
 */
function resolveUsernameToChannelId_(username, apiKey) {
  var url = 'https://www.googleapis.com/youtube/v3/channels'
    + '?part=id'
    + '&forUsername=' + encodeURIComponent(username)
    + '&key=' + apiKey;
  
  try {
    var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
    if (response.items && response.items.length > 0) {
      return response.items[0].id;
    }
  } catch (e) {
    Logger.log('Username 조회 실패: ' + username);
  }
  return null;
}
```

### 벤치마킹 시트 초기화 및 채널 등록

```javascript
/**
 * 벤치마킹 시트를 초기화한다.
 * 이미 존재하면 그대로 사용한다.
 * 
 * @return {GoogleAppsScript.Spreadsheet.Sheet} 벤치마킹 시트
 */
function initBenchmarkSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('벤치마킹');
  
  if (!sheet) {
    sheet = ss.insertSheet('벤치마킹');
    
    var headers = [
      '등록일', '채널명', '채널 ID', '구독자 수', '총 조회수',
      '영상 수', '영상당 평균 조회수', '채널 URL', '마지막 수집일', '메모'
    ];
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    var headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setBackground('#34a853');
    headerRange.setFontColor('#ffffff');
    headerRange.setFontWeight('bold');
    headerRange.setHorizontalAlignment('center');
    sheet.setFrozenRows(1);
    
    // 열 너비 설정
    var widths = [100, 180, 200, 120, 140, 80, 140, 250, 120, 200];
    widths.forEach(function(w, i) {
      sheet.setColumnWidth(i + 1, w);
    });
  }
  
  return sheet;
}

/**
 * 채널 URL 또는 ID를 벤치마킹 시트에 등록한다.
 * 
 * @param {string} input - 채널 URL 또는 채널 ID
 */
function addBenchmarkChannel(input) {
  var channelId = parseChannelUrl(input);
  
  if (!channelId) {
    SpreadsheetApp.getUi().alert(
      '채널을 찾을 수 없습니다.\n입력값: ' + input +
      '\n\n지원 형식:\n- https://www.youtube.com/@handle\n- https://www.youtube.com/channel/UCxxxx\n- 채널 ID (UC로 시작)'
    );
    return;
  }
  
  var sheet = initBenchmarkSheet_();
  
  // 이미 등록된 채널인지 확인
  var existingData = sheet.getDataRange().getValues();
  for (var i = 1; i < existingData.length; i++) {
    if (existingData[i][2] === channelId) {
      SpreadsheetApp.getUi().alert('이미 등록된 채널입니다: ' + existingData[i][1]);
      return;
    }
  }
  
  // 채널 상세 정보 조회
  var apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  var url = 'https://www.googleapis.com/youtube/v3/channels'
    + '?part=snippet,statistics'
    + '&id=' + channelId
    + '&key=' + apiKey;
  
  var response = JSON.parse(UrlFetchApp.fetch(url).getContentText());
  
  if (!response.items || response.items.length === 0) {
    SpreadsheetApp.getUi().alert('채널 정보를 가져올 수 없습니다.');
    return;
  }
  
  var ch = response.items[0];
  var stats = ch.statistics;
  var videoCount = Number(stats.videoCount);
  var viewCount = Number(stats.viewCount);
  var subscriberCount = stats.hiddenSubscriberCount ? '비공개' : Number(stats.subscriberCount);
  
  var row = [
    new Date(),
    ch.snippet.title,
    channelId,
    subscriberCount,
    viewCount,
    videoCount,
    videoCount > 0 ? Math.round(viewCount / videoCount) : 0,
    'https://www.youtube.com/channel/' + channelId,
    '',
    ''
  ];
  
  sheet.appendRow(row);
  
  // 숫자 서식 적용
  var lastRow = sheet.getLastRow();
  sheet.getRange(lastRow, 4, 1, 4).setNumberFormat('#,##0');
  sheet.getRange(lastRow, 1).setNumberFormat('yyyy-mm-dd');
  
  SpreadsheetApp.getUi().alert('채널 등록 완료: ' + ch.snippet.title);
  Logger.log('벤치마킹 채널 등록: ' + ch.snippet.title + ' (' + channelId + ')');
}

/**
 * 대화상자를 통해 벤치마킹 채널을 등록한다.
 */
function showAddBenchmarkDialog() {
  var ui = SpreadsheetApp.getUi();
  var result = ui.prompt(
    '벤치마킹 채널 등록',
    '채널 URL 또는 채널 ID를 입력하세요:\n\n예시:\n- https://www.youtube.com/@channelhandle\n- https://www.youtube.com/channel/UCxxxxxx\n- @channelhandle',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (result.getSelectedButton() === ui.Button.OK) {
    var input = result.getResponseText().trim();
    if (input) {
      addBenchmarkChannel(input);
    }
  }
}
```

---

## 8.4 [바로 실습] 저장 시트 선택창 만들기

수집한 데이터를 저장할 시트를 사용자가 선택할 수 있게 만들자. 기존 시트에 추가하거나, 새 시트를 만들 수 있는 유연한 인터페이스를 구축한다.

### HTML 사이드바 방식

```javascript
/**
 * 시트 선택 사이드바를 표시한다.
 * 채널 영상 수집 시 저장할 시트를 선택하는 용도이다.
 * 
 * @param {string} channelId - 수집 대상 채널 ID
 * @param {string} channelTitle - 채널명 (표시용)
 */
function showSheetSelector(channelId, channelTitle) {
  var html = HtmlService.createHtmlOutput(getSheetSelectorHtml_(channelId, channelTitle))
    .setTitle('저장 시트 선택')
    .setWidth(320);
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * 시트 선택기 HTML을 생성한다.
 */
function getSheetSelectorHtml_(channelId, channelTitle) {
  var sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  var sheetOptions = sheets.map(function(s) {
    return '<option value="' + s.getName() + '">' + s.getName() + '</option>';
  }).join('\n');
  
  return '\
  <!DOCTYPE html>\
  <html>\
  <head>\
    <style>\
      body { font-family: Arial, sans-serif; padding: 16px; }\
      h3 { color: #1a73e8; margin-bottom: 4px; }\
      .channel-name { color: #555; font-size: 14px; margin-bottom: 20px; }\
      label { display: block; margin: 12px 0 4px; font-weight: bold; color: #333; }\
      select, input[type="text"] {\
        width: 100%; padding: 8px; border: 1px solid #ddd;\
        border-radius: 4px; font-size: 14px; box-sizing: border-box;\
      }\
      .radio-group { margin: 12px 0; }\
      .radio-group label { display: inline; font-weight: normal; margin-left: 4px; }\
      button {\
        width: 100%; padding: 10px; margin-top: 16px;\
        background: #1a73e8; color: white; border: none;\
        border-radius: 4px; font-size: 14px; cursor: pointer;\
      }\
      button:hover { background: #1557b0; }\
      #status { margin-top: 12px; color: #666; font-size: 13px; }\
    </style>\
  </head>\
  <body>\
    <h3>저장 시트 선택</h3>\
    <p class="channel-name">채널: ' + channelTitle + '</p>\
    <div class="radio-group">\
      <input type="radio" name="mode" id="existing" value="existing" checked>\
      <label for="existing">기존 시트에 저장</label><br>\
      <input type="radio" name="mode" id="new" value="new">\
      <label for="new">새 시트 만들기</label>\
    </div>\
    <div id="existingSection">\
      <label for="sheetSelect">시트 선택:</label>\
      <select id="sheetSelect">' + sheetOptions + '</select>\
    </div>\
    <div id="newSection" style="display:none">\
      <label for="newSheetName">새 시트 이름:</label>\
      <input type="text" id="newSheetName" value="' + channelTitle + '_영상목록">\
    </div>\
    <button onclick="startCollection()">수집 시작</button>\
    <div id="status"></div>\
    <script>\
      document.querySelectorAll("input[name=mode]").forEach(function(radio) {\
        radio.addEventListener("change", function() {\
          document.getElementById("existingSection").style.display =\
            this.value === "existing" ? "block" : "none";\
          document.getElementById("newSection").style.display =\
            this.value === "new" ? "block" : "none";\
        });\
      });\
      function startCollection() {\
        var mode = document.querySelector("input[name=mode]:checked").value;\
        var sheetName = mode === "existing"\
          ? document.getElementById("sheetSelect").value\
          : document.getElementById("newSheetName").value;\
        document.getElementById("status").innerText = "수집 중...";\
        google.script.run\
          .withSuccessHandler(function(result) {\
            document.getElementById("status").innerText = result;\
          })\
          .withFailureHandler(function(err) {\
            document.getElementById("status").innerText = "오류: " + err.message;\
          })\
          .collectChannelVideosToSheet("' + channelId + '", sheetName, mode === "new");\
      }\
    </script>\
  </body>\
  </html>';
}

/**
 * 선택된 시트에 채널 영상을 수집한다.
 * 사이드바에서 호출된다.
 * 
 * @param {string} channelId - 채널 ID
 * @param {string} sheetName - 시트 이름
 * @param {boolean} createNew - 새 시트를 만들지 여부
 * @return {string} 결과 메시지
 */
function collectChannelVideosToSheet(channelId, sheetName, createNew) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet;
  
  if (createNew) {
    sheet = ss.getSheetByName(sheetName);
    if (sheet) {
      sheet.clear();
    } else {
      sheet = ss.insertSheet(sheetName);
    }
  } else {
    sheet = ss.getSheetByName(sheetName);
    if (!sheet) {
      throw new Error('시트를 찾을 수 없습니다: ' + sheetName);
    }
  }
  
  var videos = getAllChannelVideos(channelId);
  writeVideosToSheet_(sheet, videos, createNew);
  
  // 벤치마킹 시트의 마지막 수집일 업데이트
  updateLastCollectedDate_(channelId);
  
  return videos.length + '개 영상을 수집했습니다.';
}
```

---

## 8.5 [바로 실습] 벤치마킹 채널 전체 영상 수집하기

이제 이번 장의 핵심 기능, **채널의 전체 영상을 수집하는 함수**를 구현한다. 여기서 가장 중요한 것은 API 할당량 효율이다.

### 왜 playlistItems.list를 사용하는가?

채널 영상을 가져오는 방법은 크게 두 가지다.

| 방법 | API | 단위 비용 | 영상 500개 비용 | 제한 |
|---|---|---|---|---|
| search.list | search | 100 unit/호출 | 1,000 units | 최대 500개 결과 |
| playlistItems.list | playlistItems | 1 unit/호출 | 10 units | 제한 없음 |

**playlistItems.list가 100배 효율적이다.** 모든 YouTube 채널에는 자동으로 생성되는 "uploads" 재생목록이 있고, 이 목록에는 채널의 모든 공개 영상이 업로드 역순으로 들어 있다.

### 전체 영상 수집 구현

```javascript
/**
 * API 키를 안전하게 가져오는 헬퍼 함수
 * @return {string} YouTube Data API 키
 */
function getApiKey_() {
  var key = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  if (!key) {
    throw new Error('YOUTUBE_API_KEY가 설정되지 않았습니다.');
  }
  return key;
}

/**
 * 채널의 전체 영상 정보를 수집한다.
 * 
 * API 호출 전략:
 * 1. channels.list로 업로드 재생목록 ID 조회 (1 unit)
 * 2. playlistItems.list로 전체 영상 ID 수집 (1 unit / 50개)
 * 3. videos.list로 영상 상세 정보 조회 (1 unit / 50개)
 * 
 * 영상 500개 기준 총 ~21 unit 소모
 * 
 * @param {string} channelId - YouTube 채널 ID
 * @return {Array<Object>} 영상 정보 배열
 */
function getAllChannelVideos(channelId) {
  var apiKey = getApiKey_();
  
  // Step 1: 업로드 재생목록 ID 가져오기 (1 unit)
  var channelUrl = 'https://www.googleapis.com/youtube/v3/channels'
    + '?part=contentDetails,snippet'
    + '&id=' + channelId
    + '&key=' + apiKey;
  
  var channelResponse = JSON.parse(UrlFetchApp.fetch(channelUrl).getContentText());
  
  if (!channelResponse.items || channelResponse.items.length === 0) {
    throw new Error('채널을 찾을 수 없습니다: ' + channelId);
  }
  
  var channelTitle = channelResponse.items[0].snippet.title;
  var uploadsPlaylistId = channelResponse.items[0].contentDetails.relatedPlaylists.uploads;
  Logger.log('채널: ' + channelTitle + ', 업로드 재생목록: ' + uploadsPlaylistId);
  
  // Step 2: 전체 영상 ID 수집 (1 unit / 50개)
  var videoIds = [];
  var pageToken = '';
  var pageCount = 0;
  
  do {
    var playlistUrl = 'https://www.googleapis.com/youtube/v3/playlistItems'
      + '?part=contentDetails,snippet'
      + '&playlistId=' + uploadsPlaylistId
      + '&maxResults=50'
      + (pageToken ? '&pageToken=' + pageToken : '')
      + '&key=' + apiKey;
    
    var playlistResponse = JSON.parse(UrlFetchApp.fetch(playlistUrl).getContentText());
    
    playlistResponse.items.forEach(function(item) {
      videoIds.push(item.contentDetails.videoId);
    });
    
    pageToken = playlistResponse.nextPageToken || '';
    pageCount++;
    Logger.log('재생목록 페이지 ' + pageCount + ' 처리 완료. 누적 영상 수: ' + videoIds.length);
    
  } while (pageToken);
  
  Logger.log('총 ' + videoIds.length + '개 영상 ID 수집 완료');
  
  // Step 3: 영상 상세 정보 조회 (1 unit / 50개)
  var allVideos = [];
  
  for (var i = 0; i < videoIds.length; i += 50) {
    var batchIds = videoIds.slice(i, i + 50).join(',');
    var videosUrl = 'https://www.googleapis.com/youtube/v3/videos'
      + '?part=snippet,statistics,contentDetails'
      + '&id=' + batchIds
      + '&key=' + apiKey;
    
    var videosResponse = JSON.parse(UrlFetchApp.fetch(videosUrl).getContentText());
    
    videosResponse.items.forEach(function(video) {
      var stats = video.statistics;
      var viewCount = Number(stats.viewCount || 0);
      var likeCount = Number(stats.likeCount || 0);
      var commentCount = Number(stats.commentCount || 0);
      var engagement = viewCount > 0
        ? ((likeCount + commentCount) / viewCount * 100).toFixed(2)
        : '0.00';
      
      allVideos.push({
        videoId: video.id,
        title: video.snippet.title,
        description: video.snippet.description,
        publishedAt: video.snippet.publishedAt,
        thumbnail: video.snippet.thumbnails.medium
          ? video.snippet.thumbnails.medium.url
          : video.snippet.thumbnails.default.url,
        tags: video.snippet.tags ? video.snippet.tags.join(', ') : '',
        categoryId: video.snippet.categoryId,
        duration: parseDuration_(video.contentDetails.duration),
        durationRaw: video.contentDetails.duration,
        viewCount: viewCount,
        likeCount: likeCount,
        commentCount: commentCount,
        engagementRate: Number(engagement),
        url: 'https://www.youtube.com/watch?v=' + video.id
      });
    });
    
    Logger.log('영상 상세 정보 ' + Math.min(i + 50, videoIds.length) + '/' + videoIds.length + ' 처리');
  }
  
  // 업로드일 기준 내림차순 정렬
  allVideos.sort(function(a, b) {
    return new Date(b.publishedAt) - new Date(a.publishedAt);
  });
  
  Logger.log('전체 ' + allVideos.length + '개 영상 수집 완료');
  return allVideos;
}

/**
 * ISO 8601 영상 길이를 초 단위로 변환한다.
 * 예: PT1H2M30S → 3750 (초)
 * 
 * @param {string} duration - ISO 8601 형식 시간 (예: PT1H2M30S)
 * @return {number} 초 단위 길이
 */
function parseDuration_(duration) {
  var match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return 0;
  
  var hours = parseInt(match[1] || 0);
  var minutes = parseInt(match[2] || 0);
  var seconds = parseInt(match[3] || 0);
  
  return hours * 3600 + minutes * 60 + seconds;
}

/**
 * 초 단위 시간을 읽기 쉬운 형식으로 변환한다.
 * 예: 3750 → "1:02:30"
 * 
 * @param {number} totalSeconds - 초 단위 시간
 * @return {string} "H:MM:SS" 또는 "M:SS" 형식
 */
function formatDuration_(totalSeconds) {
  var hours = Math.floor(totalSeconds / 3600);
  var minutes = Math.floor((totalSeconds % 3600) / 60);
  var seconds = totalSeconds % 60;
  
  if (hours > 0) {
    return hours + ':' + padZero_(minutes) + ':' + padZero_(seconds);
  }
  return minutes + ':' + padZero_(seconds);
}

function padZero_(n) {
  return n < 10 ? '0' + n : '' + n;
}

/**
 * 수집한 영상 데이터를 시트에 기록한다.
 * 
 * @param {GoogleAppsScript.Spreadsheet.Sheet} sheet - 대상 시트
 * @param {Array<Object>} videos - 영상 정보 배열
 * @param {boolean} writeHeaders - 헤더를 쓸지 여부
 */
function writeVideosToSheet_(sheet, videos, writeHeaders) {
  if (videos.length === 0) {
    Logger.log('기록할 영상이 없습니다.');
    return;
  }
  
  var startRow = 1;
  
  if (writeHeaders) {
    var headers = [
      '썸네일', '제목', '업로드일', '조회수', '좋아요', '댓글 수',
      '참여율(%)', '영상 길이', '태그', '영상 URL', '영상 ID'
    ];
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    var headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setBackground('#4285f4');
    headerRange.setFontColor('#ffffff');
    headerRange.setFontWeight('bold');
    headerRange.setHorizontalAlignment('center');
    sheet.setFrozenRows(1);
    startRow = 2;
  } else {
    startRow = sheet.getLastRow() + 1;
  }
  
  // 데이터 변환
  var data = videos.map(function(v) {
    return [
      '=IMAGE("' + v.thumbnail + '")',
      v.title,
      v.publishedAt.split('T')[0],
      v.viewCount,
      v.likeCount,
      v.commentCount,
      v.engagementRate,
      formatDuration_(v.duration),
      v.tags,
      v.url,
      v.videoId
    ];
  });
  
  // 한 번에 기록 (성능 최적화)
  sheet.getRange(startRow, 1, data.length, data[0].length).setValues(data);
  
  // 서식 적용
  var dataRange = sheet.getRange(startRow, 4, data.length, 3);
  dataRange.setNumberFormat('#,##0');
  
  sheet.getRange(startRow, 7, data.length, 1).setNumberFormat('0.00');
  
  // 열 너비 조정
  sheet.setColumnWidth(1, 120);   // 썸네일
  sheet.setColumnWidth(2, 350);   // 제목
  sheet.setColumnWidth(3, 100);   // 업로드일
  sheet.setColumnWidth(9, 250);   // 태그
  sheet.setColumnWidth(10, 300);  // URL
  
  // 행 높이 조정 (썸네일)
  for (var i = startRow; i < startRow + data.length; i++) {
    sheet.setRowHeight(i, 68);
  }
  
  Logger.log(data.length + '개 영상 데이터를 시트에 기록했습니다.');
}

/**
 * 벤치마킹 시트의 마지막 수집일을 업데이트한다.
 */
function updateLastCollectedDate_(channelId) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('벤치마킹');
  if (!sheet) return;
  
  var data = sheet.getDataRange().getValues();
  for (var i = 1; i < data.length; i++) {
    if (data[i][2] === channelId) {
      sheet.getRange(i + 1, 9).setValue(new Date()).setNumberFormat('yyyy-mm-dd HH:mm');
      break;
    }
  }
}
```

### 벤치마킹 시트에서 바로 수집하기

벤치마킹 시트에 등록된 채널의 영상을 한 번에 수집하는 기능도 추가한다.

```javascript
/**
 * 벤치마킹 시트에서 선택한 채널의 영상을 수집한다.
 * 활성 셀이 있는 행의 채널을 대상으로 한다.
 */
function collectSelectedChannelVideos() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('벤치마킹');
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('벤치마킹 시트가 없습니다. 먼저 채널을 등록해 주세요.');
    return;
  }
  
  var activeRow = sheet.getActiveCell().getRow();
  if (activeRow <= 1) {
    SpreadsheetApp.getUi().alert('수집할 채널 행을 선택해 주세요. (2행 이하)');
    return;
  }
  
  var rowData = sheet.getRange(activeRow, 1, 1, 10).getValues()[0];
  var channelTitle = rowData[1];
  var channelId = rowData[2];
  
  if (!channelId) {
    SpreadsheetApp.getUi().alert('채널 ID가 없습니다.');
    return;
  }
  
  showSheetSelector(channelId, channelTitle);
}

/**
 * 벤치마킹 시트의 모든 채널 영상을 일괄 수집한다.
 * 각 채널별로 별도 시트에 저장한다.
 */
function collectAllBenchmarkChannels() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('벤치마킹');
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('벤치마킹 시트가 없습니다.');
    return;
  }
  
  var data = sheet.getDataRange().getValues();
  var totalChannels = data.length - 1;
  
  if (totalChannels <= 0) {
    SpreadsheetApp.getUi().alert('등록된 채널이 없습니다.');
    return;
  }
  
  var ui = SpreadsheetApp.getUi();
  var confirm = ui.alert(
    '전체 채널 수집',
    totalChannels + '개 채널의 영상을 수집합니다.\n' +
    '채널당 별도 시트가 생성됩니다.\n\n계속하시겠습니까?',
    ui.ButtonSet.YES_NO
  );
  
  if (confirm !== ui.Button.YES) return;
  
  var successCount = 0;
  var failCount = 0;
  
  for (var i = 1; i < data.length; i++) {
    var channelTitle = data[i][1];
    var channelId = data[i][2];
    
    try {
      var sheetName = channelTitle.substring(0, 30) + '_영상';
      var result = collectChannelVideosToSheet(channelId, sheetName, true);
      Logger.log('[성공] ' + channelTitle + ': ' + result);
      successCount++;
    } catch (e) {
      Logger.log('[실패] ' + channelTitle + ': ' + e.message);
      failCount++;
    }
  }
  
  ui.alert(
    '수집 완료',
    '성공: ' + successCount + '개 채널\n실패: ' + failCount + '개 채널',
    ui.ButtonSet.OK
  );
}
```

---

## 8.6 [바로 실습] 업로드 패턴 분석하기

영상 데이터를 수집했다면, 이제 그 안에서 패턴을 찾아보자. 경쟁 채널이 **언제, 얼마나 자주, 어떤 길이의** 영상을 올리는지 분석한다.

```javascript
/**
 * 수집된 영상 데이터에서 업로드 패턴을 분석한다.
 * 
 * @param {string} channelSheetName - 영상 데이터가 있는 시트 이름
 */
function analyzeUploadPattern(channelSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheetByName(channelSheetName);
  
  if (!sourceSheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다: ' + channelSheetName);
    return;
  }
  
  var data = sourceSheet.getDataRange().getValues();
  if (data.length <= 1) {
    SpreadsheetApp.getUi().alert('분석할 영상 데이터가 없습니다.');
    return;
  }
  
  // 데이터 파싱 (헤더 제외)
  var videos = [];
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    var uploadDate = new Date(row[2]);  // 업로드일
    if (isNaN(uploadDate.getTime())) continue;
    
    videos.push({
      title: row[1],
      uploadDate: uploadDate,
      viewCount: Number(row[3]) || 0,
      likeCount: Number(row[4]) || 0,
      commentCount: Number(row[5]) || 0,
      engagementRate: Number(row[6]) || 0,
      duration: row[7]  // "M:SS" 또는 "H:MM:SS" 형식
    });
  }
  
  if (videos.length === 0) {
    SpreadsheetApp.getUi().alert('유효한 영상 데이터가 없습니다.');
    return;
  }
  
  // 업로드일 기준 오름차순 정렬
  videos.sort(function(a, b) { return a.uploadDate - b.uploadDate; });
  
  // === 분석 1: 월별 업로드 수 ===
  var monthlyUploads = {};
  videos.forEach(function(v) {
    var key = v.uploadDate.getFullYear() + '-' + padZero_(v.uploadDate.getMonth() + 1);
    monthlyUploads[key] = (monthlyUploads[key] || 0) + 1;
  });
  
  // === 분석 2: 업로드 간격 ===
  var gaps = [];
  for (var j = 1; j < videos.length; j++) {
    var gapDays = (videos[j].uploadDate - videos[j - 1].uploadDate) / (1000 * 60 * 60 * 24);
    gaps.push(gapDays);
  }
  var avgGap = gaps.length > 0 ? gaps.reduce(function(a, b) { return a + b; }, 0) / gaps.length : 0;
  
  // === 분석 3: 요일별 업로드 수 및 평균 조회수 ===
  var dayNames = ['일', '월', '화', '수', '목', '금', '토'];
  var dayStats = {};
  dayNames.forEach(function(d) { dayStats[d] = { count: 0, totalViews: 0 }; });
  
  videos.forEach(function(v) {
    var dayName = dayNames[v.uploadDate.getDay()];
    dayStats[dayName].count++;
    dayStats[dayName].totalViews += v.viewCount;
  });
  
  // === 분석 4: 영상 길이 분포 ===
  var durationBuckets = {
    '1분 미만 (Shorts)': { count: 0, totalViews: 0, maxSeconds: 60 },
    '1~5분': { count: 0, totalViews: 0, maxSeconds: 300 },
    '5~10분': { count: 0, totalViews: 0, maxSeconds: 600 },
    '10~20분': { count: 0, totalViews: 0, maxSeconds: 1200 },
    '20~60분': { count: 0, totalViews: 0, maxSeconds: 3600 },
    '60분 이상': { count: 0, totalViews: 0, maxSeconds: Infinity }
  };
  
  videos.forEach(function(v) {
    var seconds = parseDurationString_(v.duration);
    for (var bucket in durationBuckets) {
      if (seconds < durationBuckets[bucket].maxSeconds) {
        durationBuckets[bucket].count++;
        durationBuckets[bucket].totalViews += v.viewCount;
        break;
      }
    }
  });
  
  // === 분석 5: 시간대별 업로드 (가능한 경우) ===
  var hourStats = {};
  for (var h = 0; h < 24; h++) { hourStats[h] = { count: 0, totalViews: 0 }; }
  
  // 원본 시트에서 더 정확한 시간 정보를 가져오려면 ISO 형식의 날짜가 필요하다.
  // 현재 시트에는 'YYYY-MM-DD' 형식만 있으므로, 시간대 분석은 참고용이다.
  
  // === 결과 시트 작성 ===
  var analysisSheetName = channelSheetName.replace(/_영상$|_영상목록$/, '') + '_분석';
  var analysisSheet = ss.getSheetByName(analysisSheetName);
  if (analysisSheet) {
    analysisSheet.clear();
  } else {
    analysisSheet = ss.insertSheet(analysisSheetName);
  }
  
  var currentRow = 1;
  
  // 헤더: 기본 통계
  analysisSheet.getRange(currentRow, 1).setValue('📊 업로드 패턴 분석 결과');
  analysisSheet.getRange(currentRow, 1).setFontSize(16).setFontWeight('bold');
  currentRow += 2;
  
  // 기본 통계
  var basicStats = [
    ['기본 통계', ''],
    ['총 영상 수', videos.length],
    ['분석 기간', videos[0].uploadDate.toISOString().split('T')[0] + ' ~ ' +
      videos[videos.length - 1].uploadDate.toISOString().split('T')[0]],
    ['평균 업로드 간격', avgGap.toFixed(1) + '일'],
    ['주당 평균 업로드', (7 / avgGap).toFixed(1) + '회'],
    ['월당 평균 업로드', (30 / avgGap).toFixed(1) + '회'],
    ['평균 조회수', Math.round(videos.reduce(function(s, v) { return s + v.viewCount; }, 0) / videos.length)],
    ['평균 참여율', (videos.reduce(function(s, v) { return s + v.engagementRate; }, 0) / videos.length).toFixed(2) + '%']
  ];
  
  analysisSheet.getRange(currentRow, 1, basicStats.length, 2).setValues(basicStats);
  analysisSheet.getRange(currentRow, 1, 1, 2).setBackground('#e8f0fe').setFontWeight('bold');
  currentRow += basicStats.length + 2;
  
  // 요일별 분석
  var dayHeader = [['요일별 업로드 분석', '', '']];
  var dayData = [['요일', '업로드 수', '평균 조회수']];
  
  dayNames.forEach(function(d) {
    var stat = dayStats[d];
    dayData.push([
      d + '요일',
      stat.count,
      stat.count > 0 ? Math.round(stat.totalViews / stat.count) : 0
    ]);
  });
  
  analysisSheet.getRange(currentRow, 1, 1, 3).setValues(dayHeader);
  analysisSheet.getRange(currentRow, 1).setBackground('#e8f0fe').setFontWeight('bold');
  currentRow++;
  analysisSheet.getRange(currentRow, 1, dayData.length, 3).setValues(dayData);
  analysisSheet.getRange(currentRow, 1, 1, 3).setFontWeight('bold');
  currentRow += dayData.length + 2;
  
  // 영상 길이별 분석
  var durationHeader = [['영상 길이별 분석', '', '']];
  var durationData = [['길이 구간', '영상 수', '평균 조회수']];
  
  for (var bucket in durationBuckets) {
    var b = durationBuckets[bucket];
    durationData.push([
      bucket,
      b.count,
      b.count > 0 ? Math.round(b.totalViews / b.count) : 0
    ]);
  }
  
  analysisSheet.getRange(currentRow, 1, 1, 3).setValues(durationHeader);
  analysisSheet.getRange(currentRow, 1).setBackground('#e8f0fe').setFontWeight('bold');
  currentRow++;
  analysisSheet.getRange(currentRow, 1, durationData.length, 3).setValues(durationData);
  analysisSheet.getRange(currentRow, 1, 1, 3).setFontWeight('bold');
  currentRow += durationData.length + 2;
  
  // 월별 업로드 추이
  var monthHeader = [['월별 업로드 추이', '']];
  var monthData = [['월', '업로드 수']];
  var sortedMonths = Object.keys(monthlyUploads).sort();
  sortedMonths.forEach(function(m) {
    monthData.push([m, monthlyUploads[m]]);
  });
  
  analysisSheet.getRange(currentRow, 1, 1, 2).setValues(monthHeader);
  analysisSheet.getRange(currentRow, 1).setBackground('#e8f0fe').setFontWeight('bold');
  currentRow++;
  analysisSheet.getRange(currentRow, 1, monthData.length, 2).setValues(monthData);
  analysisSheet.getRange(currentRow, 1, 1, 2).setFontWeight('bold');
  
  // 열 너비 조정
  analysisSheet.setColumnWidth(1, 180);
  analysisSheet.setColumnWidth(2, 150);
  analysisSheet.setColumnWidth(3, 150);
  
  // 숫자 서식
  analysisSheet.getRange(3, 2, basicStats.length, 1).setNumberFormat('#,##0');
  
  SpreadsheetApp.getUi().alert('업로드 패턴 분석이 완료되었습니다.\n시트: ' + analysisSheetName);
  ss.setActiveSheet(analysisSheet);
}

/**
 * "M:SS" 또는 "H:MM:SS" 형식 문자열을 초로 변환한다.
 */
function parseDurationString_(str) {
  if (!str || typeof str !== 'string') return 0;
  var parts = str.split(':').map(Number);
  if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  } else if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  }
  return 0;
}
```

### 분석 실행 메뉴 함수

```javascript
/**
 * 업로드 패턴 분석 대화상자를 표시한다.
 */
function showUploadPatternAnalysis() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  var sheetNames = sheets.map(function(s) { return s.getName(); })
    .filter(function(name) {
      return name.indexOf('_영상') > -1 || name.indexOf('영상목록') > -1;
    });
  
  if (sheetNames.length === 0) {
    SpreadsheetApp.getUi().alert(
      '영상 데이터가 있는 시트가 없습니다.\n먼저 채널 영상을 수집해 주세요.'
    );
    return;
  }
  
  var ui = SpreadsheetApp.getUi();
  var result = ui.prompt(
    '업로드 패턴 분석',
    '분석할 시트 이름을 입력하세요:\n\n영상 데이터 시트 목록:\n' + sheetNames.join('\n'),
    ui.ButtonSet.OK_CANCEL
  );
  
  if (result.getSelectedButton() === ui.Button.OK) {
    var sheetName = result.getResponseText().trim();
    if (sheetName) {
      analyzeUploadPattern(sheetName);
    }
  }
}
```

---

## 8.7 [바로 실습] 인기 영상 Top10 정리하기

경쟁 채널 분석의 꽃은 역시 **어떤 영상이 가장 잘 됐는지** 파악하는 것이다. 단순 조회수 순위뿐 아니라, 채널 평균 대비 얼마나 폭발적으로 성장했는지를 나타내는 **"떡상 점수"**까지 계산한다.

### 떡상 점수란?

조회수가 100만인 영상이 있다고 하자. 이 영상이 평균 조회수 50만 채널의 것인지, 평균 1,000인 채널의 것인지에 따라 의미가 완전히 다르다.

**떡상 점수 = 해당 영상 조회수 / 채널 영상 평균 조회수**

- 떡상 점수 1.0 = 평균 수준
- 떡상 점수 2.0 = 평균의 2배 → 꽤 잘된 영상
- 떡상 점수 5.0 이상 = 평균의 5배 → 히트 영상
- 떡상 점수 10.0 이상 = 바이럴 폭발

```javascript
/**
 * 채널의 인기 영상 Top10을 정리한다.
 * 조회수, 참여율, 떡상 점수 기준으로 각각 순위를 매긴다.
 * 
 * @param {string} channelSheetName - 영상 데이터 시트 이름
 */
function createTop10Sheet(channelSheetName) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheetByName(channelSheetName);
  
  if (!sourceSheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다: ' + channelSheetName);
    return;
  }
  
  var data = sourceSheet.getDataRange().getValues();
  if (data.length <= 1) {
    SpreadsheetApp.getUi().alert('영상 데이터가 없습니다.');
    return;
  }
  
  // 데이터 파싱
  var videos = [];
  for (var i = 1; i < data.length; i++) {
    var row = data[i];
    videos.push({
      thumbnail: row[0],     // IMAGE 수식
      title: row[1],
      uploadDate: row[2],
      viewCount: Number(row[3]) || 0,
      likeCount: Number(row[4]) || 0,
      commentCount: Number(row[5]) || 0,
      engagementRate: Number(row[6]) || 0,
      duration: row[7],
      url: row[9] || ''
    });
  }
  
  // 평균 조회수 계산
  var totalViews = videos.reduce(function(sum, v) { return sum + v.viewCount; }, 0);
  var avgViews = totalViews / videos.length;
  
  // 떡상 점수 계산
  videos.forEach(function(v) {
    v.viralScore = avgViews > 0 ? (v.viewCount / avgViews) : 0;
  });
  
  // 결과 시트 생성
  var topSheetName = channelSheetName.replace(/_영상$|_영상목록$/, '') + '_Top10';
  var topSheet = ss.getSheetByName(topSheetName);
  if (topSheet) {
    topSheet.clear();
  } else {
    topSheet = ss.insertSheet(topSheetName);
  }
  
  var currentRow = 1;
  
  // === Top 10 by 조회수 ===
  currentRow = writeTop10Section_(
    topSheet, currentRow,
    '🏆 조회수 Top 10',
    videos.slice().sort(function(a, b) { return b.viewCount - a.viewCount; }).slice(0, 10),
    avgViews
  );
  
  currentRow += 2;
  
  // === Top 10 by 떡상 점수 ===
  currentRow = writeTop10Section_(
    topSheet, currentRow,
    '🚀 떡상 점수 Top 10 (채널 평균 대비)',
    videos.slice().sort(function(a, b) { return b.viralScore - a.viralScore; }).slice(0, 10),
    avgViews
  );
  
  currentRow += 2;
  
  // === Top 10 by 참여율 ===
  // 조회수가 너무 적은 영상은 참여율이 왜곡될 수 있으므로,
  // 평균 조회수의 10% 이상인 영상만 대상으로 한다.
  var filteredVideos = videos.filter(function(v) {
    return v.viewCount >= avgViews * 0.1;
  });
  
  currentRow = writeTop10Section_(
    topSheet, currentRow,
    '💬 참여율 Top 10 (조회수 하위 10% 제외)',
    filteredVideos.slice().sort(function(a, b) { return b.engagementRate - a.engagementRate; }).slice(0, 10),
    avgViews
  );
  
  // 열 너비 설정
  topSheet.setColumnWidth(1, 40);    // 순위
  topSheet.setColumnWidth(2, 120);   // 썸네일
  topSheet.setColumnWidth(3, 300);   // 제목
  topSheet.setColumnWidth(4, 100);   // 업로드일
  topSheet.setColumnWidth(5, 110);   // 조회수
  topSheet.setColumnWidth(6, 90);    // 좋아요
  topSheet.setColumnWidth(7, 90);    // 참여율
  topSheet.setColumnWidth(8, 100);   // 떡상 점수
  topSheet.setColumnWidth(9, 300);   // URL
  
  SpreadsheetApp.getUi().alert('인기 영상 Top 10 분석이 완료되었습니다.\n시트: ' + topSheetName);
  ss.setActiveSheet(topSheet);
}

/**
 * Top 10 섹션을 시트에 기록한다.
 * 
 * @return {number} 다음 기록할 행 번호
 */
function writeTop10Section_(sheet, startRow, title, videos, avgViews) {
  // 섹션 제목
  sheet.getRange(startRow, 1).setValue(title);
  sheet.getRange(startRow, 1, 1, 9)
    .merge()
    .setFontSize(14)
    .setFontWeight('bold')
    .setBackground('#1a73e8')
    .setFontColor('#ffffff');
  startRow++;
  
  // 채널 평균 정보
  sheet.getRange(startRow, 1).setValue('채널 평균 조회수: ' + Math.round(avgViews).toLocaleString());
  sheet.getRange(startRow, 1, 1, 9)
    .merge()
    .setBackground('#e8f0fe')
    .setFontStyle('italic');
  startRow++;
  
  // 헤더
  var headers = ['순위', '썸네일', '제목', '업로드일', '조회수', '좋아요', '참여율(%)', '떡상 점수', 'URL'];
  sheet.getRange(startRow, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(startRow, 1, 1, headers.length)
    .setBackground('#f1f3f4')
    .setFontWeight('bold')
    .setHorizontalAlignment('center');
  startRow++;
  
  // 데이터
  for (var i = 0; i < videos.length; i++) {
    var v = videos[i];
    var rowData = [
      i + 1,
      v.thumbnail,  // IMAGE 수식이 이미 포함
      v.title,
      v.uploadDate,
      v.viewCount,
      v.likeCount,
      v.engagementRate,
      v.viralScore.toFixed(1) + 'x',
      v.url
    ];
    sheet.getRange(startRow + i, 1, 1, rowData.length).setValues([rowData]);
    sheet.setRowHeight(startRow + i, 68);
    
    // 떡상 점수에 따른 배경색
    var scoreCell = sheet.getRange(startRow + i, 8);
    if (v.viralScore >= 10) {
      scoreCell.setBackground('#ea4335').setFontColor('#ffffff');  // 빨강
    } else if (v.viralScore >= 5) {
      scoreCell.setBackground('#fbbc04');  // 노랑
    } else if (v.viralScore >= 2) {
      scoreCell.setBackground('#e8f5e9');  // 연두
    }
  }
  
  // 숫자 서식
  sheet.getRange(startRow, 5, videos.length, 2).setNumberFormat('#,##0');
  sheet.getRange(startRow, 7, videos.length, 1).setNumberFormat('0.00');
  
  return startRow + videos.length;
}
```

### Top10 분석 실행 함수

```javascript
/**
 * Top 10 인기 영상 분석을 실행한다.
 */
function showTop10Analysis() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheets = ss.getSheets();
  var sheetNames = sheets.map(function(s) { return s.getName(); })
    .filter(function(name) {
      return name.indexOf('_영상') > -1 || name.indexOf('영상목록') > -1;
    });
  
  if (sheetNames.length === 0) {
    SpreadsheetApp.getUi().alert('영상 데이터가 있는 시트가 없습니다.');
    return;
  }
  
  var ui = SpreadsheetApp.getUi();
  var result = ui.prompt(
    '인기 영상 Top 10',
    '분석할 시트 이름을 입력하세요:\n\n' + sheetNames.join('\n'),
    ui.ButtonSet.OK_CANCEL
  );
  
  if (result.getSelectedButton() === ui.Button.OK) {
    var sheetName = result.getResponseText().trim();
    if (sheetName) {
      createTop10Sheet(sheetName);
    }
  }
}
```

---

## 8.8 메뉴 통합

지금까지 만든 모든 기능을 하나의 메뉴로 통합한다.

```javascript
/**
 * 스프레드시트가 열릴 때 메뉴를 생성한다.
 */
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
    .addToUi();
}
```

---

## 정리

이번 장에서 구현한 기능을 정리한다.

| 기능 | 함수명 | API 비용 |
|---|---|---|
| 키워드 채널 검색 | `searchChannels()` | 100 + 1 units |
| 채널 URL 파싱 | `parseChannelUrl()` | 0~100 units |
| 벤치마킹 채널 등록 | `addBenchmarkChannel()` | 1 unit |
| 전체 영상 수집 | `getAllChannelVideos()` | ~21 units/500영상 |
| 업로드 패턴 분석 | `analyzeUploadPattern()` | 0 units (시트 데이터 활용) |
| 인기 영상 Top 10 | `createTop10Sheet()` | 0 units (시트 데이터 활용) |

핵심은 **search.list 대신 playlistItems.list를 활용하여 API 비용을 100분의 1로 절감**한 것이다. 채널 하나의 전체 영상을 분석하는 데 20여 unit이면 충분하므로, 일일 할당량 안에서 수백 개 채널을 분석할 수 있다.

다음 장에서는 이렇게 수집한 영상의 **댓글을 수집하고 분석**하여, 시청자가 어떤 반응을 보이는지까지 파악하는 시스템을 구축한다.
