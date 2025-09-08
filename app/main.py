import json
import os
from dotenv import load_dotenv
import requests
import streamlit as st
from components.history import save_consultation
from components.sidebar import render_sidebar
from utils.state_manager import init_session_state, reset_session_state


class AgentType:
    DOCTOR = "DOCTOR_AGENT"
    PATIENT = "PATIENT_AGENT"
    COORDINATOR = "COORDINATOR_AGENT"


def process_event_data(event_data):
    """이벤트 데이터 처리"""
    
    # 이벤트 종료
    if event_data.get("type") == "end":
        return True

    # 새로운 메시지
    if event_data.get("type") == "update":
        # state 추출
        data = event_data.get("data", {})

        role = data.get("role")
        response = data["response"]
        patient_query = data["patient_query"]
        messages = data["messages"]
        current_turn = data["current_turn"]
        max_turns = data["max_turns"]
        docs = data.get("docs", {})

        if role == AgentType.DOCTOR:
            st.subheader(f"{current_turn}/{max_turns} 상담 턴")

        message = response

        # 아바타 설정
        if role == AgentType.DOCTOR:
            avatar = "👨‍⚕️"
        elif role == AgentType.PATIENT:
            avatar = "🤒"
        elif role == AgentType.COORDINATOR:
            avatar = "👩‍💼"

        with st.chat_message(role, avatar=avatar):
            st.markdown(message)

        # 상담 조정자의 응답이면 상담 완료
        if role == AgentType.COORDINATOR:
            st.session_state.app_mode = "results"
            st.session_state.viewing_history = False
            st.session_state.messages = messages
            st.session_state.docs = docs

            # 완료된 상담 정보 저장
            save_consultation(
                patient_query,
                data.get("consultation_type", "일반"),
                data.get("patient_info", {}),
                messages,
                docs,
            )

            # 참고 자료 표시
            if st.session_state.docs:
                render_source_materials()

            if st.button("새 상담 시작"):
                reset_session_state()
                st.session_state.app_mode = "input"
                st.rerun()

    return False


def process_streaming_response(response):
    """스트리밍 응답 처리"""
    for chunk in response.iter_lines():
        if not chunk:
            continue

        # 'data: ' 접두사 제거
        line = chunk.decode("utf-8")

        # line의 형태는 'data: {"type": "update", "data": {}}'
        if not line.startswith("data: "):
            continue

        data_str = line[6:]  # 'data: ' 부분 제거

        try:
            # JSON 데이터 파싱
            event_data = json.loads(data_str)

            # 이벤트 데이터 처리
            is_complete = process_event_data(event_data)

            if is_complete:
                break

        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류: {e}")


