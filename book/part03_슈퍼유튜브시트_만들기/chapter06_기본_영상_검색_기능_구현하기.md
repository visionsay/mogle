# Chapter 06: 기본 영상 검색 기능 구현하기

이 장에서는 구글 시트 위에 유튜브 영상 검색 시스템을 처음부터 끝까지 구축한다. 사용자 정의 메뉴, API 키 관리, 검색 로직, 사이드바 UI, 결과 출력까지 — 모든 코드는 복사해서 바로 실행할 수 있는 완전한 형태로 제공한다.

---

## [바로 실습] 나만의 메뉴 만들기

구글 시트를 열 때마다 상단 메뉴바에 우리만의 커스텀 메뉴가 자동으로 나타나도록 만든다. `onOpen()`은 구글 앱스 스크립트가 제공하는 **심플 트리거(Simple Trigger)**로, 스프레드시트가 열릴 때 자동 실행된다.

### 기본 메뉴 구조 만들기

앱스 스크립트 편집기에서 새 스크립트 파일을 만들고 이름을 `01_메뉴.gs`로 지정한다. 아래 코드를 입력하자.

```javascript
/**
 * 스프레드시트가 열릴 때 자동 실행되는 트리거
 * 상단 메뉴바에 '슈퍼유튜브시트' 메뉴를 추가한다
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  
  // 서브메뉴: 검색 옵션
  const searchSubMenu = ui.createMenu('🔍 검색 옵션')
    .addItem('📋 기본 검색', 'showSearchSidebar')
    .addItem('🎯 고급 검색 (필터)', 'showAdvancedSearchSidebar')
    .addItem('📺 채널 영상 검색', 'showChannelVideoSearch');

  // 서브메뉴: 분석 도구
  const analysisSubMenu = ui.createMenu('📊 분석 도구')
    .addItem('📈 채널 분석', 'showChannelAnalysis')
    .addItem('🔥 떡상 영상 분석', 'highlightViralVideos')
    .addItem('📉 트렌드 비교', 'showTrendComparison');

  // 메인 메뉴 구성
  ui.createMenu('🎬 슈퍼유튜브시트')
    .addSubMenu(searchSubMenu)
    .addSubMenu(analysisSubMenu)
    .addItem('💬 댓글 수집', 'showCommentCollector')
    .addSeparator()
    .addItem('📑 목차 업데이트', 'updateTableOfContents')
    .addItem('🎨 서식 자동 적용', 'autoFormatCurrentSheet')
    .addSeparator()
    .addItem('⚙️ API 키 설정', 'showApiKeyDialog')
    .addItem('ℹ️ 사용 가이드', 'showUserGuide')
    .addToUi();
}

/**
 * 사용 가이드 대화상자를 표시한다
 */
function showUserGuide() {
  const html = HtmlService.createHtmlOutput(`
    <div style="font-family: 'Google Sans', Arial, sans-serif; padding: 16px; line-height: 1.8;">
      <h2 style="color: #1a73e8;">🎬 슈퍼유튜브시트 사용 가이드</h2>
      <hr style="border: 1px solid #e0e0e0;">
      <h3>🔍 영상 검색</h3>
      <p>메뉴에서 <b>검색 옵션 → 기본 검색</b>을 선택하면 사이드바가 열립니다.<br>
      검색어를 입력하고 검색 버튼을 클릭하세요.</p>
      <h3>⚙️ 최초 설정</h3>
      <p>사용 전 반드시 <b>API 키 설정</b>에서 YouTube Data API v3 키를 등록하세요.</p>
      <h3>📊 결과 확인</h3>
      <p>검색 결과는 새 시트에 자동으로 생성됩니다.<br>
      각 시트 이름에는 검색어와 날짜가 포함됩니다.</p>
      <h3>🔥 떡상 영상</h3>
      <p>검색 후 <b>분석 도구 → 떡상 영상 분석</b>을 실행하면<br>
      바이럴 지수에 따라 셀이 자동으로 색칠됩니다.</p>
    </div>
  `)
    .setWidth(420)
    .setHeight(480);
  
  SpreadsheetApp.getUi().showModalDialog(html, '사용 가이드');
}
```

이 코드를 저장하고 스프레드시트를 새로고침하면, 상단 메뉴바에 **🎬 슈퍼유튜브시트** 메뉴가 나타난다. 서브메뉴까지 포함해 체계적인 메뉴 구조를 갖추었다.

> **핵심 포인트:** `onOpen()`은 반드시 이 정확한 이름이어야 한다. 이름을 바꾸면 자동 실행되지 않는다. 또한 `onOpen()`에서는 권한이 필요한 서비스(예: `UrlFetchApp`)를 직접 호출할 수 없다. 메뉴 항목을 클릭했을 때 실행되는 함수에서 호출해야 한다.

---

## [바로 실습] 유튜브 API 키 안전하게 저장하기

API 키를 코드에 직접 하드코딩하면 보안상 위험하다. `PropertiesService`를 사용하면 키를 암호화된 형태로 서버 측에 저장할 수 있다. 새 스크립트 파일 `02_API키관리.gs`를 만들자.

### API 키 저장/조회 함수

```javascript
/**
 * YouTube API 키를 PropertiesService에 안전하게 저장한다
 * @param {string} apiKey - YouTube Data API v3 키
 * @returns {Object} 저장 결과 {success: boolean, message: string}
 */
function saveApiKey(apiKey) {
  try {
    // 입력값 기본 검증
    if (!apiKey || apiKey.trim().length === 0) {
      return { success: false, message: 'API 키를 입력해주세요.' };
    }
    
    const trimmedKey = apiKey.trim();
    
    // API 키 형식 검증 (Google API 키는 보통 39자)
    if (trimmedKey.length < 30 || trimmedKey.length > 50) {
      return { success: false, message: 'API 키 형식이 올바르지 않습니다. 길이를 확인해주세요.' };
    }
    
    // 실제 API 호출로 키 유효성 검증
    const validationResult = validateApiKey(trimmedKey);
    if (!validationResult.valid) {
      return { success: false, message: validationResult.message };
    }
    
    // PropertiesService에 저장 (서버 측 암호화 저장)
    PropertiesService.getScriptProperties().setProperty('YOUTUBE_API_KEY', trimmedKey);
    
    return { success: true, message: 'API 키가 성공적으로 저장되었습니다! ✅' };
  } catch (error) {
    return { success: false, message: '저장 중 오류가 발생했습니다: ' + error.message };
  }
}

/**
 * 저장된 API 키를 가져온다
 * @returns {string|null} 저장된 API 키 또는 null
 */
function getApiKey() {
  return PropertiesService.getScriptProperties().getProperty('YOUTUBE_API_KEY');
}

/**
 * API 키가 실제로 작동하는지 YouTube API를 호출하여 검증한다
 * @param {string} apiKey - 검증할 API 키
 * @returns {Object} {valid: boolean, message: string}
 */
function validateApiKey(apiKey) {
  try {
    // 가장 가벼운 API 호출: videoCategories.list
    const testUrl = 'https://www.googleapis.com/youtube/v3/videoCategories'
      + '?part=snippet'
      + '&regionCode=KR'
      + '&key=' + apiKey;
    
    const response = UrlFetchApp.fetch(testUrl, { muteHttpExceptions: true });
    const statusCode = response.getResponseCode();
    
    if (statusCode === 200) {
      return { valid: true, message: '유효한 API 키입니다.' };
    } else if (statusCode === 400) {
      return { valid: false, message: 'API 키 형식이 올바르지 않습니다.' };
    } else if (statusCode === 403) {
      const errorData = JSON.parse(response.getContentText());
      const errorReason = errorData.error?.errors?.[0]?.reason || 'unknown';
      
      if (errorReason === 'accessNotConfigured') {
        return { 
          valid: false, 
          message: 'YouTube Data API v3가 활성화되지 않았습니다. Google Cloud Console에서 API를 활성화해주세요.' 
        };
      }
      return { valid: false, message: 'API 키 권한이 부족합니다: ' + errorReason };
    } else {
      return { valid: false, message: '알 수 없는 오류 (HTTP ' + statusCode + ')' };
    }
  } catch (error) {
    return { valid: false, message: 'API 연결 테스트 실패: ' + error.message };
  }
}

/**
 * 저장된 API 키를 삭제한다
 */
function deleteApiKey() {
  PropertiesService.getScriptProperties().deleteProperty('YOUTUBE_API_KEY');
  return { success: true, message: 'API 키가 삭제되었습니다.' };
}

/**
 * 현재 API 키 상태를 확인한다 (키 값은 마스킹 처리)
 * @returns {Object} {hasKey: boolean, maskedKey: string}
 */
function getApiKeyStatus() {
  const key = getApiKey();
  if (!key) {
    return { hasKey: false, maskedKey: '' };
  }
  // 앞 4자리만 보이고 나머지는 마스킹
  const masked = key.substring(0, 4) + '****' + key.substring(key.length - 4);
  return { hasKey: true, maskedKey: masked };
}
```

### API 키 입력 대화상자

```javascript
/**
 * API 키 설정 대화상자를 표시한다
 */
function showApiKeyDialog() {
  const html = HtmlService.createHtmlOutput(`
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          font-family: 'Google Sans', 'Noto Sans KR', Arial, sans-serif;
          padding: 24px;
          background: #fafafa;
          color: #202124;
        }
        .container { max-width: 100%; }
        h2 {
          font-size: 20px;
          font-weight: 600;
          margin-bottom: 8px;
          color: #1a73e8;
        }
        .description {
          font-size: 13px;
          color: #5f6368;
          margin-bottom: 20px;
          line-height: 1.6;
        }
        .status-box {
          background: #fff;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 20px;
        }
        .status-label {
          font-size: 12px;
          color: #5f6368;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 4px;
        }
        .status-value {
          font-size: 14px;
          font-weight: 500;
        }
        .status-active { color: #1e8e3e; }
        .status-inactive { color: #d93025; }
        
        label {
          display: block;
          font-size: 13px;
          font-weight: 500;
          margin-bottom: 6px;
          color: #3c4043;
        }
        input[type="text"] {
          width: 100%;
          padding: 10px 12px;
          border: 1px solid #dadce0;
          border-radius: 6px;
          font-size: 14px;
          font-family: 'Roboto Mono', monospace;
          transition: border-color 0.2s;
          outline: none;
        }
        input[type="text"]:focus {
          border-color: #1a73e8;
          box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.15);
        }
        .btn-group {
          display: flex;
          gap: 8px;
          margin-top: 16px;
        }
        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        .btn-primary {
          background: #1a73e8;
          color: white;
          flex: 1;
        }
        .btn-primary:hover { background: #1557b0; }
        .btn-danger {
          background: #fff;
          color: #d93025;
          border: 1px solid #d93025;
        }
        .btn-danger:hover { background: #fce8e6; }
        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
        
        .message {
          margin-top: 16px;
          padding: 12px;
          border-radius: 6px;
          font-size: 13px;
          display: none;
        }
        .message.success { background: #e6f4ea; color: #1e8e3e; display: block; }
        .message.error { background: #fce8e6; color: #d93025; display: block; }
        .message.loading { background: #e8f0fe; color: #1a73e8; display: block; }
        
        .help-link {
          display: block;
          margin-top: 16px;
          font-size: 12px;
          color: #1a73e8;
          text-decoration: none;
        }
        .spinner {
          display: inline-block;
          width: 14px;
          height: 14px;
          border: 2px solid #1a73e8;
          border-top-color: transparent;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
          margin-right: 6px;
          vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      </style>
    </head>
    <body>
      <div class="container">
        <h2>⚙️ YouTube API 키 설정</h2>
        <p class="description">
          YouTube Data API v3 키를 입력하세요.<br>
          키는 서버에 암호화되어 안전하게 저장됩니다.
        </p>
        
        <div class="status-box" id="statusBox">
          <div class="status-label">현재 상태</div>
          <div class="status-value" id="statusValue">확인 중...</div>
        </div>
        
        <label for="apiKeyInput">API 키</label>
        <input type="text" id="apiKeyInput" placeholder="AIzaSy... 형태의 API 키를 붙여넣으세요">
        
        <div class="btn-group">
          <button class="btn btn-primary" id="saveBtn" onclick="saveKey()">
            저장 및 검증
          </button>
          <button class="btn btn-danger" id="deleteBtn" onclick="deleteKey()">
            삭제
          </button>
        </div>
        
        <div id="message"></div>
        
        <a class="help-link" href="https://console.cloud.google.com/apis/credentials" 
           target="_blank">
          🔗 Google Cloud Console에서 API 키 발급받기
        </a>
      </div>

      <script>
        // 페이지 로드 시 현재 키 상태 확인
        google.script.run
          .withSuccessHandler(function(status) {
            const el = document.getElementById('statusValue');
            if (status.hasKey) {
              el.textContent = '✅ 등록됨 (' + status.maskedKey + ')';
              el.className = 'status-value status-active';
            } else {
              el.textContent = '❌ 미등록';
              el.className = 'status-value status-inactive';
            }
          })
          .getApiKeyStatus();
        
        function showMessage(text, type) {
          const el = document.getElementById('message');
          el.textContent = text;
          el.className = 'message ' + type;
        }
        
        function setLoading(isLoading) {
          const btn = document.getElementById('saveBtn');
          btn.disabled = isLoading;
          if (isLoading) {
            btn.innerHTML = '<span class="spinner"></span>검증 중...';
            showMessage('API 키를 검증하고 있습니다. 잠시만 기다려주세요...', 'loading');
          } else {
            btn.innerHTML = '저장 및 검증';
          }
        }
        
        function saveKey() {
          const key = document.getElementById('apiKeyInput').value;
          if (!key.trim()) {
            showMessage('API 키를 입력해주세요.', 'error');
            return;
          }
          
          setLoading(true);
          
          google.script.run
            .withSuccessHandler(function(result) {
              setLoading(false);
              if (result.success) {
                showMessage(result.message, 'success');
                // 상태 새로고침
                google.script.run
                  .withSuccessHandler(function(status) {
                    const el = document.getElementById('statusValue');
                    el.textContent = '✅ 등록됨 (' + status.maskedKey + ')';
                    el.className = 'status-value status-active';
                  })
                  .getApiKeyStatus();
              } else {
                showMessage(result.message, 'error');
              }
            })
            .withFailureHandler(function(error) {
              setLoading(false);
              showMessage('오류: ' + error.message, 'error');
            })
            .saveApiKey(key);
        }
        
        function deleteKey() {
          if (!confirm('정말로 API 키를 삭제하시겠습니까?')) return;
          
          google.script.run
            .withSuccessHandler(function(result) {
              showMessage(result.message, 'success');
              const el = document.getElementById('statusValue');
              el.textContent = '❌ 미등록';
              el.className = 'status-value status-inactive';
              document.getElementById('apiKeyInput').value = '';
            })
            .deleteApiKey();
        }
      </script>
    </body>
    </html>
  `)
    .setWidth(440)
    .setHeight(520);
  
  SpreadsheetApp.getUi().showModalDialog(html, 'API 키 설정');
}
```

> **보안 팁:** `PropertiesService.getScriptProperties()`에 저장된 값은 스크립트 프로젝트에 바인딩된다. 스프레드시트를 복사하더라도 Properties 값은 복사되지 않으므로, 실수로 API 키가 유출될 위험이 낮다. 절대로 코드에 직접 키를 적지 말자.

---

## [바로 실습] 첫 검색 테스트하기

유튜브 검색의 핵심 로직을 구현한다. 여기서 가장 중요한 설계 결정은 **2단계 검색 전략**이다. 새 파일 `03_검색엔진.gs`를 만들자.

### 왜 2단계 검색인가?

YouTube Data API의 `search.list`는 기본적인 정보(영상 ID, 제목, 채널명)만 반환한다. 조회수, 좋아요, 댓글수 같은 상세 데이터는 `videos.list`를 별도로 호출해야 한다. 할당량(쿼터) 관점에서도 이 방식이 효율적이다.

| API 메서드 | 할당량 비용 | 반환 데이터 |
|-----------|-----------|-----------|
| `search.list` | 100 | 영상 ID, 제목, 채널, 썸네일, 게시일 |
| `videos.list` | 1 | 조회수, 좋아요, 댓글수, 영상길이, 태그 등 전체 |

`search.list` 1회(100) + `videos.list` 1회(1) = **총 101 할당량**으로 최대 50개 영상의 전체 데이터를 가져올 수 있다.

### 검색 함수 구현

```javascript
/**
 * YouTube 영상을 검색하고 상세 정보를 가져온다 (2단계 검색)
 * @param {string} query - 검색어
 * @param {number} maxResults - 가져올 영상 수 (최대 50)
 * @param {Object} options - 추가 검색 옵션
 * @returns {Array<Object>} 영상 정보 배열
 */
function searchYouTubeVideos(query, maxResults, options) {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('API 키가 설정되지 않았습니다. 메뉴 → API 키 설정에서 등록해주세요.');
  }
  
  maxResults = Math.min(maxResults || 10, 50);
  options = options || {};
  
  // ===== 1단계: search.list로 영상 ID 목록 가져오기 =====
  let searchUrl = 'https://www.googleapis.com/youtube/v3/search'
    + '?part=snippet'
    + '&type=video'
    + '&q=' + encodeURIComponent(query)
    + '&maxResults=' + maxResults
    + '&order=' + (options.order || 'relevance')
    + '&key=' + apiKey;
  
  // 선택적 파라미터 추가
  if (options.publishedAfter)  searchUrl += '&publishedAfter=' + options.publishedAfter;
  if (options.publishedBefore) searchUrl += '&publishedBefore=' + options.publishedBefore;
  if (options.regionCode)      searchUrl += '&regionCode=' + options.regionCode;
  if (options.relevanceLanguage) searchUrl += '&relevanceLanguage=' + options.relevanceLanguage;
  if (options.videoDuration)   searchUrl += '&videoDuration=' + options.videoDuration;
  if (options.pageToken)       searchUrl += '&pageToken=' + options.pageToken;
  
  const searchResponse = UrlFetchApp.fetch(searchUrl, { muteHttpExceptions: true });
  
  if (searchResponse.getResponseCode() !== 200) {
    const errorData = JSON.parse(searchResponse.getContentText());
    throw new Error('검색 API 오류: ' + (errorData.error?.message || '알 수 없는 오류'));
  }
  
  const searchData = JSON.parse(searchResponse.getContentText());
  const videoIds = searchData.items.map(item => item.id.videoId).filter(Boolean);
  
  if (videoIds.length === 0) {
    return { videos: [], nextPageToken: null };
  }
  
  // ===== 2단계: videos.list로 상세 정보 가져오기 =====
  const videoDetails = getVideoDetails(videoIds, apiKey);
  
  return {
    videos: videoDetails,
    nextPageToken: searchData.nextPageToken || null,
    totalResults: searchData.pageInfo?.totalResults || 0
  };
}

/**
 * 영상 ID 배열로 상세 정보를 가져온다
 * @param {string[]} videoIds - 영상 ID 배열
 * @param {string} apiKey - API 키
 * @returns {Array<Object>} 상세 영상 정보 배열
 */
function getVideoDetails(videoIds, apiKey) {
  if (!apiKey) apiKey = getApiKey();
  
  const videosUrl = 'https://www.googleapis.com/youtube/v3/videos'
    + '?part=snippet,statistics,contentDetails'
    + '&id=' + videoIds.join(',')
    + '&key=' + apiKey;
  
  const videosResponse = UrlFetchApp.fetch(videosUrl, { muteHttpExceptions: true });
  
  if (videosResponse.getResponseCode() !== 200) {
    throw new Error('영상 상세 정보 조회 실패');
  }
  
  const videosData = JSON.parse(videosResponse.getContentText());
  
  return videosData.items.map(item => {
    const snippet = item.snippet;
    const stats = item.statistics;
    const contentDetails = item.contentDetails;
    
    return {
      videoId: item.id,
      title: snippet.title,
      channelTitle: snippet.channelTitle,
      channelId: snippet.channelId,
      publishedAt: snippet.publishedAt,
      description: snippet.description,
      thumbnailUrl: getThumbnailUrl(snippet.thumbnails),
      categoryId: snippet.categoryId,
      tags: snippet.tags || [],
      viewCount: parseInt(stats.viewCount || '0', 10),
      likeCount: parseInt(stats.likeCount || '0', 10),
      commentCount: parseInt(stats.commentCount || '0', 10),
      duration: contentDetails.duration,
      durationSeconds: parseDuration(contentDetails.duration),
      durationFormatted: formatDuration(contentDetails.duration),
      videoUrl: 'https://www.youtube.com/watch?v=' + item.id
    };
  });
}

/**
 * 사용 가능한 최고 해상도 썸네일 URL을 반환한다
 * @param {Object} thumbnails - 썸네일 객체
 * @returns {string} 썸네일 URL
 */
function getThumbnailUrl(thumbnails) {
  // 우선순위: maxres > high > medium > default
  if (thumbnails.maxres) return thumbnails.maxres.url;
  if (thumbnails.high)   return thumbnails.high.url;
  if (thumbnails.medium) return thumbnails.medium.url;
  return thumbnails.default.url;
}

/**
 * ISO 8601 영상 길이를 초 단위로 변환한다
 * 예: "PT1H23M45S" → 5025
 * @param {string} isoDuration - ISO 8601 형식의 영상 길이
 * @returns {number} 초 단위 길이
 */
function parseDuration(isoDuration) {
  if (!isoDuration) return 0;
  
  const match = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return 0;
  
  const hours   = parseInt(match[1] || '0', 10);
  const minutes = parseInt(match[2] || '0', 10);
  const seconds = parseInt(match[3] || '0', 10);
  
  return hours * 3600 + minutes * 60 + seconds;
}

/**
 * ISO 8601 영상 길이를 읽기 쉬운 형태로 변환한다
 * 예: "PT1H23M45S" → "1:23:45", "PT5M30S" → "5:30"
 * @param {string} isoDuration - ISO 8601 형식의 영상 길이
 * @returns {string} 포맷된 영상 길이 (H:MM:SS 또는 M:SS)
 */
function formatDuration(isoDuration) {
  if (!isoDuration) return '0:00';
  
  const totalSeconds = parseDuration(isoDuration);
  const hours   = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  
  const pad = (n) => n.toString().padStart(2, '0');
  
  if (hours > 0) {
    return hours + ':' + pad(minutes) + ':' + pad(seconds);
  }
  return minutes + ':' + pad(seconds);
}
```

### 빠른 테스트

검색 엔진이 잘 작동하는지 테스트 함수를 만들어 확인하자.

```javascript
/**
 * 검색 엔진 테스트 함수 - 스크립트 편집기에서 직접 실행
 */
function testSearch() {
  try {
    const result = searchYouTubeVideos('구글 시트 자동화', 3);
    
    result.videos.forEach((video, i) => {
      Logger.log('--- 영상 ' + (i + 1) + ' ---');
      Logger.log('제목: ' + video.title);
      Logger.log('채널: ' + video.channelTitle);
      Logger.log('조회수: ' + video.viewCount.toLocaleString());
      Logger.log('좋아요: ' + video.likeCount.toLocaleString());
      Logger.log('길이: ' + video.durationFormatted);
      Logger.log('게시일: ' + video.publishedAt);
      Logger.log('URL: ' + video.videoUrl);
      Logger.log('');
    });
    
    Logger.log('다음 페이지 토큰: ' + result.nextPageToken);
    Logger.log('총 검색 결과: ' + result.totalResults);
  } catch (error) {
    Logger.log('오류: ' + error.message);
  }
}
```

스크립트 편집기에서 `testSearch` 함수를 선택하고 실행 버튼을 누르면, 로그 창에 검색 결과가 표시된다. 이것으로 API 연동이 정상적으로 작동하는지 확인할 수 있다.

---

## [바로 실습] 간단한 사이드바 만들기

사이드바는 구글 시트 오른쪽에 열리는 패널로, 사용자가 검색어를 입력하고 결과를 확인할 수 있는 인터페이스를 제공한다. 새 HTML 파일을 만들자. 앱스 스크립트 편집기에서 **파일 → 새로 만들기 → HTML**을 선택하고 파일 이름을 `SearchSidebar`로 지정한다.

### 사이드바 열기 함수

먼저 `01_메뉴.gs`에 사이드바를 여는 함수를 추가한다.

```javascript
/**
 * 검색 사이드바를 연다
 */
function showSearchSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('SearchSidebar')
    .setTitle('🔍 유튜브 영상 검색');
  SpreadsheetApp.getUi().showSidebar(html);
}
```

### 사이드바 HTML 전체 코드

`SearchSidebar.html` 파일에 아래 전체 코드를 입력한다.

```html
<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <style>
    /* ===== 기본 리셋 및 전역 스타일 ===== */
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      font-family: 'Google Sans', 'Noto Sans KR', -apple-system, sans-serif;
      font-size: 13px;
      color: #202124;
      background: #f8f9fa;
      padding: 16px;
    }

    /* ===== 섹션 카드 스타일 ===== */
    .card {
      background: white;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    .card-title {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #5f6368;
      margin-bottom: 10px;
    }

    /* ===== 입력 필드 스타일 ===== */
    .input-group {
      margin-bottom: 10px;
    }
    .input-group label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: #3c4043;
      margin-bottom: 4px;
    }
    input[type="text"], select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #dadce0;
      border-radius: 8px;
      font-size: 13px;
      outline: none;
      transition: border-color 0.2s;
      background: #fff;
    }
    input[type="text"]:focus, select:focus {
      border-color: #1a73e8;
      box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.12);
    }

    /* ===== 필터 그리드 ===== */
    .filter-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }

    /* ===== 버튼 스타일 ===== */
    .btn-search {
      width: 100%;
      padding: 12px;
      background: #1a73e8;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }
    .btn-search:hover { background: #1557b0; }
    .btn-search:disabled {
      background: #dadce0;
      cursor: not-allowed;
    }

    /* ===== 결과 영역 ===== */
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .results-count {
      font-size: 12px;
      color: #5f6368;
    }

    .video-item {
      display: flex;
      gap: 10px;
      padding: 10px 0;
      border-bottom: 1px solid #f1f3f4;
      cursor: pointer;
      transition: background 0.15s;
    }
    .video-item:hover {
      background: #f8f9fa;
      border-radius: 8px;
      padding-left: 6px;
      margin-left: -6px;
    }
    .video-item:last-child { border-bottom: none; }

    .video-thumb {
      width: 120px;
      min-width: 120px;
      height: 68px;
      border-radius: 6px;
      object-fit: cover;
      background: #e8eaed;
    }
    .video-info { flex: 1; overflow: hidden; }
    .video-title {
      font-size: 12px;
      font-weight: 500;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      margin-bottom: 4px;
    }
    .video-channel {
      font-size: 11px;
      color: #5f6368;
      margin-bottom: 2px;
    }
    .video-stats {
      font-size: 11px;
      color: #80868b;
    }
    .video-stats span {
      margin-right: 8px;
    }

    /* ===== 상태 메시지 ===== */
    .status {
      text-align: center;
      padding: 20px;
      color: #5f6368;
      font-size: 13px;
    }
    .status.error { color: #d93025; }

    .spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 30px;
      gap: 12px;
    }
    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #e8eaed;
      border-top-color: #1a73e8;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ===== 진행 바 ===== */
    .progress-bar {
      width: 100%;
      height: 3px;
      background: #e8eaed;
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 12px;
      display: none;
    }
    .progress-bar.active { display: block; }
    .progress-bar-fill {
      height: 100%;
      background: #1a73e8;
      border-radius: 2px;
      transition: width 0.3s ease;
      width: 0%;
    }

    /* ===== 시트 저장 버튼 ===== */
    .btn-export {
      width: 100%;
      padding: 10px;
      background: #1e8e3e;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      margin-top: 8px;
      transition: background 0.2s;
    }
    .btn-export:hover { background: #137333; }
  </style>
</head>
<body>

  <!-- 검색 입력 영역 -->
  <div class="card">
    <div class="card-title">검색</div>
    <div class="input-group">
      <input type="text" id="searchQuery" placeholder="검색어를 입력하세요..."
             onkeypress="if(event.key==='Enter') performSearch()">
    </div>

    <div class="filter-grid">
      <div class="input-group">
        <label>정렬 기준</label>
        <select id="sortOrder">
          <option value="relevance">관련성</option>
          <option value="viewCount">조회수</option>
          <option value="date">최신순</option>
          <option value="rating">평점</option>
        </select>
      </div>
      <div class="input-group">
        <label>검색 개수</label>
        <select id="maxResults">
          <option value="10">10개</option>
          <option value="25" selected>25개</option>
          <option value="50">50개</option>
        </select>
      </div>
    </div>

    <button class="btn-search" id="searchBtn" onclick="performSearch()">
      🔍 검색하기
    </button>
  </div>

  <!-- 진행 상태 바 -->
  <div class="progress-bar" id="progressBar">
    <div class="progress-bar-fill" id="progressFill"></div>
  </div>

  <!-- 결과 영역 -->
  <div id="resultsArea">
    <div class="status">
      검색어를 입력하고 검색 버튼을 클릭하세요.
    </div>
  </div>

  <script>
    let currentResults = [];

    /**
     * 검색 실행
     */
    function performSearch() {
      const query = document.getElementById('searchQuery').value.trim();
      if (!query) {
        showStatus('검색어를 입력해주세요.', true);
        return;
      }

      const options = {
        order: document.getElementById('sortOrder').value,
        maxResults: parseInt(document.getElementById('maxResults').value)
      };

      // UI 상태 업데이트
      setSearching(true);
      showLoading('검색 중입니다...');
      setProgress(30);

      google.script.run
        .withSuccessHandler(function(result) {
          setSearching(false);
          setProgress(100);
          
          if (!result || !result.videos || result.videos.length === 0) {
            showStatus('검색 결과가 없습니다.', false);
            return;
          }
          
          currentResults = result.videos;
          displayResults(result.videos, result.totalResults);
        })
        .withFailureHandler(function(error) {
          setSearching(false);
          setProgress(0);
          showStatus('오류: ' + error.message, true);
        })
        .searchYouTubeVideos(query, options.maxResults, { order: options.order });
    }

    /**
     * 검색 결과를 사이드바에 표시한다
     */
    function displayResults(videos, totalResults) {
      const area = document.getElementById('resultsArea');
      
      let html = '<div class="card">';
      html += '<div class="results-header">';
      html += '<div class="card-title">검색 결과</div>';
      html += '<div class="results-count">' + videos.length + '개 / 약 ' + numberFormat(totalResults) + '개</div>';
      html += '</div>';

      videos.forEach(function(video) {
        html += '<div class="video-item" onclick="window.open(\'' + video.videoUrl + '\')">';
        html += '<img class="video-thumb" src="' + video.thumbnailUrl + '" alt="" loading="lazy">';
        html += '<div class="video-info">';
        html += '<div class="video-title">' + escapeHtml(video.title) + '</div>';
        html += '<div class="video-channel">' + escapeHtml(video.channelTitle) + '</div>';
        html += '<div class="video-stats">';
        html += '<span>👁 ' + numberFormat(video.viewCount) + '</span>';
        html += '<span>👍 ' + numberFormat(video.likeCount) + '</span>';
        html += '<span>⏱ ' + video.durationFormatted + '</span>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
      });

      html += '<button class="btn-export" onclick="exportToSheet()">📋 시트에 저장하기</button>';
      html += '</div>';
      
      area.innerHTML = html;
    }

    /**
     * 결과를 새 시트에 저장한다
     */
    function exportToSheet() {
      if (currentResults.length === 0) {
        showStatus('저장할 결과가 없습니다.', true);
        return;
      }

      showLoading('시트에 저장 중...');

      const query = document.getElementById('searchQuery').value.trim();
      
      google.script.run
        .withSuccessHandler(function(sheetName) {
          showStatus('✅ "' + sheetName + '" 시트에 저장되었습니다!', false);
        })
        .withFailureHandler(function(error) {
          showStatus('저장 오류: ' + error.message, true);
        })
        .exportSearchResults(currentResults, query);
    }

    /* ===== 유틸리티 함수 ===== */
    function showStatus(message, isError) {
      document.getElementById('resultsArea').innerHTML = 
        '<div class="status' + (isError ? ' error' : '') + '">' + message + '</div>';
    }

    function showLoading(message) {
      document.getElementById('resultsArea').innerHTML = 
        '<div class="spinner-container"><div class="spinner"></div><span>' + message + '</span></div>';
    }

    function setSearching(isSearching) {
      document.getElementById('searchBtn').disabled = isSearching;
      document.getElementById('searchBtn').innerHTML = isSearching 
        ? '<div class="spinner" style="width:18px;height:18px;border-width:2px;"></div> 검색 중...'
        : '🔍 검색하기';
    }

    function setProgress(percent) {
      const bar = document.getElementById('progressBar');
      const fill = document.getElementById('progressFill');
      bar.className = percent > 0 && percent < 100 ? 'progress-bar active' : 'progress-bar';
      fill.style.width = percent + '%';
    }

    function numberFormat(num) {
      if (num === undefined || num === null) return '0';
      return Number(num).toLocaleString('ko-KR');
    }

    function escapeHtml(text) {
      var div = document.createElement('div');
      div.appendChild(document.createTextNode(text));
      return div.innerHTML;
    }
  </script>
</body>
</html>
```

이 사이드바는 검색어 입력, 정렬 기준 선택, 결과 개수 선택, 검색 결과 미리보기, 시트 저장 기능을 모두 갖추고 있다. CSS Grid를 사용한 필터 레이아웃, Flexbox 기반 영상 카드, 로딩 스피너와 프로그레스 바까지 포함된 완성도 높은 UI이다.

---

## [바로 실습] 새 시트에 결과 출력하기

검색 결과를 새 시트에 체계적으로 출력하는 함수를 구현한다. 새 파일 `04_시트출력.gs`를 만들자.

```javascript
/**
 * 검색 결과를 새 시트에 출력한다
 * @param {Array<Object>} videos - 영상 데이터 배열
 * @param {string} query - 검색어 (시트 이름에 사용)
 * @returns {string} 생성된 시트 이름
 */
function exportSearchResults(videos, query) {
  if (!videos || videos.length === 0) {
    throw new Error('저장할 검색 결과가 없습니다.');
  }
  
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 시트 이름 생성: "검색어_날짜_시간" 형식
  const now = new Date();
  const timestamp = Utilities.formatDate(now, Session.getScriptTimeZone(), 'MMdd_HHmm');
  // 시트 이름에 사용할 수 없는 문자 제거하고 길이 제한
  const safeQuery = query.replace(/[\\\/\?\*\[\]]/g, '').substring(0, 15);
  let sheetName = safeQuery + '_' + timestamp;
  
  // 동일한 이름의 시트가 있으면 번호 추가
  let counter = 1;
  let finalName = sheetName;
  while (ss.getSheetByName(finalName)) {
    finalName = sheetName + '_' + counter;
    counter++;
  }
  sheetName = finalName;
  
  // 새 시트 생성
  const sheet = ss.insertSheet(sheetName);
  
  // ===== 헤더 설정 =====
  const headers = [
    '번호', '썸네일', '제목', '채널명', '조회수', '좋아요',
    '댓글수', '게시일', '영상길이', '태그', '설명(앞100자)',
    '참여율(%)', '영상URL'
  ];
  
  const headerRange = sheet.getRange(1, 1, 1, headers.length);
  headerRange.setValues([headers]);
  
  // 헤더 스타일링
  headerRange
    .setBackground('#1a73e8')
    .setFontColor('#ffffff')
    .setFontWeight('bold')
    .setFontSize(10)
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle')
    .setWrap(true);
  
  // 헤더 행 높이
  sheet.setRowHeight(1, 36);
  
  // ===== 데이터 행 생성 =====
  const dataRows = videos.map((video, index) => {
    // 참여율 계산: (좋아요 + 댓글수) / 조회수 * 100
    const engagementRate = video.viewCount > 0
      ? ((video.likeCount + video.commentCount) / video.viewCount * 100).toFixed(2)
      : '0.00';
    
    // 설명 앞 100자
    const shortDesc = (video.description || '').substring(0, 100).replace(/\n/g, ' ');
    
    // 태그 (최대 5개)
    const tagsStr = (video.tags || []).slice(0, 5).join(', ');
    
    // 게시일 포맷
    const publishDate = video.publishedAt 
      ? Utilities.formatDate(new Date(video.publishedAt), Session.getScriptTimeZone(), 'yyyy-MM-dd')
      : '';
    
    return [
      index + 1,                                                    // 번호
      '',                                                           // 썸네일 (수식으로 채움)
      video.title,                                                  // 제목
      video.channelTitle,                                           // 채널명
      video.viewCount,                                              // 조회수
      video.likeCount,                                              // 좋아요
      video.commentCount,                                           // 댓글수
      publishDate,                                                  // 게시일
      video.durationFormatted,                                      // 영상길이
      tagsStr,                                                      // 태그
      shortDesc,                                                    // 설명
      parseFloat(engagementRate),                                   // 참여율
      video.videoUrl                                                // 영상URL
    ];
  });
  
  // 데이터 일괄 쓰기 (setValues로 한 번에 쓰면 속도가 빠르다)
  if (dataRows.length > 0) {
    sheet.getRange(2, 1, dataRows.length, headers.length).setValues(dataRows);
  }
  
  // ===== 썸네일 이미지 수식 삽입 =====
  videos.forEach((video, index) => {
    const row = index + 2;
    const thumbnailFormula = '=IMAGE("' + video.thumbnailUrl + '", 1)';
    sheet.getRange(row, 2).setFormula(thumbnailFormula);
  });
  
  // ===== 열 너비 설정 =====
  const columnWidths = {
    1: 40,    // 번호
    2: 160,   // 썸네일
    3: 300,   // 제목
    4: 120,   // 채널명
    5: 90,    // 조회수
    6: 80,    // 좋아요
    7: 80,    // 댓글수
    8: 100,   // 게시일
    9: 80,    // 영상길이
    10: 200,  // 태그
    11: 250,  // 설명
    12: 80,   // 참여율
    13: 280   // 영상URL
  };
  
  Object.keys(columnWidths).forEach(col => {
    sheet.setColumnWidth(parseInt(col), columnWidths[col]);
  });
  
  // ===== 데이터 행 서식 =====
  if (dataRows.length > 0) {
    const dataRange = sheet.getRange(2, 1, dataRows.length, headers.length);
    
    // 행 높이 (썸네일이 보이도록)
    for (let i = 2; i <= dataRows.length + 1; i++) {
      sheet.setRowHeight(i, 90);
    }
    
    // 숫자 포맷 (조회수, 좋아요, 댓글수에 천 단위 쉼표)
    sheet.getRange(2, 5, dataRows.length, 1).setNumberFormat('#,##0');    // 조회수
    sheet.getRange(2, 6, dataRows.length, 1).setNumberFormat('#,##0');    // 좋아요
    sheet.getRange(2, 7, dataRows.length, 1).setNumberFormat('#,##0');    // 댓글수
    sheet.getRange(2, 12, dataRows.length, 1).setNumberFormat('0.00');    // 참여율
    
    // 수직 정렬 가운데
    dataRange.setVerticalAlignment('middle');
    
    // 번호 열 가운데 정렬
    sheet.getRange(2, 1, dataRows.length, 1).setHorizontalAlignment('center');
    
    // 교대 행 색상
    for (let i = 0; i < dataRows.length; i++) {
      if (i % 2 === 1) {
        sheet.getRange(i + 2, 1, 1, headers.length).setBackground('#f8f9fa');
      }
    }
  }
  
  // 첫 번째 행 고정
  sheet.setFrozenRows(1);
  
  // 새로 만든 시트를 활성화
  ss.setActiveSheet(sheet);
  
  return sheetName;
}
```

이 함수의 핵심은 `setValues()`를 사용한 **일괄 쓰기**다. 셀 하나하나에 값을 쓰면(예: `getRange(r, c).setValue(val)`) 각 호출마다 서버와 통신하기 때문에 매우 느리다. 2차원 배열을 만들어 `setValues()`로 한 번에 쓰면 데이터 양에 관계없이 빠르게 처리된다.

---

## [바로 실습] 다양한 데이터 추가하기

앞서 구현한 검색 결과에 더 풍부한 데이터를 추가한다. `videos.list` API의 `part` 파라미터를 확장하면 다양한 정보를 가져올 수 있다.

### 확장된 videos.list 호출

`03_검색엔진.gs`의 `getVideoDetails` 함수에서 `part` 파라미터를 확장한다.

```javascript
/**
 * 영상 ID 배열로 최대한 많은 상세 정보를 가져온다 (확장 버전)
 * @param {string[]} videoIds - 영상 ID 배열
 * @param {string} apiKey - API 키
 * @returns {Array<Object>} 상세 영상 정보 배열
 */
function getVideoDetailsExtended(videoIds, apiKey) {
  if (!apiKey) apiKey = getApiKey();
  
  // part에 snippet, statistics, contentDetails를 모두 포함
  // topicDetails도 추가하면 카테고리 분류를 얻을 수 있다
  const videosUrl = 'https://www.googleapis.com/youtube/v3/videos'
    + '?part=snippet,statistics,contentDetails,topicDetails'
    + '&id=' + videoIds.join(',')
    + '&key=' + apiKey;
  
  const response = UrlFetchApp.fetch(videosUrl, { muteHttpExceptions: true });
  
  if (response.getResponseCode() !== 200) {
    throw new Error('영상 상세 정보 조회 실패: ' + response.getContentText());
  }
  
  const data = JSON.parse(response.getContentText());
  
  // 채널 구독자 수를 가져오기 위해 채널 ID 수집
  const channelIds = [...new Set(data.items.map(item => item.snippet.channelId))];
  const channelMap = getChannelSubscriberCounts(channelIds, apiKey);
  
  return data.items.map(item => {
    const snippet = item.snippet;
    const stats = item.statistics;
    const contentDetails = item.contentDetails;
    const topicDetails = item.topicDetails;
    
    const viewCount = parseInt(stats.viewCount || '0', 10);
    const likeCount = parseInt(stats.likeCount || '0', 10);
    const commentCount = parseInt(stats.commentCount || '0', 10);
    const subscriberCount = channelMap[snippet.channelId] || 0;
    
    // 게시일로부터 경과일 수 계산
    const publishDate = new Date(snippet.publishedAt);
    const daysSincePublish = Math.max(1, 
      Math.floor((new Date() - publishDate) / (1000 * 60 * 60 * 24)));
    
    // 조회수/구독자 비율
    const viewsPerSubscriber = subscriberCount > 0 
      ? (viewCount / subscriberCount).toFixed(2)
      : 'N/A';
    
    // 참여율: (좋아요 + 댓글) / 조회수 * 100
    const engagementRate = viewCount > 0
      ? ((likeCount + commentCount) / viewCount * 100).toFixed(2)
      : '0.00';
    
    // 일평균 조회수 (조회수 속도)
    const viewsPerDay = Math.round(viewCount / daysSincePublish);
    
    // 카테고리 이름 변환
    const categoryName = getCategoryName(snippet.categoryId);
    
    return {
      videoId: item.id,
      title: snippet.title,
      channelTitle: snippet.channelTitle,
      channelId: snippet.channelId,
      publishedAt: snippet.publishedAt,
      description: snippet.description,
      thumbnailUrl: getThumbnailUrl(snippet.thumbnails),
      categoryId: snippet.categoryId,
      categoryName: categoryName,
      tags: snippet.tags || [],
      defaultLanguage: snippet.defaultLanguage || '',
      defaultAudioLanguage: snippet.defaultAudioLanguage || '',
      
      // 통계
      viewCount: viewCount,
      likeCount: likeCount,
      commentCount: commentCount,
      subscriberCount: subscriberCount,
      
      // 콘텐츠 상세
      duration: contentDetails.duration,
      durationSeconds: parseDuration(contentDetails.duration),
      durationFormatted: formatDuration(contentDetails.duration),
      definition: contentDetails.definition,        // 'hd' 또는 'sd'
      caption: contentDetails.caption === 'true',   // 자막 여부
      
      // 계산된 지표
      viewsPerSubscriber: viewsPerSubscriber,
      engagementRate: parseFloat(engagementRate),
      viewsPerDay: viewsPerDay,
      daysSincePublish: daysSincePublish,
      
      // 토픽
      topicCategories: topicDetails?.topicCategories || [],
      
      videoUrl: 'https://www.youtube.com/watch?v=' + item.id
    };
  });
}

/**
 * 채널 ID 배열로 구독자 수를 가져온다
 * @param {string[]} channelIds - 채널 ID 배열
 * @param {string} apiKey - API 키
 * @returns {Object} {channelId: subscriberCount} 맵
 */
function getChannelSubscriberCounts(channelIds, apiKey) {
  if (!channelIds || channelIds.length === 0) return {};
  
  const url = 'https://www.googleapis.com/youtube/v3/channels'
    + '?part=statistics'
    + '&id=' + channelIds.join(',')
    + '&key=' + apiKey;
  
  const response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  
  if (response.getResponseCode() !== 200) return {};
  
  const data = JSON.parse(response.getContentText());
  const map = {};
  
  data.items.forEach(channel => {
    map[channel.id] = parseInt(channel.statistics.subscriberCount || '0', 10);
  });
  
  return map;
}

/**
 * YouTube 카테고리 ID를 한국어 이름으로 변환한다
 * @param {string} categoryId - 카테고리 ID
 * @returns {string} 카테고리 이름
 */
function getCategoryName(categoryId) {
  const categories = {
    '1': '영화/애니메이션', '2': '자동차', '10': '음악',
    '15': '동물', '17': '스포츠', '18': '단편영화',
    '19': '여행/이벤트', '20': '게임', '21': '블로그',
    '22': '인물/블로그', '23': '코미디', '24': '엔터테인먼트',
    '25': '뉴스/정치', '26': '노하우/스타일', '27': '교육',
    '28': '과학기술', '29': '비영리/사회운동'
  };
  return categories[categoryId] || '기타(' + categoryId + ')';
}
```

### ISO 8601 Duration 파싱 심화

YouTube API가 반환하는 영상 길이는 ISO 8601 형식이다. 다양한 케이스를 정확히 처리해야 한다.

```javascript
/**
 * ISO 8601 Duration의 다양한 케이스를 처리하는 파싱 테스트
 * 실행하여 파싱이 정확한지 확인한다
 */
function testDurationParsing() {
  const testCases = [
    { input: 'PT1H23M45S',  expected: '1:23:45',  seconds: 5025 },
    { input: 'PT5M30S',     expected: '5:30',      seconds: 330 },
    { input: 'PT45S',       expected: '0:45',      seconds: 45 },
    { input: 'PT1H',        expected: '1:00:00',   seconds: 3600 },
    { input: 'PT10M',       expected: '10:00',     seconds: 600 },
    { input: 'PT0S',        expected: '0:00',      seconds: 0 },
    { input: 'PT2H5S',      expected: '2:00:05',   seconds: 7205 },
    { input: 'PT1H1M1S',    expected: '1:01:01',   seconds: 3661 },
  ];
  
  testCases.forEach(tc => {
    const gotSeconds = parseDuration(tc.input);
    const gotFormatted = formatDuration(tc.input);
    const pass = (gotSeconds === tc.seconds && gotFormatted === tc.expected);
    Logger.log((pass ? '✅' : '❌') + ' ' + tc.input 
      + ' → ' + gotFormatted + ' (' + gotSeconds + 's)'
      + (pass ? '' : ' [예상: ' + tc.expected + ' (' + tc.seconds + 's)]'));
  });
}
```

`part` 파라미터에 `topicDetails`를 추가하면 영상의 주제 분류(위키피디아 URL 형태)도 가져올 수 있다. 그리고 `channels.list`를 별도로 호출하여 채널 구독자 수를 가져오면 **조회수/구독자 비율** 같은 고급 지표도 계산할 수 있다. 이 비율이 높을수록 구독자 대비 조회수가 높은, 이른바 "떡상" 영상이다.

---

## [바로 실습] 썸네일 이미지에 하이퍼링크 연결하기

구글 시트에서 썸네일 이미지를 표시하면서 동시에 클릭하면 유튜브 영상으로 이동하도록 만들 수 있다. 이를 위해 `IMAGE()` 함수와 `HYPERLINK()` 함수를 조합한다.

### 핵심 원리

구글 시트에서 이미지와 하이퍼링크를 하나의 셀에 결합하는 직접적인 방법은 없다. 따라서 두 가지 전략을 사용한다.

**전략 1: 썸네일 셀과 링크 셀 분리** (간단하지만 실용적)

```javascript
/**
 * 썸네일 이미지와 하이퍼링크를 별도 열에 출력한다
 * @param {Object} sheet - 시트 객체
 * @param {Array<Object>} videos - 영상 데이터 배열
 */
function addThumbnailsWithLinks(sheet, videos) {
  videos.forEach((video, index) => {
    const row = index + 2; // 헤더가 1행

    // B열: 썸네일 이미지
    const imageFormula = '=IMAGE("' + video.thumbnailUrl + '", 1)';
    sheet.getRange(row, 2).setFormula(imageFormula);

    // C열: 제목을 하이퍼링크로 설정
    const hyperlinkFormula = '=HYPERLINK("' + video.videoUrl + '", "' + 
      video.title.replace(/"/g, '""') + '")';
    sheet.getRange(row, 3).setFormula(hyperlinkFormula);
  });
}
```

**전략 2: 제목 열에 하이퍼링크를 설정하고, 썸네일에는 클릭 유도 표시 추가** (권장)

```javascript
/**
 * 썸네일 열에 이미지를 넣고, 제목 열은 하이퍼링크로 만든다
 * 추가로 영상 URL 열도 하이퍼링크로 출력한다
 * @param {Object} sheet - 시트 객체
 * @param {Array<Object>} videos - 영상 데이터 배열
 * @param {number} thumbCol - 썸네일 열 번호
 * @param {number} titleCol - 제목 열 번호
 * @param {number} urlCol - URL 열 번호
 */
function addThumbnailsAndHyperlinks(sheet, videos, thumbCol, titleCol, urlCol) {
  thumbCol = thumbCol || 2;
  titleCol = titleCol || 3;
  urlCol = urlCol || 13;
  
  // 배치 처리를 위한 수식 배열 준비
  const thumbFormulas = [];
  const titleFormulas = [];
  const urlFormulas = [];
  
  videos.forEach(video => {
    // 썸네일 URL 선택 (medium 사이즈가 셀 내 표시에 최적)
    const thumbUrl = video.thumbnailUrl.replace('maxresdefault', 'mqdefault')
      || video.thumbnailUrl;
    
    thumbFormulas.push(['=IMAGE("' + thumbUrl + '", 1)']);
    
    // 제목에 하이퍼링크 (제목 안의 따옴표 이스케이프)
    const safeTitle = video.title.replace(/"/g, '""');
    titleFormulas.push(['=HYPERLINK("' + video.videoUrl + '","' + safeTitle + '")']);
    
    // URL 열에도 하이퍼링크
    urlFormulas.push(['=HYPERLINK("' + video.videoUrl + '","▶ 보기")']);
  });
  
  // 수식 일괄 삽입
  if (videos.length > 0) {
    sheet.getRange(2, thumbCol, videos.length, 1).setFormulas(thumbFormulas);
    sheet.getRange(2, titleCol, videos.length, 1).setFormulas(titleFormulas);
    sheet.getRange(2, urlCol, videos.length, 1).setFormulas(urlFormulas);
    
    // 제목 열 스타일: 하이퍼링크 파란색
    sheet.getRange(2, titleCol, videos.length, 1)
      .setFontColor('#1a73e8')
      .setFontLine('underline');
    
    // URL 열 스타일
    sheet.getRange(2, urlCol, videos.length, 1)
      .setHorizontalAlignment('center')
      .setFontColor('#1a73e8');
  }
}
```

### 썸네일 해상도 선택 가이드

YouTube는 영상마다 여러 해상도의 썸네일을 제공한다.

```javascript
/**
 * 용도에 맞는 썸네일 URL을 선택한다
 * @param {Object} thumbnails - API가 반환한 thumbnails 객체
 * @param {string} purpose - 'cell'(시트 셀 내), 'preview'(미리보기), 'download'(다운로드)
 * @returns {string} 선택된 썸네일 URL
 */
function selectThumbnail(thumbnails, purpose) {
  /*
   * 해상도별 정보:
   * default   : 120 x 90px   → 매우 작음, 목록에서 빠른 로딩
   * medium    : 320 x 180px  → 시트 셀 내 표시에 최적
   * high      : 480 x 360px  → 사이드바 미리보기에 적합
   * standard  : 640 x 480px  → 고화질 필요 시
   * maxres    : 1280 x 720px → 원본급, 모든 영상에 있지는 않음
   */
  
  switch (purpose) {
    case 'cell':
      // 시트 셀: medium이 가장 적합 (너무 크면 로딩 느림)
      return thumbnails.medium?.url || thumbnails.default?.url;
    
    case 'preview':
      // 미리보기: high 추천
      return thumbnails.high?.url || thumbnails.medium?.url;
    
    case 'download':
      // 최고 해상도
      return thumbnails.maxres?.url 
        || thumbnails.standard?.url 
        || thumbnails.high?.url;
    
    default:
      return thumbnails.medium?.url || thumbnails.default?.url;
  }
}
```

> **성능 팁:** 50개 이상의 영상을 시트에 출력할 때 `maxres` 썸네일을 사용하면 시트 로딩이 느려진다. 셀 내 표시에는 `medium` (320x180) 해상도면 충분하다. `=IMAGE(url, 1)`에서 두 번째 인자 `1`은 이미지를 셀 크기에 맞추라는 의미다. `2`로 바꾸면 원본 비율을 유지하면서 셀에 맞춘다.

---

## 이 장에서 만든 코드 구조 정리

이 장에서 만든 파일과 함수들의 전체 구조를 정리한다.

| 파일명 | 함수 | 역할 |
|-------|------|------|
| `01_메뉴.gs` | `onOpen()` | 커스텀 메뉴 생성 |
| | `showSearchSidebar()` | 검색 사이드바 열기 |
| | `showUserGuide()` | 사용 가이드 대화상자 |
| `02_API키관리.gs` | `saveApiKey()` | API 키 저장 |
| | `getApiKey()` | API 키 조회 |
| | `validateApiKey()` | API 키 유효성 검증 |
| | `getApiKeyStatus()` | 키 상태 확인 (마스킹) |
| | `showApiKeyDialog()` | API 키 설정 대화상자 |
| `03_검색엔진.gs` | `searchYouTubeVideos()` | 2단계 검색 메인 함수 |
| | `getVideoDetails()` | 영상 상세 정보 조회 |
| | `getVideoDetailsExtended()` | 확장 상세 정보 조회 |
| | `getChannelSubscriberCounts()` | 채널 구독자 수 조회 |
| | `parseDuration()` | ISO 8601 → 초 변환 |
| | `formatDuration()` | ISO 8601 → 읽기 쉬운 형태 |
| | `getCategoryName()` | 카테고리 ID → 이름 |
| `04_시트출력.gs` | `exportSearchResults()` | 결과를 새 시트에 출력 |
| | `addThumbnailsAndHyperlinks()` | 썸네일+하이퍼링크 삽입 |
| | `selectThumbnail()` | 용도별 썸네일 선택 |
| `SearchSidebar.html` | — | 검색 사이드바 UI |

다음 장에서는 이 기본 구조 위에 고급 기능을 추가한다: 필터, 배치 처리, 기간별 검색, 떡상 영상 하이라이팅, 자동 서식 지정까지 — 진정한 "슈퍼" 유튜브 시트를 완성할 것이다.
