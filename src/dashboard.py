# class DashboardApp(tk.Tk):
#     def __init__(self, username):
#         super().__init__()
#         self.username = username
#         self.title("Dashboard")
#         self.geometry("800x600")
#         self.configure(bg="#f0f8ff")

#         # Thanh điều hướng
#         nav_frame = tk.Frame(self, bg="#4682b4")
#         nav_frame.pack(side=tk.LEFT, fill=tk.Y)

#         tk.Button(nav_frame, text="Thay đổi mật khẩu", font=("Arial", 12), bg="#4CAF50", fg="white",
#                   command=self.change_password_form).pack(pady=10, padx=10)

#         # Vùng hiển thị chính
#         self.content_frame = tk.Frame(self, bg="#f0f8ff")
#         self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

#     def clear_content_frame(self):
#         for widget in self.content_frame.winfo_children():
#             widget.destroy()

#     def change_password_form(self):
#         self.clear_content_frame()
#         # ChangePasswordForm(self.content_frame, self.username)
