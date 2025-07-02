import streamlit as st
import os
import requests
from dotenv import load_dotenv
from gtts import gTTS
from io import BytesIO

# Load .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# ----------------------------
# Gemini Flash API Function
# ----------------------------
def call_gemini_flash(prompt):
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = { "Content-Type": "application/json" }
    body = {
        "contents": [ { "parts": [ { "text": prompt } ] } ]
    }
    params = { "key": GEMINI_API_KEY }

    response = requests.post(endpoint, headers=headers, json=body, params=params)

    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

# ----------------------------
# YouTube API Function
# ----------------------------
def get_youtube_videos(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "maxResults": 5,
        "type": "video"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        videos = []
        for item in data["items"]:
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            videos.append((title, f"https://www.youtube.com/watch?v={video_id}"))
        return videos
    else:
        return [("Error", response.text)]

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Educational Content Generator", page_icon="📚")
st.title("📚 Educational Content Generator Agent")

st.sidebar.title("Choose Task")
task = st.sidebar.radio("Select an action", [
    "Summarize Content",
    "Generate Quiz",
    "Create Flashcards",
    "Generate Audio Summary",
    "Suggest YouTube Videos"
])

st.subheader("📄 Upload or Paste Your Learning Material")
upload = st.file_uploader("Upload a .txt file", type=["txt"])
text_input = st.text_area("Or paste your content here")

content = ""
if upload:
    content = upload.read().decode("utf-8")
elif text_input:
    content = text_input

if content:
    if task == "Summarize Content":
        st.subheader("🧠 Summary")
        prompt = f"Summarize this educational content:\n{content}"
        result = call_gemini_flash(prompt)
        st.write(result)

    elif task == "Generate Quiz":
        st.subheader("📝 Quiz")
        prompt = f"Generate 5 multiple-choice questions with 4 options each and the correct answer labeled based on:\n{content}"
        result = call_gemini_flash(prompt)
        st.markdown(result)

    elif task == "Create Flashcards":
        st.subheader("📇 Flashcards")
        prompt = f"Create 10 flashcards from the following content in the format: Term - Definition:\n{content}"
        result = call_gemini_flash(prompt)
        st.markdown(result)

    elif task == "Generate Audio Summary":
        st.subheader("🔊 Audio Summary")
        prompt = f"Give a short spoken summary (approx. 1 minute) of this educational content:\n{content}"
        text = call_gemini_flash(prompt)
        tts = gTTS(text)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        st.audio(audio_fp, format='audio/mp3')
        st.markdown("📝 Text Summary:")
        st.write(text)

    elif task == "Suggest YouTube Videos":
        st.subheader("🎥 YouTube Videos")
        st.info("Based on topic keywords from your content")
        query = f"educational videos about {content[:80]}"
        videos = get_youtube_videos(query)
        for title, url in videos:
            st.markdown(f"- [{title}]({url})")
else:
    st.info("Please upload or paste educational content to continue.")
