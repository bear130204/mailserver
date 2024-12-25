import mysql.connector
from mysql.connector import Error
import socket
import threading
import logging
import signal
from concurrent.futures import ThreadPoolExecutor
from user_management import log_action

# Thiết lập logging
logging.basicConfig(
    filename="smtp_server.log", level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def send_to_smtp_server(sender, recipient, subject, body):
        """Hàm giả lập gửi email đến server SMTP"""
        log_action(sender, f"Gửi email đến {recipient} với tiêu đề '{subject}'")
        print(f"Gửi email từ {sender} đến {recipient}")
        print(f"Tiêu đề: {subject}")
        print(f"Nội dung: {body}")
        # Giả lập gửi email thành công
        return True

def get_connection():
    """Kết nối tới cơ sở dữ liệu MySQL"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Thay bằng mật khẩu MySQL
        database="mailserver"
    )

class SMTPServer:
    def __init__(self, host="172.20.10.3", port=1025, max_threads=10):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.executor = ThreadPoolExecutor(max_threads)
        self.connected_clients = []

    def start(self):
        signal.signal(signal.SIGINT, self.stop_server)  # Xử lý tín hiệu Ctrl+C
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"SMTP Server đang chạy tại {self.host}:{self.port}")
        logging.info(f"SMTP Server đang chạy tại {self.host}:{self.port}")
        while True:
            client, addr = self.server.accept()
            print(f"Kết nối từ: {addr}")
            logging.info(f"Kết nối từ: {addr}")
            self.connected_clients.append(addr)
            self.executor.submit(self.handle_client, client)

    def stop_server(self, signum, frame):
        print("Đang dừng server...")
        logging.info("Server đang dừng...")
        self.server.close()
        exit(0)

    def handle_client(self, client_socket):
        """Hàm xử lý kết nối từ client"""
        client_socket.send(b"220 SMTP Server Ready\r\n")  # Phản hồi ban đầu từ server
        try:
            while True:
                data = client_socket.recv(1024).decode("utf-8")  # Nhận dữ liệu từ client
                if not data:
                    break

                print(f"Nhận được từ client: {data.strip()}")  # Hiển thị dữ liệu nhận được

            # Kiểm tra loại lệnh
                if data.startswith("SEND"):
                    self.handle_send(data, client_socket)  # Xử lý lệnh gửi tin nhắn
                elif data.startswith("QUIT"):
                    client_socket.send(b"221 Bye\r\n")  # Phản hồi cho client trước khi đóng kết nối
                    break
                else:
                    client_socket.send(b"502 Command not implemented\r\n")  # Lệnh không hợp lệ
        except ConnectionResetError:
            print(f"Kết nối từ client bị mất: {client_socket.getpeername()}")
        finally:
            client_socket.close()  # Đóng kết nối

    def handle_send(self, data, client_socket):
        try:
            parts = data.split("\n")
            sender = parts[1].strip()
            receiver = parts[2].strip()
            subject = parts[3].strip()
            body = "\n".join(parts[4:]).strip()

        # Lưu tin nhắn vào cơ sở dữ liệu
            conn = get_connection()
            cursor = conn.cursor()

        # Thêm bản ghi vào bảng emails
            cursor.execute(
            """
            INSERT INTO emails (sender, receiver, subject, body)
            VALUES (%s, %s, %s, %s)
            """,
            (sender, receiver, subject, body)
        )
            email_id = cursor.lastrowid  # Lấy ID email vừa thêm

        # Xử lý tệp đính kèm nếu có
            if "attachment:" in data:
                attachment_index = data.index("attachment:") + len("attachment:")
                filename, file_data = data[attachment_index:].split(":", 1)
                cursor.execute(
                """
                INSERT INTO attachments (email_id, filename, file_data)
                VALUES (%s, %s, %s)
                """,
                (email_id, filename.strip(), file_data.encode())
            )

            conn.commit()
            conn.close()

            print(f"Tin nhắn từ {sender} đến {receiver} đã được lưu vào cơ sở dữ liệu.")
            client_socket.send(b"250 Message received\r\n")
        except Error as e:
            print(f"Lỗi lưu tin nhắn: {e}")
            client_socket.send(b"550 Message not saved\r\n")
    def forward_email_to_receiver(receiver_ip, receiver_port, sender, receiver, subject, body):
        """Gửi email tới client nhận thông qua IP và cổng"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((receiver_ip, receiver_port))  # Kết nối đến máy nhận
            message = f"RECEIVE\n{sender}\n{receiver}\n{subject}\n{body}\n"
            client_socket.sendall(message.encode("utf-8"))
            client_socket.close()
            print(f"Email đã được chuyển tiếp đến {receiver_ip}:{receiver_port}")
        except Exception as e:
            print(f"Lỗi khi chuyển tiếp email: {e}")


if __name__ == "__main__":
    server = SMTPServer()
    server.start()
