import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from user_management import get_connection


def log_action(user, action):
    """Ghi nhật ký hành động vào cơ sở dữ liệu"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_logs (user, action) VALUES (%s, %s)", (user, action))
        conn.commit()
        conn.close()
    except Error as e:
        print(f"Lỗi ghi nhật ký: {e}")


class ServerDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Server Management Dashboard")
        self.geometry("800x600")
        self.configure(bg="#f0f8ff")

        # Tiêu đề chính
        tk.Label(self, text="Server Management Dashboard", font=("Helvetica", 18, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        # Khung điều hướng bên trái
        nav_frame = tk.Frame(self, bg="#4682b4")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Các nút điều hướng
        tk.Button(nav_frame, text="Quản lý tài khoản", font=("Arial", 12), bg="#ffa500", fg="white",
                  command=self.open_account_management).pack(pady=10, padx=10)

        tk.Button(nav_frame, text="Nhật ký hoạt động", font=("Arial", 12), bg="#4CAF50", fg="white",
                  command=self.open_activity_logs).pack(pady=10, padx=10)

        tk.Button(nav_frame, text="Khởi động lại server", font=("Arial", 12), bg="#ff4d4d", fg="white",
                  command=self.restart_server).pack(pady=10, padx=10)

        # Khung nội dung chính
        self.content_frame = tk.Frame(self, bg="#f0f8ff")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Hiển thị mặc định
        self.open_activity_logs()

    def clear_content_frame(self):
        """Xóa nội dung cũ trong content_frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def open_account_management(self):
        """Mở giao diện quản lý tài khoản"""
        self.clear_content_frame()
        AccountManagementWindow(self.content_frame)

    def open_activity_logs(self):
        """Mở giao diện nhật ký hoạt động"""
        self.clear_content_frame()
        ActivityLogWindow(self.content_frame)

    def restart_server(self):
        """Khởi động lại server"""
        result = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn khởi động lại server?")
        if result:
            try:
                # Giả lập khởi động lại server
                messagebox.showinfo("Thành công", "Server đã được khởi động lại.")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể khởi động lại server: {e}")

class AccountManagementWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f8ff")
        self.pack(fill=tk.BOTH, expand=True)

        # Tiêu đề
        tk.Label(self, text="Quản lý tài khoản", font=("Helvetica", 16, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        # Bảng hiển thị tài khoản
        self.tree = ttk.Treeview(self, columns=("Username", "Email", "Role"), show="headings")
        self.tree.heading("Username", text="Tên tài khoản")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Vai trò")
        self.tree.column("Username", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Role", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Nút chức năng
        button_frame = tk.Frame(self, bg="#f0f8ff")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Thêm tài khoản", bg="#4CAF50", fg="white", font=("Arial", 12),
                  command=self.add_account).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Xóa tài khoản", bg="#ff4d4d", fg="white", font=("Arial", 12),
                  command=self.delete_account).grid(row=0, column=1, padx=10)
        tk.Button(button_frame, text="Chỉnh sửa tài khoản", bg="#ffa500", fg="white", font=("Arial", 12),
                  command=self.edit_account).grid(row=0, column=2, padx=10)

        self.load_accounts()

    def load_accounts(self):
        """Tải danh sách tài khoản từ cơ sở dữ liệu"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT username, email, role FROM users")
            accounts = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())  # Xóa dữ liệu cũ
            for account in accounts:
                self.tree.insert("", tk.END, values=(account["username"], account["email"], account["role"]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách tài khoản: {e}")

    def add_account(self):
        """Thêm tài khoản mới"""
        AddAccountForm(self, self.load_accounts)

    def delete_account(self):
        """Xóa tài khoản được chọn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một tài khoản để xóa!")
            return

        username = self.tree.item(selected_item[0], "values")[0]
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", f"Tài khoản '{username}' đã bị xóa.")
            self.load_accounts()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa tài khoản: {e}")

    def edit_account(self):
        """Chỉnh sửa tài khoản được chọn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một tài khoản để chỉnh sửa!")
            return

        username = self.tree.item(selected_item[0], "values")[0]
        EditAccountForm(self, username, self.load_accounts)

class ActivityLogWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#f0f8ff")
        self.pack(fill=tk.BOTH, expand=True)

        # Tiêu đề
        tk.Label(self, text="Nhật ký hoạt động", font=("Helvetica", 16, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        # Bảng hiển thị nhật ký
        self.tree = ttk.Treeview(self, columns=("Time", "User", "Action"), show="headings")
        self.tree.heading("Time", text="Thời gian")
        self.tree.heading("User", text="Người dùng")
        self.tree.heading("Action", text="Hành động")
        self.tree.column("Time", width=150)
        self.tree.column("User", width=150)
        self.tree.column("Action", width=300)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.load_logs()

    def load_logs(self):
        """Tải nhật ký hoạt động từ cơ sở dữ liệu"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT timestamp, user, action FROM activity_logs")
            logs = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())  # Xóa dữ liệu cũ
            for log in logs:
                self.tree.insert("", tk.END, values=(log["timestamp"], log["user"], log["action"]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải nhật ký hoạt động: {e}")


class AddAccountForm(tk.Toplevel):
    def __init__(self, parent, refresh_callback):
        super().__init__(parent)
        self.title("Thêm tài khoản")
        self.geometry("400x300")
        self.configure(bg="#f0f8ff")
        self.refresh_callback = refresh_callback

        tk.Label(self, text="Thêm tài khoản mới", font=("Helvetica", 16, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        form_frame = tk.Frame(self, bg="#f0f8ff")
        form_frame.pack(pady=20)

        tk.Label(form_frame, text="Tên tài khoản:", bg="#f0f8ff", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Email:", bg="#f0f8ff", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(form_frame, font=("Arial", 12))
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(form_frame, text="Mật khẩu:", bg="#f0f8ff", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self, text="Thêm tài khoản", bg="#4CAF50", fg="white", font=("Arial", 12),
                  command=self.save_account).pack(pady=10)

    def save_account(self):
        """Lưu tài khoản mới vào cơ sở dữ liệu"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not email or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", f"Tài khoản '{username}' đã được thêm.")
            self.refresh_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm tài khoản: {e}")

class EditAccountForm(AddAccountForm):
    def __init__(self, parent, username, refresh_callback):
        super().__init__(parent, refresh_callback)
        self.title("Chỉnh sửa tài khoản")
        self.username_entry.insert(0, username)
        self.username_entry.config(state="disabled")  # Không cho chỉnh sửa username

        tk.Button(self, text="Cập nhật tài khoản", bg="#ffa500", fg="white", font=("Arial", 12),
                  command=self.update_account).pack(pady=10)

    def update_account(self):
        """Cập nhật thông tin tài khoản"""
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET email = %s, password = %s WHERE username = %s", (email, password, self.username_entry.get()))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", f"Tài khoản '{self.username_entry.get()}' đã được cập nhật.")
            self.refresh_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật tài khoản: {e}")

if __name__ == "__main__":
    app = ServerDashboard()
    app.mainloop()
