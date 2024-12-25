import tkinter as tk
from tkinter import ttk, messagebox
from email_client import get_inbox

class InboxViewerApp(tk.Toplevel):
    def __init__(self, receiver):
        super().__init__()
        self.receiver = receiver
        self.title("Hộp Thư Đến")
        self.geometry("600x400")
        self.configure(bg="#f0f8ff")

        # Tiêu đề
        tk.Label(self, text="Hộp Thư Đến", font=("Helvetica", 18, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        # Khung chính
        self.frame = tk.Frame(self, bg="#f0f8ff")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bảng danh sách email
        self.tree = ttk.Treeview(self.frame, columns=("ID", "Người gửi", "Tiêu đề", "Thời gian"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Người gửi", text="Người gửi")
        self.tree.heading("Tiêu đề", text="Tiêu đề")
        self.tree.heading("Thời gian", text="Thời gian")
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Người gửi", width=150)
        self.tree.column("Tiêu đề", width=200)
        self.tree.column("Thời gian", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Nút xem chi tiết email
        self.details_button = tk.Button(self, text="Xem Chi Tiết", font=("Arial", 12), bg="#4682b4", fg="white", command=self.view_email_details)
        self.details_button.pack(pady=10)

        # Load email
        self.load_inbox()

    def load_inbox(self):
        """Lấy danh sách email từ cơ sở dữ liệu và hiển thị"""
        try:
            emails = get_inbox(self.receiver)
            for email in emails:
                self.tree.insert("", tk.END, values=(email["id"], email["sender"], email["subject"], email["timestamp"]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hộp thư đến: {e}")

    def view_email_details(self):
        """Xem chi tiết email được chọn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một email để xem chi tiết!")
            return

        email_id = self.tree.item(selected_item[0], "values")[0]
        email_details = next((email for email in get_inbox(self.receiver) if email["id"] == int(email_id)), None)

        if email_details:
            messagebox.showinfo(
                "Chi Tiết Email",
                f"Người gửi: {email_details['sender']}\nTiêu đề: {email_details['subject']}\n\nNội dung:\n{email_details['body']}",
            )
        else:
            messagebox.showerror("Lỗi", "Không thể tìm thấy chi tiết email!")
