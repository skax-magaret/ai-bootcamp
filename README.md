# 🏥 척추 유합술 AI 상담 시스템

LangChain & LangGraph 기반 Multi-Agent 척추 유합술 전문 상담 시스템

## 📋 프로젝트 개요

이 프로젝트는 척추 유합술 환자를 위한 AI 기반 상담 시스템입니다. 전문의, 환자, 상담 조정자의 3개 AI 에이전트가 협력하여 실제와 같은 의료 상담을 제공합니다.

### 🎯 주요 특징

- **🩺 전문의 AI**: 의학적 전문 지식을 바탕으로 정확한 정보와 조언 제공
- **🤒 환자 AI**: 실제 환자의 관점에서 자연스러운 질문과 우려사항 표현
- **👩‍💼 상담 조정자**: 상담 내용을 정리하고 종합적인 요약 제공
- **🔍 RAG 시스템**: 척추 유합술 전문 자료를 활용한 정확한 정보 검색
- **💬 최적화된 프롬프트**: Chain-of-Thought와 Few-shot Learning 활용

## 🛠 기술 스택

### Backend
- **LangChain & LangGraph**: Multi-Agent 시스템 구현
- **FastAPI**: RESTful API 서버
- **SQLite**: 상담 기록 저장
- **FAISS**: 벡터 데이터베이스 (RAG)
- **OpenAI GPT**: 대화형 AI 모델

### Frontend
- **Streamlit**: 웹 인터페이스
- **Python**: 백엔드 로직

### 기타
- **Docker**: 배포 환경 (선택사항)
- **Langfuse**: 대화 추적 및 모니터링

## 📁 프로젝트 구조

```
homework/
├── app/                          # Streamlit 프론트엔드
│   ├── main.py                   # 메인 UI 애플리케이션
│   ├── components/               # UI 컴포넌트
│   │   ├── history.py           # 상담 기록 관리
│   │   └── sidebar.py           # 사이드바 UI
│   └── utils/
│       └── state_manager.py     # 세션 상태 관리
├── server/                       # FastAPI 백엔드
│   ├── main.py                  # FastAPI 서버
│   ├── workflow/                # Multi-Agent 워크플로우
│   │   ├── consultation_graph.py # 상담 그래프
│   │   ├── state.py             # 상담 상태 정의
│   │   └── agents/              # AI 에이전트들
│   │       ├── doctor_agent.py  # 의사 에이전트
│   │       ├── patient_agent.py # 환자 에이전트
│   │       └── coordinator_agent.py # 조정자 에이전트
│   ├── retrieval/               # RAG 시스템
│   │   └── vector_store.py      # 벡터 스토어 관리
│   ├── routers/                 # API 라우터
│   │   └── consultation.py      # 상담 API
│   └── db/                      # 데이터베이스
│       ├── models.py            # 데이터 모델
│       └── database.py          # DB 연결
├── data/                        # 데이터 파일
│   ├── 척추 유합술 환자를 위한 상세 지침서.pdf
│   └── spinal_fusion_content.txt # 처리된 텍스트 데이터
└── requirements.txt             # 의존성 목록
```

## 🚀 설치 및 실행

### 1. 저장소 클론
```bash
git clone <repository-url>
cd homework
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
`.env` 파일을 생성하고 다음 내용을 추가:
```env
OPENAI_API_KEY=your_openai_api_key_here
API_BASE_URL=http://localhost:8000
LANGFUSE_SECRET_KEY=your_langfuse_key_here  # 선택사항
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here  # 선택사항
```

### 5. 백엔드 서버 실행
```bash
cd server
python main.py
```
또는
```bash
cd server
uvicorn main:app --reload --port 8000
```

### 6. 프론트엔드 실행 (새 터미널)
```bash
cd app
streamlit run main.py
```

## 💻 사용 방법

### 1. 상담 시작
- 웹 인터페이스에서 환자 정보 입력
- 상담 유형 선택 (수술 전/후, 재활, 합병증, 일반)
- 질문 또는 상담 내용 작성

### 2. 상담 진행
- 의사 AI가 전문적인 답변 제공
- 환자 AI가 자연스러운 추가 질문
- 대화가 자동으로 진행됨

### 3. 상담 완료
- 상담 조정자가 종합 요약 제공
- 실행 사항 및 주의사항 정리
- 상담 기록 자동 저장

### 4. 기록 관리
- 사이드바에서 이전 상담 기록 조회
- 상담 통계 확인
- JSON 형태로 내보내기 가능

## 🔧 주요 기능

### 1. Prompt Engineering
- **Chain-of-Thought**: 단계별 사고 과정을 통한 논리적 답변
- **Few-shot Learning**: 상담 유형별 예시를 활용한 자연스러운 대화
- **Role-based Prompting**: 의사, 환자, 조정자 역할에 맞는 최적화된 프롬프트

### 2. Multi-Agent System
- **의사 에이전트**: 의학적 전문성과 환자 중심적 소통
- **환자 에이전트**: 실제 환자의 우려와 질문을 자연스럽게 표현
- **조정자 에이전트**: 상담 내용 정리 및 체계적 요약

### 3. RAG (Retrieval-Augmented Generation)
- **FAISS 벡터 스토어**: 척추 유합술 전문 자료 검색
- **상담 유형별 검색**: 수술 전/후, 재활 등에 맞는 정보 제공
- **실시간 정보 검색**: 질문에 따른 관련 의학 정보 자동 검색

### 4. 메모리 및 상태 관리
- **멀티턴 대화**: 이전 대화 내용을 기억하는 연속적 상담
- **상담 상태 추적**: 현재 진행 상황과 완료 여부 관리
- **세션 관리**: 사용자별 상담 세션 유지

## 📊 API 엔드포인트

### 상담 관련
- `POST /api/v1/consultation/stream` - 스트리밍 상담 시작
- `POST /api/v1/consultation/` - 일반 상담 실행
- `GET /api/v1/consultation/health` - 상담 시스템 상태 확인
- `GET /api/v1/consultation/types` - 상담 유형 목록

### 시스템
- `GET /` - 시스템 정보
- `GET /health` - 전체 헬스체크

## 🧪 테스트

### 단위 테스트 실행
```bash
pytest tests/
```

### 통합 테스트
```bash
python -m pytest tests/integration/
```

### API 테스트
```bash
# 상담 시스템 헬스체크
curl http://localhost:8000/api/v1/consultation/health

# 상담 유형 조회
curl http://localhost:8000/api/v1/consultation/types
```

## 🐳 Docker 배포 (선택사항)

### Dockerfile 생성
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "server/main.py"]
```

### Docker 실행
```bash
docker build -t spinal-fusion-ai .
docker run -p 8000:8000 -p 8501:8501 spinal-fusion-ai
```

## 📈 모니터링

### Langfuse 연동 (선택사항)
- 대화 품질 추적
- 에이전트 성능 모니터링
- 사용자 피드백 수집

## 🔒 보안 고려사항

- API 키 환경변수 관리
- 의료 정보 보호를 위한 데이터 암호화
- 세션 보안 및 사용자 인증 (필요시 구현)

## 🤝 기여 방법

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

This project is licensed under the MIT License.

## 📞 문의

프로젝트 관련 문의사항은 이슈를 통해 남겨주세요.

## 🔄 업데이트 로그

### v2.0.0 (Current)
- 척추 유합술 전문 상담 시스템으로 전환
- Multi-Agent 아키텍처 구현
- RAG 기반 지식 검색 시스템 추가
- Chain-of-Thought 프롬프트 최적화

### v1.0.0 (Legacy)
- 기본 토론 시스템 구현 