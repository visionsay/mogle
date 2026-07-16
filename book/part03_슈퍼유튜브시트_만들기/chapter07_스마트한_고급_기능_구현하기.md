# Chapter 07: 스마트한 고급 기능 구현하기

6장에서 만든 기본 검색 시스템 위에 실전에서 필요한 고급 기능들을 추가한다. 필터, 배치 처리, 기간/국가별 검색, 쇼츠 필터링, 떡상 영상 분석, 자동 서식까지 — 모든 코드는 바로 실행할 수 있는 완전한 형태로 제공한다.

---

## [바로 실습] 필터를 통해 쉽게 정렬하기

검색 결과 시트에 자동 필터를 적용하면, 사용자가 열 헤더의 드롭다운으로 데이터를 즉시 정렬하고 필터링할 수 있다. `05_필터정렬.gs` 파일을 새로 만들자.

### 자동 필터 적용

```javascript
/**
 * 지정된 시트에 자동 필터를 적용한다
 * @param {string} sheetName - 시트 이름 (생략 시 현재 활성 시트)
 */
function applyAutoFilter(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = sheetName ? ss.getSheetByName(sheetName) : ss.getActiveSheet();
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert('시트를 찾을 수 없습니다: ' + sheetName);
    return;
  }
  
  // 기존 필터가 있으면 제거
  const existingFilter = sheet.getFilter();
  if (existingFilter) {
    existingFilter.remove();
  }
  
  // 데이터가 있는 전체 범위에 필터 적용
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  
  if (lastRow < 2) {
    SpreadsheetApp.getUi().alert('데이터가 없습니다.');
    return;
  }
  
  const range = sheet.getRange(1, 1, lastRow, lastCol);
  range.createFilter();
}
```

### 커스텀 정렬 함수

자동 필터 외에, 특정 기준으로 프로그래밍 방식 정렬이 필요할 때 사용하는 함수들이다.

```javascript
/**
 * 시트 데이터를 특정 열 기준으로 정렬한다
 * @param {string} sheetName - 시트 이름
 * @param {number} column - 정렬 기준 열 번호 (1부터 시작)
 * @param {boolean} ascending - true: 오름차순, false: 내림차순
 */
function sortSheetByColumn(sheetName, column, ascending) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = sheetName ? ss.getSheetByName(sheetName) : ss.getActiveSheet();
  
  if (!sheet) return;
  
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  
  if (lastRow < 2) return;
  
  // 헤더를 제외한 데이터 범위만 정렬
  const dataRange = sheet.getRange(2, 1, lastRow - 1, lastCol);
  dataRange.sort({ column: column, ascending: ascending });
}

/**
 * 조회수 기준 내림차순 정렬
 */
function sortByViews() {
  sortSheetByColumn(null, 5, false); // 5번째 열 = 조회수
}

/**
 * 참여율 기준 내림차순 정렬
 */
function sortByEngagement() {
  sortSheetByColumn(null, 12, false); // 12번째 열 = 참여율
}

/**
 * 게시일 기준 최신순 정렬
 */
function sortByDate() {
  sortSheetByColumn(null, 8, false); // 8번째 열 = 게시일
}

/**
 * 좋아요 기준 내림차순 정렬
 */
function sortByLikes() {
  sortSheetByColumn(null, 6, false); // 6번째 열 = 좋아요
}

/**
 * 필터 조건을 프로그래밍 방식으로 설정한다
 * 예: 조회수 10,000 이상만 보기
 * @param {string} sheetName - 시트 이름
 * @param {number} column - 필터를 적용할 열 번호
 * @param {number} minValue - 최소값
 */
function applyMinValueFilter(sheetName, column, minValue) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = sheetName ? ss.getSheetByName(sheetName) : ss.getActiveSheet();
  
  if (!sheet) return;
  
  // 필터가 없으면 먼저 생성
  let filter = sheet.getFilter();
  if (!filter) {
    const range = sheet.getRange(1, 1, sheet.getLastRow(), sheet.getLastColumn());
    filter = range.createFilter();
  }
  
  // 조건 설정: 지정된 값 이상만 표시
  const criteria = SpreadsheetApp.newFilterCriteria()
    .whenNumberGreaterThanOrEqualTo(minValue)
    .build();
  
  filter.setColumnFilterCriteria(column, criteria);
}

/**
 * 인기 영상 필터: 조회수 10,000 이상 + 참여율 3% 이상만 표시
 */
function filterPopularVideos() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const sheetName = sheet.getName();
  
  // 필터 생성
  let filter = sheet.getFilter();
  if (!filter) {
    const range = sheet.getRange(1, 1, sheet.getLastRow(), sheet.getLastColumn());
    filter = range.createFilter();
  }
  
  // 조회수 10,000 이상
  const viewCriteria = SpreadsheetApp.newFilterCriteria()
    .whenNumberGreaterThanOrEqualTo(10000)
    .build();
  filter.setColumnFilterCriteria(5, viewCriteria);
  
  // 참여율 3% 이상
  const engagementCriteria = SpreadsheetApp.newFilterCriteria()
    .whenNumberGreaterThanOrEqualTo(3)
    .build();
  filter.setColumnFilterCriteria(12, engagementCriteria);
  
  SpreadsheetApp.getUi().alert('필터 적용 완료: 조회수 10,000 이상 & 참여율 3% 이상');
}
```

> **팁:** 자동 필터가 적용된 상태에서 사용자가 열 헤더의 드롭다운 화살표를 클릭하면, "A→Z 정렬", "Z→A 정렬", 값 필터링 등을 GUI로 조작할 수 있다. 프로그래밍 방식 정렬과 GUI 필터를 함께 사용하면 매우 유연한 데이터 탐색이 가능하다.

---

## [바로 실습] 영상 개수 선택 기능 추가하기(배치처리)

YouTube Data API의 `search.list`는 한 번에 최대 50개 결과만 반환한다. 100개, 200개 이상의 결과가 필요하면 `pageToken`을 사용한 **페이지네이션**이 필요하다. `06_배치처리.gs` 파일을 만들자.

### 배치 검색 함수

```javascript
/**
 * 페이지네이션을 통해 대량의 검색 결과를 가져온다
 * @param {string} query - 검색어
 * @param {number} totalResults - 원하는 총 결과 수
 * @param {Object} options - 검색 옵션
 * @returns {Object} {videos: Array, totalFetched: number}
 */
function batchSearchYouTubeVideos(query, totalResults, options) {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('API 키가 설정되지 않았습니다.');
  }
  
  options = options || {};
  totalResults = totalResults || 50;
  
  const allVideos = [];
  let nextPageToken = null;
  let fetchedCount = 0;
  const perPage = 50; // API 최대값
  
  // 총 필요 페이지 수 계산
  const totalPages = Math.ceil(totalResults / perPage);
  
  for (let page = 0; page < totalPages; page++) {
    const remaining = totalResults - fetchedCount;
    const currentPageSize = Math.min(remaining, perPage);
    
    // 검색 옵션 구성
    const searchOptions = Object.assign({}, options);
    if (nextPageToken) {
      searchOptions.pageToken = nextPageToken;
    }
    
    try {
      const result = searchYouTubeVideos(query, currentPageSize, searchOptions);
      
      if (!result.videos || result.videos.length === 0) {
        break; // 더 이상 결과 없음
      }
      
      allVideos.push(...result.videos);
      fetchedCount += result.videos.length;
      nextPageToken = result.nextPageToken;
      
      // 다음 페이지 토큰이 없으면 종료
      if (!nextPageToken) break;
      
      // API 속도 제한 방지를 위한 짧은 대기
      if (page < totalPages - 1) {
        Utilities.sleep(200);
      }
      
    } catch (error) {
      Logger.log('배치 검색 오류 (페이지 ' + (page + 1) + '): ' + error.message);
      break;
    }
  }
  
  return {
    videos: allVideos,
    totalFetched: allVideos.length,
    requestedTotal: totalResults
  };
}

/**
 * 사이드바에서 호출되는 배치 검색 + 시트 저장 통합 함수
 * 진행 상황을 사이드바로 전달한다
 * @param {string} query - 검색어
 * @param {number} totalResults - 원하는 총 결과 수
 * @param {Object} options - 검색 옵션
 * @returns {Object} {sheetName: string, totalSaved: number}
 */
function batchSearchAndExport(query, totalResults, options) {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error('API 키가 설정되지 않았습니다.');
  }
  
  options = options || {};
  totalResults = totalResults || 50;
  
  const allVideos = [];
  let nextPageToken = null;
  const perPage = 50;
  const totalPages = Math.ceil(totalResults / perPage);
  
  for (let page = 0; page < totalPages; page++) {
    const remaining = totalResults - allVideos.length;
    const currentPageSize = Math.min(remaining, perPage);
    
    const searchOptions = Object.assign({}, options);
    if (nextPageToken) {
      searchOptions.pageToken = nextPageToken;
    }
    
    try {
      const result = searchYouTubeVideos(query, currentPageSize, searchOptions);
      
      if (!result.videos || result.videos.length === 0) break;
      
      allVideos.push(...result.videos);
      nextPageToken = result.nextPageToken;
      
      if (!nextPageToken) break;
      if (page < totalPages - 1) Utilities.sleep(200);
      
    } catch (error) {
      Logger.log('배치 검색 오류: ' + error.message);
      break;
    }
  }
  
  if (allVideos.length === 0) {
    throw new Error('검색 결과가 없습니다.');
  }
  
  // 시트에 저장
  const sheetName = exportSearchResults(allVideos, query);
  
  // 자동 필터 적용
  applyAutoFilter(sheetName);
  
  return {
    sheetName: sheetName,
    totalSaved: allVideos.length
  };
}
```

