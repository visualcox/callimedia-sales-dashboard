# 🏷️ 브랜드 분석 기능 업데이트 가이드

브랜드별 매출 분석 기능을 추가하는 방법입니다.

## 📋 추가된 파일

### 1. `utils/brand_analysis.py`
브랜드 분석 핵심 함수들:
- `extract_brand_from_product()` - 제품명에서 브랜드 추출
- `load_brand_list()` - 브랜드 리스트 로드
- `add_brand_column()` - 매출 데이터에 브랜드 컬럼 추가
- `analyze_sales_by_brand()` - 브랜드별 매출 분석
- `analyze_brand_trend()` - 브랜드별 시계열 추이
- `get_brand_product_detail()` - 브랜드 내 제품 상세
- `compare_brand_growth()` - 브랜드별 성장률
- `get_brand_statistics()` - 브랜드 통계

### 2. `pages_brand.py`
브랜드 분석 페이지 함수들:
- `page_brand_upload()` - 브랜드 리스트 업로드
- `page_brand_analysis()` - 브랜드별 매출 분석

## 🔧 app.py 수정 방법

### STEP 1: 임포트 추가

`app.py` 파일 상단의 임포트 섹션에 다음 코드 추가:

```python
# 기존 임포트 아래에 추가
from utils.brand_analysis import (
    load_brand_list,
    add_brand_column,
    get_brand_statistics
)
```

### STEP 2: 메뉴에 브랜드 분석 추가

`main()` 함수의 사이드바 메뉴 부분을 다음과 같이 수정:

```python
# 기존 코드 (약 95번째 줄 근처)
menu = st.radio(
    "메뉴 선택",
    ["📁 데이터 업로드", "📈 매출 분석", "🎯 거래처 분석", "📦 제품 분석", "🔮 매출 예측", "💬 AI 질의응답"],
    index=0
)

# 수정된 코드
menu = st.radio(
    "메뉴 선택",
    [
        "📁 데이터 업로드", 
        "🏷️ 브랜드 업로드",  # 추가
        "📈 매출 분석", 
        "🎯 거래처 분석", 
        "📦 제품 분석", 
        "🏷️ 브랜드 분석",  # 추가
        "🔮 매출 예측", 
        "💬 AI 질의응답"
    ],
    index=0
)
```

### STEP 3: 페이지 라우팅 추가

`main()` 함수의 메뉴별 페이지 부분에 추가:

```python
# 기존 메뉴 처리 아래에 추가
if menu == "📁 데이터 업로드":
    page_data_upload()
elif menu == "🏷️ 브랜드 업로드":  # 추가
    page_brand_upload()  # 추가
elif menu == "📈 매출 분석":
    page_sales_analysis()
elif menu == "🎯 거래처 분석":
    page_client_analysis()
elif menu == "📦 제품 분석":
    page_product_analysis()
elif menu == "🏷️ 브랜드 분석":  # 추가
    page_brand_analysis()  # 추가
elif menu == "🔮 매출 예측":
    page_prediction()
elif menu == "💬 AI 질의응답":
    page_ai_query()
```

### STEP 4: 브랜드 페이지 함수 추가

`app.py` 파일 끝부분에 `pages_brand.py`의 함수들을 복사하여 추가:

```python
# page_ai_query() 함수 아래에 추가

def page_brand_upload():
    """브랜드 리스트 업로드 페이지"""
    # pages_brand.py의 page_brand_upload() 함수 내용 복사
    ...

def page_brand_analysis():
    """브랜드별 매출 분석 페이지"""
    # pages_brand.py의 page_brand_analysis() 함수 내용 복사
    ...
```

## 📝 빠른 업데이트 방법

### 방법 1: GitHub에서 직접 수정

1. GitHub 저장소 접속
2. `utils/brand_analysis.py` 파일 생성
   - "Add file" → "Create new file"
   - 파일명: `utils/brand_analysis.py`
   - 내용: `utils/brand_analysis.py` 파일 내용 복사
   - Commit

3. `app.py` 파일 수정
   - `app.py` 열기
   - "Edit" 클릭
   - 위의 STEP 1~4 내용 추가
   - Commit

4. Streamlit Cloud가 자동 재배포 (1-2분)

### 방법 2: 전체 파일 다운로드 후 교체

1. 업데이트된 프로젝트 ZIP 다운로드 (AI드라이브에 저장됨)
2. 압축 해제
3. GitHub에서 기존 파일들 교체
4. Commit & Push

## 🎯 사용 방법

### 1. 브랜드 리스트 준비

브랜드 리스트 CSV 파일 형식:
```csv
브랜드명
AVMATRIX
ROXTONE
AUDIOCENTER
SUPERLUX
PROPRESENTER
```

### 2. 브랜드 리스트 업로드

1. 앱 접속
2. 사이드바에서 "🏷️ 브랜드 업로드" 선택
3. CSV 파일 업로드
4. 브랜드 목록 확인
5. 자동으로 매출 데이터에 브랜드 정보 추가

### 3. 브랜드별 분석

1. "🏷️ 브랜드 분석" 메뉴 선택
2. 다양한 브랜드 분석 확인:
   - 브랜드별 매출 순위
   - 파레토 차트
   - 브랜드별 추이
   - 브랜드별 성장률
   - 특정 브랜드 상세 분석

## 🔍 브랜드 자동 인식 방식

제품명에서 브랜드를 자동으로 인식합니다:

**예시:**
```
제품명: "AVMATRIX SC2031 3G-SDI to HDMI Converter"
→ 브랜드: AVMATRIX

제품명: "ROXTONE 케이블 5m"
→ 브랜드: ROXTONE

제품명: "SUPERLUX BES3.5 스피커"
→ 브랜드: SUPERLUX
```

## 📊 분석 기능

### 1. 브랜드별 매출 순위
- 총 매출액
- 판매건수
- 평균단가
- 매출 비중

### 2. 브랜드별 시계열 추이
- 상위 5개 브랜드의 월별 매출 추이
- 추세 파악

### 3. 브랜드별 성장률
- 최근 6개월 vs 이전 6개월
- 성장률 % 계산

### 4. 브랜드 내 제품 분석
- 특정 브랜드의 제품별 매출
- 브랜드 포트폴리오 분석

## 🐛 문제 해결

### 브랜드가 인식되지 않을 때
- 브랜드명 철자 확인
- 대소문자는 구분 안 함
- 공백 확인

### 기타로 분류될 때
- 브랜드 리스트에 해당 브랜드 추가
- 제품명 형식 확인

### 성능 문제
- 브랜드 리스트를 최소화 (필요한 것만)
- 데이터 캐싱 활용

## ✅ 업데이트 체크리스트

- [ ] `utils/brand_analysis.py` 파일 생성
- [ ] `app.py`에 임포트 추가
- [ ] `app.py`에 메뉴 추가
- [ ] `app.py`에 페이지 함수 추가
- [ ] GitHub에 Push
- [ ] Streamlit Cloud 재배포 확인
- [ ] 브랜드 리스트 업로드 테스트
- [ ] 브랜드 분석 기능 테스트

## 📞 지원

문제가 발생하면 GitHub Issues에 등록해주세요.

---

**🎉 브랜드 분석 기능으로 더욱 강력한 매출 인사이트를 얻으세요!**
