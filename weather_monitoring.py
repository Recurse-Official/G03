import requests

def get_weather(city_name):
    api_key = "e1ffa8c1b262cf030a36229de0ecb561"
    base_url = "http://api.openweathermap.org/data/2.5/weather"

    # Full URL with parameters
    complete_url = f"{base_url}?q={city_name}&appid={api_key}&units=metric"

    response = requests.get(complete_url)

    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather = data['weather'][0]

        print(f"City: {data['name']}, {data['sys']['country']}")
        print(f"Temperature: {main['temp']}°C")
        print(f"Weather: {weather['description'].capitalize()}")
        print(f"Humidity: {main['humidity']}%")
        print(f"Wind Speed: {data['wind']['speed']} m/s")
    else:
        print("City not found. Please enter a valid city name.")

# User input for city name
city_name = input("Enter the name of the city: ")
get_weather(city_name)