### 사이드바에 진행 표시 연동

6장에서 만든 `SearchSidebar.html`의 검색 개수 옵션을 확장하고, 진행 상황을 표시하는 기능을 추가한다. 기존 `<select id="maxResults">` 부분을 아래로 교체한다.

```html
<!-- 기존 maxResults select를 이 코드로 교체 -->
<div class="input-group">
  <label>검색 개수</label>
  <select id="maxResults">
    <option value="10">10개</option>
    <option value="25" selected>25개</option>
    <option value="50">50개</option>
    <option value="100">100개 (2페이지)</option>
    <option value="150">150개 (3페이지)</option>
    <option value="200">200개 (4페이지)</option>
  </select>
</div>
```

그리고 `performSearch()` 함수를 수정하여 50개 초과 시 배치 검색을 사용하도록 한다.

```javascript
/**
 * 검색 실행 (배치 처리 지원 버전)
 */
function performSearch() {
  const query = document.getElementById('searchQuery').value.trim();
  if (!query) {
    showStatus('검색어를 입력해주세요.', true);
    return;
  }

  const maxResults = parseInt(document.getElementById('maxResults').value);
  const options = {
    order: document.getElementById('sortOrder').value
  };

  // 기간 필터가 있으면 추가
  if (typeof getDateFilter === 'function') {
    var dateFilter = getDateFilter();
    if (dateFilter.publishedAfter) options.publishedAfter = dateFilter.publishedAfter;
    if (dateFilter.publishedBefore) options.publishedBefore = dateFilter.publishedBefore;
  }

  // 국가/언어 필터가 있으면 추가
  if (document.getElementById('regionCode')) {
    var region = document.getElementById('regionCode').value;
    if (region) options.regionCode = region;
  }
  if (document.getElementById('relevanceLanguage')) {
    var lang = document.getElementById('relevanceLanguage').value;
    if (lang) options.relevanceLanguage = lang;
  }

  // 영상 길이 필터
  if (document.getElementById('videoDuration')) {
    var duration = document.getElementById('videoDuration').value;
    if (duration) options.videoDuration = duration;
  }

  setSearching(true);
  
  if (maxResults <= 50) {
    // 50개 이하: 일반 검색
    showLoading('검색 중...');
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
      .withFailureHandler(handleSearchError)
      .searchYouTubeVideos(query, maxResults, options);
  } else {
    // 50개 초과: 배치 검색 → 바로 시트에 저장
    var totalPages = Math.ceil(maxResults / 50);
    showLoading('배치 검색 중... (총 ' + totalPages + '페이지)');
    setProgress(20);
    
    google.script.run
      .withSuccessHandler(function(result) {
        setSearching(false);
        setProgress(100);
        showStatus(
          '✅ 총 ' + result.totalSaved + '개 영상이 "' + result.sheetName + '" 시트에 저장되었습니다!',
          false
        );
      })
      .withFailureHandler(handleSearchError)
      .batchSearchAndExport(query, maxResults, options);
  }
}

function handleSearchError(error) {
  setSearching(false);
  setProgress(0);
  showStatus('오류: ' + error.message, true);
}
```

> **할당량 참고:** 배치 검색 시 할당량 사용은 다음과 같다. 100개 검색 = `search.list` 2회(200) + `videos.list` 2회(2) = **총 202 할당량**. YouTube Data API의 일일 할당량은 기본 10,000이므로 약 49회 배치 검색이 가능하다.

---

## [바로 실습] 기간별 검색 기능 추가하기

특정 기간에 업로드된 영상만 검색하는 기능을 추가한다. YouTube API의 `publishedAfter`와 `publishedBefore` 파라미터를 활용한다. `07_기간검색.gs` 파일을 만들자.

### 기간 프리셋 함수

```javascript
/**
 * 기간 프리셋에 따른 publishedAfter 날짜를 계산한다
 * @param {string} preset - 프리셋 코드
 * @returns {Object} {publishedAfter: string, publishedBefore: string, label: string}
 */
function getDateRange(preset) {
  const now = new Date();
  let afterDate = null;
  let label = '';
  
  switch (preset) {
    case 'last24h':
      afterDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
      label = '최근 24시간';
      break;
    
    case 'lastWeek':
      afterDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      label = '최근 1주';
      break;
    
    case 'lastMonth':
      afterDate = new Date(now);
      afterDate.setMonth(afterDate.getMonth() - 1);
      label = '최근 1달';
      break;
    
    case 'last3Months':
      afterDate = new Date(now);
      afterDate.setMonth(afterDate.getMonth() - 3);
      label = '최근 3달';
      break;
    
    case 'lastYear':
      afterDate = new Date(now);
      afterDate.setFullYear(afterDate.getFullYear() - 1);
      label = '최근 1년';
      break;
    
    case 'all':
    default:
      return { publishedAfter: null, publishedBefore: null, label: '전체 기간' };
  }
  
  // ISO 8601 형식 (RFC 3339)으로 변환 — YouTube API 요구사항
  return {
    publishedAfter: afterDate.toISOString(),
    publishedBefore: now.toISOString(),
    label: label
  };
}

/**
 * 사용자 지정 날짜 범위를 API 형식으로 변환한다
 * @param {string} startDate - 시작 날짜 (YYYY-MM-DD)
 * @param {string} endDate - 종료 날짜 (YYYY-MM-DD)
 * @returns {Object} {publishedAfter: string, publishedBefore: string}
 */
function getCustomDateRange(startDate, endDate) {
  if (!startDate) {
    throw new Error('시작 날짜를 입력해주세요.');
  }
  
  const after = new Date(startDate + 'T00:00:00Z');
  const before = endDate 
    ? new Date(endDate + 'T23:59:59Z') 
    : new Date();
  
  if (isNaN(after.getTime())) {
    throw new Error('시작 날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)');
  }
  
  if (after > before) {
    throw new Error('시작 날짜가 종료 날짜보다 뒤입니다.');
  }
  
  return {
    publishedAfter: after.toISOString(),
    publishedBefore: before.toISOString()
  };
}
```

### 사이드바 기간 필터 UI

`SearchSidebar.html`의 검색 카드(`<div class="card">`) 안에 있는 `filter-grid` 부분을 아래 확장 버전으로 교체한다.

```html
<!-- 확장된 필터 영역 -->
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
      <option value="100">100개</option>
      <option value="200">200개</option>
    </select>
  </div>
</div>

<!-- 기간 필터 -->
<div class="input-group" style="margin-top: 8px;">
  <label>업로드 기간</label>
  <select id="datePreset" onchange="toggleCustomDate()">
    <option value="all">전체 기간</option>
    <option value="last24h">최근 24시간</option>
    <option value="lastWeek">최근 1주</option>
    <option value="lastMonth">최근 1달</option>
    <option value="last3Months">최근 3달</option>
    <option value="lastYear">최근 1년</option>
    <option value="custom">사용자 지정</option>
  </select>
</div>

<!-- 사용자 지정 날짜 입력 (기본 숨김) -->
<div id="customDateArea" style="display: none;">
  <div class="filter-grid" style="margin-top: 6px;">
    <div class="input-group">
      <label>시작일</label>
      <input type="date" id="customStartDate">
    </div>
    <div class="input-group">
      <label>종료일</label>
      <input type="date" id="customEndDate">
    </div>
  </div>
</div>
```

대응하는 JavaScript 함수를 `<script>` 태그 안에 추가한다.

