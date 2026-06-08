# app.py
import streamlit as st
import json
from tools import get_financial_data, get_naver_research, get_dart_disclosure
from agents import orchestrate_agents

st.set_page_config(page_title="나만의 AI 주식 HTS", layout="wide")
st.title("🏛️ 다중 AI 멘토 주식 마스터마인드")

# 안전 금고에서 API 키 꺼내오기
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    DART_KEY = st.secrets["DART_API_KEY"]
except Exception:
    st.error("🚨 스트림릿 클라우드 설정(Secrets)에 API 키를 입력해 주세요.")
    st.stop()

# 설정 파일 읽기
try:
    with open("persona_settings.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception:
    st.error("persona_settings.json 파일이 없습니다.")
    st.stop()

with st.sidebar:
    st.header("🔍 분석 대상")
    ticker = st.text_input("종목 코드 (예: 005930.KS)", "005930.KS")
    user_query = st.text_area("질문", "장기 투자로 적합할까요?")
    selected = st.multiselect("🎙️ 참여할 멘토 선택", list(config.keys()))
    run_btn = st.button("🚀 토론 시작")

if run_btn and selected:
    with st.spinner("거장들이 데이터를 수집하고 분석 중입니다... (약 10~20초 소요)"):
        # 데이터 수집
        fin_data = get_financial_data(ticker)
        res_data = get_naver_research(ticker)
        dart_data = get_dart_disclosure(ticker, DART_KEY)
        
        data_context = f"재무: {fin_data}\n리서치: {res_data}\n공시: {dart_data}"
        
        # 화면에 기본 데이터 보여주기
        st.write("### 📋 수집된 시장 팩트 및 전망")
        st.info(data_context)
        
        # AI 토론 결과 받아오기
        st.write("### 💬 멘토들의 실시간 난상토론")
        debate_results = orchestrate_agents(GEMINI_KEY, selected, config, data_context, user_query)
        
        for name, answer in debate_results.items():
            with st.chat_message("assistant", avatar="👨‍🏫"):
                st.markdown(f"**{name}**")
                st.write(answer)