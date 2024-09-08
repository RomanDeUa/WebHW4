from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from threading import Thread
import socket
import json
from datetime import datetime
import os


# Створюємо директорію storage, якщо її немає
if not os.path.exists('storage'):
    os.makedirs('storage')

# Створюємо файл data.json, якщо його немає
data_file_path = 'storage/data.json'
if not os.path.exists(data_file_path):
    with open(data_file_path, 'w') as f:
        json.dump({}, f)


app = Flask(__name__)

# Обробка статичних файлів
@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/logo.png')
def serve_logo():
    return send_from_directory('.', 'logo.png')

# Обробка головної сторінки
@app.route('/')
def index():
    return render_template('index.html')

# Обробка сторінки з повідомленнями
@app.route('/message.html', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        data = {
            'username': username,
            'message': message
        }
        send_to_socket(data)
        return redirect(url_for('index'))
    return render_template('message.html')

# Обробка помилки 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Функція для передачі даних через сокет
def send_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5000)
    message = json.dumps(data).encode('utf-8')
    sock.sendto(message, server_address)
    sock.close()

# Сокет сервер
def socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('localhost', 5000)
    sock.bind(server_address)

    if not os.path.exists('storage'):
        os.makedirs('storage')

    while True:
        data, _ = sock.recvfrom(4096)
        message = json.loads(data.decode('utf-8'))
        timestamp = str(datetime.now())
        filename = os.path.join('storage', 'data.json')

        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        existing_data[timestamp] = message

        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=4)

# Запуск сервера та сокет сервера
if __name__ == '__main__':
    socket_thread = Thread(target=socket_server)
    socket_thread.daemon = True
    socket_thread.start()
    app.run(port=3000)
