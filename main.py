from flask import Flask, jsonify
import logging
import socket
import time
from datetime import datetime
app = Flask(__name__)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

start_time = datetime.now()
request_count = 0

STATSD_HOST = "127.0.0.1"
STATSD_PORT = 9999

def send_statsd_message(message: str):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (STATSD_HOST, STATSD_PORT))
        sock.close()
    except Exception as e:
        logging.warning(f"Не вдалося відправити повідомлення в StatsD: {e}")

@app.before_request
def before_request():
    global request_count
    request_count += 1
@app.route('/')
def home():
    logging.info('Сервіс працює')
    return 'Сервіс працює'

@app.route('/error')
def error():
    try:
        1/0
    except Exception as e:
        logging.exception(e)
        send_statsd_message(str(e))
        return 'Помилка, дивись логи'

@app.route('/status')
def status():
    uptime = datetime.now() - start_time
    data = {
        "uptime": uptime.total_seconds(),
        "request_count": request_count,
    }
    logging.info('Отримано запит на /status')
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=False)