from flask import Flask, render_template, jsonify, request
import random
import time
import json
import os
import socket
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)

# Глобальные переменные для хранения состояния игры
current_game = {"number": None, "sequence": [], "start_time": None, "steps": 0}

# История игр
history = []


def get_local_ip():
    try:
        # Получаем IP-адрес компьютера в локальной сети
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def generate_qr_code():
    # Генерируем QR-код с URL приложения
    if os.environ.get("PYTHONANYWHERE_DOMAIN"):
        # Если запущено на PythonAnywhere
        url = f"https://{os.environ.get('PYTHONANYWHERE_DOMAIN')}"
    else:
        # Если запущено локально
        ip = get_local_ip()
        url = f"http://{ip}:5000"

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Конвертируем изображение в base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str, url


def get_next_number(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1


@app.route("/")
def index():
    qr_code, url = generate_qr_code()
    return render_template("index.html", qr_code=qr_code, url=url)


@app.route("/start_random")
def start_random():
    current_game["number"] = random.randint(1, 1000)
    current_game["sequence"] = [current_game["number"]]
    current_game["start_time"] = time.time()
    current_game["steps"] = 0
    return jsonify(
        {"number": current_game["number"], "sequence": current_game["sequence"]}
    )


@app.route("/start_custom", methods=["POST"])
def start_custom():
    number = int(request.json["number"])
    if number <= 0:
        return jsonify({"error": "Число должно быть положительным"}), 400

    current_game["number"] = number
    current_game["sequence"] = [number]
    current_game["start_time"] = time.time()
    current_game["steps"] = 0
    return jsonify(
        {"number": current_game["number"], "sequence": current_game["sequence"]}
    )


@app.route("/check_answer", methods=["POST"])
def check_answer():
    answer = int(request.json["answer"])
    next_number = get_next_number(current_game["number"])

    if answer == next_number:
        current_game["number"] = next_number
        current_game["sequence"].append(next_number)
        current_game["steps"] += 1

        if next_number == 1:
            # Игра завершена
            game_time = time.time() - current_game["start_time"]
            history.append(
                {
                    "start": current_game["sequence"][0],
                    "steps": current_game["steps"],
                    "time": game_time,
                    "sequence": current_game["sequence"],
                }
            )
            return jsonify(
                {
                    "correct": True,
                    "game_over": True,
                    "sequence": current_game["sequence"],
                    "time": game_time,
                }
            )

        return jsonify(
            {
                "correct": True,
                "next_number": next_number,
                "sequence": current_game["sequence"],
            }
        )
    else:
        return jsonify({"correct": False, "expected": next_number})


@app.route("/history")
def get_history():
    return jsonify(history)


if __name__ == "__main__":
    # Определяем, запущено ли приложение на PythonAnywhere
    if os.environ.get("PYTHONANYWHERE_DOMAIN"):
        # На PythonAnywhere не нужно указывать host и port
        app.run()
    else:
        # Локальный запуск
        app.run(host="0.0.0.0", port=5000, debug=True)
