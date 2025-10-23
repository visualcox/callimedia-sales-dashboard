# 🚀 Streamlit Cloud 배포 가이드

칼라미디어 B2B 매출 분석 대시보드를 Streamlit Cloud에 배포하는 단계별 가이드입니다.

## 📋 체크리스트

배포 전 준비사항:
- [ ] GitHub 계정 생성 완료
- [ ] Streamlit Cloud 계정 가입 완료
- [ ] 프로젝트 ZIP 파일 다운로드 완료
- [ ] 매출 데이터 파일 준비 완료

---

## STEP 1: GitHub 저장소 생성 (5분)

### 1-1. GitHub 로그인
1. https://github.com 접속
2. 로그인 (계정 없으면 회원가입)

### 1-2. 새 저장소 만들기
1. 우측 상단 **"+"** → **"New repository"** 클릭
2. 저장소 설정:
   ```
   Repository name: callimedia-sales-dashboard
   Description: 칼라미디어 B2B 매출 분석 대시보드
   ⚪ Public (무료 플랜은 Public만 가능)
   ✅ Add a README file
   ✅ Add .gitignore → Python 선택
   ```
3. **"Create repository"** 클릭

---

## STEP 2: 프로젝트 파일 업로드 (10분)

### 방법 A: 웹 인터페이스로 업로드 (초보자 권장 ⭐⭐⭐⭐⭐)

1. **ZIP 파일 압축 해제**
   - `callimedia-sales-dashboard.zip` 압축 해제
   - 내부 파일 확인

2. **GitHub 저장소 페이지에서 업로드**
   ```
   1. 저장소 메인 페이지 접속
   2. "Add file" → "Upload files" 클릭
   3. 모든 파일/폴더를 드래그 앤 드롭
      ⚠️ 주의: .gitignore도 함께 업로드!
   4. 커밋 메시지 입력: "Initial commit: 프로젝트 초기 설정"
   5. "Commit changes" 클릭
   ```

3. **업로드 확인**
   - 다음 파일들이 보여야 함:
     ```
     ├── .gitignore
     ├── .streamlit/
     ├── app.py
     ├── data/
     ├── README.md
     ├── requirements.txt
     └── utils/
     ```

### 방법 B: Git 명령어 사용 (개발자용)

```bash
# 1. 프로젝트 폴더로 이동
cd callimedia-sales-dashboard

# 2. Git 초기화
git init
git add .
git commit -m "Initial commit: 프로젝트 초기 설정"

# 3. GitHub 원격 저장소 연결
git remote add origin https://github.com/your-username/callimedia-sales-dashboard.git

# 4. Push
git branch -M main
git push -u origin main
```

---

## STEP 3: Streamlit Cloud 배포 (5분)

### 3-1. Streamlit Cloud 접속
1. https://streamlit.io/cloud 접속
2. **"Sign up"** 또는 **"Get started"** 클릭
3. **"Continue with GitHub"** 선택
4. GitHub 계정으로 로그인

### 3-2. GitHub 권한 승인
```
Streamlit이 요청하는 권한:
✓ 저장소 읽기 권한
✓ 배포를 위한 쓰기 권한

→ "Authorize streamlit" 클릭
```

### 3-3. 이메일 인증
1. GitHub 이메일로 인증 메일 수신
2. **"Verify email address"** 클릭
3. Streamlit Cloud 대시보드로 자동 이동

### 3-4. 앱 배포
1. **"New app"** 버튼 클릭
2. 배포 설정 입력:
   ```
   ┌─────────────────────────────────────────┐
   │ Repository:                             │
   │ your-username/callimedia-sales-dashboard│
   │                                         │
   │ Branch: main                            │
   │                                         │
   │ Main file path: app.py                 │
   │                                         │
   │ App URL (optional):                    │
   │ callimedia-sales                       │
   │ (비워두면 자동 생성)                      │
   └─────────────────────────────────────────┘
   ```
3. **"Deploy!"** 클릭

### 3-5. 배포 진행 상황 확인
```
화면에 실시간 로그 표시:

📦 Building...
   → Installing Python 3.11
   → Installing dependencies from requirements.txt
   → Setting up Streamlit environment
   
🚀 Deploying...
   → Starting Streamlit server
   → Configuring app settings
   
✅ Your app is live at:
   https://callimedia-sales.streamlit.app
```

⏱️ 배포 시간: 약 2-5분 소요

---

## STEP 4: Secrets 설정 (3분)

민감한 정보(비밀번호, API 키)를 안전하게 설정합니다.

### 4-1. Secrets 메뉴 접속
1. Streamlit Cloud 대시보드에서 앱 선택
2. 우측 상단 **⚙️ Settings** 클릭
3. **"Secrets"** 탭 선택

### 4-2. Secrets 입력
아래 내용을 복사하여 붙여넣기 (값은 수정):

```toml
[passwords]
admin_password = "칼라미디어2024"

[api_keys]
gemini_api_key = "AIzaSyBleGoYya2uUU6Es6qw11gO_s7IlL2Ly34"
openai_api_key = "sk-proj-MLRzg3NquGEafLmcQjYIdxuK..."

[supabase]
project_url = "https://kxcihzetdnwsxxqpvvjz.supabase.co"
api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 4-3. 저장
1. **"Save"** 클릭
2. 앱이 자동으로 재시작됨 (약 30초)

---

## STEP 5: 첫 접속 및 테스트 (5분)

### 5-1. 앱 접속
1. 배포 완료 시 표시되는 URL 클릭
   - 예: `https://callimedia-sales.streamlit.app`
