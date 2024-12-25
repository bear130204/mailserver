from binascii import Error
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from email_client import send_email,get_inbox
from user_management import login_user, register_user
from inbox_viewer import InboxViewerApp
from user_management import get_connection
from tkinter.font import Font

class UserInterfaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hệ thống Mail Server")
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
            self.destroy()  # Đóng cửa sổ đăng nhập
            DashboardApp(username).mainloop()  # Mở Dashboard để chọn chức năng
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

class EmailClientApp:
    def __init__(self, parent, sender):
        self.sender = sender

        # Tiêu đề
        tk.Label(parent, text="Soạn Email", font=("Helvetica", 18, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        # Khung chính
        frame = tk.Frame(parent, bg="#f0f8ff")
        frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Nhập email người nhận
        tk.Label(frame, text="Người nhận:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.recipient_entry = ttk.Entry(frame, font=("Arial", 12), width=40)
        self.recipient_entry.grid(row=0, column=1, padx=10, pady=5)

        # Nhập tiêu đề email
        tk.Label(frame, text="Tiêu đề:", font=("Arial", 12), bg="#f0f8ff").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.subject_entry = ttk.Entry(frame, font=("Arial", 12), width=40)
        self.subject_entry.grid(row=1, column=1, padx=10, pady=5)

        # Nhập nội dung email
        tk.Label(frame, text="Nội dung:", font=("Arial", 12), bg="#f0f8ff").grid(row=2, column=0, padx=10, pady=5, sticky="ne")
        self.body_text = tk.Text(frame, font=("Arial", 12), height=10, width=50, wrap=tk.WORD)
        self.body_text.grid(row=2, column=1, padx=10, pady=5)

        # Nút gửi email
        tk.Button(frame, text="Gửi Email", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                  command=self.send_group_email).grid(row=3, column=1, pady=10, sticky="e")
        tk.Button(frame, text="Đính kèm tệp", font=("Arial", 12), bg="#4682b4", fg="white",
                  command=self.attach_file).grid(row=3, column=0, pady=10, sticky="w")
        self.attachment_path = None  # Đường dẫn tệp đính kèm
    def send_group_email(self):
        recipients = self.recipient_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", tk.END).strip()

        if not recipients or not body:
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        # Xử lý danh sách người nhận
        recipient_list = [email.strip() for email in recipients.split(",")]

        # Gửi email tới từng người
        success_count = 0
        for recipient in recipient_list:
            if send_email(self.sender, recipient, subject, body):
                success_count += 1

        messagebox.showinfo("Kết quả", f"Đã gửi thành công {success_count}/{len(recipient_list)} email.")
    def attach_file(self):
        """Hàm chọn file đính kèm"""
        self.attachment_path = filedialog.askopenfilename()
        if self.attachment_path:
            messagebox.showinfo("Thành công", f"Đã chọn tệp: {self.attachment_path}")

   
        
    def send_email(self):
        recipient = self.recipient_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", tk.END).strip()

        if not recipient or not body:
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin!")
            return

        if send_email(self.sender, recipient, subject, body, self.attachment_path):
                messagebox.showinfo("Thành công", "Email đã được gửi!")    
        else:
            messagebox.showerror("Lỗi", "Gửi email thất bại!")
        
class InboxViewerApp:
    def __init__(self, parent, receiver):
        self.receiver = receiver

        # Tiêu đề
        tk.Label(parent, text="Hộp Thư Đến", font=("Helvetica", 18, "bold"), bg="#4682b4", fg="white").pack(fill=tk.X, pady=10)

        # Khung chính
        frame = tk.Frame(parent, bg="#f0f8ff")
        frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        # Trường tìm kiếm
        filter_frame = tk.Frame(frame, bg="#f0f8ff")
        filter_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")

        tk.Label(filter_frame, text="Tiêu đề:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=0, padx=5, pady=5)
        self.subject_entry = ttk.Entry(filter_frame, font=("Arial", 12), width=20)
        self.subject_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Người gửi:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=2, padx=5, pady=5)
        self.sender_entry = ttk.Entry(filter_frame, font=("Arial", 12), width=20)
        self.sender_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(filter_frame, text="Ngày:", font=("Arial", 12), bg="#f0f8ff").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(filter_frame, font=("Arial", 12), width=20)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        tk.Button(filter_frame, text="Lọc", font=("Arial", 12), bg="#4CAF50", fg="white",
                  command=self.filter_emails).grid(row=0, column=6, padx=10, pady=5)
        tk.Button(filter_frame, text="Xóa Bộ Lọc", font=("Arial", 12), bg="#ff4d4d", fg="white",
          command=self.load_inbox).grid(row=0, column=7, padx=10, pady=5)
        # Nút xem chi tiết email
        tk.Button(frame, text="Xem Chi Tiết", font=("Arial", 12), bg="#4682b4", fg="white",
                  command=self.view_email_details).grid(row=2 , column=3,padx=10 ,sticky="e",pady=10)
        # Nút Xóa Email
        # Nút Xóa Email
        tk.Button(frame, text="Xóa Email", font=("Arial", 12), bg="#ff4d4d", fg="white",
          command=self.delete_email).grid(row=2, column=0, padx=10, pady=5, sticky="w")

# Nút Đánh Dấu Quan Trọng
        tk.Button(frame, text="Đánh Dấu Quan Trọng", font=("Arial", 12), bg="#ffa500", fg="white",
          command=self.mark_important).grid(row=2, column=1, padx=10, pady=5, sticky="e")
        # Nút Đánh Dấu Đã Đọc
        tk.Button(frame, text="Đánh Dấu Đã Đọc", font=("Arial", 12), bg="#4682b4", fg="white",
          command=self.mark_as_read).grid(row=2, column=2, padx=10, pady=5, sticky="e")
       





        # Bảng danh sách email
        self.tree = ttk.Treeview(frame, columns=("ID", "Người gửi", "Tiêu đề", "Thời gian","Trạng thái"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Người gửi", text="Người gửi")
        self.tree.heading("Tiêu đề", text="Tiêu đề")
        self.tree.heading("Thời gian", text="Thời gian")
        self.tree.heading("Trạng thái", text="Trạng thái")
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Người gửi", width=150)
        self.tree.column("Tiêu đề", width=200)
        self.tree.column("Thời gian", width=150)
        self.tree.column("Trạng thái", width=100)
        self.tree.grid(row=1, column=0, columnspan=2, pady=10)
         # Nút tải tệp
        tk.Button(frame, text="Tải Tệp Đính Kèm", font=("Arial", 12), bg="#4682b4", fg="white",
                  command=self.download_attachment).grid(row=1, column=1, pady=10, sticky="e")

        self.load_inbox()
    def download_attachment(self):
        """Tải file đính kèm"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một email có tệp đính kèm!")
            return

        email_id = self.tree.item(selected_item[0], "values")[0]

        # Kết nối tới cơ sở dữ liệu để lấy thông tin file
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT filename, file_data FROM attachments WHERE email_id = %s", (email_id,))
        attachments = cursor.fetchall()
        conn.close()

        if not attachments:
            messagebox.showinfo("Thông báo", "Email này không có tệp đính kèm!")
            return

        for attachment in attachments:
            filename = attachment["filename"]
            filedata = attachment["file_data"]

            # Lưu file xuống máy người dùng
            save_path = filedialog.asksaveasfilename(initialfile=filename, title="Lưu Tệp Đính Kèm")
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(filedata)
                messagebox.showinfo("Thành công", f"Tệp '{filename}' đã được tải xuống!")

    def filter_emails(self):
        """Lọc email dựa trên các tiêu chí"""
        subject = self.subject_entry.get().strip()
        sender = self.sender_entry.get().strip()
        date = self.date_entry.get().strip()

        # Tạo truy vấn động
        query = "SELECT id, sender, subject, body, timestamp FROM emails WHERE receiver = %s"
        params = [self.receiver]

        if subject:
            query += " AND subject LIKE %s"
            params.append(f"%{subject}%")

        if sender:
            query += " AND sender LIKE %s"
            params.append(f"%{sender}%")

        if date:
            query += " AND DATE(timestamp) = %s"
            params.append(date)

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            emails = cursor.fetchall()
            conn.close()

            # Làm mới bảng
            self.tree.delete(*self.tree.get_children())
            for email in emails:
                self.tree.insert("", tk.END, values=(email["id"], email["sender"], email["subject"], email["timestamp"]))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lọc email: {e}")

    def delete_email(self):
        """Xóa email được chọn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một email để xóa!")
            return

        email_id = self.tree.item(selected_item[0], "values")[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emails WHERE id = %s", (email_id,))
            conn.commit()
            conn.close()

        # Xóa email khỏi Treeview
            self.tree.delete(selected_item[0])

            messagebox.showinfo("Thành công", "Email đã được xóa!")
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể xóa email: {e}")
    def mark_as_read(self):
        """Đánh dấu email là đã đọc"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một email để đánh dấu là đã đọc!")
            return

        email_id = self.tree.item(selected_item[0], "values")[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE emails SET is_read = TRUE WHERE id = %s", (email_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Email đã được đánh dấu là đã đọc!")
            self.load_inbox()  # Làm mới danh sách sau khi đánh dấu
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể đánh dấu email là đã đọc: {e}")

    def mark_important(self):
        """Đánh dấu email là quan trọng"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một email để đánh dấu!")
            return

        email_id = self.tree.item(selected_item[0], "values")[0]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE emails SET is_important = TRUE WHERE id = %s", (email_id,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Thành công", "Email đã được đánh dấu là quan trọng!")
        except Error as e:
            messagebox.showerror("Lỗi", f"Không thể đánh dấu email: {e}")

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


    def load_inbox(self):
    # """Làm mới danh sách email và hiển thị trạng thái với định dạng"""
        self.tree.delete(*self.tree.get_children())  # Xóa tất cả các hàng cũ
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
            SELECT id, sender, subject, body, timestamp, is_read, is_important
            FROM emails
            WHERE receiver = %s
            ORDER BY timestamp DESC
        """, (self.receiver,))
            emails = cursor.fetchall()
            conn.close()

        # Tạo font in đậm
            bold_font = Font(weight="bold")

        # Hiển thị email trong Treeview
            for email in emails:
                status = ""
                if email["is_important"]:
                    status = "⭐ Quan trọng"
                elif not email["is_read"]:
                    status = "Chưa Đọc"

            # Thêm hàng vào Treeview
                row_id = self.tree.insert("", tk.END, values=(
                email["id"], email["sender"], email["subject"], email["timestamp"], status
            ))

            # Tùy chỉnh font: in đậm nếu chưa đọc
                if not email["is_read"]:
                    self.tree.tag_configure(row_id, font=bold_font)  # Áp dụng in đậm cho email chưa đọc

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải hộp thư đến: {e}")


    # def view_email_details(self):
    #     """Xem chi tiết email được chọn"""
    #     selected_item = self.tree.selection()
    #     if not selected_item:
    #         messagebox.showwarning("Lỗi", "Vui lòng chọn một email để xem chi tiết!")
    #         return

    #     email_id = self.tree.item(selected_item[0], "values")[0]
    #     email_details = next((email for email in get_inbox(self.receiver) if email["id"] == int(email_id)), None)

    #     if email_details:
    #         messagebox.showinfo(
    #             "Chi Tiết Email",
    #             f"Người gửi: {email_details['sender']}\nTiêu đề: {email_details['subject']}\n\nNội dung:\n{email_details['body']}",
    #         )
    #     else:
    #         messagebox.showerror("Lỗi", "Không thể tìm thấy chi tiết email!")
    
    def view_email_details(self):
        # """Xem chi tiết email được chọn"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một email để xem chi tiết!")
            return

        email_id = self.tree.item(selected_item[0], "values")[0]
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Lấy nội dung email
        cursor.execute("SELECT sender, subject, body FROM emails WHERE id = %s", (email_id,))
        email = cursor.fetchone()

        # Lấy file đính kèm
        cursor.execute("SELECT filename FROM attachments WHERE email_id = %s", (email_id,))
        attachments = cursor.fetchall()
        conn.close()

        attachment_list = "\n".join([f"- {att['filename']}" for att in attachments])
        messagebox.showinfo(
            "Chi Tiết Email",
            f"Người gửi: {email['sender']}\nTiêu đề: {email['subject']}\n\nNội dung:\n{email['body']}\n\nTệp đính kèm:\n{attachment_list}"
        )




class DashboardApp(tk.Tk):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.title(f"{self.username}")
        self.geometry("800x600")
        self.configure(bg="#f0f8ff")

        # Thanh điều hướng
        nav_frame = tk.Frame(self, bg="#4682b4")
        nav_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Nút Soạn Email
        tk.Button(nav_frame, text="Soạn Email", font=("Arial", 12), bg="#4CAF50", fg="white",
                  command=self.show_email_client).pack(pady=10, padx=10)

        # Nút Hộp Thư Đến
        tk.Button(nav_frame, text="Hộp Thư Đến", font=("Arial", 12), bg="#4682b4", fg="white",
                  command=self.show_inbox_viewer).pack(pady=10, padx=10)

        # Vùng hiển thị chính
        self.content_frame = tk.Frame(self, bg="#f0f8ff")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Mặc định hiển thị Soạn Email
        self.show_email_client()

    def clear_content_frame(self):
        """Xóa nội dung cũ trong content_frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_email_client(self):
        """Hiển thị giao diện Soạn Email"""
        self.clear_content_frame()
        EmailClientApp(self.content_frame, self.username)

    def show_inbox_viewer(self):
        """Hiển thị giao diện Hộp Thư Đến"""
        self.clear_content_frame()
        InboxViewerApp(self.content_frame, self.username)


if __name__ == "__main__":
    app = UserInterfaceApp()
    app.mainloop()
