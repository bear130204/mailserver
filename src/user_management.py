import bcrypt
import mysql.connector
from mysql.connector import Error


# Kết nối tới cơ sở dữ liệu MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",          # Địa chỉ MySQL (thường là localhost)
        user="root",               # Thay bằng username MySQL của bạn
        password="",   # Thay bằng mật khẩu MySQL của bạn
        database="mailserver"     # Tên cơ sở dữ liệu
    )

# Hàm đăng ký người dùng
def register_user(username, email, password):
    print(f"Đăng ký với username: {username}, email: {email}, password: {password}")
    if not username or not email or not password:
        print("Thông tin bị thiếu!")
        return False
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, email, password) VALUES (%s, %s, %s)
        """, (username, email, password))
        conn.commit()
        conn.close()
        print("Đăng ký thành công!")
        return True
    except Error as e:
        print(f"Lỗi đăng ký: {e}")
        return False

def log_action(user, action):
    """Ghi nhật ký hoạt động vào cơ sở dữ liệu"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_logs (user, action) VALUES (%s, %s)", (user, action))
        conn.commit()
        conn.close()
    except Error as e:
        print(f"Lỗi khi ghi nhật ký hoạt động: {e}")

# Hàm đăng nhập người dùng
def login_user(username, password):
    print(f"Đang đăng nhập với username: {username}, password: {password}")
    log_action(username, "Đăng nhập thành công")    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users WHERE username = %s AND password = %s
        """, (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            print(f"Kết quả truy vấn: {user}")
            return True
        else:
            print("Không tìm thấy tài khoản trong cơ sở dữ liệu.")
            return False
    except Error as e:
        print(f"Lỗi kết nối hoặc truy vấn MySQL: {e}")
        return False

def update_password(username, old_password, new_password):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Lấy thông tin tài khoản
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return False, "Người dùng không tồn tại"

        # Kiểm tra mật khẩu cũ
        if not bcrypt.checkpw(old_password.encode('utf-8'), user["password"].encode('utf-8')):
            return False, "Mật khẩu cũ không chính xác"

        # Cập nhật mật khẩu mới
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password, username))
        conn.commit()

        return True, "Mật khẩu đã được thay đổi thành công"
    except Error as e:
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


# Kiểm tra kết nối MySQL
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Kết nối MySQL thành công!")
        conn.close()
    except Error as e:
        print(f"Lỗi kết nối MySQL: {e}")
