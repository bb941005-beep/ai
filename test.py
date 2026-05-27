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
import base64          # 用於將音訊轉為網頁可讀的 base64 碼

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
st.title("資工的帥氣顧問")

# ================= 2. 側邊欄：知識庫外掛 =================
with st.sidebar:
    st.header("專屬知識庫")
    st.write("貼上參考資料，AI 會優先研讀內容回答！")
    
    custom_knowledge = st.text_area(
        "請在這裡貼上參考資料：",
        value="""
宏國德霖科技大學，是一所位於臺灣新北市土城區的私立科技大學，創校於1972年。原名「四海工業專科學校」，1991年更名為「四海工商專科學校」；2001年改制並更名為「德霖技術學院」。2017年8月1日改為現名。



學校沿革

四海工業專科學校時期（1952年～1991年）

1959年2月，由萬紹章發起，購買臺北縣土城鄉清化里建校基地，妥擬設校計畫。

1961年8月，奉教育部准予籌設。

1969年2月，成立董事會，完成財團法人登記，推舉李景德先生為第一屆董事長。

1972年1月，教育部核准立案，基於配合國家發展，為培育優秀專業技術人才而設立，並以「公、誠、精、毅」為校訓，砥勵師生創立四海工業專科學校，設有電子工程科、土木工程科、機械工程科。

1974年，因資金不足，教育部勒令減招。

1975年，教育部勒令停招。

1978年，由宏國關係事業董事長林謝罕見女士與謝村田、謝隆盛、謝進旺、謝金朝、昆仲捐資接辦，改組第三屆董事會，依學校發展計畫，積極擴充校地，廣建校舍，美化校園，學校恢復招生。

1983年，奉准成立夜間部二年制工科。

四海工商專科學校時期（1991年～2001年）

1991年10月，奉准成立日間部二年制商科，更易校名為「四海工商專科學校」。

1992年，增設二年制銀行保險科。

1994年，增設二年制企業管理科、國際貿易科。

1995年，增設夜間部二年制商科。

1997年，增設二年制不動產經營科、五年制應用外語科。

1998年，增設旅館管理科。

德霖技術學院時期（2001年～2017年7月）

2001年8月，奉准升格改制為技術學院，乃以「德化學子，霖霑社會」為目標，改制為「德霖技術學院」，設土木工程系、企業管理系、應用英語系、機械工程系。

2002年，國際貿易科改制為國際貿易系。銀行保險科改制為財務金融系。

2003年，增設資訊工程系、休閒事業管理系。停招不動產經營科。國際貿易系改名國際企業系。旅館管理科改制為餐旅管理系。

2005年，增設電腦與通訊工程系、空間設計系。

2006年，增設光電工程系。

2007年，增設電子工程系，機械工程系分設電腦輔助應用工程組、機電與自動化工程組之分組。整併土木工程系與空間設計系為營建科技系。

2010年，增設不動產經營系、餐飲廚藝系。營建科技系、空間設計系與新設之不動產經營系整合成立不動產學群。停招營建科技系產業經營組。

2011年，停招光電工程系、財務金融系。增設國際貿易科、餐飲廚藝科。應用外語科取消英文組；營建科技系取消資訊應用組；營建科技系空間設計組獨立為空間設計系。復招不動產經營科。

2012年，增設創意產品設計系、休閒事業管理科。停招機械工程系電腦輔助應用工程組、機械工程系機電與自動化工程組

2012年7月1日，啟動準備專案評鑑及改名科技大學。

2013年，國際企業系改名會展與觀光系。停招國際貿易科。

2014年8月25日，新建餐旅廚藝大樓動工。

2014年9月1日，圖書館改建搬遷完成。

2014年12月1日，接受教育部103學年度技術學院專案評鑑。

2015年1月28日，專案評鑑不動產經營系、空間設計系、資訊工程系、餐飲廚藝系、電腦與通訊工程系、企業管理系、休閒事業管理系獲評一等。

2015年4月15日，申請改名科技大學計畫書送教育部。

2015年9月，獲准籌備科技大學。

2016年，調整學群架構：不動產學群解散；原工程學群資訊工程系、電腦與通訊工程系、電子工程系新組電資學群；原工程學群改名工程與設計學群，並納入營建科技系及室內設計系（皆原隸不動產學群）；不動產經營系改隸商管學群。8月10日，經教育部決議，籌備科大資格展延一年，同時須參加105學年度技術學院綜合評鑑，綜合評鑑成績若未達改名科大標準，106學年度將撤消籌備科大資格。營建科技系改名為土木工程系。

宏國德霖科技大學時期（2017年8月～至今）

2017年，接受教育部評鑑。公布評鑑結果，校務行政及受評所、系、科皆通過評鑑，2017年8月1日改名為宏國德霖科技大學[4]。原工程與設計學群、電資學群、商管學群，改設工程學院、管理與設計學院、民生學院。

2018年，調整學院系所架構，原先的民生學院改名餐旅學院、管理暨設計學院改名不動產學院。原先隸屬管理暨設計學院的應用英語系、應用外語科更改隸屬餐旅學院；原先隸屬管理暨設計學院的創意產品設計系改隸屬工程學院；原先隸屬工程學院的土木工程系更改隸屬不動產學院。

2019年，增設建築科五專、園藝系四技日間部、資訊工程系、機械工程系、土木工程系二技日間部、室內設計系二技進修部；停招餐旅管理系、餐飲廚藝系四技在職專班。

2020年，增設企業管理系碩士班。

2024年，停招創意產品設計系、會展活動管理系、應用英語系。



老校名  四海工業專科學校

校訓    公 誠 精 毅[1]

創辦時間    1972年創校四海工業專科學校

1991年更名四海工商專科學校

2001年改制為德霖技術學院

2017年8月1日改名宏國德霖科技大學。

校慶日  11月6日

學校代碼    1080

學校類型    私立科技大學

校長    段葉芳

副校長  林憲陽

張遵偉

教師人數    155（2023-12）[2]

學生人數    4292（2024-12）[3]

研究生人數  37人

校址    中華民國（臺灣）

23654 新北市土城區青雲路380巷1號24°58′N 121°30′E

校區    新北市土城

總面積  13.52公頃

暱稱    宏國科大、德霖科大、宏霖科大、宏國德霖大學

所屬法人    宏國學校財團法人

隸屬    宏國關係事業
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

        # === 雲端友善 + 完全隱藏音訊播放器核心 ===
        with st.spinner("張劫腎正在錄語音訊息給你..."):
            clean_speech = re.sub(r'[^\u4e00-\u9fa50-9，。！？]', '', full_reply).strip()
            if clean_speech:
                tts = gTTS(text=clean_speech, lang='zh-tw', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    temp_mp3_path = fp.name
                
                # 讀取音訊並將其轉碼為 base64 字串
                with open(temp_mp3_path, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                b64_audio = base64.b64encode(audio_bytes).decode()
                
                # 利用 HTML5 隱藏音訊（不加 controls 屬性），並利用 JS 達成無痛自動播放
                html_audio_player = f"""
                    <audio id="bg-audio" autoplay>
                        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
                    </audio>
                    <script>
                        var audio = document.getElementById("bg-audio");
                        audio.volume = 1.0;
                        audio.play();
                    </script>
                """
                # 將元件渲染到畫面，但高度設為 0 以實現完全隱藏
                st.components.v1.html(html_audio_player, height=0)
                
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
           #& C:/Users/User/AppData/Local/Programs/Python/Python311/python.exe -m streamlit run c:/Users/User/Desktop/專題/test.py
            #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