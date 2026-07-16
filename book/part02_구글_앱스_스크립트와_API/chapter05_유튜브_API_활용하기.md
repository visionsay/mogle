# Chapter 05: 유튜브 API 활용하기

## 5.1 API란 무엇인가요?

유튜브에서 특정 키워드로 영상을 검색한다고 상상해 보세요. 여러분이 유튜브 웹사이트에서 검색창에 키워드를 입력하면, 유튜브 서버가 결과를 보여줍니다. API(Application Programming Interface)는 이 과정을 프로그램이 대신 수행할 수 있게 해주는 통신 규약입니다. 사람이 웹사이트를 클릭하는 대신, 코드가 정해진 규칙에 맞게 요청을 보내면 유튜브 서버가 데이터로 응답하는 것입니다.

### REST API의 기본 구조

유튜브 API는 REST(Representational State Transfer) 방식의 API입니다. REST API는 HTTP 프로토콜을 기반으로 동작하며, 다음 네 가지 요소로 구성됩니다.

**1. 엔드포인트(Endpoint) - "어디로 요청할 것인가"**

```
https://www.googleapis.com/youtube/v3/videos
https://www.googleapis.com/youtube/v3/search
https://www.googleapis.com/youtube/v3/channels
```

각 URL이 특정 데이터에 접근하는 창구 역할을 합니다.

**2. HTTP 메서드(Method) - "무엇을 할 것인가"**

| 메서드 | 용도 | 유튜브 API 예시 |
|--------|------|-----------------|
| GET | 데이터 조회 | 영상 정보 가져오기 |
| POST | 데이터 생성 | 댓글 작성, 재생목록 생성 |
| PUT | 데이터 수정 | 영상 메타데이터 수정 |
| DELETE | 데이터 삭제 | 재생목록에서 영상 제거 |

이 책에서는 데이터 수집이 목적이므로 GET 메서드를 주로 사용합니다.

**3. 파라미터(Parameter) - "어떤 조건으로 요청할 것인가"**

```
?part=snippet,statistics    ← 어떤 데이터를 원하는지
&id=dQw4w9WgXcQ            ← 어떤 영상인지
&key=YOUR_API_KEY           ← 인증 키
```

**4. 응답(Response) - JSON 형식의 데이터**

```json
{
  "kind": "youtube#videoListResponse",
  "items": [
    {
      "id": "dQw4w9WgXcQ",
      "snippet": {
        "title": "Rick Astley - Never Gonna Give You Up",
        "channelTitle": "Rick Astley",
        "publishedAt": "2009-10-25T06:57:33Z"
      },
      "statistics": {
        "viewCount": "1500000000",
        "likeCount": "15000000"
      }
    }
  ]
}
```

JSON(JavaScript Object Notation)은 자바스크립트의 객체 표기법을 기반으로 한 데이터 형식입니다. 중괄호 `{}`는 객체, 대괄호 `[]`는 배열을 의미합니다. 앱스 스크립트에서는 `JSON.parse()`로 문자열을 객체로 변환하여 사용합니다.

---

## 5.2 유튜브 API의 종류

구글은 유튜브 관련 API를 세 가지 제공합니다.

### YouTube Data API v3 (이 책의 핵심)

유튜브의 공개 데이터에 접근하는 API입니다. 영상 검색, 영상 상세정보 조회, 채널 정보, 댓글, 재생목록 등 유튜브에서 볼 수 있는 대부분의 데이터를 가져올 수 있습니다.

- **주 용도:** 영상 검색, 경쟁 채널 분석, 댓글 수집, 트렌드 파악
- **인증:** API 키 (읽기 전용) 또는 OAuth 2.0 (쓰기 작업)
- **할당량:** 일 10,000 유닛 (기본)

### YouTube Analytics API

자신의 채널에 대한 분석 데이터를 가져오는 API입니다. 유튜브 스튜디오에서 볼 수 있는 분석 데이터(시청 시간, 트래픽 소스, 인구통계 등)에 프로그래밍 방식으로 접근합니다.

- **주 용도:** 자체 채널의 성과 분석, 맞춤형 대시보드 제작
- **인증:** OAuth 2.0 필수 (본인 채널 데이터만 접근 가능)
- **참고:** 이 책에서는 다루지 않지만, Part 04에서 간략히 언급합니다.

### YouTube Reporting API

대용량 분석 데이터를 비동기 방식으로 다운로드하는 API입니다. 매일 자동으로 생성되는 리포트 파일을 가져올 수 있습니다.

- **주 용도:** 대규모 채널의 상세 분석
- **특징:** Analytics API보다 더 세밀한 데이터를 제공하지만, 실시간이 아닌 일 단위 리포트

> **이 책에서는 YouTube Data API v3에 집중합니다.** 경쟁 채널 분석, 키워드 조사, 트렌드 파악 등 유튜브 자동화의 핵심 작업이 모두 이 API로 가능합니다.

---

## 5.3 유튜브 API로 할 수 있는 대표 작업 5가지

### 작업 1: search.list - 키워드 검색 (100 유닛)

특정 키워드로 유튜브 영상을 검색합니다. 가장 많이 사용하지만 할당량 비용이 가장 비싼 엔드포인트입니다.

```javascript
/**
 * 유튜브 키워드 검색
 * 할당량 비용: 100 유닛/호출
 */
function searchVideos(keyword, maxResults = 10) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  const url = 'https://www.googleapis.com/youtube/v3/search'
    + `?part=snippet`
    + `&q=${encodeURIComponent(keyword)}`
    + `&type=video`
    + `&maxResults=${maxResults}`
    + `&order=relevance`
    + `&regionCode=KR`
    + `&relevanceLanguage=ko`
    + `&key=${apiKey}`;
  
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  
  if (response.getResponseCode() !== 200) {
    console.error('검색 에러:', response.getContentText());
    return [];
  }
  
  const data = JSON.parse(response.getContentText());
  const results = data.items.map(item => ({
    videoId: item.id.videoId,
    title: item.snippet.title,
    channelTitle: item.snippet.channelTitle,
    channelId: item.snippet.channelId,
    publishedAt: item.snippet.publishedAt,
    description: item.snippet.description,
    thumbnail: item.snippet.thumbnails.high.url
  }));
  
  console.log(`'${keyword}' 검색 결과: ${results.length}건`);
  results.forEach((r, i) => console.log(`  ${i + 1}. ${r.title} (${r.channelTitle})`));
  
  return results;
}

/**
 * 검색 결과를 스프레드시트에 기록
 */
function searchAndSave() {
  const keyword = '앱스 스크립트 자동화';
  const results = searchVideos(keyword, 10);
  
  if (results.length === 0) return;
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('검색결과')
    || SpreadsheetApp.getActiveSpreadsheet().insertSheet('검색결과');
  
  // 헤더
  const headers = [['영상ID', '제목', '채널명', '채널ID', '게시일', '설명', '썸네일URL', '검색키워드', '수집일']];
  sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
  sheet.getRange(1, 1, 1, headers[0].length).setFontWeight('bold');
  
  // 데이터
  const rows = results.map(r => [
    r.videoId,
    r.title,
    r.channelTitle,
    r.channelId,
    r.publishedAt,
    r.description,
    r.thumbnail,
    keyword,
    new Date()
  ]);
  
  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
  console.log(`${rows.length}건의 검색 결과를 시트에 기록했습니다.`);
}
```

