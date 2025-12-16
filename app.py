"""
Intelligent AgroGuide - Streamlit app
Based on user's storyboard (Intelligent_AgroGuide_Storyboard (1).pptx). See file for full requirements. fileciteturn0file0

How to run:
1) pip install streamlit pandas numpy plotly pillow
2) streamlit run Intelligent_AgroGuide_streamlit_app.py

Notes:
- This is a self-contained demo that simulates AI outputs. Replace the `mock_ai_response`
  and `call_gemini()` placeholders with your real Gemini/GenAI calls.
- Animations are done with CSS + small HTML components for smooth, portable UI.

Author: ChatGPT (GPT-5 Thinking mini)
"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import random
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# ----------------------- Page config -----------------------
st.set_page_config(
    page_title="Intelligent AgroGuide",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------- Helper utils -----------------------

def header_animation():
    st.markdown(
        """
        <style>
        .hero {background: linear-gradient(90deg,#0f172a,#0b1220);padding:40px;border-radius:14px;color:white}
        .pulse {animation: pulse 2.6s infinite}
        @keyframes pulse {0%{transform:scale(1)}50%{transform:scale(1.02)}100%{transform:scale(1)} }
        .feature-card{background:white;border-radius:12px;padding:18px;margin:8px;box-shadow:0 6px 20px rgba(2,6,23,0.2)}
        .small{font-size:14px;color:#6b7280}
        </style>
        <div class='hero'>
          <h1 style='margin:0'>🌾 Intelligent AgroGuide</h1>
          <p style='margin:4px 0 0 0;color:#d1d5db'>AI-assistant for climate-smart farming — crop planning, pest detection, irrigation alerts, soil advice and market insights.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def two_column_feature(title, body, hint=""):
    st.markdown(f"<div class='feature-card'><h3 style='margin:0'>{title}</h3><p class='small'>{body}</p><p style='margin:0;font-size:13px;color:#111'>{hint}</p></div>", unsafe_allow_html=True)


def mock_ai_response(prompt: str) -> str:
    """Simple deterministic-but-randomized mock to simulate GenAI output."""
    # Keep outputs consistent for repeated prompts in a session
    seed = (hash(prompt) + 12345) % 10_000
    rnd = random.Random(seed)
    samples = [
        "Try drought-tolerant millets like ragi and bajra; use mulching to reduce evaporation.",
        "White insects likely whiteflies — use neem-spray or sticky traps; prune affected leaves.",
        "Irrigate lightly in the morning; avoid waterlogging; use drip if available.",
        "If pH > 8.0 consider gypsum and organic compost; prefer sorghum or legumes for rotation.",
        "Try garlic-chili spray and pheromone traps for organic pest control; rotate crops annually.",
    ]
    return rnd.choice(samples)


# ----------------------- Sidebar / persona -----------------------
with st.sidebar:
    st.header("👨‍🌾 Farmer profile")
    name = st.text_input("Name", "S. Muthuvel")
    location = st.text_input("Location", "Krishnagiri, Tamil Nadu")
    soil_type = st.selectbox("Dominant soil type", ["Loamy", "Sandy", "Clay", "Alkaline (saline)"])
    default_ph = 7.2 if soil_type != "Alkaline (saline)" else 8.2
    soil_ph = st.slider("Soil pH", 4.0, 10.0, float(default_ph), 0.1)
    st.divider()
    st.markdown("**Interests**")
    features_on = {
        "Crop Planner": st.checkbox("Intelligent Crop Planner", True),
        "Pest Detector": st.checkbox("AI Pest Detector (mock)", True),
        "Irrigation": st.checkbox("Irrigation Alerts", True),
        "Soil": st.checkbox("Soil Health Analyzer", True),
        "Market": st.checkbox("Smart Market Navigator", True),
    }
    st.divider()
    st.markdown("<small class='small'>Tip: Replace the mock AI with your Gemini key. See top of script for placeholder.</small>", unsafe_allow_html=True)

# ----------------------- Header -----------------------
header_animation()

# ----------------------- Main layout -----------------------
col1, col2 = st.columns((2,1))

with col1:
    st.markdown("### Live assistant — Ask AgroGuide")
    user_q = st.text_input("Describe your problem or ask a farming question:", value="White insects on tomato leaves — what should I do?")
    if st.button("Ask AgroGuide"):
        with st.spinner("Consulting the AgroGuide models..."):
            ai_out = mock_ai_response(user_q)
            st.success("Response ready")
            st.info(ai_out)

    st.markdown("---")
    st.markdown("### Feature panels")
    # Feature Cards
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        if features_on["Crop Planner"]:
            two_column_feature("🌱 Intelligent Crop Planner",
                               "Get drought- and soil-appropriate crop suggestions and simple seasonal timing.",
                               "Enter expected rainfall and cropping season below.")
    with fc2:
        if features_on["Pest Detector"]:
            two_column_feature("🔍 AI-driven Pest Detector",
                               "Upload a leaf photo (or use sample) and get likely pest diagnosis and organic remedies.",
                               "Image-based detection uses model APIs (mock here).")
    with fc3:
        if features_on["Market"]:
            two_column_feature("📈 Smart Market Navigator",
                               "Quick mandi price estimates + selling strategy guidance.",
                               "Choose crop and get simulated mandi rates.")

    st.markdown("---")
    # Crop Planner interactive
    st.subheader("Intelligent Crop Planner")
    rain_mm = st.slider("Expected monthly rainfall (mm)", 0, 500, 80)
    season = st.selectbox("Season", ["Kharif", "Rabi", "Summer"])
    if st.button("Get crop suggestions"):
        prompt = f"Suggest crops for {soil_type} soil, pH {soil_ph:.1f}, rainfall {rain_mm}mm in {season}"
        out = mock_ai_response(prompt)
        st.write("**Recommended crops & quick notes:**")
        st.success(out)

    st.markdown("---")
    # Pest Detector
    st.subheader("AI-driven Pest Detector — Upload leaf photo")
    uploaded = st.file_uploader("Choose a photo", type=["png","jpg","jpeg"])
    use_sample = st.button("Use sample leaf")
    if uploaded or use_sample:
        if uploaded:
            img = Image.open(uploaded).convert('RGB')
        else:
            # simple generated sample image
            img = Image.new('RGB', (600,400), color=(255,255,240))
            d = ImageDraw.Draw(img)
            d.text((20,20), "Sample leaf: white spots", fill=(20,40,20))
        st.image(img, caption="Uploaded / Sample leaf", use_column_width=True)
        if st.button("Analyze image"):
            with st.spinner("Running pest detector..."):
                # Placeholder for image model
                diagnosis = "Likely whitefly infestation. Recommend: neem oil spray, sticky traps, remove heavy-infested leaves."
                st.warning(diagnosis)
                st.markdown("**Organic treatment plan (3 steps):**\n1. Apply neem-kernel extract every 7 days.\n2. Introduce ladybird beetles if available.\n3. Monitor and prune infected leaves.")

    st.markdown("---")
    # Soil Health Analyzer
    st.subheader("Soil Health Analyzer")
    ph_note = f"Your soil pH: {soil_ph:.1f}"
    st.write(ph_note)
    if st.button("Explain soil advice"):
        advice = "Use organic compost and green manure to buffer pH. For alkaline soils, gypsum and organic matter help lower ESP and improve structure. Prefer legumes in rotation to improve nitrogen."
        st.info(advice)

with col2:
    st.markdown("### Quick dashboard")
    # Simple simulated price chart using plotly
    crops = ["Rice","Wheat","Tomato","Ragi","Maize","Bajra"]
    chosen = st.selectbox("Choose crop for price view", crops, index=3)
    days = np.arange(0,30)
    base = random.randint(800,1200)
    noise = np.random.normal(scale=15, size=days.shape)
    trend = np.linspace(0, random.uniform(-20,20), days.size)
    prices = np.round(base + trend + noise + (100*np.sin(days/6)), 2)
    df_prices = pd.DataFrame({"day": days.tolist(), "price": prices.tolist()})
    st.line_chart(df_prices.set_index('day'))
    st.caption("Simulated mandi price (₹/quintal) — for demo only")

    st.markdown("---")
    st.markdown("### Irrigation Alerts")
    next_day_rain = st.slider("Forecast chance of rain tomorrow (%)", 0, 100, 23)
    soil_moisture = st.slider("Soil moisture level (relative)", 0, 100, 42)
    if st.button("Irrigation advice"):
        if next_day_rain > 60 and soil_moisture > 40:
            st.success("Skip irrigation tomorrow — good rainfall expected and moisture is adequate.")
        elif soil_moisture < 30:
            st.warning("Irrigate lightly in the morning; prioritize drip or mulch to conserve water.")
        else:
            st.info("Monitor in the morning; consider a light irrigation if crop shows stress.")

    st.markdown("---")
    st.markdown("### Organic Farming Tips")
    tips = [
        "Make a garlic-chili insect spray: crush garlic + chili, steep in hot water, filter and dilute before spraying.",
        "Use mulching to reduce evaporation and suppress weeds.",
        "Rotate legumes every 2-3 seasons to restore soil nitrogen.",
        "Apply compost tea to improve soil microbiome.",
        "Use pheromone traps for fruit-borer monitoring.",
    ]
    if st.button("Show me an organic tip"):
        st.info(random.choice(tips))

    st.markdown("---")
    st.markdown("### Export & Logging")
    if st.button("Save current profile & log a note"):
        note = f"Profile saved for {name} at {location} — soil {soil_type} pH {soil_ph:.1f}"
        st.success(note)

# ----------------------- Footer / advanced notes -----------------------
st.markdown("---")
col_f1, col_f2 = st.columns([3,1])
with col_f1:
    st.markdown("### Deployment notes & Gemini integration")
    st.markdown(
        """
        This demo uses deterministic mock functions so you can prototype the UI and interactions.
        To connect a real generative model (e.g., Gemini) replace `mock_ai_response` with a
        function that calls your model, for example:

        ```python
        import google.generativeai as genai
        genai.configure(api_key='YOUR_API_KEY')
        def call_gemini(prompt):
            model = genai.GenerativeModel('gemini-1.5-flash')
            resp = model.generate_content(prompt)
            return resp.text
        ```

        Make sure to keep API keys out of source control and use environment variables.
        """,
    )
with col_f2:
    st.markdown("#### Credits")
    st.markdown("Built using Streamlit — UI, simple simulated AI, and helpful defaults for demoing the storyboard.")

# small celebratory animation using HTML
st.markdown(
    """
    <div style='text-align:center;margin-top:18px'>
      <div style='display:inline-block;padding:12px 18px;border-radius:999px;background:linear-gradient(90deg,#10b981,#06b6d4);color:white;box-shadow:0 8px 30px rgba(16,185,129,0.18)'>
         <strong>You're ready — AgroGuide is live 🚀</strong>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# END