```javascript
/**
 * 사용자 지정 날짜 입력 영역 토글
 */
function toggleCustomDate() {
  var preset = document.getElementById('datePreset').value;
  document.getElementById('customDateArea').style.display = 
    (preset === 'custom') ? 'block' : 'none';
}

/**
 * 현재 선택된 기간 필터 값을 반환한다
 * @returns {Object} {publishedAfter, publishedBefore}
 */
function getDateFilter() {
  var preset = document.getElementById('datePreset').value;
  
  if (preset === 'all') {
    return {};
  }
  
  if (preset === 'custom') {
    var startDate = document.getElementById('customStartDate').value;
    var endDate = document.getElementById('customEndDate').value;
    
    if (!startDate) return {};
    
    return {
      publishedAfter: new Date(startDate + 'T00:00:00Z').toISOString(),
      publishedBefore: endDate 
        ? new Date(endDate + 'T23:59:59Z').toISOString()
        : new Date().toISOString()
    };
  }
  
  // 프리셋 계산 (클라이언트 측)
  var now = new Date();
  var afterDate;
  
  switch (preset) {
    case 'last24h':
      afterDate = new Date(now.getTime() - 24 * 60 * 60 * 1000); break;
    case 'lastWeek':
      afterDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); break;
    case 'lastMonth':
      afterDate = new Date(now); afterDate.setMonth(afterDate.getMonth() - 1); break;
    case 'last3Months':
      afterDate = new Date(now); afterDate.setMonth(afterDate.getMonth() - 3); break;
    case 'lastYear':
      afterDate = new Date(now); afterDate.setFullYear(afterDate.getFullYear() - 1); break;
    default:
      return {};
  }
  
  return {
    publishedAfter: afterDate.toISOString(),
    publishedBefore: now.toISOString()
  };
}
```

---

## [바로 실습] 언어, 국가별 검색 기능 추가하기

YouTube API의 `relevanceLanguage`와 `regionCode` 파라미터를 활용하면 특정 언어와 국가의 콘텐츠를 집중적으로 검색할 수 있다.

### 국가/언어 코드 참조 데이터

`08_국가언어.gs` 파일을 만들자.

```javascript
/**
 * 주요 국가 코드와 이름 목록을 반환한다
 * @returns {Array<Object>} [{code, name}] 배열
 */
function getCountryList() {
  return [
    { code: '',   name: '전체 (기본)' },
    { code: 'KR', name: '🇰🇷 한국' },
    { code: 'US', name: '🇺🇸 미국' },
    { code: 'JP', name: '🇯🇵 일본' },
    { code: 'GB', name: '🇬🇧 영국' },
    { code: 'DE', name: '🇩🇪 독일' },
    { code: 'FR', name: '🇫🇷 프랑스' },
    { code: 'CA', name: '🇨🇦 캐나다' },
    { code: 'AU', name: '🇦🇺 호주' },
    { code: 'IN', name: '🇮🇳 인도' },
    { code: 'BR', name: '🇧🇷 브라질' },
    { code: 'TW', name: '🇹🇼 대만' },
    { code: 'TH', name: '🇹🇭 태국' },
    { code: 'VN', name: '🇻🇳 베트남' },
    { code: 'ID', name: '🇮🇩 인도네시아' },
    { code: 'MX', name: '🇲🇽 멕시코' },
    { code: 'ES', name: '🇪🇸 스페인' },
    { code: 'IT', name: '🇮🇹 이탈리아' },
    { code: 'RU', name: '🇷🇺 러시아' },
    { code: 'PH', name: '🇵🇭 필리핀' }
  ];
}

/**
 * 주요 언어 코드와 이름 목록을 반환한다
 * @returns {Array<Object>} [{code, name}] 배열
 */
function getLanguageList() {
  return [
    { code: '',   name: '전체 (기본)' },
    { code: 'ko', name: '한국어' },
    { code: 'en', name: '영어' },
    { code: 'ja', name: '일본어' },
    { code: 'zh', name: '중국어' },
    { code: 'es', name: '스페인어' },
    { code: 'fr', name: '프랑스어' },
    { code: 'de', name: '독일어' },
    { code: 'pt', name: '포르투갈어' },
    { code: 'ru', name: '러시아어' },
    { code: 'hi', name: '힌디어' },
    { code: 'ar', name: '아랍어' },
    { code: 'th', name: '태국어' },
    { code: 'vi', name: '베트남어' },
    { code: 'id', name: '인도네시아어' }
  ];
}
```

### 사이드바 국가/언어 드롭다운

`SearchSidebar.html`의 기간 필터 아래에 다음 코드를 추가한다.

```html
<!-- 국가/언어 필터 -->
<div class="filter-grid" style="margin-top: 8px;">
  <div class="input-group">
    <label>국가</label>
    <select id="regionCode">
      <!-- 동적으로 채워짐 -->
    </select>
  </div>
  <div class="input-group">
    <label>언어</label>
    <select id="relevanceLanguage">
      <!-- 동적으로 채워짐 -->
    </select>
  </div>
</div>
```

페이지 로드 시 드롭다운을 채우는 초기화 코드를 `<script>` 태그 안에 추가한다.

```javascript
/**
 * 페이지 로드 시 국가/언어 드롭다운을 채운다
 */
(function initRegionLanguage() {
  // 국가 목록 로드
  google.script.run
    .withSuccessHandler(function(countries) {
      var select = document.getElementById('regionCode');
      countries.forEach(function(c) {
        var option = document.createElement('option');
        option.value = c.code;
        option.textContent = c.name;
        if (c.code === 'KR') option.selected = true;
        select.appendChild(option);
      });
    })
    .getCountryList();
  
  // 언어 목록 로드
  google.script.run
    .withSuccessHandler(function(languages) {
      var select = document.getElementById('relevanceLanguage');
      languages.forEach(function(l) {
        var option = document.createElement('option');
        option.value = l.code;
        option.textContent = l.name;
        if (l.code === 'ko') option.selected = true;
        select.appendChild(option);
      });
    })
    .getLanguageList();
})();
```

> **참고:** `regionCode`는 해당 국가에서 인기 있는 영상에 가중치를 둔다. `relevanceLanguage`는 해당 언어의 영상을 우선적으로 보여주지만, 다른 언어 영상이 완전히 제외되지는 않는다. 정확한 언어 필터링이 필요하면 검색 결과를 가져온 후 `defaultAudioLanguage` 값으로 후처리 필터링을 해야 한다.

---

## [바로 실습] 쇼츠와 일반 영상 선택 기능 추가하기

YouTube 쇼츠(Shorts)와 일반 영상을 구분하여 검색하는 기능을 구현한다. API의 `videoDuration` 파라미터와 실제 영상 길이를 조합하여 정확한 필터링을 수행한다.

### 영상 유형 필터링

`09_쇼츠필터.gs` 파일을 만들자.

```javascript
/**
 * 영상 유형에 따른 검색 옵션을 반환한다
 * 
 * YouTube API videoDuration 값:
 * - 'any': 모든 길이 (기본)
 * - 'short': 4분 미만
 * - 'medium': 4분 이상 20분 미만
 * - 'long': 20분 이상
 * 
 * 쇼츠는 60초 이하이므로, 'short'로 검색 후 60초 이하만 필터링해야 정확하다.
 * 
 * @param {string} videoType - 'all', 'shorts', 'regular', 'long'
 * @returns {Object} {videoDuration: string, postFilter: Function}
 */
function getVideoTypeFilter(videoType) {
  switch (videoType) {
    case 'shorts':
      return {
        videoDuration: 'short',
        // 후처리 필터: 60초 이하만 쇼츠
        postFilter: function(videos) {
          return videos.filter(v => v.durationSeconds <= 60);
        },
        label: '쇼츠 (60초 이하)'
      };
    
    case 'regular':
      return {
        videoDuration: 'medium',
        postFilter: null, // 후처리 불필요
        label: '일반 영상 (4~20분)'
      };
    
    case 'long':
      return {
        videoDuration: 'long',
        postFilter: null,
        label: '긴 영상 (20분 이상)'
      };
    
    case 'noShorts':
      return {
        videoDuration: 'any',
        // 후처리 필터: 60초 초과만 (쇼츠 제외)
        postFilter: function(videos) {
          return videos.filter(v => v.durationSeconds > 60);
        },
        label: '쇼츠 제외'
      };
    
    default:
      return {
        videoDuration: 'any',
        postFilter: null,
        label: '전체'
      };
  }
}

/**
 * 쇼츠/일반 영상 필터링이 포함된 검색 함수
 * @param {string} query - 검색어
 * @param {number} maxResults - 결과 수
 * @param {Object} options - 검색 옵션 (videoType 포함)
 * @returns {Object} 검색 결과
 */
function searchWithVideoTypeFilter(query, maxResults, options) {
  options = options || {};
  const videoType = options.videoType || 'all';
  const typeFilter = getVideoTypeFilter(videoType);
  
  // API 검색 옵션에 videoDuration 추가
  const searchOptions = Object.assign({}, options, {
    videoDuration: typeFilter.videoDuration
  });
  delete searchOptions.videoType; // API에 보내지 않는 커스텀 파라미터 제거
  
  // 후처리 필터가 있는 경우, 필터링 후 결과가 줄어들 것을 감안하여 더 많이 요청
  let fetchCount = maxResults;
  if (typeFilter.postFilter) {
    fetchCount = Math.min(maxResults * 2, 50); // 최대 50개까지 (API 제한)
  }
  
  const result = searchYouTubeVideos(query, fetchCount, searchOptions);
  
  // 후처리 필터 적용
  if (typeFilter.postFilter && result.videos) {
    result.videos = typeFilter.postFilter(result.videos);
    // 요청한 수만큼 자르기
    result.videos = result.videos.slice(0, maxResults);
  }
  
  return result;
}
```