### 작업 2: videos.list - 영상 상세정보 (1 유닛)

영상 ID로 조회수, 좋아요 수, 댓글 수 등 상세 통계를 가져옵니다. search.list보다 100배 저렴합니다.

```javascript
/**
 * 영상 상세정보 조회
 * 할당량 비용: 1 유닛/호출 (최대 50개 영상 동시 조회)
 */
function getVideoDetails(videoIds) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  // videoIds가 배열이면 콤마로 연결, 문자열이면 그대로 사용
  const ids = Array.isArray(videoIds) ? videoIds.join(',') : videoIds;
  
  const url = 'https://www.googleapis.com/youtube/v3/videos'
    + `?part=snippet,statistics,contentDetails`
    + `&id=${ids}`
    + `&key=${apiKey}`;
  
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  
  if (response.getResponseCode() !== 200) {
    console.error('영상 조회 에러:', response.getContentText());
    return [];
  }
  
  const data = JSON.parse(response.getContentText());
  
  return data.items.map(item => ({
    videoId: item.id,
    title: item.snippet.title,
    channelTitle: item.snippet.channelTitle,
    channelId: item.snippet.channelId,
    publishedAt: item.snippet.publishedAt,
    description: item.snippet.description,
    tags: item.snippet.tags || [],
    categoryId: item.snippet.categoryId,
    duration: item.contentDetails.duration,
    viewCount: parseInt(item.statistics.viewCount || '0'),
    likeCount: parseInt(item.statistics.likeCount || '0'),
    commentCount: parseInt(item.statistics.commentCount || '0'),
    thumbnail: item.snippet.thumbnails.high?.url || item.snippet.thumbnails.default.url
  }));
}

/**
 * 여러 영상의 상세정보를 한 번에 가져오기 (50개 단위로 분할)
 */
function getVideoDetailsBatch(videoIds) {
  const allDetails = [];
  const batchSize = 50; // API 한 번에 최대 50개
  
  for (let i = 0; i < videoIds.length; i += batchSize) {
    const batch = videoIds.slice(i, i + batchSize);
    const details = getVideoDetails(batch);
    allDetails.push(...details);
    
    console.log(`배치 ${Math.floor(i / batchSize) + 1}: ${details.length}개 영상 조회 완료`);
    
    // API 호출 간 약간의 딜레이
    if (i + batchSize < videoIds.length) {
      Utilities.sleep(100);
    }
  }
  
  console.log(`총 ${allDetails.length}개 영상의 상세정보를 조회했습니다.`);
  return allDetails;
}
```

### 작업 3: channels.list - 채널 정보 (1 유닛)

채널의 구독자 수, 총 영상 수, 총 조회수 등 채널 레벨의 정보를 가져옵니다.

```javascript
/**
 * 채널 정보 조회
 * 할당량 비용: 1 유닛/호출
 */
function getChannelInfo(channelId) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  const url = 'https://www.googleapis.com/youtube/v3/channels'
    + `?part=snippet,statistics,contentDetails,brandingSettings`
    + `&id=${channelId}`
    + `&key=${apiKey}`;
  
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  
  if (response.getResponseCode() !== 200) {
    console.error('채널 조회 에러:', response.getContentText());
    return null;
  }
  
  const data = JSON.parse(response.getContentText());
  
  if (!data.items || data.items.length === 0) {
    console.warn('채널을 찾을 수 없습니다:', channelId);
    return null;
  }
  
  const channel = data.items[0];
  return {
    channelId: channel.id,
    title: channel.snippet.title,
    description: channel.snippet.description,
    customUrl: channel.snippet.customUrl,
    publishedAt: channel.snippet.publishedAt,
    thumbnail: channel.snippet.thumbnails.high?.url,
    country: channel.snippet.country,
    subscriberCount: parseInt(channel.statistics.subscriberCount || '0'),
    videoCount: parseInt(channel.statistics.videoCount || '0'),
    viewCount: parseInt(channel.statistics.viewCount || '0'),
    uploadsPlaylistId: channel.contentDetails.relatedPlaylists.uploads,
    keywords: channel.brandingSettings?.channel?.keywords || ''
  };
}

/**
 * 채널 정보를 조회하여 스프레드시트에 기록
 */
function analyzeChannel() {
  const channelId = 'UC_x5XG1OV2P6uZZ5FSM9Ttw'; // Google Developers 채널
  const info = getChannelInfo(channelId);
  
  if (!info) return;
  
  console.log(`채널명: ${info.title}`);
  console.log(`구독자: ${info.subscriberCount.toLocaleString()}명`);
  console.log(`영상 수: ${info.videoCount.toLocaleString()}개`);
  console.log(`총 조회수: ${info.viewCount.toLocaleString()}회`);
  console.log(`업로드 재생목록 ID: ${info.uploadsPlaylistId}`);
  
  // 영상당 평균 조회수
  const avgViews = Math.round(info.viewCount / info.videoCount);
  console.log(`영상당 평균 조회수: ${avgViews.toLocaleString()}회`);
}
```

### 작업 4: commentThreads.list - 댓글 수집 (1 유닛)

영상의 최상위 댓글(댓글 스레드)을 수집합니다.

