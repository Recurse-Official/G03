import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import requests
from datetime import datetime
import geocoder

# Load the pre-trained model
model = load_model("stage_classification_model.h5")

# Define available stages
stages = [
    "exterior finishing",
    "foundation",
    "ssuperstructure",
    "interior finishing",
    "site cleaning",
]

# Define Weather Emoji Map
emoji_map = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
}

# Function: Detect Current Location
def get_current_location():
    g = geocoder.ip('me')  # Get current location using IP
    if g.ok:
        return g.city
    else:
        return None

# Function: Weather Information
def get_weather(city_name):
    api_key = "e1ffa8c1b262cf030a36229de0ecb561"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather = data['weather'][0]
        weather_emoji = emoji_map.get(weather['main'].lower(), "🌈")

        return {
            "city": data['name'],
            "country": data['sys']['country'],
            "temp": main['temp'],
            "description": weather['description'].capitalize(),
            "humidity": main['humidity'],
            "wind_speed": data['wind']['speed'],
            "emoji": weather_emoji,
        }
    else:
        return None

# Function: Weekly Forecast
def get_weekly_forecast(city_name):
    api_key = "e1ffa8c1b262cf030a36229de0ecb561"
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric"

    response = requests.get(complete_url)
    if response.status_code == 200:
        data = response.json()
        forecast_list = []
        for i in range(0, len(data['list']), 8):  # 8 intervals per day in 3-hour steps
            forecast = data['list'][i]
            date = datetime.fromtimestamp(forecast['dt']).strftime('%A, %d %b %Y')
            temp = forecast['main']['temp']
            description = forecast['weather'][0]['description']
            weather_emoji = emoji_map.get(forecast['weather'][0]['main'].lower(), "🌈")
            forecast_list.append((date, temp, description.capitalize(), weather_emoji))
        return forecast_list
    else:
        return None

# Function: Recommendations based on weather
def generate_recommendations(forecast):
    recommendations = []
    for day, temp, description, emoji in forecast:
        if "rain" in description.lower() or "drizzle" in description.lower():
            recommendations.append(f"{day}: {emoji} Avoid superstructure work; focus on indoor tasks.")
        elif "clear" in description.lower() or "clouds" in description.lower():
            recommendations.append(f"{day}: {emoji} Good day for external activities like roofing or finishing.")
        elif "thunderstorm" in description.lower():
            recommendations.append(f"{day}: {emoji} Avoid all outdoor work; ensure site safety.")
        elif "snow" in description.lower():
            recommendations.append(f"{day}: {emoji} Delay outdoor work and monitor material conditions.")
        else:
            recommendations.append(f"{day}: {emoji} Proceed based on project priorities.")
    return recommendations

# Function: Project Stage Verification
def stage_verification(uploaded_file, selected_stage):
    if uploaded_file:
        with open("temp_image.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load and preprocess the image
        img_path = "temp_image.jpg"
        img = load_img(img_path, target_size=(150, 150))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict stage
        predictions = model.predict(img_array)
        class_labels = stages
        predicted_stage = class_labels[np.argmax(predictions)]
        return predicted_stage
    else:
        return None

# Streamlit Dashboard Layout
st.set_page_config(layout="wide", page_title="Construction Dashboard")

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")
selected_option = st.sidebar.selectbox(
    "Select Dashboard Section",
    ["Project Verification", "Weather Information"]
)

# Main Layout
st.title("🏗️ Construction Project Dashboard")

if selected_option == "Project Verification":
    # Project Verification Section
    st.header("🔍 Project Stage Verification")
    project_name = st.text_input("Project Name")
    project_id = st.text_input("Project ID")
    description = st.text_area("Project Description")

    st.write("### Stage Details")
    selected_stage = st.selectbox("Select Stage", options=stages)
    uploaded_file = st.file_uploader("Upload Stage Image", type=["jpg", "png", "jpeg"])

    if st.button("Verify Stage"):
        if not all([project_name, project_id, selected_stage, uploaded_file]):
            st.error("Please fill in all details and upload an image.")
        else:
            predicted_stage = stage_verification(uploaded_file, selected_stage)
            if predicted_stage:
                st.write(f"**Predicted Stage:** {predicted_stage}")
                if predicted_stage == selected_stage:
                    st.success("STAGE VERIFIED: Selected stage matches the predicted stage.")
                else:
                    st.error("STAGE MISMATCH: Selected stage does not match the predicted stage.")
            else:
                st.error("Error in processing the image. Please try again.")

elif selected_option == "Weather Information":
    # Weather Information Section
    st.header("🌤️ Weather Information")
    city_name = get_current_location() or st.text_input("Enter City Name")

    if st.button("Get Weather & Recommendations"):
        weather_data = get_weather(city_name)
        if weather_data:
            st.write(f"### Today's Weather in {weather_data['city']}, {weather_data['country']}")
            st.write(f"**Temperature:** {weather_data['temp']}°C {weather_data['emoji']}")
            st.write(f"**Description:** {weather_data['description']}")
            st.write(f"**Humidity:** {weather_data['humidity']}%")
            st.write(f"**Wind Speed:** {weather_data['wind_speed']} m/s")

            weekly_forecast = get_weekly_forecast(city_name)
            if weekly_forecast:
                st.write("### 7-Day Weather Recommendations")
                recommendations = generate_recommendations(weekly_forecast)
                for rec in recommendations:
                    st.write(rec)
            else:
                st.error("Unable to fetch weekly forecast.")
        else:
            st.error("Unable to fetch weather data. Please check the city name.")
