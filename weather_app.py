import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("WEATHER_API_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route("/", methods=["GET", "POST"])
def home():
    weather = None
    error = None

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        if not city:
            error = "Please enter a city name."

        else:

            params = {
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            }

            try:

                response = requests.get(
                    WEATHER_URL,
                    params=params,
                    timeout=10
                )

                if response.status_code == 200:

                    data = response.json()

                    weather = {
                        "city": data["name"],
                        "country": data["sys"]["country"],
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "wind_speed": data["wind"]["speed"],
                        "description": data["weather"][0]["description"]
                    }

                elif response.status_code == 404:

                    error = "City not found."

                else:

                    error = (
                        f"Weather API error: "
                        f"{response.status_code}"
                    )

            except requests.RequestException as e:

                error = f"Could not connect to weather service: {e}"

    return render_template(
        "index.html",
        weather=weather,
        error=error
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )