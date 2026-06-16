import requests
from datetime import datetime
import os
api_key = os.environ.get("WEATHER_API_KEY")


def get_weather_data(city):
    # Используем /forecast вместо /weather для получения прогноза
    # Добавили &lang=ru, чтобы описание погоды (если нужно) было на русском
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric&lang=ru"

    try:
        response = requests.get(url)
        data = response.json()

        # ИСПРАВЛЕНО: проверяем, что код ТАКИ РАВЕН 200 (запрос успешный)
        # OpenWeatherMap иногда присылает cod как строку "200", а иногда как число 200, поэтому приводим к строке
        if str(data.get("cod")) == "200":

            # Самая первая запись в списке — это текущая погода
            current_weather = data["list"][0]
            city_info = data["city"]

            # Собираем прогноз (так как API выдает данные каждые 3 часа,
            # мы возьмем только те точки, которые приходятся на 12:00 дня)
            forecast_list = []
            days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

            for item in data["list"]:
                # Проверяем, есть ли "12:00:00" в строке даты
                if "12:00:00" in item["dt_txt"]:
                    date_obj = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    day_name = days_of_week[date_obj.weekday()]

                    # Мапим иконки OpenWeatherMap в эмодзи
                    owm_icon = item["weather"][0]["icon"]
                    emoji = "☀️"
                    if "d" in owm_icon:  # дневные иконки
                        if owm_icon in ["01d"]:
                            emoji = "☀️"
                        elif owm_icon in ["02d", "03d", "04d"]:
                            emoji = "🌤️"
                        elif owm_icon in ["09d", "10d"]:
                            emoji = "🌧️"
                        elif owm_icon in ["11d"]:
                            emoji = "⛈️"
                        elif owm_icon in ["13d"]:
                            emoji = "❄️"
                        elif owm_icon in ["50d"]:
                            emoji = "🌫️"

                    forecast_list.append({
                        "day": day_name,
                        "temp": f"{round(item['main']['temp'])}°",
                        "icon": emoji
                    })

            # Если вдруг список прогноза оказался пуст (например, запустили поздно ночью),
            # просто возьмем несколько обычных элементов из списка подряд
            if not forecast_list:
                for item in data["list"][:5]:
                    date_obj = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
                    day_name = days_of_week[date_obj.weekday()]
                    forecast_list.append({
                        "day": day_name,
                        "temp": f"{round(item['main']['temp'])}°",
                        "icon": "🌤️"
                    })

            return {
                "success": True,
                "temp": round(current_weather["main"]["temp"]),
                "wind_speed": round(current_weather["wind"]["speed"], 1),
                "feels_like": round(current_weather["main"]["feels_like"]),
                "humidity": current_weather["main"]["humidity"],
                "country": city_info["country"],
                "forecast": forecast_list  # Передаем массив для карточек во Flet
            }
        else:
            return {"success": False}

    except Exception as e:
        print(f"Ошибка: {e}")
        return {"success": False}