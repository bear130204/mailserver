import tkinter as tk
from tkinter import ttk, messagebox
from user_management import register_user, login_user
from dashboard import DashboardApp

class LoginRegisterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập/Đăng ký")
        self.geometry("400x400")
        self.configure(bg="#f0f8ff")

        # Tiêu đề
        tk.Label(self, text="Hệ thống Mail Server", font=("Helvetica", 16, "bold"), bg="#f0f8ff", fg="#4682b4").pack(pady=20)

        # Frame nhập thông tin
        self.main_frame = tk.Frame(self, bg="#f0f8ff")
        self.main_frame.pack(pady=10)

        # Nhập Tên người dùng
        tk.Label(self.main_frame, text="Tên người dùng:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.username_entry = ttk.Entry(self.main_frame, font=("Arial", 12))
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        # Nhập Email (ẩn khi đăng nhập)
        self.email_label = tk.Label(self.main_frame, text="Email:", font=("Arial", 12), bg="#f0f8ff")
        self.email_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.email_entry = ttk.Entry(self.main_frame, font=("Arial", 12))
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)
        self.email_label.grid_remove()
        self.email_entry.grid_remove()

        # Nhập Mật khẩu
        tk.Label(self.main_frame, text="Mật khẩu:", font=("Arial", 12), bg="#f0f8ff").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.password_entry = ttk.Entry(self.main_frame, font=("Arial", 12), show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        # Nút chuyển đổi chế độ
        self.switch_button = tk.Button(self, text="Chuyển sang Đăng ký", font=("Arial", 10), bg="#87cefa", command=self.switch_mode)
        self.switch_button.pack(pady=10)

        # Nút thực hiện hành động
        self.action_button = tk.Button(self, text="Đăng nhập", font=("Arial", 12, "bold"), bg="#4682b4", fg="white", command=self.handle_action)
        self.action_button.pack(pady=10)

        self.current_action = "login"  # Mặc định là chế độ đăng nhập

    def switch_mode(self):
        """Chuyển đổi giữa chế độ Đăng nhập và Đăng ký"""
        if self.current_action == "login":
            self.current_action = "register"
            self.email_label.grid()
            self.email_entry.grid()
            self.action_button.config(text="Đăng ký")
            self.switch_button.config(text="Chuyển sang Đăng nhập")
        else:
            self.current_action = "login"
            self.email_label.grid_remove()
            self.email_entry.grid_remove()
            self.action_button.config(text="Đăng nhập")
            self.switch_button.config(text="Chuyển sang Đăng ký")

    def handle_action(self):
        """Xử lý Đăng nhập hoặc Đăng ký"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if self.current_action == "login":
            self.handle_login(username, password)
        elif self.current_action == "register":
            email = self.email_entry.get().strip()
            self.handle_register(username, email, password)

    def handle_login(self, username, password):
        """Xử lý đăng nhập"""
        if not username or not password:
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if login_user(username, password):
            messagebox.showinfo("Thành công", "Đăng nhập thành công!")
            self.destroy()
            DashboardApp(username).mainloop()
        else:
            messagebox.showerror("Lỗi", "Tên người dùng hoặc mật khẩu không đúng!")

    def handle_register(self, username, email, password):
        """Xử lý đăng ký"""
        if not username or not email or not password:
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if register_user(username, email, password):
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            self.switch_mode()  # Tự động chuyển sang chế độ Đăng nhập sau khi Đăng ký thành công
        else:
            messagebox.showerror("Lỗi", "Tên người dùng hoặc email đã tồn tại!")

if __name__ == "__main__":
    app = LoginRegisterApp()
    app.mainloop()
