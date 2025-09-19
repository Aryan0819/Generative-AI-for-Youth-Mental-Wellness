# =============================
# Install dependencies
# =============================
!pip install fastapi uvicorn pyngrok streamlit nest-asyncio requests groq

import os
import nest_asyncio
import uvicorn
import threading
import time
import traceback
import base64
import requests
import streamlit as st
from groq import Groq
import asyncio
import random
from fastapi import FastAPI, Query
from pydantic import BaseModel
from pyngrok import ngrok

# Allow nested event loop (for Colab/Notebook environments)
nest_asyncio.apply()

# =============================
# Environment Variables
# =============================
os.environ["GROQ_API_KEY"] = "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"
os.environ["NGROK_AUTH_TOKEN"] = "32QXi209TnQkMogwVPpD66o2Te4_GDpj5DPiX2SU2Lmyory8"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Please set GROQ_API_KEY environment variable with your Groq API key.")

NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Model to use
GROQ_CHAT_MODEL = "llama-3.3-70b-versatile"

app = FastAPI()

# =============================
# Quotes Text
# =============================
quotes_text = """
1. It’s easy to stand in the crowd but it takes courage to stand alone.
2. Loneliness is not lack of company, loneliness is lack of purpose.
3. The woman who follows the crowd will usually go no further than the crowd. The woman who walks alone is likely to find herself in places no one has ever been before.
4. The thing that makes you exceptional, if you are at all, is inevitably that which makes you lonely.
5. Time spent undistracted and alone, in self-examination, journaling, meditation, resolves the unresolved and takes us from mentally fat to fit.
6. When they are alone they want to be with others, and when they are with others they want to be alone. After all, human beings are like that.
7. The price of being a sheep is boredom. The price of being a wolf is loneliness. Choose one or the other with great care.
8. Loneliness is a tax we have to pay to atone for a certain complexity of mind.
9. If you are never alone, you cannot know yourself.
10. By all means use sometimes to be alone. Salute thyself; see what thy soul doth wear.
11. We feel alone, and in this we are connected.
12. Every single human being who is alive has felt this kind of pain, hopelessness, and loneliness at one time or another. We are all connected through this shared pain and struggle.
13. Our great depression is our lives. We’ve all been raised on television to believe that one day we’d all be millionaires, and movie gods, and rock stars, but we won’t. We’re slowly learning that fact. And we’re very, very pissed off.
14. The worst part of holding the memories is not the pain. It’s the loneliness of it. Memories need to be shared.
15. Remember never to say that you are alone, for you are not alone; nay, God is within, and your genius is within.
16. Lonely is not being alone, it’s the feeling that no one cares.
17. What a lovely surprise to discover how unlonely being alone can be.
18. If you are afraid of being lonely, don’t try to be right.
19. After 10 years of depression and loneliness, I realized the person I missed the most was not another, but myself.
20. The reality is life is a single-player game. You’re born alone. You’re going to die alone. All of your interpretations are alone. All your memories are alone. You’re gone in three generations and nobody cares. Before you showed up, nobody cared. It’s all single-player.
21. Loneliness isn’t the physical absence of other people, he said – it’s the sense that you’re not sharing anything that matters with anyone else.
22. You cannot be lonely if you like the person you’re alone with.
23. I don’t mind being alone. I just don’t want to be part of the crowd.
24. It is an interesting paradox. Despite the fact that people today are rarely alone, we are increasingly lonely. Michael Easter.
25. He who’s mind is not steady does not find happiness either amongst the people or in the solitude of the forest. When alone, he longs for company, and when in company, he longs for solitude.
26. Although I am a typical loner in my daily life, my awareness of belonging to the invisible community of those who strive for truth, beauty, and justice has prevented me from feelings of isolation.
"""

# =============================
# Mood-to-Quote Mapping
# =============================
mood_to_quotes = {
    "calm": [quotes_text.split('\n')[4], quotes_text.split('\n')[9], quotes_text.split('\n')[16], quotes_text.split('\n')[21]],
    "sad": [quotes_text.split('\n')[11], quotes_text.split('\n')[13], quotes_text.split('\n')[18]],
    "anxious": [quotes_text.split('\n')[24], quotes_text.split('\n')[7]],
    "stressed": [quotes_text.split('\n')[6], quotes_text.split('\n')[19]],
    "lonely": [quotes_text.split('\n')[1], quotes_text.split('\n')[3], quotes_text.split('\n')[5]],
    "grateful": [quotes_text.split('\n')[10], quotes_text.split('\n')[14]],
    "energized": [quotes_text.split('\n')[0], quotes_text.split('\n')[22], quotes_text.split('\n')[25]],
}

# =============================
# Mood-to-Image Mapping (Google Drive)
# =============================
mood_to_images = {
    "calm": "/content/drive/MyDrive/images/calm 2.jpg",
    "sad": "/content/drive/MyDrive/images/sad.jpeg",
    "anxious": "/content/drive/MyDrive/images/anxiety.jpg",
    "stressed": "/content/drive/MyDrive/images/stressed 2.jpg",
    "lonely": "/content/drive/MyDrive/images/loneliness.jpg",
    "grateful": "/content/drive/MyDrive/images/grateful.jpg",
    "energized": "/content/drive/MyDrive/images/eneegized.jpg",
}