2. 또는 Streamlit Cloud 대시보드에서 **"Open app"** 클릭

### 5-2. 로그인
```
비밀번호: 칼라미디어2024
(또는 Secrets에서 설정한 비밀번호)
```

### 5-3. 데이터 업로드 테스트
1. 사이드바에서 **"📁 데이터 업로드"** 선택
2. 거래처 리스트 파일 업로드
3. 매출 데이터 파일 업로드 (여러 개 가능)
4. 데이터 로드 완료 확인

### 5-4. 기능 테스트
- [ ] 📈 매출 분석 차트 표시
- [ ] 🎯 거래처 분석 작동
- [ ] 📦 제품 분석 작동
- [ ] 🔮 매출 예측 작동

---

## STEP 6: URL 공유 (1분)

### 배포된 앱 URL
```
https://your-app-name.streamlit.app
```

### 공유 방법
1. **URL 복사**: 동료들에게 링크 전달
2. **비밀번호 공유**: 로그인 비밀번호 별도 전달
3. **접속 안내**:
   ```
   칼라미디어 매출 분석 시스템
   
   URL: https://callimedia-sales.streamlit.app
   비밀번호: [별도 전달]
   
   사용법:
   1. 로그인
   2. 데이터 업로드
   3. 분석 메뉴 선택
   ```

---

## 🔄 앱 업데이트 방법

### 코드 수정 시
1. GitHub에서 파일 수정
2. **"Commit changes"** 클릭
3. Streamlit이 자동 감지하여 재배포 (1-2분)
4. 앱 새로고침

### 버그 수정 프로세스
```
1. GitHub에서 파일 수정
2. 커밋 메시지 입력: "Fix: 버그 설명"
3. Commit
4. Streamlit Cloud에서 배포 로그 확인
5. 앱 테스트
```

---

## 🐛 문제 해결

### ❌ 배포 실패 시

#### 문제 1: requirements.txt 오류
```
해결:
1. GitHub에서 requirements.txt 열기
2. 패키지 버전 확인
3. 문제되는 패키지 버전 수정
4. Commit
```

#### 문제 2: 파일을 찾을 수 없음
```
해결:
1. GitHub에서 파일 구조 확인
2. app.py가 루트에 있는지 확인
3. .streamlit 폴더가 있는지 확인
4. utils 폴더가 있는지 확인
```

#### 문제 3: Import 오류
```
해결:
1. utils/__init__.py 파일 추가 (빈 파일)
2. Python 경로 문제 확인
```

### ⚠️ 앱이 느릴 때
```
원인: 무료 플랜 리소스 제한
해결:
1. 데이터 캐싱 활용 (@st.cache_data)
2. 불필요한 계산 최소화
3. 유료 플랜 고려 ($20/월)
```

### 🔐 로그인 안 될 때
```
해결:
1. Secrets 설정 확인
2. 비밀번호 철자 확인
3. 브라우저 캐시 삭제
```

---

## 📊 성능 최적화

### 무료 플랜 제한
```
RAM: 1GB
CPU: 제한적
동시 접속: 제한적
앱 개수: 3개
```

### 최적화 팁
1. **데이터 캐싱 활용**
   ```python
   @st.cache_data
   def load_data():
       return pd.read_excel(file)
   ```

2. **큰 파일은 외부 저장소 사용**
   - Google Drive
   - Supabase Storage
   - AWS S3

3. **불필요한 재계산 방지**
   - Session State 활용
   - 조건부 계산

---

## 🔒 보안 강화

### 추가 보안 조치

1. **비밀번호 변경**
   - Secrets에서 강력한 비밀번호로 변경
   - 정기적 변경 (3개월마다)

2. **API 키 보호**
   - 절대 코드에 직접 입력 금지
   - Secrets에만 저장

3. **데이터 파일 보호**
   - .gitignore 확인
   - GitHub에 데이터 파일 없는지 확인

4. **접속 기록 모니터링**
   - Streamlit Cloud 로그 주기적 확인

---

## 📞 지원

### 문제 발생 시
1. Streamlit Cloud 로그 확인
2. GitHub Issues 검색
3. Streamlit Community 포럼: https://discuss.streamlit.io

### 추가 개발 요청
GitHub Issues에 등록해주세요.

---

## ✅ 배포 완료 체크리스트

최종 확인:
- [ ] GitHub 저장소 생성 완료
- [ ] 모든 파일 업로드 완료
- [ ] Streamlit Cloud 배포 완료
- [ ] Secrets 설정 완료
- [ ] 로그인 테스트 성공
- [ ] 데이터 업로드 테스트 성공
- [ ] 모든 분석 기능 정상 작동
- [ ] URL 공유 완료
- [ ] 동료들 접속 테스트 완료

---

**🎉 배포 완료! 이제 어디서든 매출 데이터를 분석할 수 있습니다!**

**Made with ❤️ by CallaMedia**
