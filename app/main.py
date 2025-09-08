import json
import os
from dotenv import load_dotenv
import requests
import streamlit as st
from components.history import save_consultation
from components.sidebar import render_sidebar
from utils.state_manager import init_session_state, reset_session_state


class AgentType:
    RATIONAL = "RATIONAL_AGENT"
    EMOTIONAL = "EMOTIONAL_AGENT"
    MEDIATOR = "MEDIATOR_AGENT"


def process_event_data(event_data):

    # 이벤트 종료
    if event_data.get("type") == "end":
        return True

    # 새로운 메세지
    if event_data.get("type") == "update":
        # state 추출
        data = event_data.get("data", {})

        role = data.get("role")
        response = data["response"]
        budget = data.get("budget", "")
        property_type = data.get("property_type", "")
        area_range = data.get("area_range", "")
        preference1 = data.get("preference1", "")
        preference2 = data.get("preference2", "")
        messages = data["messages"]
        current_round = data["current_round"]
        max_rounds = data["max_rounds"]
        docs = data.get("docs", {})
        recommended_properties = data.get("recommended_properties", [])
        additional_options = data.get("additional_options", [])

        if role == AgentType.RATIONAL:
            st.subheader(f"{current_round}/{max_rounds} 라운드")

        message = response

        if role == AgentType.RATIONAL:
            avatar = "🧠"
        elif role == AgentType.EMOTIONAL:
            avatar = "💝"
        elif role == AgentType.MEDIATOR:
            avatar = "⚖️"

        with st.chat_message(role, avatar=avatar):
            st.markdown(message)

        if role == AgentType.MEDIATOR:
            st.session_state.app_mode = "results"
            st.session_state.viewing_history = False
            st.session_state.messages = messages
            st.session_state.docs = docs
            st.session_state.recommended_properties = recommended_properties
            st.session_state.additional_options = additional_options

            # 완료된 상담 정보 저장
            save_consultation(
                budget,
                property_type,
                area_range,
                preference1,
                preference2,
                max_rounds,
                messages,
                docs,
                recommended_properties,
                additional_options,
            )

            # 참고 자료 표시
            if st.session_state.docs:
                render_source_materials()

            # 추천 매물 표시
            if st.session_state.recommended_properties:
                render_recommended_properties()

            # 추가 옵션 표시
            if st.session_state.additional_options:
                render_additional_options()

            if st.button("새 검색 시작"):
                reset_session_state()
                st.session_state.app_mode = "input"
                st.rerun()

    return False


def process_streaming_response(response):
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


def start_search():

    budget = st.session_state.ui_budget
    property_type = st.session_state.ui_property_type
    area_range = st.session_state.ui_area_range
    preference1 = st.session_state.ui_preference1
    preference2 = st.session_state.ui_preference2
    max_rounds = st.session_state.max_rounds

    enabled_rag = st.session_state.get("ui_enable_rag", False)

    with st.spinner("부동산 상담이 진행 중입니다... 완료까지 잠시 기다려주세요."):
        # API 요청 데이터
        data = {
            "budget": budget,
            "property_type": property_type,
            "area_range": area_range,
            "preference1": preference1,
            "preference2": preference2,
            "max_rounds": max_rounds,
            "enable_rag": enabled_rag,
        }

        # 포트 충돌 방지를 위해 환경변수 사용
        API_BASE_URL = os.getenv("API_BASE_URL")
        
        try:
            # 스트리밍 API 호출
            response = requests.post(
                f"{API_BASE_URL}/workflow/real-estate/stream",
                json=data,
                stream=True,
                headers={"Content-Type": "application/json"},
            )

            # stream=True로 설정하여 스트리밍 응답 처리
            # iter_lines() 또는 Iter_content()로 청크단위로 Read

            if response.status_code != 200:
                st.error(f"API 오류: {response.status_code} - {response.text}")
                return

            process_streaming_response(response)

        except requests.RequestException as e:
            st.error(f"API 요청 오류: {str(e)}")


# 참고 자료 표시
def render_source_materials():

    with st.expander("사용된 참고 자료 보기"):
        st.subheader("이성적 조언자 참고 자료")
        for i, doc in enumerate(st.session_state.docs.get(AgentType.RATIONAL, [])[:3]):
            st.markdown(f"**문서 {i+1}**")
            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
            st.divider()

        st.subheader("감성적 조언자 참고 자료")
        for i, doc in enumerate(st.session_state.docs.get(AgentType.EMOTIONAL, [])[:3]):
            st.markdown(f"**문서 {i+1}**")
            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
            st.divider()

        st.subheader("중재자 참고 자료")
        for i, doc in enumerate(st.session_state.docs.get(AgentType.MEDIATOR, [])[:3]):
            st.markdown(f"**문서 {i+1}**")
            st.text(doc[:300] + "..." if len(doc) > 300 else doc)
            st.divider()


