import os
from mysql.connector import connect, Error
from smtp_server import send_to_smtp_server  # Hàm giả lập gửi email đến server SMTP

import socket

def connect_to_server():
    """Kết nối tới server SMTP"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("172.20.10.3", 1025))  # Thay bằng IP và cổng server của bạn
        print("Kết nối tới server thành công.")
        response = client_socket.recv(1024).decode("utf-8")
        print("Phản hồi từ server:", response)
        return client_socket
    except Exception as e:
        print("Lỗi kết nối tới server:", e)
        return None

def get_connection():
    """Kết nối tới cơ sở dữ liệu MySQL"""
    return connect(
        host="localhost",
        user="root",
        password="",  # Thay bằng mật khẩu MySQL của bạn
        database="mailserver"
    )

# def send_email(sender, receiver, subject, body, attachment_path=None):
#     """Gửi email đến server và lưu vào cơ sở dữ liệu cùng tệp đính kèm nếu có"""
#     try:
#         # Gửi email đến server SMTP
#         if not send_to_smtp_server(sender, receiver, subject, body):
#             return False

#         # Lưu email vào cơ sở dữ liệu
#         conn = get_connection()
#         cursor = conn.cursor()

#         # Thêm email vào bảng emails
#         cursor.execute("""
#             INSERT INTO emails (sender, receiver, subject, body)
#             VALUES (%s, %s, %s, %s)
#         """, (sender, receiver, subject, body))
#         email_id = cursor.lastrowid  # Lấy ID của email vừa thêm

#         # Nếu có file đính kèm, thêm vào bảng attachments
#         if attachment_path:
#             with open(attachment_path, "rb") as f:
#                 file_data = f.read()
#                 filename = os.path.basename(attachment_path)
#                 cursor.execute("""
#                     INSERT INTO attachments (email_id, filename, file_data)
#                     VALUES (%s, %s, %s)
#                 """, (email_id, filename, file_data))

#         conn.commit()
#         conn.close()
#         return True
#     except Error as e:
#         print(f"Lỗi gửi email: {e}")
#         return False
#     except FileNotFoundError:
#         print("Không tìm thấy file đính kèm.")
#         return False
def start_email_receiver_server(host="0.0.0.0", port=1026):
    """Khởi chạy server nhận email từ SMTP server"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Máy nhận đang lắng nghe trên {host}:{port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Kết nối từ: {addr}")
        try:
            data = client_socket.recv(1024).decode("utf-8")
            if data.startswith("RECEIVE"):
                parts = data.split("\n")
                sender = parts[1].strip()
                receiver = parts[2].strip()
                subject = parts[3].strip()
                body = "\n".join(parts[4:]).strip()
                save_email_to_db(sender, receiver, subject, body)  # Lưu vào DB
        except Exception as e:
            print(f"Lỗi khi xử lý email: {e}")
        finally:
            client_socket.close()

def save_email_to_db(sender, receiver, subject, body):
    """Lưu email vào cơ sở dữ liệu tại máy nhận"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO emails (sender, receiver, subject, body)
            VALUES (%s, %s, %s, %s)
        """, (sender, receiver, subject, body))
        conn.commit()
        conn.close()
        print("Email đã được lưu vào cơ sở dữ liệu")
    except Error as e:
        print(f"Lỗi lưu email vào DB: {e}")

def send_email(sender, receiver, subject, body, attachment_path=None):
    """Gửi email đến server và gửi thông tin email qua socket"""
    client_socket = connect_to_server()
    if client_socket is None:
        print("Không thể kết nối tới server.")
        return False
    try:
        # Tạo dữ liệu email
        email_data = f"SEND\n{sender}\n{receiver}\n{subject}\n{body}"
        
        # Nếu có tệp đính kèm, thêm thông tin tệp
        if attachment_path:
            with open(attachment_path, "rb") as f:
                file_data = f.read()
            filename = os.path.basename(attachment_path)
            email_data += f"\nATTACHMENT:{filename}:{file_data.decode('latin1')}"

        email_data += "\nQUIT"
        
        # Gửi dữ liệu qua socket
        client_socket.sendall(email_data.encode("utf-8"))
        response = client_socket.recv(1024).decode("utf-8")
        print("Phản hồi từ server:", response)
        client_socket.close()
        return "250" in response
    except Exception as e:
        print("Lỗi khi gửi email:", e)
        return False
    except FileNotFoundError:
        print("Không tìm thấy file đính kèm.")
        return False


def get_inbox(receiver):
    """Lấy danh sách email nhận được"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, sender, subject, body, timestamp
            FROM emails
            WHERE receiver = %s
            ORDER BY timestamp DESC
        """, (receiver,))
        emails = cursor.fetchall()
        conn.close()
        return emails
    except Error as e:
        print(f"Lỗi khi lấy hộp thư đến: {e}")
        return []
from mysql.connector import connect, Error
from user_management import get_connection

def get_inbox(receiver):
    """Lấy danh sách email của người nhận"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, sender, subject, body, timestamp
            FROM emails
            WHERE receiver = %s
            ORDER BY timestamp DESC
        """, (receiver,))
        emails = cursor.fetchall()
        conn.close()
        return emails
    except Error as e:
        print(f"Lỗi khi lấy hộp thư đến: {e}")
        return []

