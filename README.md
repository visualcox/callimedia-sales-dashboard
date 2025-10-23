# 📊 칼라미디어 B2B 매출 분석 대시보드

Streamlit 기반의 매출 데이터 분석 및 시각화 웹 애플리케이션

## 🎯 주요 기능

### 1. 📁 데이터 업로드
- Excel 파일 업로드 (여러 파일 동시 업로드 가능)
- 거래처 정보 자동 병합
- 데이터 자동 정리 및 전처리

### 2. 📈 매출 분석
- 일별/주별/월별/분기별/연도별 매출 추이
- 성장률 분석
- 거래건수 및 평균 거래액 분석

### 3. 🎯 거래처 분석
- 거래처별 매출 순위
- 파레토 차트 (80/20 법칙)
- 고성장 거래처 식별
- 거래처별 평균 거래액 분석

### 4. 📦 제품 분석
- 제품별 매출 순위
- 제품별 판매건수
- 제품 포트폴리오 분석

### 5. 🔮 매출 예측
- 향후 1~12개월 매출 예측
- 추세 분석
- 최근 3/6/12개월 평균 매출

### 6. 💬 AI 질의응답 (개발 중)
- 자연어로 데이터 질문
- Gemini/OpenAI API 연동

## 🚀 빠른 시작

### Streamlit Cloud 배포

1. **GitHub 저장소 생성**
   ```
   - 저장소 이름: callimedia-sales-dashboard
   - 공개/비공개: Public (무료 플랜)
   ```

2. **파일 업로드**
   - 모든 프로젝트 파일을 GitHub에 업로드

3. **Streamlit Cloud 배포**
   - https://share.streamlit.io 접속
   - "New app" 클릭
   - GitHub 저장소 연결
   - `app.py` 파일 선택
   - "Deploy!" 클릭

4. **Secrets 설정** (선택사항)
   ```toml
   [passwords]
   admin_password = "your_password_here"
   
   [api_keys]
   gemini_api_key = "your_gemini_api_key"
   openai_api_key = "your_openai_api_key"
   
   [supabase]
   project_url = "your_supabase_url"
   api_key = "your_supabase_api_key"
   ```

### 로컬 실행

1. **저장소 클론**
   ```bash
   git clone https://github.com/your-username/callimedia-sales-dashboard.git
   cd callimedia-sales-dashboard
   ```

2. **가상환경 생성 및 활성화**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **앱 실행**
   ```bash
   streamlit run app.py
   ```

5. **브라우저에서 접속**
   ```
   http://localhost:8501
   ```

## 📂 프로젝트 구조

```
callimedia-sales-dashboard/
│
├── app.py                      # 메인 애플리케이션
├── requirements.txt            # Python 패키지 목록
├── README.md                   # 프로젝트 문서
├── .gitignore                  # Git 제외 파일
│
├── .streamlit/
│   └── config.toml            # Streamlit 설정
│
├── utils/
│   ├── data_loader.py         # 데이터 로딩 함수
│   ├── analysis.py            # 분석 함수
│   └── charts.py              # 차트 생성 함수
│
└── data/                       # 데이터 폴더 (gitignore)
    ├── clients.xlsx           # 거래처 리스트
    ├── sales_2023.xlsx        # 2023년 매출
    ├── sales_2024.xlsx        # 2024년 매출
    └── sales_2025.xlsx        # 2025년 매출
```

## 🔐 보안

- 기본 비밀번호 인증 기능 포함
- 데이터 파일은 `.gitignore`에 포함되어 GitHub에 업로드되지 않음
- API 키는 Streamlit Secrets에 안전하게 저장
- 민감한 정보는 코드에 직접 포함하지 않음

## 📊 데이터 요구사항

### 매출 데이터 파일 (Excel)
필수 컬럼:
- 날짜 관련: `날짜`, `일자`, `전표일자`, `판매일자`, `거래일자` 중 하나
- 금액 관련: `공급가액`, `금액`, `합계금액`, `매출금액` 중 하나
- 거래처 관련: `판매처명`, `거래처명`, `거래처`, `고객명` 중 하나

선택 컬럼:
- `품목명`, `제품명`, `상품명` (제품 분석용)
- `수량`, `단가` (상세 분석용)

### 거래처 리스트 파일 (Excel)
필수 컬럼:
- `거래처명`, `회사명`, `업체명` 중 하나

선택 컬럼:
- `업종`, `지역`, `담당자`, `연락처` 등

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **AI/LLM**: Google Gemini API, OpenAI API (선택)
- **Vector DB**: ChromaDB (선택)
- **Database**: Supabase (선택)

## 📝 사용 방법

1. **로그인**
   - 기본 비밀번호: `칼라미디어2024`
   - Secrets에서 비밀번호 변경 가능

2. **데이터 업로드**
   - 사이드바에서 "📁 데이터 업로드" 선택
   - 거래처 리스트 파일 업로드 (선택)
   - 매출 데이터 파일 업로드 (필수, 여러 파일 가능)

3. **분석 수행**
   - 원하는 분석 메뉴 선택
   - 차트와 테이블로 결과 확인
   - 필요 시 데이터 다운로드

## 🔄 업데이트

### 코드 수정
1. GitHub에서 파일 수정
2. Commit & Push
3. Streamlit Cloud가 자동으로 재배포 (1-2분 소요)

### 데이터 업데이트
- 앱에서 새 파일 업로드
- 또는 Google Drive / Supabase 연동 (추후 구현)

## 🐛 문제 해결

### 앱이 로드되지 않을 때
- Streamlit Cloud 로그 확인
- requirements.txt 패키지 버전 확인
- Secrets 설정 확인

### 데이터가 로드되지 않을 때
- Excel 파일 형식 확인 (.xlsx)
- 필수 컬럼 존재 확인
- 파일 인코딩 확인 (UTF-8 권장)

### 차트가 표시되지 않을 때
- 브라우저 캐시 삭제
- 페이지 새로고침 (F5)

## 📞 지원

문의사항이 있으시면 GitHub Issues에 등록해주세요.

## 📄 라이선스

이 프로젝트는 칼라미디어 내부용으로 제작되었습니다.

---

**Made with ❤️ by CallaMedia**