### 사이드바 영상 유형 드롭다운

`SearchSidebar.html`에 영상 유형 선택 드롭다운을 추가한다. 국가/언어 필터 아래에 넣는다.

```html
<!-- 영상 유형 필터 -->
<div class="input-group" style="margin-top: 8px;">
  <label>영상 유형</label>
  <select id="videoDuration">
    <option value="">전체</option>
    <option value="short">쇼츠 (60초 이하)</option>
    <option value="medium">일반 영상 (4~20분)</option>
    <option value="long">긴 영상 (20분 이상)</option>
  </select>
</div>
```

> **쇼츠 판별의 한계:** YouTube API에는 "이 영상이 쇼츠인지"를 직접 알려주는 필드가 없다(2026년 6월 기준). `videoDuration=short`로 검색하면 4분 미만 영상이 모두 포함되므로, 실제 쇼츠만 필터링하려면 영상 길이가 60초 이하인지 후처리로 확인해야 한다. 또한 세로형 영상인지(종횡비)도 API로는 직접 확인할 수 없어, 길이 기반 필터링이 현실적인 최선의 방법이다.

---

## [바로 실습] 떡상 영상 하이라이팅하기

검색 결과에서 비정상적으로 높은 성과를 보이는 "떡상" 영상을 자동으로 식별하고 시각적으로 하이라이팅한다. `10_떡상분석.gs` 파일을 만들자.

### 바이럴 지수 계산

```javascript
/**
 * 바이럴 지수(Virality Score)를 계산한다
 * 
 * 계산 요소:
 * 1. 조회수/구독자 비율 (Views/Subscriber Ratio) — 가중치 40%
 *    구독자 대비 조회수가 높을수록 알고리즘 추천을 많이 받았다는 의미
 * 
 * 2. 조회수 속도 (Views Velocity) — 가중치 35%
 *    게시 후 일일 평균 조회수. 최근 영상일수록 유리
 * 
 * 3. 참여율 (Engagement Rate) — 가중치 25%
 *    (좋아요 + 댓글수) / 조회수. 시청자가 적극적으로 반응하는 정도
 * 
 * @param {Object} video - 영상 데이터 객체
 * @returns {Object} {score, tier, details}
 */
function calculateViralityScore(video) {
  const viewCount = video.viewCount || 0;
  const likeCount = video.likeCount || 0;
  const commentCount = video.commentCount || 0;
  const subscriberCount = video.subscriberCount || 0;
  
  // 게시 후 경과일 수 (최소 1일)
  const publishDate = new Date(video.publishedAt);
  const daysSincePublish = Math.max(1,
    Math.floor((new Date() - publishDate) / (1000 * 60 * 60 * 24)));
  
  // 1. 조회수/구독자 비율 (0~100 정규화)
  let vsRatio = 0;
  if (subscriberCount > 0) {
    vsRatio = viewCount / subscriberCount;
  }
  // 비율 3 이상이면 만점 (구독자의 3배 이상 조회)
  const vsScore = Math.min(vsRatio / 3 * 100, 100);
  
  // 2. 조회수 속도 (0~100 정규화)
  const viewsPerDay = viewCount / daysSincePublish;
  // 일일 10,000뷰 이상이면 만점
  const velocityScore = Math.min(viewsPerDay / 10000 * 100, 100);
  
  // 3. 참여율 (0~100 정규화)
  let engagementRate = 0;
  if (viewCount > 0) {
    engagementRate = (likeCount + commentCount) / viewCount * 100;
  }
  // 참여율 10% 이상이면 만점
  const engagementScore = Math.min(engagementRate / 10 * 100, 100);
  
  // 가중 합산
  const totalScore = (vsScore * 0.40) + (velocityScore * 0.35) + (engagementScore * 0.25);
  
  // 등급 판정
  let tier;
  if (totalScore >= 70) {
    tier = 'viral';       // 떡상
  } else if (totalScore >= 40) {
    tier = 'growing';     // 성장 중
  } else {
    tier = 'normal';      // 보통
  }
  
  return {
    score: Math.round(totalScore * 10) / 10,
    tier: tier,
    details: {
      vsRatio: Math.round(vsRatio * 100) / 100,
      vsScore: Math.round(vsScore),
      viewsPerDay: Math.round(viewsPerDay),
      velocityScore: Math.round(velocityScore),
      engagementRate: Math.round(engagementRate * 100) / 100,
      engagementScore: Math.round(engagementScore),
      daysSincePublish: daysSincePublish
    }
  };
}
```

### 조건부 서식 적용 함수

```javascript
/**
 * 현재 활성 시트의 떡상 영상을 하이라이팅한다
 * 메뉴에서 직접 호출할 수 있다
 */
function highlightViralVideos() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const sheetName = sheet.getName();
  
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  
  if (lastRow < 2) {
    SpreadsheetApp.getUi().alert('데이터가 없습니다.');
    return;
  }
  
  // 헤더 확인 — 참여율 열과 조회수 열 위치 찾기
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  
  const viewColIndex = headers.indexOf('조회수');
  const likeColIndex = headers.indexOf('좋아요');
  const commentColIndex = headers.indexOf('댓글수');
  const engagementColIndex = headers.indexOf('참여율(%)');
  const dateColIndex = headers.indexOf('게시일');
  
  if (viewColIndex === -1) {
    SpreadsheetApp.getUi().alert('조회수 열을 찾을 수 없습니다. 검색 결과 시트에서 실행해주세요.');
    return;
  }
  
  // "바이럴 지수" 열 추가 (이미 있으면 기존 열 사용)
  let viralColIndex = headers.indexOf('바이럴 지수');
  let viralCol;
  
  if (viralColIndex === -1) {
    // 새 열 추가
    viralCol = lastCol + 1;
    sheet.getRange(1, viralCol).setValue('바이럴 지수');
    sheet.getRange(1, viralCol)
      .setBackground('#1a73e8')
      .setFontColor('#ffffff')
      .setFontWeight('bold')
      .setHorizontalAlignment('center');
  } else {
    viralCol = viralColIndex + 1; // 0-based → 1-based
  }
  
  // "등급" 열 추가
  let tierColIndex = headers.indexOf('등급');
  let tierCol;
  
  if (tierColIndex === -1) {
    tierCol = viralCol + 1;
    sheet.getRange(1, tierCol).setValue('등급');
    sheet.getRange(1, tierCol)
      .setBackground('#1a73e8')
      .setFontColor('#ffffff')
      .setFontWeight('bold')
      .setHorizontalAlignment('center');
  } else {
    tierCol = tierColIndex + 1;
  }
  
  // 데이터 읽기
  const dataRange = sheet.getRange(2, 1, lastRow - 1, lastCol);
  const data = dataRange.getValues();
  
  // 바이럴 지수 계산 및 셀 색칠
  const viralScores = [];
  const tierLabels = [];
  
  data.forEach((row, i) => {
    const rowNum = i + 2;
    
    const viewCount = parseInt(row[viewColIndex] || 0);
    const likeCount = likeColIndex !== -1 ? parseInt(row[likeColIndex] || 0) : 0;
    const commentCount = commentColIndex !== -1 ? parseInt(row[commentColIndex] || 0) : 0;
    
    // 간단한 바이럴 지수 계산 (구독자 정보 없이)
    // 참여율 기반 + 조회수 크기 기반
    const engagementRate = viewCount > 0 
      ? (likeCount + commentCount) / viewCount * 100 
      : 0;
    
    // 조회수 점수 (10만 뷰 이상 만점)
    const viewScore = Math.min(viewCount / 100000 * 100, 100);
    
    // 참여율 점수 (10% 이상 만점)
    const engScore = Math.min(engagementRate / 10 * 100, 100);
    
    // 일평균 조회수 점수
    let velocityScore = 0;
    if (dateColIndex !== -1 && row[dateColIndex]) {
      const publishDate = new Date(row[dateColIndex]);
      const days = Math.max(1, Math.floor((new Date() - publishDate) / (1000 * 60 * 60 * 24)));
      const vpd = viewCount / days;
      velocityScore = Math.min(vpd / 5000 * 100, 100);
    }
    
    const score = Math.round((viewScore * 0.30 + velocityScore * 0.40 + engScore * 0.30) * 10) / 10;
    
    let tier, bgColor;
    if (score >= 70) {
      tier = '🔥 떡상';
      bgColor = '#e6f4ea'; // 연한 초록
    } else if (score >= 40) {
      tier = '📈 성장중';
      bgColor = '#fef7e0'; // 연한 노랑
    } else {
      tier = '⬜ 보통';
      bgColor = null;
    }
    
    viralScores.push([score]);
    tierLabels.push([tier]);
    
    // 행 전체에 배경색 적용
    if (bgColor) {
      sheet.getRange(rowNum, 1, 1, Math.max(lastCol, tierCol)).setBackground(bgColor);
    }
  });
  
  // 바이럴 지수와 등급 일괄 쓰기
  if (viralScores.length > 0) {
    sheet.getRange(2, viralCol, viralScores.length, 1).setValues(viralScores);
    sheet.getRange(2, tierCol, tierLabels.length, 1).setValues(tierLabels);
    
    // 바이럴 지수 열 서식
    sheet.getRange(2, viralCol, viralScores.length, 1)
      .setNumberFormat('0.0')
      .setHorizontalAlignment('center');
    
    // 등급 열 서식
    sheet.getRange(2, tierCol, tierLabels.length, 1)
      .setHorizontalAlignment('center')
      .setFontWeight('bold');
  }
  
  // ===== 조건부 서식 규칙 추가 (바이럴 지수 열에 그라데이션) =====
  const rules = sheet.getConditionalFormatRules();
  
  // 기존 바이럴 지수 관련 규칙 제거
  const filteredRules = rules.filter(rule => {
    const ranges = rule.getRanges();
    return !ranges.some(r => r.getColumn() === viralCol);
  });
  
  // 색상 그라데이션 규칙: 빨강(낮음) → 노랑(중간) → 초록(높음)
  const gradientRule = SpreadsheetApp.newConditionalFormatRule()
    .setGradientMinpointWithValue('#ea4335', SpreadsheetApp.InterpolationType.NUMBER, '0')
    .setGradientMidpointWithValue('#fbbc04', SpreadsheetApp.InterpolationType.NUMBER, '50')
    .setGradientMaxpointWithValue('#34a853', SpreadsheetApp.InterpolationType.NUMBER, '100')
    .setRanges([sheet.getRange(2, viralCol, lastRow - 1, 1)])
    .build();
  
  filteredRules.push(gradientRule);
  sheet.setConditionalFormatRules(filteredRules);
  
  // 열 너비 조정
  sheet.setColumnWidth(viralCol, 90);
  sheet.setColumnWidth(tierCol, 90);
  
  SpreadsheetApp.getUi().alert(
    '떡상 분석 완료!\n\n'
    + '🔥 떡상 (70점 이상): ' + tierLabels.filter(t => t[0].includes('떡상')).length + '개\n'
    + '📈 성장중 (40~69점): ' + tierLabels.filter(t => t[0].includes('성장')).length + '개\n'
    + '⬜ 보통 (40점 미만): ' + tierLabels.filter(t => t[0].includes('보통')).length + '개'
  );
}
```

