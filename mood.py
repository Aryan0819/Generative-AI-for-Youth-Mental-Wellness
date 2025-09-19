# app.py
import streamlit as st
import requests
import os

# --- Backend API URL ---
# Note: You cannot run the FastAPI backend on Streamlit Cloud like you did in Colab.
# The backend needs to be deployed separately, and its URL hardcoded or fetched.
# For a hackathon, you can deploy the backend (FastAPI + ngrok) on a separate
# machine or service and paste the persistent URL here.
# For this example, let's assume a hardcoded public URL.
# Replace this with your actual, persistent backend URL.
# If you are running both frontend and backend on the same service (e.g. Render, Heroku),
# you would not use ngrok.

# For a Streamlit Cloud deployment, the FastAPI server must be running and exposed
# from a different service. You need to get the public URL from that other service.
# If you want to deploy a single app with both, you'd need a more advanced setup.
# Let's assume you've used your Colab + ngrok to get a URL that you can use for the hackathon.

# A better way would be to create a single app.py that runs all your logic
# instead of having a separate FastAPI backend.
# The following code assumes the API calls are made to an external service.
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-ngrok-backend-url.ngrok-free.app")

st.title("MindMate AI")

mood = st.radio(
    "How are you feeling today?",
    ['calm', 'sad', 'anxious', 'stressed', 'lonely', 'grateful', 'energized']
)
text = st.text_area("Write a few lines about your day...")

if st.button("Reflect with AI"):
    feelings = text.strip() or f"I'm feeling {mood}"
    with st.spinner("Generating..."):
        try:
            q = requests.get(f"{BACKEND_URL}/api/quote", params={"mood": mood})
            quote = q.json().get("quote", "")

            r = requests.post(f"{BACKEND_URL}/api/reflect", json={"text": feelings})
            reply = r.json().get("reply", "")

            p = requests.post(f"{BACKEND_URL}/api/poem", json={"mood": mood, "details": feelings})
            poem = p.json().get("poem", "")

            i = requests.post(f"{BACKEND_URL}/api/image", json={"mood": mood})
            img_url = i.json().get("imageUrl", "")

            st.subheader("MindMate says")
            st.write(reply)

            st.subheader(f"Inspirational Quote for Mood: {mood.capitalize()}")
            st.markdown(f"> {quote}")

            st.subheader("Your Thoughts")
            st.text_area("", value=poem, height=150)

            st.subheader("Calming Image")
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.write("No image available for this mood.")
        except requests.exceptions.RequestException as e:
            st.error(f"API call failed: Is the backend server running? Error: {e}")


