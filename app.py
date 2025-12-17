import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from PIL import Image, ImageDraw
import google.generativeai as genai

# ----------------------- Page config -----------------------
st.set_page_config(
    page_title="Intelligent AgroGuide",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- Gemini setup -----------------------
GEMINI_API_KEY = os.getenv("AIzaSyAGiMJugKPPyqCOnJIcNiL8c6z2e1DNCPI")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def call_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"You are an expert Indian agriculture advisor.\n"
            f"Give clear, practical, farmer-friendly advice.\n\n"
            f"Question: {prompt}"
        )
        return response.text.strip()
    except Exception as e:
        return f"⚠️ AI temporarily unavailable: {e}"

def mock_ai_response(prompt: str) -> str:
    samples = [
        "White insects are likely whiteflies. Use neem oil spray weekly and remove infected leaves.",
        "Choose millets like ragi or bajra for low rainfall and alkaline soils.",
        "Irrigate early morning using drip irrigation to reduce evaporation.",
        "Add organic compost and green manure to improve soil fertility.",
        "Rotate crops with legumes to naturally restore soil nitrogen.",
    ]
    return random.choice(samples)

def agro_ai(prompt: str) -> str:
    return call_gemini(prompt) if GEMINI_API_KEY else mock_ai_response(prompt)

# ----------------------- Styling -----------------------
def header_animation():
    st.markdown(
        """
        <style>
        .hero {background: linear-gradient(90deg,#064e3b,#022c22);
        padding:40px;border-radius:14px;color:white}
        .card{background:white;border-radius:14px;padding:18px;
        box-shadow:0 6px 20px rgba(0,0,0,0.15)}
        .small{color:#6b7280;font-size:14px}
        </style>
        <div class='hero'>
        <h1>🌾 Intelligent AgroGuide</h1>
        <p class='small'>AI-powered assistant for climate-smart farming</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ----------------------- Sidebar -----------------------
with st.sidebar:
    st.header("👨‍🌾 Farmer Profile")
    name = st.text_input("Name", "S. Muthuvel")
    location = st.text_input("Location", "Tamil Nadu")
    soil_type = st.selectbox("Soil Type", ["Loamy", "Sandy", "Clay", "Alkaline"])
    soil_ph = st.slider("Soil pH", 4.0, 10.0, 7.2, 0.1)

    st.divider()
    if GEMINI_API_KEY:
        st.success("Gemini AI Connected")
    else:
        st.info("Demo Mode (Mock AI)")

# ----------------------- Header -----------------------
header_animation()

# ----------------------- Main Layout -----------------------
col1, col2 = st.columns((2,1))

# ================= LEFT =================
with col1:
    st.subheader("💬 Ask AgroGuide")
    user_q = st.text_input(
        "Describe your farming problem:",
        "White insects on tomato leaves, what should I do?"
    )

    if st.button("Ask AI"):
        with st.spinner("Thinking like an agri-expert..."):
            reply = agro_ai(user_q)
            st.success(reply)

    st.markdown("---")

    st.subheader("🌱 Intelligent Crop Planner")
    rain = st.slider("Expected Monthly Rainfall (mm)", 0, 500, 100)
    season = st.selectbox("Season", ["Kharif", "Rabi", "Summer"])

    if st.button("Get Crop Advice"):
        prompt = (
            f"Soil: {soil_type}, pH {soil_ph}, "
            f"Rainfall: {rain}mm, Season: {season}"
        )
        st.info(agro_ai(prompt))

    st.markdown("---")

    st.subheader("🔍 Pest Detection (Demo Image)")
    uploaded = st.file_uploader("Upload leaf image", ["jpg","png","jpeg"])

    if uploaded:
        img = Image.open(uploaded)
    else:
        img = Image.new("RGB", (500,300), "#fefce8")
        d = ImageDraw.Draw(img)
        d.text((20,20), "Sample Leaf Image", fill="green")

    st.image(img, use_column_width=True)

    if st.button("Analyze Pest"):
        diagnosis = agro_ai("Identify pest and organic treatment")
        st.warning(diagnosis)

# ================= RIGHT =================
with col2:
    st.subheader("📈 Market Price Trends")
    crops = ["Rice","Tomato","Ragi","Maize","Wheat"]
    crop = st.selectbox("Select Crop", crops)

    days = np.arange(30)
    price = 900 + np.sin(days/4)*80 + np.random.normal(0,20,30)
    df = pd.DataFrame({"Day":days,"Price":price})
    st.line_chart(df.set_index("Day"))

    st.caption("Simulated mandi prices (₹/quintal)")

    st.markdown("---")

    st.subheader("💧 Irrigation Advice")
    moisture = st.slider("Soil Moisture", 0, 100, 40)
    rain_chance = st.slider("Rain Chance (%)", 0, 100, 30)

    if st.button("Get Irrigation Tip"):
        if rain_chance > 60:
            st.success("Skip irrigation — rainfall expected.")
        elif moisture < 30:
            st.warning("Light irrigation recommended in early morning.")
        else:
            st.info("Monitor crops; irrigation optional.")

# ----------------------- Footer -----------------------
st.markdown("---")
st.markdown(
    "<center><b>AgroGuide is live — powered by AI for farmers 🌱</b></center>",
    unsafe_allow_html=True
)