> **바이럴 지수 해석:** 점수 70 이상은 알고리즘에 의해 비정상적으로 많은 노출을 받고 있는 영상이다. 이런 영상의 제목, 썸네일, 주제를 분석하면 현재 어떤 콘텐츠가 유튜브 알고리즘의 선택을 받는지 파악할 수 있다.

---

## [바로 실습] 하이퍼링크 추가한 목차 자동 생성하기

검색을 여러 번 하면 시트가 많아진다. 모든 검색 결과 시트를 한눈에 관리할 수 있는 "목차" 시트를 자동으로 생성하고 업데이트하는 기능을 만든다. `11_목차.gs` 파일을 만들자.

```javascript
/**
 * 목차 시트를 생성하거나 업데이트한다
 * 모든 검색 결과 시트에 대한 하이퍼링크 목록을 만든다
 */
function updateTableOfContents() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const tocSheetName = '📑 목차';
  
  // 목차 시트 가져오기 (없으면 생성)
  let tocSheet = ss.getSheetByName(tocSheetName);
  if (!tocSheet) {
    tocSheet = ss.insertSheet(tocSheetName, 0); // 맨 앞에 삽입
  } else {
    tocSheet.clear(); // 기존 내용 초기화
  }
  
  // ===== 헤더 영역 =====
  tocSheet.getRange('A1').setValue('📑 슈퍼유튜브시트 - 검색 목차');
  tocSheet.getRange('A1')
    .setFontSize(16)
    .setFontWeight('bold')
    .setFontColor('#1a73e8');
  
  tocSheet.getRange('A2').setValue(
    '마지막 업데이트: ' + Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd HH:mm:ss')
  );
  tocSheet.getRange('A2')
    .setFontSize(10)
    .setFontColor('#5f6368');
  
  // 헤더 행
  const headers = ['번호', '시트 이름', '바로가기', '데이터 수', '생성일(추정)'];
  tocSheet.getRange(4, 1, 1, headers.length).setValues([headers]);
  tocSheet.getRange(4, 1, 1, headers.length)
    .setBackground('#1a73e8')
    .setFontColor('#ffffff')
    .setFontWeight('bold')
    .setHorizontalAlignment('center');
  
  // ===== 시트 목록 수집 =====
  const allSheets = ss.getSheets();
  const ssId = ss.getId();
  const tocEntries = [];
  let num = 1;
  
  allSheets.forEach(sheet => {
    const name = sheet.getName();
    
    // 목차 시트 자체와 기본 시트는 제외
    if (name === tocSheetName || name === 'Sheet1' || name === '시트1') {
      return;
    }
    
    const lastRow = sheet.getLastRow();
    const dataCount = lastRow > 1 ? lastRow - 1 : 0; // 헤더 제외
    const sheetId = sheet.getSheetId();
    
    // 시트 이름에서 날짜 추출 시도 (MMdd_HHmm 형식)
    const dateMatch = name.match(/(\d{4})_(\d{4})$/);
    let createdDate = '';
    if (dateMatch) {
      const month = dateMatch[1].substring(0, 2);
      const day = dateMatch[1].substring(2, 4);
      const hour = dateMatch[2].substring(0, 2);
      const minute = dateMatch[2].substring(2, 4);
      createdDate = month + '/' + day + ' ' + hour + ':' + minute;
    }
    
    // HYPERLINK 수식: 같은 스프레드시트 내 다른 시트로 이동
    const linkFormula = '=HYPERLINK("#gid=' + sheetId + '", "▶ 이동")';
    
    tocEntries.push([
      num,
      name,
      linkFormula,
      dataCount + '개',
      createdDate
    ]);
    
    num++;
  });
  
  // ===== 데이터 쓰기 =====
  if (tocEntries.length > 0) {
    // 수식이 포함된 열(3번째)은 별도 처리
    const dataWithoutFormulas = tocEntries.map(row => [row[0], row[1], '', row[3], row[4]]);
    const formulas = tocEntries.map(row => [row[2]]);
    
    tocSheet.getRange(5, 1, tocEntries.length, headers.length).setValues(dataWithoutFormulas);
    tocSheet.getRange(5, 3, formulas.length, 1).setFormulas(formulas);
    
    // 바로가기 열 스타일
    tocSheet.getRange(5, 3, formulas.length, 1)
      .setFontColor('#1a73e8')
      .setHorizontalAlignment('center');
    
    // 번호 열 가운데 정렬
    tocSheet.getRange(5, 1, tocEntries.length, 1).setHorizontalAlignment('center');
    
    // 데이터 수 열 가운데 정렬
    tocSheet.getRange(5, 4, tocEntries.length, 1).setHorizontalAlignment('center');
    
    // 교대 행 색상
    for (let i = 0; i < tocEntries.length; i++) {
      if (i % 2 === 1) {
        tocSheet.getRange(5 + i, 1, 1, headers.length).setBackground('#f8f9fa');
      }
    }
  } else {
    tocSheet.getRange(5, 1).setValue('검색 결과 시트가 없습니다.');
    tocSheet.getRange(5, 1).setFontColor('#5f6368');
  }
  
  // ===== 열 너비 설정 =====
  tocSheet.setColumnWidth(1, 50);   // 번호
  tocSheet.setColumnWidth(2, 250);  // 시트 이름
  tocSheet.setColumnWidth(3, 80);   // 바로가기
  tocSheet.setColumnWidth(4, 80);   // 데이터 수
  tocSheet.setColumnWidth(5, 120);  // 생성일
  
  // 행 고정
  tocSheet.setFrozenRows(4);
  
  // 목차 시트 활성화
  ss.setActiveSheet(tocSheet);
  
  SpreadsheetApp.getUi().alert('목차가 업데이트되었습니다!\n총 ' + tocEntries.length + '개 시트');
}
```

> **자동 업데이트 연동:** 6장에서 만든 `exportSearchResults()` 함수의 마지막 부분에 `updateTableOfContents()` 호출을 추가하면, 새 검색 결과가 저장될 때마다 목차가 자동으로 업데이트된다. 다만 실행 시간이 추가되므로, 빠른 검색이 필요할 때는 메뉴에서 수동으로 목차를 업데이트하는 것이 낫다.

---

## 한눈에 보이는 시트 만들기

