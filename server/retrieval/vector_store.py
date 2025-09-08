import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Any, Dict, Optional, List
from pathlib import Path
from utils.config import get_embeddings


def get_spinal_fusion_vector_store() -> Optional[FAISS]:
    """척추 유합술 관련 문서로 벡터 스토어 생성"""
    
    # 척추 유합술 데이터 파일 경로
    data_path = Path("data/spinal_fusion_content.txt")
    
    if not data_path.exists():
        st.error(f"척추 유합술 데이터 파일을 찾을 수 없습니다: {data_path}")
        return None
    
    try:
        # 텍스트 파일 로드
        loader = TextLoader(str(data_path), encoding='utf-8')
        documents = loader.load()
        
        # 문서를 청크로 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )
        
        # 문서 분할 및 메타데이터 추가
        splits = text_splitter.split_documents(documents)
        
        # 각 청크에 섹션 정보 추가
        for split in splits:
            content = split.page_content
            split.metadata["source"] = "척추 유합술 지침서"
            
            # 섹션 정보 추출
            if "## " in content:
                section = content.split("## ")[1].split("\n")[0]
                split.metadata["section"] = section
            elif "### " in content:
                section = content.split("### ")[1].split("\n")[0]
                split.metadata["subsection"] = section
        
        # FAISS 벡터 스토어 생성
        vector_store = FAISS.from_documents(splits, get_embeddings())
        return vector_store
        
    except Exception as e:
        st.error(f"벡터 스토어 생성 중 오류 발생: {str(e)}")
        return None


def search_spinal_fusion_topic(
    consultation_type: str, 
    query: str, 
    k: int = 5
) -> List[Any]:
    """척추 유합술 관련 정보 검색"""
    
    # 벡터 스토어 생성
    vector_store = get_spinal_fusion_vector_store()
    if not vector_store:
        return []
    
    try:
        # 상담 유형에 따른 검색 쿼리 개선
        enhanced_query = enhance_query_by_consultation_type(consultation_type, query)
        
        # 유사도 검색 수행
        docs = vector_store.similarity_search(enhanced_query, k=k)
        
        return docs
        
    except Exception as e:
        st.error(f"검색 중 오류 발생: {str(e)}")
        return []


def enhance_query_by_consultation_type(consultation_type: str, query: str) -> str:
    """상담 유형에 따른 검색 쿼리 개선"""
    
    enhancement_map = {
        "수술_전": "수술 전 준비사항 검사 주의사항",
        "수술_후": "수술 후 관리 회복 통증 상처",
        "재활": "재활 운동 물리치료 생활가이드",
        "합병증": "합병증 응급상황 주의사항 부작용",
        "일반": "척추 유합술 개요 치료 방법"
    }
    
    enhancement = enhancement_map.get(consultation_type, enhancement_map["일반"])
    enhanced_query = f"{query} {enhancement}"
    
    return enhanced_query


# 이전 함수들과의 호환성을 위한 래퍼 함수
def search_topic(topic: str, role: str, query: str, k: int = 5) -> List[Any]:
    """이전 버전과의 호환성을 위한 함수"""
    return search_spinal_fusion_topic("일반", query, k)
