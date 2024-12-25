from flask import Flask, request, jsonify
from user_management import get_db_connection

app = Flask(__name__)

# Lấy danh sách tài khoản
@app.route('/manage_accounts', methods=['GET'])
def manage_accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, email FROM users")
    accounts = cursor.fetchall()
    conn.close()
    return jsonify(accounts)

# Xóa tài khoản
@app.route('/manage_accounts', methods=['DELETE'])
def delete_account():
    username = request.json.get('username')
    if not username:
        return jsonify({"success": False, "message": "Username không hợp lệ"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Tài khoản đã bị xóa"})

# Lấy nhật ký hoạt động
@app.route('/logs', methods=['GET'])
def get_logs():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

if __name__ == "__main__":
    app.run(debug=True)
