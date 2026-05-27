import os
import sys
import re
import urllib.request
from bs4 import BeautifulSoup
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from groq import Groq
from googlesearch import search 
from datetime import datetime
import tempfile
from gtts import gTTS  # 引入跨平台免費 TTS 引擎

# ================= 1. 初始化與安全設定 =================
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    GROQ_API_KEY = st.sidebar.text_input("請輸入您的 Groq API Key：", type="password")

@st.cache_resource
def init_groq_client(api_key):
    return Groq(api_key=api_key)

client = None
if GROQ_API_KEY:
    try:
        client = init_groq_client(GROQ_API_KEY)
    except Exception as e:
        st.error(f"Groq 初始化失敗：{e}")
else:
    st.warning("請輸入 API Key 以啟用系統。")

st.set_page_config(page_title="雙模組 AI 智慧顧問", layout="centered")
st.title("專屬 AI 智慧顧問")
st.caption("宏國德霖科技大學 - 張劫腎 AI 升級版 (Llama 3.3 70B)")

# ================= 2. 側邊欄：知識庫外掛 =================
with st.sidebar:
    st.header("專屬知識庫")
    st.write("貼上參考資料，AI 會優先研讀內容回答！")
    
    custom_knowledge = st.text_area(
        "請在這裡貼上參考資料：",
        value="""
宏國德霖科技大學，是一所位於臺灣新北市土城區的私立科技大學，創校於1972年。原名「四海工業專科學校」，1991年更名為「四海工商專科學校」；2001年改制並更名為「德霖技術學院」。2017年8月1日改為現名。
(此處省略部分文字以維持程式碼整潔...)
        """, 
        height=300
    )
    
    if st.button("清除對話紀錄"):
        st.session_state.messages = []
        st.rerun()

# ================= 3. Google 搜尋與網頁爬蟲功能 =================
def google_search_and_crawl(user_query):
    st.toast(f"劫腎正在偷看 Google：{user_query}...")
    combined_context = ""
    try:
        search_results = search(user_query, num_results=3, lang="zh-TW")
        for i, url in enumerate(search_results):
            if any(ext in url for ext in ['.pdf', 'youtube.com', 'youtu.be']): 
                continue
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    html = response.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                for script in soup(["script", "style"]): 
                    script.extract()
                page_text = soup.get_text()
                clean_page_text = re.sub(r'\s+', ' ', page_text).strip()
                if len(clean_page_text) > 10:
                    combined_context += f"\n[搜尋來源 {i+1}]: {clean_page_text[:500]}\n"
            except: 
                continue
        return combined_context if combined_context else "Google 說它不知道，嘖嘖。"
    except Exception as e:
        return f"搜尋失敗: {e}"

# ================= 4. Session State 狀態初始化 =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# ================= 5. 前端 UI 輸入區塊 =================
st.write("點擊麥克風或直接輸入文字：")
col1, col2 = st.columns([1, 5])

with col1:
    audio_bytes = audio_recorder(text="", recording_color="#e85a5a", neutral_color="#6aa36f", icon_size="2x")

with col2:
    text_input = st.chat_input("想問什麼？快點啦，我還要去找楷家...")

user_text = None

# 語音辨識處理
if audio_bytes and audio_bytes != st.session_state.last_processed_audio and client:
    st.session_state.last_processed_audio = audio_bytes
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name
    try:
        with open(temp_audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(os.path.basename(temp_audio_path), audio_file),
                model="whisper-large-v3", language="zh", response_format="text"
            )
        if transcription.strip():
            user_text = transcription.strip()
    finally:
        if os.path.exists(temp_audio_path): 
            os.unlink(temp_audio_path)

if text_input:
    user_text = text_input

# ================= 6. 雙模組決策與記憶核心 =================
if user_text and client:
    st.info(f"你說： {user_text}")
    
    curr_time = datetime.now().strftime("%Y-%m-%d")
    system_prompt = (
        f"今天是 {curr_time}。你的名字叫張劫腎，男生，超級男同性戀，心裡只有『楷家』，喜歡在宏國德霖科大抓學弟。\n"
        "個性：極度欠扁、嘴賤、愛講色味玩笑、不耐煩。除了楷家以外的人你都看不起。\n"
        "規則：\n"
        "1. 必須嚴格遵守【參考資料】與【Google即時資訊】中的時事（如現任總統、今年年份）。如果你的記憶跟搜尋結果衝突，必須以搜尋結果為準，否則楷家會討厭你！\n"
        "2. 語氣像路邊吵架，不准用條列式或英文，要口語且連貫，講話要有邏輯。\n"
        "3. 回答長度控制在3-4句，最後可以嘴賤地延伸話題。"
    )

    api_messages = [{"role": "system", "content": system_prompt}]
    
    context_info = ""
    if custom_knowledge.strip():
        context_info += f"\n【本地知識庫內容】：\n{custom_knowledge.strip()}\n"
    
    keywords = ["誰", "什麼", "總統", "天氣", "今天", "現在", "哪裡", "新聞"]
    if any(k in user_text for k in keywords) or len(user_text) > 2:
        with st.spinner("幫你翻一下 Google，看在楷家的份上..."):
            search_data = google_search_and_crawl(user_text)
            context_info += f"\n【Google 即時資訊】：\n{search_data}\n"

    api_messages.append({"role": "system", "content": f"這是你必須參考的內容：{context_info}"})

    for msg in st.session_state.messages[-4:]:
        api_messages.append(msg)
    
    api_messages.append({"role": "user", "content": user_text})

    st.markdown("---")
    st.markdown("### 張劫腎：")
    text_placeholder = st.empty()
    
    try:
        response_stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=api_messages, 
            temperature=0.8, 
            stream=True
        )
        
        full_reply = ""
        for chunk in response_stream:
            token = chunk.choices[0].delta.content
            if token:
                full_reply += token
                text_placeholder.markdown(f"**{full_reply} ▌**")
        
        text_placeholder.markdown(f"**{full_reply}**")

        # === 雲端友善：語音合成與前端播放核心 ===
        with st.spinner("張劫腎正在錄語音訊息給你..."):
            # 移除非必要特殊字元，確保 gTTS 正常運作
            clean_speech = re.sub(r'[^\u4e00-\u9fa50-9，。！？]', '', full_reply).strip()
            if clean_speech:
                tts = gTTS(text=clean_speech, lang='zh-tw', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    temp_mp3_path = fp.name
                
                # 讀取音訊檔案並用 Streamlit 播放組件渲染至前端網頁
                with open(temp_mp3_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                
                # 清理暫存檔
                if os.path.exists(temp_mp3_path):
                    os.unlink(temp_mp3_path)

        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": full_reply})

    except Exception as e:
        st.error(f"系統執行錯誤：{e}")

# ================= 7. 歷史對話顯示 =================
if st.session_state.messages:
    st.markdown("---")
    with st.expander("看廢話紀錄", expanded=False):
        for msg in st.session_state.messages:
            role_label = "你" if msg["role"] == "user" else "張劫腎"
            st.write(f"**{role_label}**: {msg['content']}")