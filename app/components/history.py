import os
import streamlit as st
import requests
import json
from utils.state_manager import reset_session_state

# 포트 충돌 방지를 위해 환경변수 사용
API_BASE_URL = os.getenv("API_BASE_URL")
st.w

# API로 부동산 상담 이력 조회
def fetch_consultation_history():
    """API를 통해 부동산 상담 이력 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/real-estate-consultations/")
        if response.status_code == 200:
            consultations = response.json()
            # API 응답 형식에 맞게 데이터 변환 (id, budget, property_type, area_range, date, rounds)
            return [
                (consultation["id"], consultation["budget"], consultation["property_type"], 
                 consultation["area_range"], consultation["created_at"], consultation["rounds"])
                for consultation in consultations
            ]
        else:
            st.error(f"상담 이력 조회 실패: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"fetch_consultation_history : API 호출 오류: {str(e)}")
        return []


# API로 특정 상담 데이터 조회
def fetch_consultation_by_id(consultation_id):
    """API를 통해 특정 상담 데이터 가져오기"""
    try:
        response = requests.get(f"{API_BASE_URL}/real-estate-consultations/{consultation_id}")
        if response.status_code == 200:
            consultation = response.json()
            budget = consultation["budget"]
            property_type = consultation["property_type"]
            area_range = consultation["area_range"]
            # 실제 API 응답 구조에 맞게 변환 필요
            messages = (
                json.loads(consultation["messages"])
                if isinstance(consultation["messages"], str)
                else consultation["messages"]
            )
            docs = (
                json.loads(consultation["docs"])
                if isinstance(consultation["docs"], str)
                else consultation.get("docs", {})
            )
            recommended_properties = (
                json.loads(consultation["recommended_properties"])
                if isinstance(consultation.get("recommended_properties"), str)
                else consultation.get("recommended_properties", [])
            )
            additional_options = (
                json.loads(consultation["additional_options"])
                if isinstance(consultation.get("additional_options"), str)
                else consultation.get("additional_options", [])
            )
            return budget, property_type, area_range, messages, docs, recommended_properties, additional_options
        else:
            st.error(f"상담 데이터 조회 실패: {response.status_code}")
            return None, None, None, None, None, None, None
    except Exception as e:
        st.error(f"fetch_consultation_by_id : API 호출 오류: {str(e)}")
        return None, None, None, None, None, None, None


# API로 상담 삭제
def delete_consultation_by_id(consultation_id):
    """API를 통해 특정 상담 삭제"""
    try:
        response = requests.delete(f"{API_BASE_URL}/real-estate-consultations/{consultation_id}")
        if response.status_code == 200:
            st.success("상담이 삭제되었습니다.")
            return True
        else:
            st.error(f"상담 삭제 실패: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"delete_consultation_by_id : API 호출 오류: {str(e)}")
        return False


# API로 모든 상담 삭제
def delete_all_consultations():
    """API를 통해 모든 상담 삭제"""
    try:
        # 모든 상담 목록 조회
        consultations = fetch_consultation_history()
        if not consultations:
            return True

        # 각 상담 항목 삭제
        success = True
        for consultation_id, _, _, _, _ in consultations:
            response = requests.delete(f"{API_BASE_URL}/real-estate-consultations/{consultation_id}")
            if response.status_code != 200:
                success = False

        if success:
            st.success("모든 상담이 삭제되었습니다.")
        return success
    except Exception as e:
        st.error(f"delete_all_consultations : API 호출 오류: {str(e)}")
        return False


# API로 상담 저장
def save_consultation(budget, property_type, area_range, preference1, preference2, rounds, messages, docs=None, recommended_properties=None, additional_options=None):
    """API를 통해 상담 결과를 데이터베이스에 저장"""
    try:
        # API 요청 데이터 준비
        consultation_data = {
            "budget": budget,
            "property_type": property_type,
            "area_range": area_range,
            "preference1": preference1,
            "preference2": preference2,
            "rounds": rounds,
            "messages": (
                json.dumps(messages) if not isinstance(messages, str) else messages
            ),
            "docs": (
                json.dumps(docs)
                if docs and not isinstance(docs, str)
                else (docs or "{}")
            ),
            "recommended_properties": (
                json.dumps(recommended_properties)
                if recommended_properties and not isinstance(recommended_properties, str)
                else (recommended_properties or "[]")
            ),
            "additional_options": (
                json.dumps(additional_options)
                if additional_options and not isinstance(additional_options, str)
                else (additional_options or "[]")
            ),
        }

        response = requests.post(f"{API_BASE_URL}/real-estate-consultations/", json=consultation_data)

        if response.status_code == 200 or response.status_code == 201:
            st.success("상담이 성공적으로 저장되었습니다.")
            return response.json().get("id")  # 저장된 상담 ID 반환
        else:
            st.error(f"상담 저장 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"save_consultation : API 호출 오류: {str(e)}")
        return None


# 상담 이력 UI 렌더링
def render_history_ui():

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("이력 새로고침", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("전체 이력 삭제", type="primary", use_container_width=True):
            if delete_all_consultations():
                st.rerun()

    # 상담 이력 로드
    consultation_history = fetch_consultation_history()

    if not consultation_history:
        st.info("저장된 상담 이력이 없습니다.")
    else:
        render_history_list(consultation_history)


# 상담 이력 목록 렌더링
def render_history_list(consultation_history):
    for id, budget, property_type, area_range, date, rounds in consultation_history:
        with st.container(border=True):

            # 상담 정보
            st.write(f"***{budget} | {property_type} | {area_range}***")

            col1, col2, col3 = st.columns([3, 1, 1])
            # 상담 정보
            with col1:
                st.caption(f"날짜: {date} | 라운드: {rounds}")

            # 보기 버튼
            with col2:
                if st.button("보기", key=f"view_{id}", use_container_width=True):
                    budget, property_type, area_range, messages, docs, recommended_properties, additional_options = fetch_consultation_by_id(id)
                    if budget and messages:
                        st.session_state.viewing_history = True
                        st.session_state.messages = messages
                        st.session_state.loaded_budget = budget
                        st.session_state.loaded_property_type = property_type
                        st.session_state.loaded_area_range = area_range
                        st.session_state.loaded_consultation_id = id
                        st.session_state.docs = docs
                        st.session_state.recommended_properties = recommended_properties
                        st.session_state.additional_options = additional_options
                        st.session_state.app_mode = "results"
                        st.rerun()

            # 삭제 버튼
            with col3:
                if st.button("삭제", key=f"del_{id}", use_container_width=True):
                    if delete_consultation_by_id(id):
                        reset_session_state()
                        st.rerun()