데이터 시트의 가독성은 서식에 달려 있다. 다음 원칙을 따르면 정보를 빠르게 파악할 수 있는 시트를 만들 수 있다.

### 시트 디자인 원칙

**1. 시각적 계층 구조**

- 헤더 행은 진한 배경색과 흰색 글자로 데이터와 명확히 구분한다
- 데이터 영역은 교대 행 색상(zebra striping)으로 가독성을 높인다
- 중요한 열(제목, 조회수)은 더 넓게, 부차적인 열은 좁게 설정한다

**2. 숫자 가독성**

- 큰 숫자에는 반드시 천 단위 쉼표를 적용한다 (`#,##0`)
- 비율/퍼센트는 소수점 2자리까지 (`0.00%`)
- 날짜는 `yyyy-MM-dd` 형식으로 통일한다

**3. 고정 행/열**

- 헤더 행은 항상 고정(`setFrozenRows(1)`)하여 스크롤해도 보이게 한다
- 썸네일+제목 열까지 고정하면 오른쪽으로 스크롤해도 어떤 영상인지 알 수 있다

**4. 색상 체계**

- 브랜드 색상을 일관되게 사용한다 (예: 구글 블루 `#1a73e8`)
- 떡상/성장/보통 등급에 초록/노랑/회색 같은 직관적 색상을 사용한다
- 너무 많은 색상을 사용하면 오히려 가독성이 떨어진다

---

## [바로 실습] 구글 시트 서식 수동으로 다듬어보기

코드로 서식을 자동화하기 전에, 수동으로 서식을 다듬는 방법을 익혀두면 자동화 코드를 이해하기 쉽다. 앱스 스크립트의 서식 관련 주요 메서드를 정리한다.

```javascript
/**
 * 서식 관련 주요 메서드 사용 예시
 * 참고용 — 아래 autoFormatCurrentSheet()에서 실제로 사용된다
 */
function formattingExamples() {
  const sheet = SpreadsheetApp.getActiveSheet();
  
  // ===== 열 너비 =====
  sheet.setColumnWidth(1, 100);                          // 1열 너비 100px
  sheet.setColumnWidths(1, 5, 120);                      // 1~5열 모두 120px
  sheet.autoResizeColumn(3);                             // 3열 내용에 맞게 자동 조절
  sheet.autoResizeColumns(1, sheet.getLastColumn());     // 전체 열 자동 조절
  
  // ===== 행 높이 =====
  sheet.setRowHeight(1, 40);                             // 헤더 행 높이
  sheet.setRowHeights(2, 10, 90);                        // 2~11행 높이 90px (썸네일용)
  
  // ===== 행/열 고정 =====
  sheet.setFrozenRows(1);                                // 첫 번째 행 고정
  sheet.setFrozenColumns(3);                             // 1~3열 고정
  
  // ===== 셀 배경색 =====
  sheet.getRange('A1:M1').setBackground('#1a73e8');       // 헤더 배경
  sheet.getRange('A3').setBackgrounds([['#e6f4ea']]);     // 배열로 설정
  
  // ===== 글자 서식 =====
  sheet.getRange('A1:M1').setFontWeight('bold');          // 볼드
  sheet.getRange('A1:M1').setFontColor('#ffffff');        // 흰색 글자
  sheet.getRange('A1:M1').setFontSize(10);               // 폰트 크기
  sheet.getRange('A1:M1').setFontFamily('Google Sans');   // 폰트 종류
  
  // ===== 정렬 =====
  sheet.getRange('A1:M1').setHorizontalAlignment('center');  // 수평 가운데
  sheet.getRange('A1:M1').setVerticalAlignment('middle');    // 수직 가운데
  sheet.getRange('C2:C100').setWrap(true);                  // 자동 줄바꿈
  
  // ===== 숫자 형식 =====
  sheet.getRange('E2:E100').setNumberFormat('#,##0');        // 천 단위 쉼표
  sheet.getRange('L2:L100').setNumberFormat('0.00"%"');      // 퍼센트 표시
  sheet.getRange('H2:H100').setNumberFormat('yyyy-mm-dd');   // 날짜 형식
  
  // ===== 테두리 =====
  sheet.getRange('A1:M1').setBorder(
    true, true, true, true, false, false,  // top, left, bottom, right, vertical, horizontal
    '#dadce0',                              // 색상
    SpreadsheetApp.BorderStyle.SOLID        // 스타일
  );
}
```

---

## [바로 실습] 서식 지정 자동화하기

검색 결과 시트에 한 번의 클릭으로 전문적인 서식을 적용하는 함수를 만든다. `12_서식자동화.gs` 파일을 만들자.

### 완전한 자동 서식 함수

```javascript
/**
 * 현재 활성 시트에 자동 서식을 적용한다
 * 메뉴에서 직접 호출 가능
 */
function autoFormatCurrentSheet() {
  const sheet = SpreadsheetApp.getActiveSheet();
  formatSearchResults(sheet);
  SpreadsheetApp.getUi().alert('서식 자동 적용이 완료되었습니다!');
}

/**
 * 검색 결과 시트에 전문적인 서식을 자동 적용한다
 * @param {Object} sheet - Google Sheets 시트 객체
 */
function formatSearchResults(sheet) {
  const lastRow = sheet.getLastRow();
  const lastCol = sheet.getLastColumn();
  
  if (lastRow < 2 || lastCol < 3) {
    return; // 데이터가 없으면 종료
  }
  
  // 전체 범위
  const allRange = sheet.getRange(1, 1, lastRow, lastCol);
  
  // ===== 1. 기본 폰트 설정 =====
  allRange.setFontFamily('Google Sans');
  allRange.setFontSize(10);
  allRange.setVerticalAlignment('middle');
  
  // ===== 2. 헤더 행 스타일링 =====
  const headerRange = sheet.getRange(1, 1, 1, lastCol);
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
  
  // 헤더 하단 테두리 강조
  headerRange.setBorder(
    false, false, true, false, false, false,
    '#0d47a1', SpreadsheetApp.BorderStyle.SOLID_MEDIUM
  );
  
  // ===== 3. 열 너비 설정 =====
  // 헤더 텍스트로 열 유형 판별
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  
  headers.forEach((header, i) => {
    const col = i + 1;
    const h = String(header).toLowerCase();
    
    if (h.includes('번호') || h === '#') {
      sheet.setColumnWidth(col, 45);
    } else if (h.includes('썸네일')) {
      sheet.setColumnWidth(col, 160);
    } else if (h.includes('제목')) {
      sheet.setColumnWidth(col, 300);
    } else if (h.includes('채널')) {
      sheet.setColumnWidth(col, 130);
    } else if (h.includes('조회수') || h.includes('좋아요') || h.includes('댓글')) {
      sheet.setColumnWidth(col, 90);
    } else if (h.includes('게시일') || h.includes('날짜')) {
      sheet.setColumnWidth(col, 100);
    } else if (h.includes('길이') || h.includes('시간')) {
      sheet.setColumnWidth(col, 80);
    } else if (h.includes('태그')) {
      sheet.setColumnWidth(col, 200);
    } else if (h.includes('설명')) {
      sheet.setColumnWidth(col, 250);
    } else if (h.includes('참여율') || h.includes('바이럴') || h.includes('등급')) {
      sheet.setColumnWidth(col, 90);
    } else if (h.includes('url') || h.includes('링크')) {
      sheet.setColumnWidth(col, 280);
    } else {
      sheet.setColumnWidth(col, 100);
    }
  });
  
  // ===== 4. 숫자 포맷 =====
  if (lastRow > 1) {
    const dataRows = lastRow - 1;
    
    headers.forEach((header, i) => {
      const col = i + 1;
      const h = String(header);
      
      // 조회수, 좋아요, 댓글수 — 천 단위 쉼표
      if (h.includes('조회수') || h.includes('좋아요') || h.includes('댓글수') || h.includes('구독자')) {
        sheet.getRange(2, col, dataRows, 1).setNumberFormat('#,##0');
      }
      
      // 참여율 — 소수점 2자리
      if (h.includes('참여율')) {
        sheet.getRange(2, col, dataRows, 1).setNumberFormat('0.00');
      }
      
      // 바이럴 지수 — 소수점 1자리
      if (h.includes('바이럴')) {
        sheet.getRange(2, col, dataRows, 1).setNumberFormat('0.0');
      }
      
      // 날짜 형식
      if (h.includes('게시일') || h.includes('날짜')) {
        sheet.getRange(2, col, dataRows, 1).setNumberFormat('yyyy-mm-dd');
      }
    });
  }
  
  // ===== 5. 데이터 행 높이 (썸네일이 있으면 높게) =====
  const hasThumbnail = headers.some(h => String(h).includes('썸네일'));
  const dataRowHeight = hasThumbnail ? 90 : 30;
  
  for (let r = 2; r <= lastRow; r++) {
    sheet.setRowHeight(r, dataRowHeight);
  }
  
  // ===== 6. 교대 행 색상 (Zebra Striping) =====
  for (let r = 2; r <= lastRow; r++) {
    const rowRange = sheet.getRange(r, 1, 1, lastCol);
    // 이미 하이라이팅된 행(떡상 분석)은 건너뛰기
    const currentBg = rowRange.getBackground();
    if (currentBg === '#e6f4ea' || currentBg === '#fef7e0') {
      continue; // 떡상/성장 중 색상 유지
    }
    
    if (r % 2 === 0) {
      rowRange.setBackground('#f8f9fa');
    } else {
      rowRange.setBackground('#ffffff');
    }
  }
  
  // ===== 7. 번호 열 가운데 정렬 =====
  headers.forEach((header, i) => {
    const h = String(header);
    if (h.includes('번호') || h === '#' || h.includes('길이') || 
        h.includes('참여율') || h.includes('바이럴') || h.includes('등급')) {
      sheet.getRange(2, i + 1, lastRow - 1, 1).setHorizontalAlignment('center');
    }
  });
  
  // ===== 8. 제목 열 줄바꿈 =====
  headers.forEach((header, i) => {
    if (String(header).includes('제목') || String(header).includes('설명')) {
      sheet.getRange(2, i + 1, lastRow - 1, 1).setWrap(true);
    }
  });
  
  // ===== 9. 행/열 고정 =====
  sheet.setFrozenRows(1);
  
  // 썸네일+제목까지 고정 (3열까지)
  if (lastCol >= 3) {
    sheet.setFrozenColumns(3);
  }
  
  // ===== 10. 전체 테두리 (연한 회색) =====
  allRange.setBorder(
    true, true, true, true, true, true,
    '#e0e0e0', SpreadsheetApp.BorderStyle.SOLID
  );
  
  // ===== 11. 자동 필터 =====
  if (!sheet.getFilter()) {
    sheet.getRange(1, 1, lastRow, lastCol).createFilter();
  }
}

/**
 * 시트 탭 색상을 설정한다
 * 검색 결과 시트에 시각적 구분을 더한다
 * @param {Object} sheet - 시트 객체
 * @param {string} type - 'search', 'analysis', 'toc'
 */
function setSheetTabColor(sheet, type) {
  const colors = {
    search: '#1a73e8',     // 파란색: 검색 결과
    analysis: '#34a853',   // 초록색: 분석 결과
    toc: '#fbbc04',        // 노란색: 목차
    default: '#5f6368'     // 회색: 기타
  };
  
  sheet.setTabColor(colors[type] || colors.default);
}
```

