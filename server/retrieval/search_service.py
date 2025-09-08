import streamlit as st
from langchain.schema import Document
from typing import List, Literal
from duckduckgo_search import DDGS
from langchain.schema import HumanMessage, SystemMessage
from utils.config import get_llm


def improve_search_query(
    budget: str,
    property_type: str,
    preference1: str,
    preference2: str,
    role: Literal["RATIONAL_AGENT", "EMOTIONAL_AGENT", "MEDIATOR_AGENT"] = "MEDIATOR_AGENT",
) -> List[str]:

    template = "부동산 매물 검색을 위해 다음 조건에 맞는 3개의 검색어를 제안해주세요. 예산: {budget}, 매물유형: {property_type}, 선호조건1: {preference1}, 선호조건2: {preference2}. {perspective} 각 검색어는 25자 이내로 작성하고 콤마로 구분하세요. 검색어만 제공하고 설명은 하지 마세요."

    perspective_map = {
        "RATIONAL_AGENT": "이성적이고 현실적인 관점에서 교통, 생활환경, 재정적 안정성을 중시하는 검색어를 제안해주세요.",
        "EMOTIONAL_AGENT": "감성적이고 로맨틱한 관점에서 삶의 질, 뷰, 편의시설을 중시하는 검색어를 제안해주세요.",
        "MEDIATOR_AGENT": "균형잡힌 관점에서 객관적인 부동산 정보와 시장 동향을 찾는 검색어를 제안해주세요.",
    }

    prompt = template.format(
        budget=budget, 
        property_type=property_type, 
        preference1=preference1, 
        preference2=preference2,
        perspective=perspective_map[role]
    )

    messages = [
        SystemMessage(
            content="당신은 부동산 검색 전문가입니다. 주어진 조건에 대해 가장 관련성 높은 검색어를 제안해주세요."
        ),
        HumanMessage(content=prompt),
    ]

    # 스트리밍 응답 받기
    response = get_llm().invoke(messages)

    # ,로 구분된 검색어 추출
    suggested_queries = [q.strip() for q in response.content.split(",")]

    return suggested_queries[:3]


def get_search_content(
    improved_queries: str,
    language: str = "ko",
    max_results: int = 5,
) -> List[Document]:

    try:
        documents = []

        ddgs = DDGS()

        # 각 개선된 검색어에 대해 검색 수행
        for query in improved_queries:
            try:
                # 검색 수행
                results = ddgs.text(
                    query,
                    region=language,
                    safesearch="moderate",
                    timelimit="y",  # 최근 1년 내 결과
                    max_results=max_results,
                )

                if not results:
                    continue

                # 검색 결과 처리
                for result in results:
                    title = result.get("title", "")
                    body = result.get("body", "")
                    url = result.get("href", "")

                    if body:
                        documents.append(
                            Document(
                                page_content=body,
                                metadata={
                                    "source": url,
                                    "section": "content",
                                    "topic": title,
                                    "query": query,
                                },
                            )
                        )

            except Exception as e:
                st.warning(f"검색 중 오류 발생: {str(e)}")

        return documents

    except Exception as e:
        st.error(f"검색 서비스 오류 발생: {str(e)}")
        return []
