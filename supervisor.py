import streamlit as st
import mysql.connector
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
import os
import numpy as np
import requests
from datetime import datetime
import geocoder



# MySQL Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Replace with your MySQL host
        user="root",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
        database="costruction"  # Replace with your MySQL database name
    )

# Load the pre-trained model
model = load_model("stage_classification_model.h5")

# Define available stages
stages = [
    "exterior finishing",
    "foundation",
    "superstructure",
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
    api_key = "USE_API_KEY_HERE"
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
    api_key = "USE_API_KEY_HERE"
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

# Streamlit Dashboard Layout
st.set_page_config(layout="wide", page_title="Construction Dashboard")

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")
selected_option = st.sidebar.selectbox(
    "Select Dashboard Section",
    ["Project Verification", "Weather Information"]
)

# Function to save a project with an image to the database
def save_project(project_id, project_name, project_description, verified_stage, day_no, image_path):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO projects (project_id, project_name, project_description, verified_stage, day_no, image_path)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (project_id, project_name, project_description, verified_stage, day_no, image_path))
    conn.commit()
    cursor.close()
    conn.close()

# Project Stage Verification
def stage_verification(uploaded_file, selected_stage):
    if uploaded_file:
        img_path = "temp_image.jpg"
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load and preprocess the image
        img = load_img(img_path, target_size=(150, 150))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict stage
        predictions = model.predict(img_array)
        predicted_stage = stages[np.argmax(predictions)]
        return predicted_stage
    else:
        return None

# Main Layout
st.title("🏗️ Construction Project Dashboard")

if selected_option == "Project Verification":
    # Project Verification Section
    st.header("🔍 Project Stage Verification")

    # Manually Enter Project Details
    project_id = st.text_input("Enter Project ID")
    project_name = st.text_input("Enter Project Name")
    project_description = st.text_area("Enter Project Description")
    
    selected_stage = st.selectbox("Select Stage", options=stages)
    day_no = st.number_input("Enter Day Number (e.g., 1, 2, ...)", min_value=1, step=1)
    uploaded_file = st.file_uploader("Upload Stage Image", type=["jpg", "png", "jpeg"])

    # Save Project Button
    if st.button("Save Project"):
        if not all([project_id, project_name, project_description, selected_stage, day_no, uploaded_file]):
            st.error("Please fill in all details and upload an image.")
        else:
            # Save the project details and image to the database
            img_path = "uploads/" + project_id + ".jpg"  # Save image with project ID name
            if not os.path.exists("uploads"):
                os.makedirs("uploads")
            with open(img_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            save_project(project_id, project_name, project_description, selected_stage, day_no, img_path)

            st.success("Project details have been saved successfully!")

            # Optionally verify the stage
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
        if city_name:
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
        else:
            st.error("Please enter a city name.")
