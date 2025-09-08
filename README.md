# AI 부동산 중개 에이전트

## 프로젝트 소개

이 프로젝트는 3개의 AI 에이전트가 협력하여 사용자의 부동산 매물 검색을 도와주는 멀티 에이전트 시스템입니다.

### 에이전트 구성

1. **이성적 조언자 (Rational Agent)**: 현실적이고 냉철한 부동산 전문가
   - 출퇴근, 생활 환경, 재정적 리스크를 최우선으로 고려
   - 통계 데이터나 객관적인 사실을 근거로 조언
   - 안전하고 안정적인 선택을 강조

2. **감성적 조언자 (Emotional Agent)**: 고객의 낭만과 로망을 존중하는 감성적인 전문가
   - 고객의 감정적인 만족도와 삶의 질을 중시
   - 비현실적이지 않은 범위 내에서 고객이 원하는 가치를 실현하도록 도움
   - 무언가를 얻기 위해 다른 부분을 희생할 수도 있음을 부드럽게 설득

3. **중재자 (Mediator Agent)**: 두 에이전트의 의견을 종합하고 핵심을 정리하여 가장 합리적인 결론을 내리는 중재자
   - 앞선 두 에이전트의 대화를 요약하고 장단점을 명확하게 분석
   - 사용자가 최종 결정을 내릴 수 있도록 객관적이고 균형 잡힌 정보를 제공

## 기술 스택

### 프론트엔드
- **Streamlit**: 사용자 인터페이스
- **Python**: 메인 개발 언어

### 백엔드
- **FastAPI**: REST API 서버
- **SQLAlchemy**: ORM
- **SQLite**: 데이터베이스

### AI/ML
- **LangChain**: LLM 프레임워크
- **LangGraph**: 멀티 에이전트 워크플로우
- **FAISS**: 벡터 데이터베이스
- **DuckDuckGo Search**: 웹 검색

### 기타
- **Docker**: 컨테이너화
- **Pydantic**: 데이터 검증

## 주요 기능

1. **부동산 매물 검색 조건 입력**
   - 예산 (천만원 또는 억 단위)
   - 매물 유형 (아파트, 빌라, 단독주택, 오피스텔 등)
   - 선호 조건1 (지하철역근처, 학교근처, 병원근처, 터미널, 마트, 학원)
   - 선호 조건2 (자유 입력)

2. **멀티 에이전트 상담**
   - 3개의 AI 에이전트가 서로 다른 관점에서 조언
   - 실시간 스트리밍 대화
   - RAG 기반 지식 검색

3. **추천 매물 및 추가 옵션**
   - 에이전트들이 추천하는 매물 정보
   - 검색 범위를 좁힐 수 있는 추가 옵션 제시

4. **상담 이력 관리**
   - 이전 상담 기록 저장 및 조회
   - 상담 결과 분석

## 설치 및 실행

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```
OPENAI_API_KEY=your_openai_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
API_BASE_URL=http://localhost:8001
```

### 3. 서버 실행
```bash
# 백엔드 서버 실행
cd server
uvicorn main:app --port=8001 --reload

# 프론트엔드 실행 (새 터미널)
cd app
streamlit run main.py
```

### 4. Docker 실행 (선택사항)
```bash
# Docker Compose로 전체 서비스 실행
docker-compose up --build
```

## API 엔드포인트

### 부동산 상담
- `POST /api/v1/workflow/real-estate/stream`: 부동산 상담 스트리밍

### 상담 이력
- `GET /api/v1/real-estate-consultations/`: 상담 목록 조회
- `POST /api/v1/real-estate-consultations/`: 상담 생성
- `GET /api/v1/real-estate-consultations/{id}`: 특정 상담 조회
- `DELETE /api/v1/real-estate-consultations/{id}`: 상담 삭제

### 매물 관리
- `GET /api/v1/properties/`: 매물 목록 조회
- `POST /api/v1/properties/`: 매물 생성

## 프로젝트 구조

```
├── app/                    # Streamlit 프론트엔드
│   ├── components/         # UI 컴포넌트
│   ├── utils/             # 유틸리티 함수
│   └── main.py            # 메인 애플리케이션
├── server/                # FastAPI 백엔드
│   ├── db/                # 데이터베이스 모델 및 스키마
│   ├── routers/           # API 라우터
│   ├── workflow/          # LangGraph 워크플로우
│   │   └── agents/        # AI 에이전트들
│   ├── retrieval/         # RAG 시스템
│   └── utils/             # 유틸리티 함수
└── requirements.txt       # Python 의존성
```

## 사용 예시

1. **매물 검색 시작**
   - 예산: "15억"
   - 매물 유형: "아파트"
   - 선호 조건1: "지하철역근처"
   - 선호 조건2: "조용하고 뷰가 좋은 곳"

2. **에이전트 상담 과정**
   - 이성적 조언자가 교통편의성과 재정적 안정성 관점에서 조언
   - 감성적 조언자가 뷰와 삶의 질 관점에서 조언
   - 중재자가 두 의견을 종합하여 최종 추천

3. **결과 확인**
   - 추천 매물 정보 확인
   - 추가 검색 옵션 선택
   - 상담 이력 저장

## 라이선스

MIT License