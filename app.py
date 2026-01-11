from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse as urlparse
from pathlib import Path
import os


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Парсим URL
        parsed_path = urlparse.urlparse(self.path)
        path = parsed_path.path

        # Определяем какой файл показывать
        if path == '/':
            template_file = 'templates/index.html'
        elif path == '/catalog':
            template_file = 'templates/catalog.html'
        elif path == '/category':
            template_file = 'templates/category.html'
        elif path == '/contacts':
            template_file = 'templates/contacts.html'
        elif path.startswith('/static/'):
            # Обслуживание статических файлов
            static_file = path[1:]  # Убираем первый слэш
            self.serve_static(static_file)
            return
        else:
            # 404 для неизвестных путей
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>404 Not Found</h1>')
            return

        try:
            # Читаем HTML файл
            with open(template_file, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Отправляем успешный ответ
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))

        except FileNotFoundError:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Template not found</h1>')

    def serve_static(self, path):
        """Обслуживание статических файлов"""
        if not os.path.exists(path):
            self.send_response(404)
            self.end_headers()
            return

        # Определяем тип контента
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.ico': 'image/x-icon'
        }

        ext = os.path.splitext(path)[1]
        content_type = content_types.get(ext, 'text/plain')

        try:
            with open(path, 'rb') as file:
                content = file.read()

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except:
            self.send_response(500)
            self.end_headers()

    def do_POST(self):
        """Обработка POST-запросов (дополнительное задание)"""
        # Получаем длину данных
        content_length = int(self.headers['Content-Length'])
        # Читаем данные
        post_data = self.rfile.read(content_length)

        # Декодируем данные
        try:
            data = urlparse.parse_qs(post_data.decode('utf-8'))
            print("=" * 50)
            print("POST данные получены:")
            for key, value in data.items():
                print(f"{key}: {', '.join(value)}")
            print("=" * 50)
        except Exception as e:
            print(f"Ошибка обработки POST данных: {e}")
            print("=" * 50)
            print("POST данные (raw):")
            print(post_data.decode('utf-8', errors='ignore'))
            print("=" * 50)

        # Перенаправляем на главную страницу
        self.send_response(303)  # 303 See Other
        self.send_header('Location', '/')
        self.end_headers()


def run_server(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print(f'Сервер запущен на http://localhost:8000')
    print('Доступные страницы:')
    print('  / - Главная')
    print('  /catalog - Каталог')
    print('  /category - Категория')
    print('  /contacts - Контакты')
    print('\nPOST-запросы обрабатываются и выводятся в консоль')
    print('Для остановки сервера нажмите Ctrl+C')
    httpd.serve_forever()


if __name__ == '__main__':
    # Создаем необходимые директории
    Path("templates").mkdir(exist_ok=True)
    Path("static/css").mkdir(exist_ok=True, parents=True)

    # Создаем простой CSS файл
    css_content = """
    /* Дополнительные кастомные стили */
    .card {
        border-radius: 10px;
        overflow: hidden;
    }

    .btn-primary {
        padding: 10px 20px;
        font-weight: 500;
    }

    /* Анимации */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .product-card {
        animation: fadeIn 0.5s ease-out;
    }
    """

    with open('static/css/custom.css', 'w', encoding='utf-8') as f:
        f.write(css_content)

    # Запускаем сервер
    run_server()