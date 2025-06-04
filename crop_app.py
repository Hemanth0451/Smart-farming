import streamlit as st
import pandas as pd
import joblib
import requests
import pyttsx3
from crop_data import crop_info

from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("AIzaSyDRWO2rU0Vy_VsaxPSdwQI4SqKUzk2T4fs")


# --- Load ML Model ---
model = joblib.load("crop_model.pkl")

# --- Crop Name Mapping (for consistency) ---
crop_name_mapping = {
    "groundnut": "ground nuts",
    "millet": "millets",
    "pulse": "pulses"
    # Add more if needed
}

# --- Weather Function ---
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["main"]["temp"], data["main"]["humidity"]
    else:
        return None, None

# --- Voice Output Function ---
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.say(text)
    engine.runAndWait()

# --- Fertilizer Recommendation ---
def recommend_fertilizer(n, p, k):
    recommendation = ""
    if n < 90:
        recommendation += "🌿 Nitrogen is low. Use Urea or Ammonium Sulphate.\n"
    elif n > 120:
        recommendation += "🚫 Nitrogen is high. Avoid nitrogen-rich fertilizers.\n"

    if p < 40:
        recommendation += "🌿 Phosphorus is low. Use Single Super Phosphate (SSP).\n"
    elif p > 60:
        recommendation += "🚫 Phosphorus is high. Avoid over-fertilizing.\n"

    if k < 40:
        recommendation += "🌿 Potassium is low. Use Muriate of Potash (MOP).\n"
    elif k > 60:
        recommendation += "🚫 Potassium is high. Reduce potash-based fertilizers.\n"

    return recommendation if recommendation else "✅ NPK levels are in optimal range. No extra fertilizers needed."

# --- UI Header ---
st.markdown(
    "<h1 style='font-size: 2 rem;'>🌾 Smart Crop Recommendation System</h1>",
    unsafe_allow_html=True
)


# --- Weather Input ---
city = st.text_input("Enter your city name (e.g. Kadapa,IN):")
if city:
    temperature, humidity = get_weather(city)
    if temperature is not None:
        st.success(f"🌡 Temperature: {temperature}°C  |  💧 Humidity: {humidity}%")
    else:
        st.error("❌ Failed to fetch weather data. Check city name or API key.")
else:
    temperature, humidity = None, None

# --- Input Fields ---
n = st.number_input("Nitrogen (N)", min_value=0)
p = st.number_input("Phosphorus (P)", min_value=0)
k = st.number_input("Potassium (K)", min_value=0)

temp = st.number_input("Temperature (°C)", value=temperature if temperature else 25.0)
hum = st.number_input("Humidity (%)", value=humidity if humidity else 50.0)

ph = st.number_input("pH value", min_value=0.0, max_value=14.0, value=6.5)
rain = st.number_input("Rainfall (mm)", min_value=0.0, value=100.0)

# --- Prediction Button ---
if st.button("Predict Crop"):
    prediction = model.predict([[n, p, k, temp, hum, ph, rain]])
    crop_name = prediction[0].lower()
    crop_key = crop_name_mapping.get(crop_name, crop_name)

    st.success(f"🌱 Recommended Crop: **{crop_name.title()}**")
    speak_text(f"The recommended crop is {crop_name}")

    # --- Fertilizer Suggestion ---
    fertilizer_advice = recommend_fertilizer(n, p, k)
    st.info("🧪 **Fertilizer Suggestion:**")
    st.write(fertilizer_advice)
    speak_text(fertilizer_advice.replace('\n', ' '))

    # --- Crop Growing Tips ---
    crop_tips = {
        "rice": "Keep soil flooded, apply fertilizer in 3 stages, and control weeds weekly.",
        "wheat": "Sow in cool weather, irrigate after 20 days, and apply nitrogen in 2 doses.",
        "maize": "Ensure full sunlight, water regularly, and protect from pests like stem borer.",
        "cotton": "Use deep well-drained soil, avoid waterlogging, and spray neem-based pesticide.",
        "sugarcane": "Use well-rotted compost, ensure drip irrigation, and remove dry leaves regularly.",
        "banana": "Maintain high humidity, use potassium-rich fertilizer, and support the plant during wind.",
        "millets": "Tolerates drought, grow in sandy soil, and avoid over-irrigation.",
        "ground nuts": "Use sandy loam soil, apply gypsum during flowering, and avoid waterlogging for better yield.",
        "orange": "Needs well-drained sandy loam soil with pH between 5.5 and 6.5. Regular watering and good sunlight are essential.",
    }

    tips = crop_tips.get(crop_key, "Sorry, no tips available for this crop.")
    st.info("💡 **Crop Growing Tips:**")
    st.write(tips)
    speak_text(tips)

    # --- Detailed Crop Info ---
    if crop_key in crop_info:
        info = crop_info[crop_key]
        st.subheader("📘 Crop Details:")
        st.write(f"🌡️ Ideal Temperature: {info['temperature']}")
        st.write(f"🌱 Ideal pH: {info['ph']}")
        st.write(f"🌧️ Ideal Rainfall: {info['rainfall']}")
        st.write(f"📝 Tips: {info['tips']}")
        st.write(f"⏳ Harvest Time: {info['harvest_time']}")
    else:
        st.warning("ℹ️ No detailed info available for this crop.")