### 서식 적용 통합 함수

검색 결과를 시트에 저장할 때 서식까지 한 번에 적용하도록, 6장의 `exportSearchResults()` 함수 마지막에 서식 적용 코드를 추가하면 된다.

```javascript
/**
 * exportSearchResults 함수 끝에 다음 코드를 추가한다:
 * 
 *   // 서식 자동 적용
 *   formatSearchResults(sheet);
 *   
 *   // 시트 탭 색상
 *   setSheetTabColor(sheet, 'search');
 *   
 *   // 자동 필터
 *   applyAutoFilter(sheetName);
 */
```

또는 `exportSearchResults()` 함수를 호출한 직후 서식을 적용하는 래퍼 함수를 만든다.

```javascript
/**
 * 검색 결과를 시트에 저장하고 서식까지 자동 적용하는 통합 함수
 * @param {Array<Object>} videos - 영상 데이터 배열
 * @param {string} query - 검색어
 * @returns {string} 생성된 시트 이름
 */
function exportAndFormat(videos, query) {
  // 1. 데이터 저장
  const sheetName = exportSearchResults(videos, query);
  
  // 2. 서식 적용
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (sheet) {
    formatSearchResults(sheet);
    setSheetTabColor(sheet, 'search');
  }
  
  // 3. 목차 업데이트 (선택적 — 성능 고려 시 생략 가능)
  // updateTableOfContents();
  
  return sheetName;
}
```

---

## 이 장에서 만든 코드 구조 정리

| 파일명 | 주요 함수 | 역할 |
|-------|---------|------|
| `05_필터정렬.gs` | `applyAutoFilter()` | 자동 필터 적용 |
| | `sortSheetByColumn()` | 프로그래밍 방식 정렬 |
| | `filterPopularVideos()` | 조회수+참여율 복합 필터 |
| `06_배치처리.gs` | `batchSearchYouTubeVideos()` | 페이지네이션 배치 검색 |
| | `batchSearchAndExport()` | 배치 검색 + 시트 저장 |
| `07_기간검색.gs` | `getDateRange()` | 기간 프리셋 계산 |
| | `getCustomDateRange()` | 사용자 지정 날짜 범위 |
| `08_국가언어.gs` | `getCountryList()` | 국가 코드 목록 |
| | `getLanguageList()` | 언어 코드 목록 |
| `09_쇼츠필터.gs` | `getVideoTypeFilter()` | 영상 유형 필터 |
| | `searchWithVideoTypeFilter()` | 쇼츠/일반 구분 검색 |
| `10_떡상분석.gs` | `calculateViralityScore()` | 바이럴 지수 계산 |
| | `highlightViralVideos()` | 떡상 영상 하이라이팅 |
| `11_목차.gs` | `updateTableOfContents()` | 목차 시트 자동 생성 |
| `12_서식자동화.gs` | `formatSearchResults()` | 전체 서식 자동 적용 |
| | `autoFormatCurrentSheet()` | 현재 시트 서식 (메뉴용) |
| | `exportAndFormat()` | 저장 + 서식 통합 |

---

## 완성된 사이드바 전체 코드

6장과 7장에서 추가한 모든 필터 기능이 통합된 최종 `SearchSidebar.html` 코드이다. 기존 파일을 이 전체 코드로 교체한다.

