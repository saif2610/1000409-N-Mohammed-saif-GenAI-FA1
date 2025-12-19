"""
Intelligent AgroGuide - Streamlit App
(Smart fallback + Crash-proof Gemini integration)
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
from PIL import Image, ImageDraw

# ----------------------- Page config -----------------------
st.set_page_config(
    page_title="Intelligent AgroGuide",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- API Key (Streamlit Secrets) -----------------------
GEMINI_API_KEY = st.secrets.get("GENAI_API_KEY", None)

# ----------------------- SAFE Gemini Loader -----------------------
def get_gemini():
    try:
        import google.generativeai as genai
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            return genai
        return None
    except ModuleNotFoundError:
        return None

# ----------------------- SMART MOCK AI (NO RANDOM WRONG ANSWERS) -----------------------
def mock_ai_response(prompt: str) -> str:
    p = prompt.lower()

    # Pest / insect detection
    if any(word in p for word in ["white insect", "whitefly", "tomato", "leaf", "pest"]):
        return (
            "White insects on tomato leaves are usually whiteflies. "
            "Spray neem oil or neem seed kernel extract every 7 days, "
            "remove heavily infected leaves, and use yellow sticky traps "
            "to control their spread."
        )

    # Crop planning
    if any(word in p for word in ["crop", "rainfall", "season", "soil"]):
        return (
            "Based on soil type and rainfall, crops like ragi, bajra, "
            "sorghum, or pulses are suitable options. "
            "Choose crops that match local climate conditions."
        )

    # Irrigation
    if any(word in p for word in ["irrigation", "water", "moisture"]):
        return (
            "Irrigate early in the morning to reduce evaporation losses. "
            "Use drip irrigation or mulching to conserve water."
        )

    # Soil health
    if "ph" in p or "soil health" in p:
        return (
            "Add organic compost and green manure to improve soil health. "
            "Crop rotation with legumes helps restore nutrients naturally."
        )

    # Default safe response
    return (
        "Maintain regular crop monitoring, use organic inputs where possible, "
        "and follow climate-appropriate farming practices."
    )

# ----------------------- GEMINI CALL -----------------------
def call_gemini(prompt: str) -> str:
    genai = get_gemini()
    if not genai:
        return mock_ai_response(prompt)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"You are an expert Indian agriculture advisor.\n"
            f"Give clear, practical, farmer-friendly advice.\n\n"
            f"Question: {prompt}"
        )
        return response.text.strip()
    except Exception:
        return mock_ai_response(prompt)

def agro_ai(prompt: str) -> str:
    if GEMINI_API_KEY:
        return call_gemini(prompt)
    return mock_ai_response(prompt)

# ----------------------- Styling -----------------------
def header_animation():
    st.markdown(
        """
        <style>
        .hero {
            background: linear-gradient(90deg,#065f46,#022c22);
            padding:40px;
            border-radius:14px;
            color:white;
        }
        .small {color:#d1fae5;font-size:14px}
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
    if GEMINI_API_KEY and get_gemini():
        st.success("Gemini AI Connected")
    else:
        st.info("Demo Mode (Smart Fallback AI)")

# ----------------------- Header -----------------------
header_animation()

# ----------------------- Main Layout -----------------------
col1, col2 = st.columns((2, 1))

# ================= LEFT COLUMN =================
with col1:
    st.subheader("💬 Ask AgroGuide")
    user_q = st.text_input(
        "Describe your farming problem:",
        "White insects on tomato leaves, what should I do?"
    )

    if st.button("Ask AgroGuide"):
        with st.spinner("Analyzing your question..."):
            st.success(agro_ai(user_q))

    st.markdown("---")

    st.subheader("🌱 Intelligent Crop Planner")
    rainfall = st.slider("Expected Monthly Rainfall (mm)", 0, 500, 100)
    season = st.selectbox("Season", ["Kharif", "Rabi", "Summer"])

    if st.button("Get Crop Suggestions"):
        prompt = (
            f"Soil type: {soil_type}, pH: {soil_ph}, "
            f"Rainfall: {rainfall}mm, Season: {season}"
        )
        st.info(agro_ai(prompt))

    st.markdown("---")

    st.subheader("🔍 Pest Detection (Demo)")
    uploaded = st.file_uploader("Upload a leaf image", ["jpg", "png", "jpeg"])

    if uploaded:
        image = Image.open(uploaded)
    else:
        image = Image.new("RGB", (500, 300), "#fefce8")
        draw = ImageDraw.Draw(image)
        draw.text((20, 20), "Sample Leaf Image", fill="green")

    st.image(image, use_column_width=True)

    if st.button("Analyze Pest"):
        st.warning(agro_ai("White insects on tomato leaves"))

# ================= RIGHT COLUMN =================
with col2:
    st.subheader("📈 Market Price Trends")
    crop = st.selectbox("Select Crop", ["Rice", "Tomato", "Ragi", "Maize", "Wheat"])

    days = np.arange(30)
    prices = 900 + np.sin(days / 4) * 80 + np.random.normal(0, 20, 30)
    df = pd.DataFrame({"Day": days, "Price": prices})

    st.line_chart(df.set_index("Day"))
    st.caption("Simulated mandi prices (₹/quintal)")

    st.markdown("---")

    st.subheader("💧 Irrigation Advice")
    moisture = st.slider("Soil Moisture Level", 0, 100, 40)
    rain_chance = st.slider("Rain Chance (%)", 0, 100, 30)

    if st.button("Get Irrigation Advice"):
        if rain_chance > 60:
            st.success("Skip irrigation — rainfall expected.")
        elif moisture < 30:
            st.warning("Light irrigation recommended early morning.")
        else:
            st.info("Monitor crop condition; irrigation optional.")

# ----------------------- Footer -----------------------
st.markdown("---")
st.markdown(
    "<center><b>AgroGuide is live — smart farming made simple 🌱</b></center>",
    unsafe_allow_html=True,
)