# 추천 매물 표시
def render_recommended_properties():
    with st.expander("🏠 추천 매물 보기", expanded=True):
        properties = st.session_state.recommended_properties
        if properties:
            for i, property_info in enumerate(properties[:3]):
                st.markdown(f"**매물 {i+1}**")
                st.write(f"📍 위치: {property_info.get('location', 'N/A')}")
                st.write(f"💰 가격: {property_info.get('price', 'N/A')}")
                st.write(f"🏠 유형: {property_info.get('property_type', 'N/A')}")
                st.write(f"📐 면적: {property_info.get('area', 'N/A')}평")
                if property_info.get('description'):
                    st.write(f"📝 설명: {property_info['description']}")
                st.divider()
        else:
            st.info("추천 매물이 없습니다.")


# 추가 옵션 표시
def render_additional_options():
    with st.expander("🔍 추가 검색 옵션", expanded=True):
        options = st.session_state.additional_options
        if options:
            st.write("다음 조건 중 하나를 선택하여 검색 범위를 좁혀보세요:")
            for i, option in enumerate(options):
                if st.button(f"옵션 {i+1}: {option}", key=f"option_{i}"):
                    # 추가 옵션 선택 시 새로운 검색 시작
                    st.session_state.selected_option = option
                    st.session_state.app_mode = "search"
                    st.rerun()
        else:
            st.info("추가 옵션이 없습니다.")


def display_search_results():

    if st.session_state.viewing_history:
        st.info("📚 이전에 저장된 상담을 보고 있습니다.")
        budget = st.session_state.loaded_budget
        property_type = st.session_state.loaded_property_type
        area_range = st.session_state.loaded_area_range
    else:
        budget = st.session_state.ui_budget
        property_type = st.session_state.ui_property_type
        area_range = st.session_state.ui_area_range

    # 검색 조건 표시
    st.header(f"🏠 부동산 상담 결과")
    st.write(f"**예산:** {budget}")
    st.write(f"**매물 유형:** {property_type}")
    st.write(f"**평형대:** {area_range}")

    for message in st.session_state.messages:

        role = message["role"]
        if role not in [
            AgentType.RATIONAL,
            AgentType.EMOTIONAL,
            AgentType.MEDIATOR,
        ]:
            continue

        if message["role"] == AgentType.RATIONAL:
            avatar = "🧠"
        elif message["role"] == AgentType.EMOTIONAL:
            avatar = "💝"
        elif message["role"] == AgentType.MEDIATOR:
            avatar = "⚖️"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    if role == AgentType.MEDIATOR:
        st.session_state.search_active = True
        st.session_state.viewing_history = False

    # 참고 자료 표시
    if st.session_state.docs:
        render_source_materials()

    # 추천 매물 표시
    if hasattr(st.session_state, 'recommended_properties') and st.session_state.recommended_properties:
        render_recommended_properties()

    # 추가 옵션 표시
    if hasattr(st.session_state, 'additional_options') and st.session_state.additional_options:
        render_additional_options()

    if st.button("새 검색 시작"):
        reset_session_state()
        st.session_state.app_mode = "input"
        st.rerun()


def render_ui():
    # 페이지 설정
    st.set_page_config(page_title="AI 부동산 중개", page_icon="🏠")

    # 제목 및 소개
    st.title("🏠 AI 부동산 중개 - 멀티 에이전트")
    st.markdown(
        """
        ### 프로젝트 소개
        이 애플리케이션은 3개의 AI 에이전트(이성적 조언자, 감성적 조언자, 중재자)가 사용자의 부동산 매물 검색을 도와줍니다.
        각 AI는 서로의 의견을 듣고 토론하며, 최종적으로 사용자에게 최적의 매물을 추천합니다.
        """
    )

    render_sidebar()

    current_mode = st.session_state.app_mode

    if current_mode == "search":
        start_search()
    elif current_mode == "results":
        display_search_results()


if __name__ == "__main__":

    load_dotenv()

    # 세션 상태 초기화
    init_session_state()

    render_ui()