# =============================
# Utility Functions
# =============================
def get_quote_for_mood(mood: str) -> str:
    quotes = mood_to_quotes.get(mood.lower(), [])
    if quotes:
        return random.choice(quotes).strip()
    return "Remember, it's okay to feel what you are feeling. You are not alone."

async def groq_text(prompt, model=GROQ_CHAT_MODEL, max_tokens=150, temperature=0.7):
    messages = [
        {"role": "system", "content": "You are MindMate, an empathetic companion for youth mental wellness. Validate feelings in plain language. Offer one small actionable step. Keep under 120 words. Avoid medical claims."},
        {"role": "user", "content": prompt}
    ]

    def call_groq():
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens_to_sample=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()

    return await asyncio.to_thread(call_groq)

# =============================
# Request Models
# =============================
class ReflectRequest(BaseModel):
    text: str

class PoemRequest(BaseModel):
    mood: str = "mixed"
    details: str = ""

class ImageRequest(BaseModel):
    mood: str = "calm"

# =============================
# API Routes
# =============================
@app.get("/api/quote")
async def get_quote(mood: str = Query(..., description="Mood keyword")):
    try:
        return {"quote": get_quote_for_mood(mood)}
    except Exception as e:
        print("Error in /api/quote:", e)
        return {"error": "Internal server error"}

@app.post("/api/reflect")
async def reflect(req: ReflectRequest):
    try:
        prompt = f"Here are some inspiring quotes:\n{quotes_text}\nUser says: {req.text}"
        reply = await groq_text(prompt)
        return {"reply": reply}
    except Exception as e:
        print("Error in /api/reflect:", e)
        return {"error": "Internal server error"}

@app.post("/api/poem")
async def poem(req: PoemRequest):
    try:
        prompt = (f"Using these quotes:\n{quotes_text}\n"
                  f"Write a short, hopeful free-verse poem (6-9 lines) for someone feeling {req.mood}. Context: {req.details}")
        poem_text = await groq_text(prompt, max_tokens=200, temperature=0.8)
        return {"poem": poem_text}
    except Exception as e:
        print("Error in /api/poem:", e)
        return {"error": "Internal server error"}

@app.post("/api/image")
async def image(req: ImageRequest):
    try:
        img_url = mood_to_images.get(req.mood.lower(), "")
        return {"imageUrl": img_url}
    except Exception as e:
        print("Error in /api/image:", e)
        return {"error": "Internal server error"}

# =============================
# Run Backend with ngrok
# =============================
def run_backend():
    uvicorn.run(app, host="0.0.0.0", port=8000)

!ngrok authtoken $NGROK_AUTH_TOKEN
ngrok.kill()

backend_thread = threading.Thread(target=run_backend, daemon=True)
backend_thread.start()
time.sleep(5)

backend_tunnel = ngrok.connect(8000, "http")
backend_url = backend_tunnel.public_url
print("Backend API public URL:", backend_url)

# =============================
# Streamlit Frontend Code
# =============================
streamlit_code = f"""
import streamlit as st
import requests

BACKEND_URL = "{backend_url}"

st.title("MindMate AI")

mood = st.radio(
    "How are you feeling today?",
    ['calm', 'sad', 'anxious', 'stressed', 'lonely', 'grateful', 'energized']
)
text = st.text_area("Write a few lines about your day...")

if st.button("Reflect with AI"):
    feelings = text.strip() or f"I'm feeling {{mood}}"
    with st.spinner("Generating..."):
        try:
            q = requests.get(f"{{BACKEND_URL}}/api/quote", params={{"mood": mood}}, verify=False)
            quote = q.json().get("quote", "")

            r = requests.post(f"{{BACKEND_URL}}/api/reflect", json={{"text": feelings}}, verify=False)
            reply = r.json().get("reply", "")

            p = requests.post(f"{{BACKEND_URL}}/api/poem", json={{"mood": mood, "details": feelings}}, verify=False)
            poem = p.json().get("poem", "")

            i = requests.post(f"{{BACKEND_URL}}/api/image", json={{"mood": mood}}, verify=False)
            img_url = i.json().get("imageUrl", "")

            st.subheader("MindMate says")
            st.write(reply)

            st.subheader(f"Inspirational Quote for Mood: {{mood.capitalize()}}")
            st.markdown(f"> {{quote}}")

            st.subheader("Your Thoughts")
            st.text_area("", value=poem, height=150)

            st.subheader("Calming Image")
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.write("No image available for this mood.")
        except Exception as e:
            st.error(f"API call failed: {{e}}")
"""

with open("app.py", "w") as f:
    f.write(streamlit_code)

frontend_tunnel = ngrok.connect(8501)
frontend_url = frontend_tunnel.public_url
print("Streamlit app URL:", frontend_url)

!streamlit run app.py --server.port 8501 --server.headless true