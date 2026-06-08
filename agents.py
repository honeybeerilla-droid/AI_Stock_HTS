# agents.py
import os
import json
import concurrent.futures
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_text(urls):
    # 유튜브 자막을 쿠키(cookies.txt)를 이용해 긁어옵니다.
    full_text = ""
    for url in urls:
        try:
            video_id = url.split("v=")[1].split("&")[0]
            if os.path.exists("cookies.txt"):
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'], cookies='cookies.txt')
            else:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            full_text += " ".join([t['text'] for t in transcript]) + "\n"
        except Exception:
            pass
    return full_text

def run_agent(api_key, persona_name, persona_info, data_context, user_query):
    # 제미나이 AI에게 역할을 부여하고 대답을 받아냅니다.
    genai.configure(api_key=api_key)
    
    # 사전에 설정한 유튜브 자막을 학습
    youtube_knowledge = get_youtube_text(persona_info.get("youtube_urls", []))
    
    system_instruction = f"""
    너는 '{persona_name}'이다. 역할: {persona_info['role']}
    배경지식: {youtube_knowledge[:10000]} # 글자 수 제한 방지
    1. DART(팩트)와 리서치(해석)를 분리하여 분석하라.
    2. 마지막에는 반드시 사용자의 편향을 깨는 '소크라테스식 다층적 역질문'을 1~2개 던져라.
    """
    
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=system_instruction)
    prompt = f"[시장 데이터]\n{data_context}\n\n[사용자 질문]\n{user_query}"
    
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"에러 발생: {e}"

def orchestrate_agents(api_key, selected_mentors, persona_config, data_context, user_query):
    # 여러 명의 멘토를 동시에 실행시킵니다.
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(run_agent, api_key, name, persona_config[name], data_context, user_query): name 
            for name in selected_mentors
        }
        for future in concurrent.futures.as_completed(futures):
            results[futures[future]] = future.result()
    return results