```html
<!DOCTYPE html>
<html>
<head>
  <base target="_top">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Google Sans', 'Noto Sans KR', -apple-system, sans-serif;
      font-size: 13px;
      color: #202124;
      background: #f8f9fa;
      padding: 16px;
    }
    .card {
      background: white;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .card-title {
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #5f6368;
      margin-bottom: 10px;
    }
    .input-group { margin-bottom: 10px; }
    .input-group label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: #3c4043;
      margin-bottom: 4px;
    }
    input[type="text"], input[type="date"], select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #dadce0;
      border-radius: 8px;
      font-size: 13px;
      outline: none;
      transition: border-color 0.2s;
      background: #fff;
    }
    input:focus, select:focus {
      border-color: #1a73e8;
      box-shadow: 0 0 0 2px rgba(26,115,232,0.12);
    }
    .filter-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
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
    .btn-search:disabled { background: #dadce0; cursor: not-allowed; }
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }
    .results-count { font-size: 12px; color: #5f6368; }
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
    .video-channel { font-size: 11px; color: #5f6368; margin-bottom: 2px; }
    .video-stats { font-size: 11px; color: #80868b; }
    .video-stats span { margin-right: 8px; }
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
      transition: width 0.3s;
      width: 0%;
    }
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
    .collapsible-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      cursor: pointer;
      user-select: none;
    }
    .collapsible-header .arrow { transition: transform 0.2s; }
    .collapsible-header.open .arrow { transform: rotate(180deg); }
    .collapsible-body {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s ease;
    }
    .collapsible-body.open { max-height: 500px; }
  </style>
</head>
<body>

  <!-- 검색 입력 -->
  <div class="card">
    <div class="card-title">검색</div>
    <div class="input-group">
      <input type="text" id="searchQuery" placeholder="검색어를 입력하세요..."
             onkeypress="if(event.key==='Enter') performSearch()">
    </div>
    <div class="filter-grid">
      <div class="input-group">
        <label>정렬</label>
        <select id="sortOrder">
          <option value="relevance">관련성</option>
          <option value="viewCount">조회수</option>
          <option value="date">최신순</option>
          <option value="rating">평점</option>
        </select>
      </div>
      <div class="input-group">
        <label>개수</label>
        <select id="maxResults">
          <option value="10">10개</option>
          <option value="25" selected>25개</option>
          <option value="50">50개</option>
          <option value="100">100개</option>
          <option value="200">200개</option>
        </select>
      </div>
    </div>
    <button class="btn-search" id="searchBtn" onclick="performSearch()">
      🔍 검색하기
    </button>
  </div>

  <!-- 고급 필터 (접기/펼치기) -->
  <div class="card">
    <div class="collapsible-header" onclick="toggleFilters(this)">
      <span class="card-title" style="margin-bottom:0">고급 필터</span>
      <span class="arrow">▼</span>
    </div>
    <div class="collapsible-body" id="advancedFilters">
      <div style="padding-top: 12px;">
        <!-- 기간 -->
        <div class="input-group">
          <label>업로드 기간</label>
          <select id="datePreset" onchange="toggleCustomDate()">
            <option value="all">전체 기간</option>
            <option value="last24h">최근 24시간</option>
            <option value="lastWeek">최근 1주</option>
            <option value="lastMonth">최근 1달</option>
            <option value="last3Months">최근 3달</option>
            <option value="lastYear">최근 1년</option>
            <option value="custom">사용자 지정</option>
          </select>
        </div>
        <div id="customDateArea" style="display:none;">
          <div class="filter-grid">
            <div class="input-group">
              <label>시작일</label>
              <input type="date" id="customStartDate">
            </div>
            <div class="input-group">
              <label>종료일</label>
              <input type="date" id="customEndDate">
            </div>
          </div>
        </div>

        <!-- 국가/언어 -->
        <div class="filter-grid">
          <div class="input-group">
            <label>국가</label>
            <select id="regionCode"></select>
          </div>
          <div class="input-group">
            <label>언어</label>
            <select id="relevanceLanguage"></select>
          </div>
        </div>

        <!-- 영상 유형 -->
        <div class="input-group">
          <label>영상 유형</label>
          <select id="videoDuration">
            <option value="">전체</option>
            <option value="short">쇼츠 (60초 이하)</option>
            <option value="medium">일반 (4~20분)</option>
            <option value="long">긴 영상 (20분+)</option>
          </select>
        </div>
      </div>
    </div>
  </div>

  <!-- 진행 바 -->
  <div class="progress-bar" id="progressBar">
    <div class="progress-bar-fill" id="progressFill"></div>
  </div>

  <!-- 결과 -->
  <div id="resultsArea">
    <div class="status">검색어를 입력하고 검색 버튼을 클릭하세요.</div>
  </div>

  <script>
    var currentResults = [];

    // 페이지 로드 시 국가/언어 드롭다운 초기화
    (function init() {
      google.script.run.withSuccessHandler(function(countries) {
        var sel = document.getElementById('regionCode');
        countries.forEach(function(c) {
          var opt = document.createElement('option');
          opt.value = c.code;
          opt.textContent = c.name;
          if (c.code === 'KR') opt.selected = true;
          sel.appendChild(opt);
        });
      }).getCountryList();

      google.script.run.withSuccessHandler(function(languages) {
        var sel = document.getElementById('relevanceLanguage');
        languages.forEach(function(l) {
          var opt = document.createElement('option');
          opt.value = l.code;
          opt.textContent = l.name;
          if (l.code === 'ko') opt.selected = true;
          sel.appendChild(opt);
        });
      }).getLanguageList();
    })();

    function toggleFilters(el) {
      el.classList.toggle('open');
      document.getElementById('advancedFilters').classList.toggle('open');
    }

    function toggleCustomDate() {
      var preset = document.getElementById('datePreset').value;
      document.getElementById('customDateArea').style.display =
        (preset === 'custom') ? 'block' : 'none';
    }

    function getDateFilter() {
      var preset = document.getElementById('datePreset').value;
      if (preset === 'all') return {};
      if (preset === 'custom') {
        var s = document.getElementById('customStartDate').value;
        var e = document.getElementById('customEndDate').value;
        if (!s) return {};
        return {
          publishedAfter: new Date(s + 'T00:00:00Z').toISOString(),
          publishedBefore: e ? new Date(e + 'T23:59:59Z').toISOString() : new Date().toISOString()
        };
      }
      var now = new Date(), after;
      switch (preset) {
        case 'last24h': after = new Date(now.getTime() - 86400000); break;
        case 'lastWeek': after = new Date(now.getTime() - 604800000); break;
        case 'lastMonth': after = new Date(now); after.setMonth(after.getMonth()-1); break;
        case 'last3Months': after = new Date(now); after.setMonth(after.getMonth()-3); break;
        case 'lastYear': after = new Date(now); after.setFullYear(after.getFullYear()-1); break;
        default: return {};
      }
      return { publishedAfter: after.toISOString(), publishedBefore: now.toISOString() };
    }

    function performSearch() {
      var query = document.getElementById('searchQuery').value.trim();
      if (!query) { showStatus('검색어를 입력해주세요.', true); return; }

      var maxResults = parseInt(document.getElementById('maxResults').value);
      var options = { order: document.getElementById('sortOrder').value };

      // 기간 필터
      var df = getDateFilter();
      if (df.publishedAfter) options.publishedAfter = df.publishedAfter;
      if (df.publishedBefore) options.publishedBefore = df.publishedBefore;

      // 국가/언어
      var region = document.getElementById('regionCode').value;
      if (region) options.regionCode = region;
      var lang = document.getElementById('relevanceLanguage').value;
      if (lang) options.relevanceLanguage = lang;

      // 영상 유형
      var dur = document.getElementById('videoDuration').value;
      if (dur) options.videoDuration = dur;

      setSearching(true);

      if (maxResults <= 50) {
        showLoading('검색 중...');
        setProgress(30);
        google.script.run
          .withSuccessHandler(function(result) {
            setSearching(false); setProgress(100);
            if (!result || !result.videos || result.videos.length === 0) {
              showStatus('검색 결과가 없습니다.', false); return;
            }
            currentResults = result.videos;
            displayResults(result.videos, result.totalResults);
          })
          .withFailureHandler(handleError)
          .searchYouTubeVideos(query, maxResults, options);
      } else {
        showLoading('배치 검색 중... (약 ' + Math.ceil(maxResults/50) + '페이지)');
        setProgress(20);
        google.script.run
          .withSuccessHandler(function(result) {
            setSearching(false); setProgress(100);
            showStatus('✅ ' + result.totalSaved + '개 영상 → "' + result.sheetName + '" 시트 저장 완료!', false);
          })
          .withFailureHandler(handleError)
          .batchSearchAndExport(query, maxResults, options);
      }
    }

    function displayResults(videos, totalResults) {
      var area = document.getElementById('resultsArea');
      var html = '<div class="card">';
      html += '<div class="results-header">';
      html += '<div class="card-title">검색 결과</div>';
      html += '<div class="results-count">' + videos.length + '개 / 약 ' + fmt(totalResults) + '개</div>';
      html += '</div>';
      videos.forEach(function(v) {
        html += '<div class="video-item" onclick="window.open(\'' + v.videoUrl + '\')">';
        html += '<img class="video-thumb" src="' + v.thumbnailUrl + '" loading="lazy">';
        html += '<div class="video-info">';
        html += '<div class="video-title">' + esc(v.title) + '</div>';
        html += '<div class="video-channel">' + esc(v.channelTitle) + '</div>';
        html += '<div class="video-stats">';
        html += '<span>👁 ' + fmt(v.viewCount) + '</span>';
        html += '<span>👍 ' + fmt(v.likeCount) + '</span>';
        html += '<span>⏱ ' + v.durationFormatted + '</span>';
        html += '</div></div></div>';
      });
      html += '<button class="btn-export" onclick="exportToSheet()">📋 시트에 저장하기</button>';
      html += '</div>';
      area.innerHTML = html;
    }

    function exportToSheet() {
      if (!currentResults.length) { showStatus('저장할 결과가 없습니다.', true); return; }
      showLoading('시트에 저장 중...');
      var query = document.getElementById('searchQuery').value.trim();
      google.script.run
        .withSuccessHandler(function(name) {
          showStatus('✅ "' + name + '" 시트에 저장 완료!', false);
        })
        .withFailureHandler(handleError)
        .exportAndFormat(currentResults, query);
    }

    function handleError(e) { setSearching(false); setProgress(0); showStatus('오류: ' + e.message, true); }
    function showStatus(msg, err) {
      document.getElementById('resultsArea').innerHTML =
        '<div class="status' + (err ? ' error' : '') + '">' + msg + '</div>';
    }
    function showLoading(msg) {
      document.getElementById('resultsArea').innerHTML =
        '<div class="spinner-container"><div class="spinner"></div><span>' + msg + '</span></div>';
    }
    function setSearching(b) {
      var btn = document.getElementById('searchBtn');
      btn.disabled = b;
      btn.innerHTML = b
        ? '<div class="spinner" style="width:18px;height:18px;border-width:2px"></div> 검색 중...'
        : '🔍 검색하기';
    }
    function setProgress(p) {
      var bar = document.getElementById('progressBar');
      bar.className = (p > 0 && p < 100) ? 'progress-bar active' : 'progress-bar';
      document.getElementById('progressFill').style.width = p + '%';
    }
    function fmt(n) { return n == null ? '0' : Number(n).toLocaleString('ko-KR'); }
    function esc(t) { var d = document.createElement('div'); d.appendChild(document.createTextNode(t)); return d.innerHTML; }
  </script>
</body>
</html>
```

이로써 Part 03의 핵심 기능 구현이 완료되었다. 6장에서 만든 기본 검색 시스템 위에 7장의 고급 기능들이 쌓여, 전문 유튜브 리서치 도구로서의 면모를 갖추게 되었다. 다음 장에서는 이 시스템을 더욱 확장하여 댓글 수집, 트렌드 분석 등의 기능을 추가할 것이다.
