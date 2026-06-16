import flet as ft
from cfg_weather import get_weather_data  # Импортируем новую функцию со словарем


def main(page: ft.Page):
    page.title = "Weather App"
    page.window_width = 450
    page.window_height = 680
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1A1C23"

    page.vertical_alignment = ft.VerticalAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user = ft.TextField(
        label="Введите город",
        width=320,
        border_radius=12,
        bgcolor="#2D3748",
    )

    # Вместо одного ft.Text создаем отдельные элементы для каждого показателя
    temp_text = ft.Text("", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)
    feels_like_text = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_200)

    # Контейнеры для детальной информации (ветер, давление и т.д.)
    wind_text = ft.Text("", size=14)
    humidity_text = ft.Text("", size=14)
    geo_text = ft.Text("", size=14, weight=ft.FontWeight.W_500)

    forecast_row = ft.Row(
        spacing=10,
        scroll=ft.ScrollMode.AUTO
    )

    # Невидимый в начале блок, где будет показываться погода
    result_card = ft.Container(
        visible=False,  # Скрыт, пока не нажали кнопку
        bgcolor="#232732",
        padding=20,
        border_radius=15,
        width=320,
        content=ft.Column([
            ft.Row([geo_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([temp_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([feels_like_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(color="#2D3748"),
            ft.Row([ft.Icon(ft.Icons.AIR, size=18), wind_text], alignment=ft.MainAxisAlignment.START),
            ft.Row([ft.Icon(ft.Icons.COMPASS_CALIBRATION, size=18), humidity_text],
                   alignment=ft.MainAxisAlignment.START),
            ft.Divider(color="#2D3748"),

            ft.Row([
                ft.Text("Прогноз на 7 дней", size=14, color=ft.Colors.BLUE_GREY_100, weight=ft.FontWeight.W_600),
            ], alignment=ft.MainAxisAlignment.START),
            ft.Container(content=forecast_row, margin=ft.margin.only(5)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    )

    # Функция обработки клика
    def get_info(e):
        # Очищаем текст от случайных пробелов по краям
        city_name = user.value.strip()

        # 1. Проверка на длину
        if len(city_name) < 2:
            return

        # 2. ЖЁСТКИЙ ФИЛЬТР: Если ввели только цифры (типа 123, 9999 и т.д.)
        if city_name.isdigit():
            geo_text.value = "❌ Название города не может быть числом"
            temp_text.value = ""
            feels_like_text.value = ""
            wind_text.value = ""
            humidity_text.value = ""
            result_card.visible = True
            page.update()
            return  # Выходим из функции, дальше код идти не будет

        # Если проверки пройдены, делаем нормальный запрос
        data = get_weather_data(city_name)

        if data and data.get("success"):
            geo_text.value = f"📍 {city_name.capitalize()}, {data['country']}"
            temp_text.value = f"{data['temp']}°C"
            feels_like_text.value = f"Ощущается как {data['feels_like']}°C"
            wind_text.value = f"Ветер: {data['wind_speed']} м/с"
            humidity_text.value = f"Давление/Влажность: {data['humidity']} мм.рт"

            forecast_row.controls.clear()

            days_forecast = data.get("forecast",[
                {"day": "Пн", "temp": "", },
                {"day": "Вт", "temp": "", },
                {"day": "Ср", "temp": "", },
                {"day": "Чт", "temp": "", },
                {"day": "Пт", "temp": "", },
                {"day": "Сб", "temp": "", },
                {"day": "Вс", "temp": "", },
            ])

            for day_data in days_forecast:
                card = ft.Container(
                    bgcolor="#2D3748",
                    padding=10,
                    border_radius=10,
                    width=65,  # Фиксированная ширина карточки дня
                    content=ft.Column([
                        ft.Text(day_data["day"], size=12, weight=ft.FontWeight.W_500, color=ft.Colors.BLUE_GREY_200),
                        ft.Text(day_data["icon"], size=20),
                        ft.Text(f"{day_data['temp']}", size=13, weight=ft.FontWeight.BOLD),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
                )
                forecast_row.controls.append(card)

            result_card.visible = True
        else:
            geo_text.value = "❌ Город не найден"
            temp_text.value = ""
            feels_like_text.value = ""
            wind_text.value = ""
            humidity_text.value = ""
            result_card.visible = True

        page.update()

    # Динамическая кнопка
    submit_btn = ft.Container(
        content=ft.Text("Получить", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        alignment=ft.alignment.center,
        width=320,
        height=50,
        bgcolor="#3182CE",
        border_radius=12,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        scale=1.0,
        on_click=get_info
    )

    def on_hover(e):
        submit_btn.bgcolor = "#2B6CB0" if e.data == "true" else "#3182CE"
        submit_btn.scale = 1.04 if e.data == "true" else 1.0
        submit_btn.update()

    submit_btn.on_hover = on_hover

    # Главная колонка приложения
    main_layout = ft.Column(
        controls=[
            ft.Text("Введи город и узнай погоду 🌤️", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(height=10, color="transparent"),
            user,
            submit_btn,
            ft.Divider(height=10, color="transparent"),
            result_card,  # Сюда вставляем нашу карточку с результатами
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    page.add(main_layout)


if __name__ == "__main__":
    import os
    # Render сам назначит порт, а если мы запускаем дома — включится 8502
    port = int(os.environ.get("PORT", 8502))
    # Запускаем Flet как веб-сервер, который слушает все входящие соединения
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)