```javascript
/**
 * 영상 댓글 수집
 * 할당량 비용: 1 유닛/호출 (페이지당)
 */
function getVideoComments(videoId, maxComments = 100) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  const allComments = [];
  let pageToken = '';
  
  while (allComments.length < maxComments) {
    const url = 'https://www.googleapis.com/youtube/v3/commentThreads'
      + `?part=snippet`
      + `&videoId=${videoId}`
      + `&maxResults=${Math.min(100, maxComments - allComments.length)}`
      + `&order=relevance`
      + `&textFormat=plainText`
      + (pageToken ? `&pageToken=${pageToken}` : '')
      + `&key=${apiKey}`;
    
    const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    
    if (response.getResponseCode() !== 200) {
      const errorData = JSON.parse(response.getContentText());
      // 댓글이 비활성화된 영상
      if (errorData.error?.errors?.[0]?.reason === 'commentsDisabled') {
        console.warn('이 영상은 댓글이 비활성화되어 있습니다.');
        return allComments;
      }
      console.error('댓글 조회 에러:', response.getContentText());
      break;
    }
    
    const data = JSON.parse(response.getContentText());
    
    const comments = data.items.map(item => {
      const comment = item.snippet.topLevelComment.snippet;
      return {
        commentId: item.id,
        author: comment.authorDisplayName,
        authorChannelId: comment.authorChannelId?.value || '',
        text: comment.textDisplay,
        likeCount: comment.likeCount,
        publishedAt: comment.publishedAt,
        updatedAt: comment.updatedAt,
        replyCount: item.snippet.totalReplyCount
      };
    });
    
    allComments.push(...comments);
    console.log(`댓글 수집 중... 현재 ${allComments.length}개`);
    
    // 다음 페이지가 없으면 종료
    pageToken = data.nextPageToken;
    if (!pageToken) break;
    
    Utilities.sleep(100);
  }
  
  console.log(`총 ${allComments.length}개의 댓글을 수집했습니다.`);
  return allComments;
}

/**
 * 댓글을 수집하여 스프레드시트에 기록
 */
function collectAndSaveComments() {
  const videoId = 'dQw4w9WgXcQ';
  const comments = getVideoComments(videoId, 200);
  
  if (comments.length === 0) {
    console.log('수집된 댓글이 없습니다.');
    return;
  }
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('댓글')
    || SpreadsheetApp.getActiveSpreadsheet().insertSheet('댓글');
  
  // 헤더
  if (sheet.getLastRow() === 0) {
    const headers = [['댓글ID', '작성자', '작성자채널ID', '댓글내용', '좋아요', '작성일', '수정일', '답글수']];
    sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
    sheet.getRange(1, 1, 1, headers[0].length).setFontWeight('bold');
  }
  
  // 데이터
  const rows = comments.map(c => [
    c.commentId,
    c.author,
    c.authorChannelId,
    c.text,
    c.likeCount,
    c.publishedAt,
    c.updatedAt,
    c.replyCount
  ]);
  
  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
  console.log(`${rows.length}개의 댓글을 시트에 기록했습니다.`);
}
```

### 작업 5: playlistItems.list - 재생목록/업로드 영상 (1 유닛)

재생목록의 영상 목록을 가져옵니다. 채널의 모든 업로드 영상을 가져올 때도 이 API를 사용합니다(업로드 영상 자체가 하나의 재생목록이기 때문입니다).

```javascript
/**
 * 재생목록 영상 조회 (채널의 전체 업로드 영상 목록 가져오기)
 * 할당량 비용: 1 유닛/호출 (페이지당)
 */
function getPlaylistItems(playlistId, maxItems = 50) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  const allItems = [];
  let pageToken = '';
  
  while (allItems.length < maxItems) {
    const url = 'https://www.googleapis.com/youtube/v3/playlistItems'
      + `?part=snippet,contentDetails`
      + `&playlistId=${playlistId}`
      + `&maxResults=${Math.min(50, maxItems - allItems.length)}`
      + (pageToken ? `&pageToken=${pageToken}` : '')
      + `&key=${apiKey}`;
    
    const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    
    if (response.getResponseCode() !== 200) {
      console.error('재생목록 조회 에러:', response.getContentText());
      break;
    }
    
    const data = JSON.parse(response.getContentText());
    
    const items = data.items.map(item => ({
      videoId: item.contentDetails.videoId,
      title: item.snippet.title,
      description: item.snippet.description,
      publishedAt: item.contentDetails.videoPublishedAt,
      position: item.snippet.position,
      thumbnail: item.snippet.thumbnails?.high?.url || item.snippet.thumbnails?.default?.url || ''
    }));
    
    allItems.push(...items);
    console.log(`재생목록 조회 중... 현재 ${allItems.length}개`);
    
    pageToken = data.nextPageToken;
    if (!pageToken) break;
    
    Utilities.sleep(100);
  }
  
  console.log(`총 ${allItems.length}개의 영상을 조회했습니다.`);
  return allItems;
}

/**
 * 채널의 전체 업로드 영상 목록 가져오기
 * 1단계: channels.list로 업로드 재생목록 ID 가져오기
 * 2단계: playlistItems.list로 영상 목록 가져오기
 */
function getAllChannelVideos(channelId, maxVideos = 100) {
  // 1단계: 채널의 업로드 재생목록 ID 가져오기 (1 유닛)
  const channelInfo = getChannelInfo(channelId);
  
  if (!channelInfo) {
    console.error('채널 정보를 가져올 수 없습니다.');
    return [];
  }
  
  const uploadsPlaylistId = channelInfo.uploadsPlaylistId;
  console.log(`채널 '${channelInfo.title}'의 업로드 재생목록: ${uploadsPlaylistId}`);
  
  // 2단계: 업로드 재생목록의 영상 목록 가져오기
  const videos = getPlaylistItems(uploadsPlaylistId, maxVideos);
  
  console.log(`'${channelInfo.title}' 채널의 최근 ${videos.length}개 영상을 가져왔습니다.`);
  return videos;
}
```

---

## 5.4 유튜브 API의 일일 사용 한도 알아보기

### 기본 할당량: 10,000 유닛/일

유튜브 Data API v3는 매일 10,000 유닛의 무료 할당량을 제공합니다. 태평양 표준시(PST) 기준 자정에 초기화됩니다. 한국 시간으로는 오후 4시(하절기 기준) 또는 오후 5시(동절기 기준)에 리셋됩니다.

### 엔드포인트별 할당량 비용표

| 엔드포인트 | 작업 | 비용(유닛) | 비고 |
|------------|------|-----------|------|
| search.list | 검색 | 100 | 가장 비쌈! |
| videos.list | 영상 정보 | 1 | 최대 50개 동시 조회 가능 |
| channels.list | 채널 정보 | 1 | |
| commentThreads.list | 댓글 조회 | 1 | 페이지당 |
| playlistItems.list | 재생목록 | 1 | 페이지당 |
| comments.list | 답글 조회 | 1 | 페이지당 |
| captions.list | 자막 목록 | 50 | |
| videos.insert | 영상 업로드 | 1,600 | |
| videos.update | 영상 수정 | 50 | |
| playlists.insert | 재생목록 생성 | 50 | |

### 일일 사용량 계산기

스프레드시트에서 아래 수식을 사용하여 하루에 사용할 수 있는 API 호출 횟수를 계산할 수 있습니다.

스프레드시트에 다음과 같이 작성하세요.

| | A | B | C | D |
|---|---|---|---|---|
| 1 | **작업 유형** | **1회 비용(유닛)** | **일일 호출 횟수** | **소요 유닛** |
| 2 | search.list | 100 | 10 | =B2*C2 |
| 3 | videos.list | 1 | 50 | =B3*C3 |
| 4 | channels.list | 1 | 5 | =B4*C4 |
| 5 | commentThreads.list | 1 | 20 | =B5*C5 |
| 6 | playlistItems.list | 1 | 10 | =B6*C6 |
| 7 | **총 사용량** | | | =SUM(D2:D6) |
| 8 | **잔여 할당량** | | | =10000-D7 |
| 9 | **사용률** | | | =D7/10000 |

위 예시에서 search.list를 하루 10번, videos.list를 50번, channels.list를 5번, commentThreads.list를 20번, playlistItems.list를 10번 호출하면 총 1,085 유닛을 사용합니다. 10,000 유닛 중 약 10.9%만 사용하는 것이므로 충분히 여유가 있습니다.

---

## 5.5 유튜브 API 키 없이 활용하기: Google 고급 서비스

앱스 스크립트에는 YouTube Data API를 직접 호출할 수 있는 **고급 서비스(Advanced Services)**가 내장되어 있습니다. API 키 없이도 유튜브 데이터에 접근할 수 있어, 처음 시작할 때 매우 편리합니다.

### 고급 서비스 활성화 방법

1. 앱스 스크립트 편집기에서 왼쪽의 **서비스(Services)** 항목 옆의 **+** 버튼을 클릭합니다.
2. 목록에서 **YouTube Data API v3**를 찾아 선택합니다.
3. 식별자(Identifier)가 `YouTube`로 설정되어 있는지 확인합니다.
4. **추가** 버튼을 클릭합니다.

이제 코드에서 `YouTube.Search.list()`, `YouTube.Videos.list()` 등을 바로 사용할 수 있습니다.

### 고급 서비스 사용 예시

```javascript
/**
 * Google 고급 서비스를 사용한 유튜브 검색
 * API 키가 필요 없습니다!
 * 
 * 사전 설정: 편집기 > 서비스(+) > YouTube Data API v3 추가
 */
function searchWithAdvancedService(keyword, maxResults = 10) {
  try {
    const results = YouTube.Search.list('snippet', {
      q: keyword,
      type: 'video',
      maxResults: maxResults,
      order: 'relevance',
      regionCode: 'KR',
      relevanceLanguage: 'ko'
    });
    
    if (!results.items || results.items.length === 0) {
      console.log('검색 결과가 없습니다.');
      return [];
    }
    
    const videos = results.items.map(item => ({
      videoId: item.id.videoId,
      title: item.snippet.title,
      channelTitle: item.snippet.channelTitle,
      publishedAt: item.snippet.publishedAt
    }));
    
    videos.forEach((v, i) => console.log(`${i + 1}. ${v.title}`));
    return videos;
    
  } catch (error) {
    console.error('검색 에러:', error.message);
    return [];
  }
}

/**
 * Google 고급 서비스를 사용한 영상 상세정보 조회
 */
function getVideoDetailsWithAdvancedService(videoIds) {
  try {
    const ids = Array.isArray(videoIds) ? videoIds.join(',') : videoIds;
    
    const results = YouTube.Videos.list('snippet,statistics,contentDetails', {
      id: ids
    });
    
    return results.items.map(item => ({
      videoId: item.id,
      title: item.snippet.title,
      channelTitle: item.snippet.channelTitle,
      viewCount: parseInt(item.statistics.viewCount || '0'),
      likeCount: parseInt(item.statistics.likeCount || '0'),
      commentCount: parseInt(item.statistics.commentCount || '0'),
      duration: item.contentDetails.duration
    }));
    
  } catch (error) {
    console.error('영상 조회 에러:', error.message);
    return [];
  }
}

/**
 * Google 고급 서비스를 사용한 채널 정보 조회
 */
function getChannelWithAdvancedService(channelId) {
  try {
    const results = YouTube.Channels.list('snippet,statistics,contentDetails', {
      id: channelId
    });
    
    if (!results.items || results.items.length === 0) {
      console.warn('채널을 찾을 수 없습니다.');
      return null;
    }
    
    const channel = results.items[0];
    return {
      channelId: channel.id,
      title: channel.snippet.title,
      subscriberCount: parseInt(channel.statistics.subscriberCount || '0'),
      videoCount: parseInt(channel.statistics.videoCount || '0'),
      viewCount: parseInt(channel.statistics.viewCount || '0'),
      uploadsPlaylistId: channel.contentDetails.relatedPlaylists.uploads
    };
    
  } catch (error) {
    console.error('채널 조회 에러:', error.message);
    return null;
  }
}
```

### REST API vs 고급 서비스 비교

| 항목 | REST API (UrlFetchApp) | 고급 서비스 (YouTube.xxx) |
|------|----------------------|--------------------------|
| API 키 | 필요 | 불필요 (OAuth 자동 처리) |
| 코드량 | 상대적으로 많음 | 간결함 |
| 유연성 | 모든 파라미터 제어 가능 | 일부 파라미터 미지원 가능 |
| 에러 처리 | HTTP 응답 코드로 상세 처리 | try-catch 기본 처리 |
| 할당량 | API 키의 프로젝트 할당량 사용 | 스크립트 소유자의 할당량 사용 |
| 인증 범위 | 읽기(API 키) / 쓰기(OAuth) | 모두 OAuth (권한 승인 필요) |

