import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import streamlit as st


def get_db_connection():
    """데이터베이스 연결 생성"""
    db_path = Path("server/history.db")
    conn = sqlite3.connect(str(db_path))
    return conn


def init_consultation_db():
    """상담 기록 데이터베이스 초기화"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 상담 기록 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consultations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_query TEXT NOT NULL,
            consultation_type TEXT NOT NULL,
            patient_info TEXT NOT NULL,
            messages TEXT NOT NULL,
            docs TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def save_consultation(
    patient_query: str,
    consultation_type: str,
    patient_info: Dict[str, Any],
    messages: List[Dict[str, Any]],
    docs: Dict[str, List[str]],
):
    """상담 기록 저장"""
    try:
        init_consultation_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO consultations (patient_query, consultation_type, patient_info, messages, docs)
            VALUES (?, ?, ?, ?, ?)
        """, (
            patient_query,
            consultation_type,
            json.dumps(patient_info, ensure_ascii=False),
            json.dumps(messages, ensure_ascii=False),
            json.dumps(docs, ensure_ascii=False)
        ))
        
        conn.commit()
        conn.close()
        
        st.success("✅ 상담 기록이 저장되었습니다!")
        
    except Exception as e:
        st.error(f"❌ 상담 저장 중 오류가 발생했습니다: {str(e)}")


def load_consultation_history() -> List[Dict[str, Any]]:
    """상담 기록 목록 조회"""
    try:
        init_consultation_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, patient_query, consultation_type, patient_info, messages, docs, created_at
            FROM consultations
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        consultations = []
        for row in rows:
            consultation = {
                "id": row[0],
                "patient_query": row[1],
                "consultation_type": row[2],
                "patient_info": json.loads(row[3]) if row[3] else {},
                "messages": json.loads(row[4]) if row[4] else [],
                "docs": json.loads(row[5]) if row[5] else {},
                "created_at": row[6]
            }
            consultations.append(consultation)
        
        return consultations
        
    except Exception as e:
        st.error(f"❌ 상담 기록 조회 중 오류가 발생했습니다: {str(e)}")
        return []


def delete_consultation(consultation_id: int):
    """특정 상담 기록 삭제"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM consultations WHERE id = ?", (consultation_id,))
        
        conn.commit()
        conn.close()
        
        st.success("✅ 상담 기록이 삭제되었습니다!")
        
    except Exception as e:
        st.error(f"❌ 상담 삭제 중 오류가 발생했습니다: {str(e)}")


def render_consultation_history():
    """상담 기록 목록 렌더링"""
    st.subheader("📚 상담 기록")
    
    consultations = load_consultation_history()
    
    if not consultations:
        st.info("저장된 상담 기록이 없습니다.")
        return
    
    for consultation in consultations:
        with st.expander(
            f"🩺 {consultation['patient_query'][:50]}{'...' if len(consultation['patient_query']) > 50 else ''} "
            f"({consultation['created_at'][:16]})"
        ):
            st.markdown(f"**상담 유형:** {consultation['consultation_type']}")
            
            # 환자 정보 표시
            patient_info = consultation['patient_info']
            st.markdown(f"**환자 정보:** {patient_info.get('age', 'N/A')}세, {patient_info.get('occupation', 'N/A')}")
            st.markdown(f"**수술 후 기간:** {patient_info.get('post_surgery_period', 'N/A')}")
            
            # 메시지 개수 표시
            message_count = len(consultation['messages'])
            st.markdown(f"**대화 수:** {message_count}개")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button(f"상담 보기", key=f"view_{consultation['id']}"):
                    # 상담 내용을 세션 상태에 로드
                    st.session_state.messages = consultation['messages']
                    st.session_state.docs = consultation['docs']
                    st.session_state.loaded_query = consultation['patient_query']
                    st.session_state.viewing_history = True
                    st.session_state.app_mode = "results"
                    st.rerun()
            
            with col2:
                if st.button(f"삭제", key=f"delete_{consultation['id']}", type="secondary"):
                    delete_consultation(consultation['id'])
                    st.rerun()


def export_consultation_history():
    """상담 기록을 JSON 파일로 내보내기"""
    consultations = load_consultation_history()
    
    if not consultations:
        st.warning("내보낼 상담 기록이 없습니다.")
        return
    
    # JSON 파일 생성
    export_data = {
        "export_date": datetime.now().isoformat(),
        "consultations": consultations
    }
    
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    
    st.download_button(
        label="📥 상담 기록 내보내기 (JSON)",
        data=json_str,
        file_name=f"consultation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def get_consultation_statistics():
    """상담 통계 정보 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 전체 상담 수
        cursor.execute("SELECT COUNT(*) FROM consultations")
        total_consultations = cursor.fetchone()[0]
        
        # 상담 유형별 통계
        cursor.execute("""
            SELECT consultation_type, COUNT(*) as count
            FROM consultations
            GROUP BY consultation_type
            ORDER BY count DESC
        """)
        type_stats = cursor.fetchall()
        
        # 최근 7일간 상담 수
        cursor.execute("""
            SELECT COUNT(*) FROM consultations
            WHERE created_at >= datetime('now', '-7 days')
        """)
        recent_consultations = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total_consultations,
            "by_type": dict(type_stats),
            "recent_week": recent_consultations
        }
        
    except Exception as e:
        st.error(f"❌ 통계 조회 중 오류가 발생했습니다: {str(e)}")
        return {"total": 0, "by_type": {}, "recent_week": 0}


def render_consultation_statistics():
    """상담 통계 렌더링"""
    st.subheader("📊 상담 통계")
    
    stats = get_consultation_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("전체 상담 수", stats["total"])
    
    with col2:
        st.metric("최근 7일", stats["recent_week"])
    
    with col3:
        most_common_type = max(stats["by_type"].items(), key=lambda x: x[1])[0] if stats["by_type"] else "없음"
        st.metric("가장 많은 상담 유형", most_common_type)
    
    # 상담 유형별 차트
    if stats["by_type"]:
        st.bar_chart(stats["by_type"])