def start_consultation():
    """상담 시작"""
    
    patient_query = st.session_state.patient_query
    patient_info = {
        "age": st.session_state.get("patient_age", "50"),
        "occupation": st.session_state.get("patient_occupation", "사무직"),
        "family": st.session_state.get("patient_family", "배우자와 자녀 2명"),
        "post_surgery_period": st.session_state.get("post_surgery_period", "수술 예정"),
        "symptoms": st.session_state.get("patient_symptoms", "허리 통증")
    }
    consultation_type = st.session_state.get("consultation_type", "일반")
    max_turns = st.session_state.get("max_turns", 6)
    enabled_rag = st.session_state.get("ui_enable_rag", True)

    with st.spinner("상담이 진행 중입니다... 완료까지 잠시 기다려주세요."):
        # API 요청 데이터
        data = {
            "patient_query": patient_query,
            "patient_info": patient_info,
            "consultation_type": consultation_type,
            "max_turns": max_turns,
            "enable_rag": enabled_rag,
        }

        # 포트 충돌 방지를 위해 환경변수 사용
        API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
        
        try:
            # 스트리밍 API 호출
            response = requests.post(
                f"{API_BASE_URL}/workflow/consultation/stream",
                json=data,
                stream=True,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                st.error(f"API 오류: {response.status_code} - {response.text}")
                return

            process_streaming_response(response)

        except requests.RequestException as e:
            st.error(f"API 요청 오류: {str(e)}")


def render_source_materials():
    """참고 자료 표시"""
    
    with st.expander("사용된 참고 자료 보기"):
        st.subheader("의사 참고 자료")
        for i, doc in enumerate(st.session_state.docs.get(AgentType.DOCTOR, [])[:3]):
            st.markdown(f"**문서 {i+1}**")
            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
            st.divider()

        st.subheader("환자 참고 자료")
        for i, doc in enumerate(st.session_state.docs.get(AgentType.PATIENT, [])[:3]):
            st.markdown(f"**문서 {i+1}**")
            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
            st.divider()

        st.subheader("조정자 참고 자료")
        for i, doc in enumerate(st.session_state.docs.get(AgentType.COORDINATOR, [])[:3]):
            st.markdown(f"**문서 {i+1}**")
            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
            st.divider()


def display_consultation_results():
    """상담 결과 표시"""
    
    if st.session_state.viewing_history:
        st.info("📚 이전에 저장된 상담을 보고 있습니다.")
        patient_query = st.session_state.loaded_query
    else:
        patient_query = st.session_state.patient_query

    # 상담 주제 표시
    st.header(f"🩺 환자 질문: {patient_query}")

    for message in st.session_state.messages:
        role = message["role"]
        if role not in [
            AgentType.DOCTOR,
            AgentType.PATIENT,
            AgentType.COORDINATOR,
        ]:
            continue

        # 아바타 설정
        if message["role"] == AgentType.DOCTOR:
            avatar = "👨‍⚕️"
        elif message["role"] == AgentType.PATIENT:
            avatar = "🤒"
        elif message["role"] == AgentType.COORDINATOR:
            avatar = "👩‍💼"
            
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # 참고 자료 표시
    if st.session_state.docs:
        render_source_materials()

    if st.button("새 상담 시작"):
        reset_session_state()
        st.session_state.app_mode = "input"
        st.rerun()


def render_consultation_input():
    """상담 입력 폼"""
    
    st.header("🏥 척추 유합술 상담 시스템")
    
    with st.form("consultation_form"):
        st.subheader("환자 정보")
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_age = st.number_input("나이", min_value=20, max_value=100, value=50)
            patient_occupation = st.selectbox("직업", ["사무직", "육체노동", "주부", "학생", "기타"])
            consultation_type = st.selectbox(
                "상담 유형", 
                ["수술_전", "수술_후", "재활", "합병증", "일반"]
            )
        
        with col2:
            post_surgery_period = st.selectbox(
                "수술 후 기간",
                ["수술 예정", "수술 후 1주", "수술 후 1개월", "수술 후 3개월", "수술 후 6개월", "수술 후 1년 이상"]
            )
            patient_symptoms = st.text_input("주요 증상", value="허리 통증")
            max_turns = st.number_input("최대 상담 턴 수", min_value=2, max_value=10, value=6)
        
        patient_family = st.text_input("가족 상황", value="배우자와 자녀 2명")
        patient_query = st.text_area(
            "질문 또는 상담 내용",
            placeholder="예: 수술 후 언제부터 일상생활이 가능한가요?",
            height=100
        )
        
        enable_rag = st.checkbox("RAG 기반 지식 검색 사용", value=True)
        
        submitted = st.form_submit_button("상담 시작")
        
        if submitted:
            if not patient_query.strip():
                st.error("질문 또는 상담 내용을 입력해주세요.")
                return
            
            # 세션 상태 업데이트
            st.session_state.patient_query = patient_query
            st.session_state.patient_age = str(patient_age)
            st.session_state.patient_occupation = patient_occupation
            st.session_state.patient_family = patient_family
            st.session_state.post_surgery_period = post_surgery_period
            st.session_state.patient_symptoms = patient_symptoms
            st.session_state.consultation_type = consultation_type
            st.session_state.max_turns = max_turns
            st.session_state.ui_enable_rag = enable_rag
            st.session_state.app_mode = "consultation"
            
            st.rerun()


def render_ui():
    """메인 UI 렌더링"""
    
    # 페이지 설정
    st.set_page_config(page_title="척추 유합술 AI 상담", page_icon="🏥")

    # 제목 및 소개
    st.title("🏥 척추 유합술 AI 상담 시스템")
    st.markdown(
        """
        ### 프로젝트 소개
        이 애플리케이션은 척추 유합술 전문의와 환자 간의 상담을 시뮬레이션하는 AI 시스템입니다.
        - **의사 AI**: 의학적 전문 지식을 바탕으로 정확한 정보와 조언 제공
        - **환자 AI**: 실제 환자의 관점에서 자연스러운 질문과 우려사항 표현
        - **상담 조정자**: 상담 내용을 정리하고 종합적인 요약 제공
        
        ### 주요 기능
        - 🔍 **RAG 기반 지식 검색**: 척추 유합술 전문 자료를 활용한 정확한 정보 제공
        - 💬 **자연스러운 대화**: Chain-of-Thought와 Few-shot Learning을 활용한 최적화된 프롬프트
        - 📊 **상담 요약**: 상담 내용의 핵심 포인트와 실행 사항 정리
        - 📚 **상담 기록**: 이전 상담 내용 저장 및 조회 기능
        """
    )

    render_sidebar()

    current_mode = st.session_state.app_mode

    if current_mode == "input":
        render_consultation_input()
    elif current_mode == "consultation":
        start_consultation()
    elif current_mode == "results":
        display_consultation_results()


if __name__ == "__main__":
    load_dotenv()

    # 세션 상태 초기화
    init_session_state()

    render_ui()