> **추천 가이드:** 처음 시작할 때는 고급 서비스가 편리합니다. 하지만 프로젝트가 커지면 REST API가 더 유연합니다. 이 책에서는 두 가지 방법을 모두 제공하므로, 상황에 맞게 선택하세요. 다만 이후 챕터의 코드는 주로 REST API를 기준으로 작성합니다. 할당량 관리와 에러 처리가 더 세밀하게 가능하기 때문입니다.

---

## 5.6 유튜브 API 키 발급받기

### Google Cloud Console에서 API 키 발급하기

REST API를 사용하려면 API 키가 필요합니다. 다음 단계를 따라 발급받으세요.

**1단계: Google Cloud Console 접속**

[console.cloud.google.com](https://console.cloud.google.com)에 접속하여 구글 계정으로 로그인합니다.

**2단계: 새 프로젝트 생성**

1. 상단의 프로젝트 선택 드롭다운을 클릭합니다.
2. **새 프로젝트**를 클릭합니다.
3. 프로젝트 이름에 `youtube-automation` (또는 원하는 이름)을 입력합니다.
4. **만들기**를 클릭합니다.
5. 생성된 프로젝트가 자동으로 선택되지 않으면, 드롭다운에서 수동으로 선택합니다.

**3단계: YouTube Data API v3 활성화**

1. 왼쪽 메뉴에서 **API 및 서비스 > 라이브러리**를 클릭합니다.
2. 검색창에 `YouTube Data API v3`를 입력합니다.
3. 검색 결과에서 **YouTube Data API v3**를 클릭합니다.
4. **사용** 버튼을 클릭하여 API를 활성화합니다.

**4단계: API 키 생성**

1. 왼쪽 메뉴에서 **API 및 서비스 > 사용자 인증 정보**를 클릭합니다.
2. 상단의 **+ 사용자 인증 정보 만들기**를 클릭합니다.
3. **API 키**를 선택합니다.
4. API 키가 생성됩니다. 이 키를 복사해 두세요.

**5단계: API 키 제한 설정 (보안 필수!)**

생성된 API 키를 클릭하여 편집 화면으로 들어갑니다.

1. **애플리케이션 제한사항**: 실습 단계에서는 "없음"으로 둡니다.
2. **API 제한사항**: **키 제한**을 선택하고, **YouTube Data API v3**만 체크합니다.
3. **저장**을 클릭합니다.

> **보안 경고:** API 키를 코드에 직접 입력하지 마세요! 코드가 공개되면 다른 사람이 여러분의 할당량을 도용할 수 있습니다. 반드시 `PropertiesService`를 사용하여 안전하게 저장하세요.

### API 키를 앱스 스크립트에 저장하기

4장에서 배운 `PropertiesService`를 사용합니다.

```javascript
/**
 * API 키를 PropertiesService에 저장하는 함수
 * 이 함수를 한 번만 실행하세요. 실행 후 API 키 값을 코드에서 삭제하세요!
 */
function setupApiKey() {
  // ★ 아래 값을 실제 API 키로 변경하세요 ★
  const apiKey = 'YOUR_API_KEY_HERE';
  
  PropertiesService.getScriptProperties().setProperty('YOUTUBE_API_KEY', apiKey);
  console.log('YouTube API 키가 안전하게 저장되었습니다.');
  
  // 저장 확인
  const saved = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  console.log('저장 확인:', saved ? `${saved.substring(0, 8)}... (${saved.length}자)` : '실패');
}

/**
 * API 키가 정상 동작하는지 테스트하는 함수
 */
function testApiKey() {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  if (!apiKey) {
    console.error('API 키가 저장되지 않았습니다. setupApiKey()를 먼저 실행하세요.');
    return;
  }
  
  // 간단한 API 호출로 키 유효성 테스트
  const url = `https://www.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key=${apiKey}`;
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  const code = response.getResponseCode();
  
  if (code === 200) {
    const data = JSON.parse(response.getContentText());
    console.log('API 키 테스트 성공!');
    console.log('테스트 영상:', data.items[0].snippet.title);
  } else if (code === 400) {
    console.error('API 키 형식이 잘못되었습니다.');
  } else if (code === 403) {
    const error = JSON.parse(response.getContentText());
    console.error('API 키 에러:', error.error.message);
  } else {
    console.error(`예상치 못한 응답 (HTTP ${code}):`, response.getContentText());
  }
}
```

---

## 5.7 유튜브 API를 100배 효율적으로 쓰기

10,000 유닛은 생각보다 빨리 소진됩니다. search.list를 100번만 호출해도 하루 할당량이 전부 사라지니까요. 여기서 소개하는 최적화 기법들을 적용하면 같은 할당량으로 10배에서 100배 더 많은 데이터를 수집할 수 있습니다.

### 전략 1: part 파라미터 최적화

`part` 파라미터에 불필요한 항목을 넣지 마세요. 필요한 데이터만 요청하면 응답 속도도 빨라지고, 쿼터 소비도 줄일 수 있습니다.

```javascript
// 나쁜 예: 모든 part를 한꺼번에 요청
// 응답이 무거워지고 불필요한 데이터까지 전송
const badUrl = '...?part=snippet,statistics,contentDetails,topicDetails,recordingDetails,status';

// 좋은 예: 필요한 part만 요청
// 제목과 조회수만 필요하다면
const goodUrl = '...?part=snippet,statistics';
```

주요 `part` 항목의 용도는 다음과 같습니다.

| part | 포함 데이터 | 용도 |
|------|------------|------|
| snippet | 제목, 설명, 채널명, 게시일, 썸네일 | 기본 정보 (거의 항상 필요) |
| statistics | 조회수, 좋아요, 댓글 수 | 성과 분석 |
| contentDetails | 영상 길이, 화질, 캡션 여부 | 영상 상세 분석 |
| topicDetails | 주제 카테고리 | 주제 분류 |
| status | 공개/비공개 상태, 라이선스 | 상태 확인 |

### 전략 2: search.list 대신 videos.list 사용하기

**이것이 가장 중요한 최적화 전략입니다.** search.list는 호출 한 번에 100 유닛이지만, videos.list는 1 유닛입니다. 가능하면 search.list의 사용을 최소화하고 videos.list를 활용하세요.

예를 들어 채널의 최근 영상 50개의 상세정보가 필요한 경우를 비교해 보겠습니다.

```javascript
// 비효율적 방법: search.list로 바로 검색 → 100 유닛 x 여러 페이지
function inefficientApproach(channelId) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  // search.list로 채널의 영상 검색 → 100 유닛!
  const url = 'https://www.googleapis.com/youtube/v3/search'
    + `?part=snippet`
    + `&channelId=${channelId}`
    + `&type=video`
    + `&maxResults=50`
    + `&order=date`
    + `&key=${apiKey}`;
  
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  const data = JSON.parse(response.getContentText());
  
  // 이 방법으로는 statistics(조회수 등)를 가져올 수 없습니다!
  // search.list의 snippet에는 statistics가 포함되지 않기 때문입니다.
  // 결국 videos.list를 추가로 호출해야 합니다.
  // 총 비용: 100 + 1 = 101 유닛
  
  return data.items;
}

