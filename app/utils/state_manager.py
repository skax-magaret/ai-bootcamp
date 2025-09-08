import streamlit as st


def init_session_state():
    """세션 상태 초기화"""
    
    # 애플리케이션 모드 설정
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "input"  # input, consultation, results
    
    # 상담 관련 상태
    if "patient_query" not in st.session_state:
        st.session_state.patient_query = ""
    
    if "patient_info" not in st.session_state:
        st.session_state.patient_info = {}
    
    if "consultation_type" not in st.session_state:
        st.session_state.consultation_type = "일반"
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "docs" not in st.session_state:
        st.session_state.docs = {}
    
    if "current_turn" not in st.session_state:
        st.session_state.current_turn = 0
    
    if "max_turns" not in st.session_state:
        st.session_state.max_turns = 6
    
    # UI 설정
    if "ui_enable_rag" not in st.session_state:
        st.session_state.ui_enable_rag = True
    
    # 히스토리 관련
    if "viewing_history" not in st.session_state:
        st.session_state.viewing_history = False
    
    if "loaded_query" not in st.session_state:
        st.session_state.loaded_query = ""
    
    # 환자 정보 관련
    if "patient_age" not in st.session_state:
        st.session_state.patient_age = "50"
    
    if "patient_occupation" not in st.session_state:
        st.session_state.patient_occupation = "사무직"
    
    if "patient_family" not in st.session_state:
        st.session_state.patient_family = "배우자와 자녀 2명"
    
    if "post_surgery_period" not in st.session_state:
        st.session_state.post_surgery_period = "수술 예정"
    
    if "patient_symptoms" not in st.session_state:
        st.session_state.patient_symptoms = "허리 통증"


def reset_session_state():
    """세션 상태 초기화 (상담 관련 데이터만)"""
    
    consultation_keys = [
        "patient_query", "patient_info", "consultation_type", 
        "messages", "docs", "current_turn", "viewing_history",
        "loaded_query", "patient_age", "patient_occupation",
        "patient_family", "post_surgery_period", "patient_symptoms"
    ]
    
    for key in consultation_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # 기본값으로 재설정
    st.session_state.app_mode = "input"
    st.session_state.patient_query = ""
    st.session_state.patient_info = {}
    st.session_state.consultation_type = "일반"
    st.session_state.messages = []
    st.session_state.docs = {}
    st.session_state.current_turn = 0
    st.session_state.viewing_history = False
    st.session_state.loaded_query = ""
    
    # 환자 정보 기본값
    st.session_state.patient_age = "50"
    st.session_state.patient_occupation = "사무직"
    st.session_state.patient_family = "배우자와 자녀 2명"
    st.session_state.post_surgery_period = "수술 예정"
    st.session_state.patient_symptoms = "허리 통증"


def get_consultation_state():
    """현재 상담 상태 반환"""
    
    return {
        "patient_query": st.session_state.get("patient_query", ""),
        "patient_info": {
            "age": st.session_state.get("patient_age", "50"),
            "occupation": st.session_state.get("patient_occupation", "사무직"),
            "family": st.session_state.get("patient_family", "배우자와 자녀 2명"),
            "post_surgery_period": st.session_state.get("post_surgery_period", "수술 예정"),
            "symptoms": st.session_state.get("patient_symptoms", "허리 통증")
        },
        "consultation_type": st.session_state.get("consultation_type", "일반"),
        "messages": st.session_state.get("messages", []),
        "docs": st.session_state.get("docs", {}),
        "current_turn": st.session_state.get("current_turn", 0),
        "max_turns": st.session_state.get("max_turns", 6),
        "is_completed": False,
        "summary": ""
    }


def update_consultation_state(new_state):
    """상담 상태 업데이트"""
    
    st.session_state.messages = new_state.get("messages", [])
    st.session_state.docs = new_state.get("docs", {})
    st.session_state.current_turn = new_state.get("current_turn", 0)
    
    # 상담 완료 여부 확인
    if new_state.get("is_completed", False):
        st.session_state.app_mode = "results"
