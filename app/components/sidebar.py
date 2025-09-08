import streamlit as st

from typing import Dict, Any

from components.history import render_history_ui


def render_input_form():
    with st.form("real_estate_form", border=False):
        st.subheader("🏠 부동산 매물 검색")
        
        # 예산 입력
        budget = st.text_input(
            label="예산 (예: 15억, 5천만원):",
            placeholder="15억",
            key="ui_budget",
        )
        
        # 매물 유형 선택
        property_type = st.selectbox(
            label="매물 유형:",
            options=["아파트", "빌라", "단독주택", "오피스텔", "원룸", "투룸"],
            key="ui_property_type",
        )
        
        # 선호 조건1 선택
        preference1 = st.selectbox(
            label="선호 조건1:",
            options=["지하철역근처", "학교근처", "병원근처", "터미널", "마트", "학원"],
            key="ui_preference1",
        )
        
        # 선호 조건2 자유 입력
        preference2 = st.text_input(
            label="선호 조건2 (자유 입력):",
            placeholder="예: 주변에 맛집이 많은 조용한 곳",
            key="ui_preference2",
        )

        max_rounds = st.slider("상담 라운드 수", min_value=1, max_value=3, value=1)
        st.session_state.max_rounds = max_rounds
        
        st.form_submit_button(
            "매물 검색 시작",
            on_click=lambda: st.session_state.update({"app_mode": "search"}),
        )
        
        # RAG 기능 활성화 옵션
        st.checkbox(
            "RAG 활성화",
            value=True,
            help="부동산 매물 데이터를 검색하여 추천에 활용합니다.",
            key="ui_enable_rag",
        )


def render_sidebar() -> Dict[str, Any]:
    with st.sidebar:

        tab1, tab2 = st.tabs(["새 검색", "검색 이력"])

        with tab1:
            render_input_form()

        with tab2:
            render_history_ui()