// 효율적 방법: channels.list → playlistItems.list → videos.list
function efficientApproach(channelId) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  // 1단계: 채널의 업로드 재생목록 ID 가져오기 (1 유닛)
  const channelUrl = 'https://www.googleapis.com/youtube/v3/channels'
    + `?part=contentDetails`
    + `&id=${channelId}`
    + `&key=${apiKey}`;
  
  const channelResponse = UrlFetchApp.fetch(channelUrl, { muteHttpExceptions: true });
  const channelData = JSON.parse(channelResponse.getContentText());
  const uploadsPlaylistId = channelData.items[0].contentDetails.relatedPlaylists.uploads;
  
  // 2단계: 업로드 재생목록에서 영상 ID 목록 가져오기 (1 유닛)
  const playlistUrl = 'https://www.googleapis.com/youtube/v3/playlistItems'
    + `?part=contentDetails`
    + `&playlistId=${uploadsPlaylistId}`
    + `&maxResults=50`
    + `&key=${apiKey}`;
  
  const playlistResponse = UrlFetchApp.fetch(playlistUrl, { muteHttpExceptions: true });
  const playlistData = JSON.parse(playlistResponse.getContentText());
  const videoIds = playlistData.items.map(item => item.contentDetails.videoId);
  
  // 3단계: videos.list로 상세정보 가져오기 (1 유닛 - 50개 동시 조회!)
  const videosUrl = 'https://www.googleapis.com/youtube/v3/videos'
    + `?part=snippet,statistics,contentDetails`
    + `&id=${videoIds.join(',')}`
    + `&key=${apiKey}`;
  
  const videosResponse = UrlFetchApp.fetch(videosUrl, { muteHttpExceptions: true });
  const videosData = JSON.parse(videosResponse.getContentText());
  
  // 총 비용: 1 + 1 + 1 = 3 유닛! (101 유닛 대비 약 33배 절약)
  return videosData.items;
}
```

### 전략 3: 2단계 검색 패턴

키워드 검색이 반드시 필요한 경우에도 최적화할 수 있습니다. search.list에서는 영상 ID만 가져오고(part=id로 변경할 수는 없지만, snippet만 최소한으로 요청), videos.list에서 상세정보를 가져오는 2단계 패턴을 사용합니다.

```javascript
/**
 * 효율적인 키워드 검색 함수
 * search.list (100 유닛) + videos.list (1 유닛) = 총 101 유닛으로
 * 최대 50개 영상의 전체 정보(snippet + statistics + contentDetails)를 가져옵니다.
 *
 * 만약 search.list만으로 statistics까지 가져오려 했다면,
 * search.list는 statistics를 제공하지 않으므로 어차피 videos.list가 필요합니다.
 */
function efficientSearch(keyword, maxResults = 50) {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  // Step 1: search.list로 영상 ID만 수집 (100 유닛)
  console.log(`[Step 1] '${keyword}' 키워드 검색 중...`);
  
  const searchUrl = 'https://www.googleapis.com/youtube/v3/search'
    + `?part=snippet`
    + `&q=${encodeURIComponent(keyword)}`
    + `&type=video`
    + `&maxResults=${maxResults}`
    + `&order=relevance`
    + `&regionCode=KR`
    + `&key=${apiKey}`;
  
  const searchResponse = UrlFetchApp.fetch(searchUrl, { muteHttpExceptions: true });
  
  if (searchResponse.getResponseCode() !== 200) {
    console.error('검색 에러:', searchResponse.getContentText());
    return [];
  }
  
  const searchData = JSON.parse(searchResponse.getContentText());
  const videoIds = searchData.items.map(item => item.id.videoId);
  
  console.log(`  → ${videoIds.length}개 영상 ID 수집 완료`);
  
  if (videoIds.length === 0) return [];
  
  // Step 2: videos.list로 상세정보 일괄 조회 (1 유닛)
  console.log('[Step 2] 영상 상세정보 조회 중...');
  
  const videosUrl = 'https://www.googleapis.com/youtube/v3/videos'
    + `?part=snippet,statistics,contentDetails`
    + `&id=${videoIds.join(',')}`
    + `&key=${apiKey}`;
  
  const videosResponse = UrlFetchApp.fetch(videosUrl, { muteHttpExceptions: true });
  
  if (videosResponse.getResponseCode() !== 200) {
    console.error('영상 조회 에러:', videosResponse.getContentText());
    return [];
  }
  
  const videosData = JSON.parse(videosResponse.getContentText());
  
  const results = videosData.items.map(item => ({
    videoId: item.id,
    title: item.snippet.title,
    channelTitle: item.snippet.channelTitle,
    channelId: item.snippet.channelId,
    publishedAt: item.snippet.publishedAt,
    description: item.snippet.description,
    tags: (item.snippet.tags || []).join(', '),
    categoryId: item.snippet.categoryId,
    duration: item.contentDetails.duration,
    viewCount: parseInt(item.statistics.viewCount || '0'),
    likeCount: parseInt(item.statistics.likeCount || '0'),
    commentCount: parseInt(item.statistics.commentCount || '0'),
    thumbnail: item.snippet.thumbnails.high?.url || ''
  }));
  
  // 총 비용 로그
  console.log(`[완료] 총 할당량 사용: 약 101 유닛 (search: 100 + videos: 1)`);
  console.log(`  → ${results.length}개 영상의 전체 상세정보를 가져왔습니다.`);
  
  return results;
}

/**
 * 효율적 검색 결과를 스프레드시트에 저장
 */
