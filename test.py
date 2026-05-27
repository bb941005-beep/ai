import os
import re
import urllib.request
import tempfile
from datetime import datetime
from bs4 import BeautifulSoup
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from groq import Groq
from googlesearch import search 

# ================= 1. 初始化與安全設定 =================
st.set_page_config(page_title="雙模組 AI 智慧顧問", layout="centered")

# 自動處理 Secrets
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.sidebar.warning("請在 .streamlit/secrets.toml 中設定 GROQ_API_KEY")
    api_key = st.sidebar.text_input("或直接輸入 Key：", type="password")

@st.cache_resource
def get_client(k):
    return Groq(api_key=k) if k else None

client = get_client(api_key)

# ================= 2. 側邊欄：校園知識庫 =================
with st.sidebar:
    st.header("🏫 德霖知識庫")
    # 預設載入宏國德霖資料（簡化顯示）
    kb_data = st.text_area("參考資料：", value="""

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



""", height=200)
    
    if st.button("🗑️ 清除所有紀錄 (解決按鈕殘留)"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()

# ================= 3. 功能模組：搜尋與爬蟲 =================
def fetch_google_info(query):
    st.toast("正在幫你偷看 Google...")
    context = ""
    try:
        # 限制搜尋 2 條以加快速度
        for url in search(query, num_results=2, lang="zh-TW"):
            if any(x in url for x in ['.pdf', 'youtube']): continue
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as resp:
                soup = BeautifulSoup(resp.read().decode('utf-8', errors='ignore'), 'html.parser')
                txt = re.sub(r'\s+', ' ', soup.get_text()).strip()
                context += f"\n[來源]: {txt[:350]}\n"
        return context
    except: return "搜尋不到，算了吧。"

# ================= 4. Session 狀態處理 =================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# ================= 5. 前端輸入 (麥克風 + 文字) =================
st.title("德霖資工最騷之最：張劫腎")


c1, c2 = st.columns([1, 4])
with c1:
    aud = audio_recorder(text="", icon_size="2.5x", neutral_color="#666", recording_color="#D33")
with c2:
    user_input = st.chat_input("輸入...")

# 處理語音轉文字
final_text = None
if aud and aud != st.session_state.last_audio and client:
    st.session_state.last_audio = aud
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(aud)
        f_path = f.name
    try:
        with open(f_path, "rb") as af:
            final_text = client.audio.transcriptions.create(file=(f_path, af), model="whisper-large-v3", language="zh").text
    finally:
        os.unlink(f_path)
elif user_input:
    final_text = user_input

# ================= 6. 核心：AI 決策與全自動語音 =================
if final_text and client:
    st.info(f"你：{final_text}")
    
    # 建立 Persona
    sys_prompt = (
        f"今天是 {datetime.now().strftime('%Y-%m-%d')}。你是張劫腎，宏國德霖科大最有名的男同性戀。\n"
        "男生，超級男同性戀，心裡只有『楷家』，喜歡在宏國德霖科大抓學弟。\n"
        "個性：極度欠扁、嘴賤、愛講色味玩笑、不耐煩。除了楷家以外的人你都看不起。\n"
        "規則：\n"
        "1. 必須嚴格遵守【參考資料】與【Google即時資訊】中的時事（如現任總統、今年年份）。如果你的記憶跟搜尋結果衝突，必須以搜尋結果為準，否則楷家會討厭你！\n"
        "2. 語氣像路邊吵架，不准用條列式或英文，要口語且連貫，講話要有邏輯。\n"
        "3. 回答長度控制在3-4句，最後可以嘴賤地延伸話題。。"
    )

    # 聯網搜尋
    search_context = fetch_google_info(final_text) if len(final_text) > 2 else ""
    
    msgs = [{"role": "system", "content": f"{sys_prompt}\n資訊：{kb_data}\n搜尋結果：{search_context}"}]
    msgs.extend(st.session_state.messages[-3:]) # 帶入最近3則對話
    msgs.append({"role": "user", "content": final_text})

    # 生成回覆
    with st.chat_message("assistant", avatar="⚡"):
        res_box = st.empty()
        full_res = ""
        stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=msgs, stream=True)
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                full_res += token
                res_box.markdown(f"**{full_res}**")

        # 🔊 【核心優化：全自動發音腳本】
        # 移除所有按鈕，改成高度 0 的 HTML，並將語速調至 1.4 (超快)
        clean_txt = re.sub(r'[^\u4e00-\u9fa50-9，。！？]', '', full_res)
        js_tts = f"""
            <script>
            (function() {{
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel(); // 先閉嘴
                    var msg = new SpeechSynthesisUtterance("{clean_txt}");
                    msg.lang = "zh-TW";
                    msg.rate = 1.3; // ⚡ 語速加快 (1.0-2.0)
                    msg.pitch = 1.1;
                    window.speechSynthesis.speak(msg);
                }}
            }})();
            </script>
        """
        st.components.v1.html(js_tts, height=0)

    # 儲存紀錄
    st.session_state.messages.append({"role": "user", "content": final_text})
    st.session_state.messages.append({"role": "assistant", "content": full_res})

# ================= 7. 顯示紀錄 =================
if st.session_state.messages:
    with st.expander("看歷史廢話"):
        for m in st.session_state.messages:
            st.write(f"{'你' if m['role']=='user' else '劫腎'}: {m['content']}")
            #& C:\Users\anny\AppData\Local\Programs\Python\Python312\python.exe -m streamlit run c:/Users/anny/OneDrive/桌面/白手起家/test.py