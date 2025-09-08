import streamlit as st
from components.history import (
    render_consultation_history, 
    render_consultation_statistics,
    export_consultation_history
)


def render_sidebar():
    """사이드바 렌더링"""
    
    with st.sidebar:
        st.title("🏥 상담 관리")
        
        # 상담 설정 섹션
        with st.expander("⚙️ 상담 설정", expanded=False):
            st.subheader("기본 설정")
            
            # RAG 설정
            st.session_state.ui_enable_rag = st.checkbox(
                "RAG 기반 지식 검색 사용", 
                value=st.session_state.get("ui_enable_rag", True),
                help="척추 유합술 전문 자료를 활용한 정확한 정보 제공"
            )
            
            # 상담 턴 수 설정
            max_turns = st.slider(
                "최대 상담 턴 수", 
                min_value=2, 
                max_value=10, 
                value=st.session_state.get("max_turns", 6),
                help="의사와 환자 간 대화 횟수 제한"
            )
            st.session_state.max_turns = max_turns
            
            st.divider()
            
            # 환자 정보 미리보기
            if hasattr(st.session_state, 'patient_query') and st.session_state.patient_query:
                st.subheader("현재 상담 정보")
                st.write(f"**질문:** {st.session_state.patient_query[:50]}...")
                st.write(f"**상담 유형:** {st.session_state.get('consultation_type', '일반')}")
                st.write(f"**환자 나이:** {st.session_state.get('patient_age', '50')}세")
        
        st.divider()
        
        # 상담 기록 관리
        with st.expander("📚 상담 기록 관리", expanded=True):
            render_consultation_history()
            
            st.divider()
            
            # 내보내기 기능
            export_consultation_history()
        
        st.divider()
        
        # 상담 통계
        with st.expander("📊 상담 통계", expanded=False):
            render_consultation_statistics()
        
        st.divider()
        
        # 시스템 정보
        with st.expander("ℹ️ 시스템 정보", expanded=False):
            st.subheader("기술 스택")
            st.markdown("""
            - **LangChain & LangGraph**: Multi-Agent 시스템
            - **FAISS**: 벡터 데이터베이스
            - **OpenAI GPT**: 대화형 AI 모델
            - **Streamlit**: 웹 인터페이스
            - **FastAPI**: 백엔드 API
            - **SQLite**: 상담 기록 저장
            """)
            
            st.subheader("주요 기능")
            st.markdown("""
            - 🩺 **의사 AI**: 전문의 수준의 의학 상담
            - 🤒 **환자 AI**: 실제 환자 관점의 질문
            - 👩‍💼 **상담 조정자**: 체계적인 상담 요약
            - 🔍 **RAG 시스템**: 전문 의학 자료 검색
            - 💬 **Chain-of-Thought**: 단계별 사고 과정
            - 📝 **Few-shot Learning**: 예시 기반 학습
            """)
        
        # 새 상담 시작 버튼
        if st.session_state.get("app_mode") != "input":
            st.divider()
            if st.button("🆕 새 상담 시작", use_container_width=True, type="primary"):
                # 상담 관련 세션 상태 초기화
                consultation_keys = [
                    'patient_query', 'patient_age', 'patient_occupation', 
                    'patient_family', 'post_surgery_period', 'patient_symptoms',
                    'consultation_type', 'messages', 'docs', 'viewing_history'
                ]
                
                for key in consultation_keys:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.session_state.app_mode = "input"
                st.rerun()
        
        # 현재 모드 표시
        current_mode = st.session_state.get("app_mode", "input")
        mode_display = {
            "input": "📝 상담 정보 입력",
            "consultation": "💬 상담 진행 중",
            "results": "📋 상담 결과"
        }
        
        st.divider()
        st.caption(f"현재 모드: {mode_display.get(current_mode, current_mode)}")
        
        # 개발 정보
        st.caption("---")
        st.caption("🏥 척추 유합술 AI 상담 시스템")
        st.caption("Multi-Agent RAG System")
        st.caption("Built with LangChain & LangGraph")