function efficientSearchAndSave() {
  const keyword = '유튜브 자동화';
  const results = efficientSearch(keyword, 50);
  
  if (results.length === 0) {
    console.log('검색 결과가 없습니다.');
    return;
  }
  
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('효율검색')
    || SpreadsheetApp.getActiveSpreadsheet().insertSheet('효율검색');
  
  // 헤더 (첫 번째 실행 시에만)
  if (sheet.getLastRow() === 0) {
    const headers = [[
      '영상ID', '제목', '채널명', '채널ID', '게시일', 
      '태그', '카테고리ID', '영상길이',
      '조회수', '좋아요', '댓글수',
      '검색키워드', '수집일'
    ]];
    sheet.getRange(1, 1, 1, headers[0].length).setValues(headers);
    sheet.getRange(1, 1, 1, headers[0].length).setFontWeight('bold').setBackground('#4285f4').setFontColor('#ffffff');
  }
  
  // 데이터 기록
  const rows = results.map(r => [
    r.videoId, r.title, r.channelTitle, r.channelId, r.publishedAt,
    r.tags, r.categoryId, r.duration,
    r.viewCount, r.likeCount, r.commentCount,
    keyword, new Date()
  ]);
  
  const startRow = sheet.getLastRow() + 1;
  sheet.getRange(startRow, 1, rows.length, rows[0].length).setValues(rows);
  
  // 조회수 기준 내림차순 정렬 (헤더 제외)
  if (sheet.getLastRow() > 1) {
    const dataRange = sheet.getRange(2, 1, sheet.getLastRow() - 1, sheet.getLastColumn());
    dataRange.sort({ column: 9, ascending: false }); // 9번째 열 = 조회수
  }
  
  console.log(`${rows.length}개 영상을 스프레드시트에 저장했습니다.`);
}
```

### 전략 4: 스프레드시트 캐싱으로 중복 호출 방지

이미 수집한 영상의 데이터를 다시 API로 조회하는 것은 할당량 낭비입니다. 스프레드시트에 저장된 데이터를 캐시로 활용하세요.

```javascript
/**
 * 스프레드시트 캐싱을 적용한 영상 정보 조회
 * 이미 수집한 영상은 API를 호출하지 않습니다.
 */
function getVideoDetailsWithCache(videoIds) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('영상캐시');
  
  // 캐시 시트가 없으면 생성
  if (!sheet) {
    const newSheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet('영상캐시');
    newSheet.getRange(1, 1, 1, 5).setValues([['영상ID', '제목', '조회수', '수집일', 'JSON데이터']]);
    return getVideoDetails(videoIds); // 캐시가 없으니 전부 API 호출
  }
  
  // 기존 캐시 데이터 로드
  const cacheData = sheet.getDataRange().getValues();
  const cachedIds = new Set(cacheData.slice(1).map(row => row[0]));
  
  // 캐시에 없는 영상만 필터링
  const uncachedIds = videoIds.filter(id => !cachedIds.has(id));
  
  console.log(`전체 ${videoIds.length}개 중 캐시 히트: ${videoIds.length - uncachedIds.length}개, 새로 조회 필요: ${uncachedIds.length}개`);
  
  if (uncachedIds.length === 0) {
    console.log('모든 데이터가 캐시에 있습니다. API 호출을 하지 않습니다.');
    // 캐시에서 데이터 반환
    return cacheData.slice(1)
      .filter(row => videoIds.includes(row[0]))
      .map(row => JSON.parse(row[4]));
  }
  
  // 캐시에 없는 영상만 API 호출
  const newDetails = getVideoDetailsBatch(uncachedIds);
  
  // 새로 가져온 데이터를 캐시에 저장
  if (newDetails.length > 0) {
    const newRows = newDetails.map(v => [
      v.videoId,
      v.title,
      v.viewCount,
      new Date(),
      JSON.stringify(v)
    ]);
    
    const startRow = sheet.getLastRow() + 1;
    sheet.getRange(startRow, 1, newRows.length, newRows[0].length).setValues(newRows);
    console.log(`${newRows.length}개의 영상 데이터를 캐시에 저장했습니다.`);
  }
  
  // 캐시 데이터 + 새 데이터 합쳐서 반환
  const cachedDetails = cacheData.slice(1)
    .filter(row => videoIds.includes(row[0]) && cachedIds.has(row[0]))
    .map(row => JSON.parse(row[4]));
  
  return [...cachedDetails, ...newDetails];
}
```

### 할당량 사용 현황을 모니터링하는 유틸리티

```javascript
/**
 * 현재 할당량 사용 현황을 추적하는 간단한 카운터
 * 스크립트 실행 중 사용한 유닛을 추적합니다.
 */
const QuotaTracker = {
  _used: 0,
  _daily_limit: 10000,
  _log: [],
  
  add(units, endpoint) {
    this._used += units;
    this._log.push({
      time: new Date().toLocaleTimeString(),
      endpoint: endpoint,
      units: units,
      cumulative: this._used
    });
    
    const remaining = this._daily_limit - this._used;
    if (remaining < 1000) {
      console.warn(`경고: 잔여 할당량이 ${remaining} 유닛입니다!`);
    }
  },
  
  getUsed() { return this._used; },
  getRemaining() { return this._daily_limit - this._used; },
  
  report() {
    console.log('=== 할당량 사용 리포트 ===');
    console.log(`사용: ${this._used} / ${this._daily_limit} 유닛`);
    console.log(`잔여: ${this.getRemaining()} 유닛 (${((this.getRemaining() / this._daily_limit) * 100).toFixed(1)}%)`);
    console.log('--- 상세 내역 ---');
    this._log.forEach(entry => {
      console.log(`  [${entry.time}] ${entry.endpoint}: ${entry.units} 유닛 (누적: ${entry.cumulative})`);
    });
  }
};

/**
 * 할당량 추적이 포함된 검색 함수 사용 예시
 */
