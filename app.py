import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageDraw
import google.generativeai as genai

# ----------------------- API Key & Config -----------------------
# Ensure this matches the key name in your .streamlit/secrets.toml
GEMINI_API_KEY = st.secrets.get("GENAI_API_KEY", None)

st.set_page_config(
    page_title="Intelligent AgroGuide",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- Gemini Setup -----------------------
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("⚠️ GENAI_API_KEY not found in Streamlit Secrets.")

def call_gemini(prompt: str, image=None) -> str:
    """Sends text and optional image to Gemini 1.5 Flash."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # System instructions included in the prompt for context
        full_prompt = (
            f"You are an expert Indian agriculture advisor. "
            f"Answer in Tamil in a clear, farmer-friendly way.\n\n"
            f"Question: {prompt}"
        )
        
        if image:
            response = model.generate_content([full_prompt, image])
        else:
            response = model.generate_content(full_prompt)
            
        return response.text.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ----------------------- UI Styling -----------------------
def header_animation():
    st.markdown(
        """
        <style>
        .hero {
            background: linear-gradient(90deg,#065f46,#022c22);
            padding:40px;
            border-radius:14px;
            color:white;
            margin-bottom: 25px;
        }
        .small {color:#d1fae5;font-size:16px}
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
    soil_type = st.selectbox("Soil Type", ["Loamy", "Sandy", "Clay", "Red Soil", "Black Soil", "Alkaline"])
    soil_ph = st.slider("Soil pH", 4.0, 10.0, 7.2, 0.1)

    st.divider()
    if GEMINI_API_KEY:
        st.success("✅ Gemini AI Connected")
    else:
        st.error("❌ API Key Missing")

# ----------------------- Main Layout -----------------------
header_animation()

col1, col2 = st.columns((2, 1))

# ================= LEFT COLUMN: AI Interaction =================
with col1:
    st.subheader("💬 Ask AgroGuide")
    user_q = st.text_input(
        "Describe your farming problem:",
        "White insects on tomato leaves, what should I do?"
    )

    if st.button("Ask AgroGuide", use_container_width=True):
        with st.spinner("Analyzing with Gemini AI..."):
            answer = call_gemini(user_q)
            st.success(answer)

    st.markdown("---")

    st.subheader("🌱 Intelligent Crop Planner")
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        rainfall = st.slider("Monthly Rainfall (mm)", 0, 500, 100)
    with r_col2:
        season = st.selectbox("Season", ["Kharif", "Rabi", "Summer"])

    if st.button("Get Crop Suggestions", use_container_width=True):
        planner_prompt = (
            f"Based on Soil: {soil_type}, pH: {soil_ph}, "
            f"Rainfall: {rainfall}mm, and Season: {season}, "
            f"suggest the best crops to plant."
        )
        with st.spinner("Planning crops..."):
            st.info(call_gemini(planner_prompt))

    st.markdown("---")

    st.subheader("🔍 Pest Detection")
    uploaded = st.file_uploader("Upload a leaf image", type=["jpg", "png", "jpeg"])

    if uploaded:
        image_data = Image.open(uploaded)
        st.image(image_data, caption="Uploaded Image", use_container_width=True)
        
        if st.button("Analyze Pest & Disease", use_container_width=True):
            with st.spinner("Scanning image..."):
                pest_prompt = "Examine this leaf image. Identify any pests or diseases and suggest organic treatments in Tamil."
                st.warning(call_gemini(pest_prompt, image=image_data))
    else:
        st.info("Please upload an image to use the Pest Detection feature.")

# ================= RIGHT COLUMN: Analytics =================
with col2:
    st.subheader("📈 Market Price Trends")
    crop = st.selectbox("Select Crop", ["Rice", "Tomato", "Ragi", "Maize", "Wheat"])

    days = np.arange(30)
    prices = 900 + np.sin(days / 4) * 80 + np.random.normal(0, 20, 30)
    df = pd.DataFrame({"Day": days, "Price": prices})
    st.line_chart(df.set_index("Day"))
    st.caption(f"Simulated {crop} mandi prices (₹/quintal)")

    st.markdown("---")

    st.subheader("💧 Irrigation Advice")
    moisture = st.slider("Soil Moisture %", 0, 100, 40)
    rain_chance = st.slider("Rain Chance %", 0, 100, 30)

    if st.button("Get Irrigation Advice", use_container_width=True):
        irr_prompt = (
            f"Current soil moisture is {moisture}% and rain probability is {rain_chance}%. "
            "Should I irrigate today? Answer in Tamil."
        )
        st.info(call_gemini(irr_prompt))

# ----------------------- Footer -----------------------
st.markdown("---")
st.markdown(
    "<center><b>AgroGuide is live — smart farming made simple 🌱</b></center>",
    unsafe_allow_html=True,
)