function searchWithQuotaTracking() {
  const apiKey = PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
  
  // search.list 호출
  const searchUrl = `https://www.googleapis.com/youtube/v3/search?part=snippet&q=${encodeURIComponent('앱스 스크립트')}&type=video&maxResults=10&key=${apiKey}`;
  const searchResponse = UrlFetchApp.fetch(searchUrl, { muteHttpExceptions: true });
  QuotaTracker.add(100, 'search.list');
  
  if (searchResponse.getResponseCode() === 200) {
    const searchData = JSON.parse(searchResponse.getContentText());
    const videoIds = searchData.items.map(item => item.id.videoId).join(',');
    
    // videos.list 호출
    const videosUrl = `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id=${videoIds}&key=${apiKey}`;
    const videosResponse = UrlFetchApp.fetch(videosUrl, { muteHttpExceptions: true });
    QuotaTracker.add(1, 'videos.list');
  }
  
  // 리포트 출력
  QuotaTracker.report();
}
```

---

## 5.8 구글에 할당량 추가 요청하기

하루 10,000 유닛으로 부족하다면 구글에 할당량 증가를 요청할 수 있습니다. 정당한 사용 목적이 있다면 대부분 승인됩니다.

### 할당량 증가 요청 절차

**1단계: Google Cloud Console 접속**

[console.cloud.google.com](https://console.cloud.google.com)에서 해당 프로젝트를 선택합니다.

**2단계: 할당량 페이지 접근**

왼쪽 메뉴에서 **API 및 서비스 > YouTube Data API v3**을 클릭한 후, **할당량(Quotas)** 탭으로 이동합니다.

**3단계: 할당량 증가 요청**

상단의 연필 아이콘 또는 **할당량 수정 요청** 링크를 클릭합니다. Google Cloud Console의 "Quotas & System Limits" 페이지에서 해당 할당량을 선택하고 **Edit Quotas** 버튼을 클릭합니다.

**4단계: 요청서 작성**

요청 양식에 다음 내용을 포함해야 합니다.

### 요청서 작성 가이드

요청서를 작성할 때 구글이 확인하는 핵심 정보는 다음과 같습니다.

**1. 서비스 설명 (Project Description)**

```
YouTube 영상 분석 도구입니다. Google Sheets와 Apps Script를 사용하여 
키워드 트렌드 분석, 채널 성과 비교, 댓글 감성 분석 기능을 제공합니다.
현재 [N]명의 사용자가 사용 중이며, 일일 약 [N]건의 영상 데이터를 
분석합니다. 읽기 전용(GET) 요청만 사용하며, 데이터는 내부 분석 
목적으로만 활용합니다.
```

**2. 현재 사용량과 필요 사용량 근거**

```
현재 일일 할당량: 10,000 유닛
현재 평균 사용량: 약 8,500 유닛/일
요청 할당량: 50,000 유닛/일

사용량 내역:
- search.list: 일 30회 x 100 유닛 = 3,000 유닛
- videos.list: 일 200회 x 1 유닛 = 200 유닛
- channels.list: 일 50회 x 1 유닛 = 50 유닛
- playlistItems.list: 일 100회 x 1 유닛 = 100 유닛
- 기타: 약 150 유닛

증가 필요 사유: 분석 대상 채널 수가 현재 10개에서 50개로 확대됨에 따라
search.list 호출이 일 150회로 증가할 예정
```

**3. YouTube API 서비스 약관 준수 확인**

- 수집한 데이터를 재판매하거나 제3자에게 제공하지 않는다는 내용
- 30일 이상 캐싱하지 않는다는 내용 (YouTube API Terms of Service)
- 사용자의 개인정보를 수집하지 않는다는 내용

### 현실적인 기대치

| 요청 규모 | 승인 가능성 | 소요 시간 |
|-----------|------------|-----------|
| 10,000 → 50,000 유닛 | 높음 | 1-3일 |
| 10,000 → 100,000 유닛 | 보통 | 3-7일 |
| 10,000 → 1,000,000 유닛 | 낮음 (상세 심사 필요) | 1-4주 |

> **실용적 조언:** 처음에는 50,000 유닛을 요청하세요. 승인 확률이 높고, 대부분의 유튜브 자동화 프로젝트에 충분합니다. 5.7절에서 배운 최적화 기법을 적용하면 50,000 유닛으로 하루에 수천 개의 영상 데이터를 분석할 수 있습니다. 그래도 부족하면 추가로 증가를 요청할 수 있습니다.

### 할당량 초과 시 대응 방법

할당량이 초과되면 API가 HTTP 403 에러를 반환합니다. 이를 코드에서 감지하고 대응하는 방법입니다.

```javascript
/**
 * 할당량 초과를 감지하고 대응하는 API 호출 래퍼
 */
function quotaAwareFetch(url, options = {}) {
  const response = UrlFetchApp.fetch(url, { 
    muteHttpExceptions: true, 
    ...options 
  });
  
  if (response.getResponseCode() === 403) {
    const errorData = JSON.parse(response.getContentText());
    const reason = errorData.error?.errors?.[0]?.reason;
    
    if (reason === 'quotaExceeded' || reason === 'dailyLimitExceeded') {
      console.error('일일 할당량이 초과되었습니다!');
      
      // 할당량 초과 시 실행 중인 작업을 중단하고 상태를 저장
      const props = PropertiesService.getScriptProperties();
      props.setProperty('QUOTA_EXCEEDED_DATE', new Date().toISOString());
      props.setProperty('PENDING_TASK', JSON.stringify({
        url: url,
        timestamp: new Date().toISOString()
      }));
      
      // 이메일 알림 (선택사항)
      // MailApp.sendEmail(
      //   'your@email.com', 
      //   '[유튜브 자동화] 할당량 초과 알림',
      //   `일일 API 할당량이 초과되었습니다.\n시간: ${new Date()}\n내일 자동으로 재시도됩니다.`
      // );
      
      throw new Error('QUOTA_EXCEEDED');
    }
  }
  
  return response;
}
```

---

## 5.9 이 장의 핵심 정리

| 항목 | 핵심 내용 |
|------|-----------|
| API란? | 프로그램이 서비스와 소통하는 규약. URL + 파라미터로 요청, JSON으로 응답 |
| 주요 API | YouTube Data API v3 (이 책에서 집중 사용) |
| 핵심 엔드포인트 | search.list(100유닛), videos.list(1유닛), channels.list(1유닛), commentThreads.list(1유닛), playlistItems.list(1유닛) |
| 기본 할당량 | 일 10,000 유닛 (PST 자정 리셋) |
| API 키 없이 사용 | Google 고급 서비스 (편집기 > 서비스 > YouTube Data API v3 추가) |
| API 키 발급 | Google Cloud Console > 프로젝트 생성 > API 활성화 > 인증정보 생성 |
| 핵심 최적화 | search.list 최소화, 2단계 검색 패턴, 캐싱, part 파라미터 최적화 |
| 할당량 증가 | Cloud Console에서 요청. 50,000 유닛까지는 보통 승인됨 |

다음 장에서는 이 장에서 배운 API 활용법을 기반으로, 유튜브 데이터를 자동으로 수집하고 스프레드시트에 정리하는 실전 자동화 시스템을 구축해 보겠습니다.
