
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

DB_NAME = "expenses.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                category TEXT NOT NULL
            )
        """)


@app.route("/")
def home():
    return jsonify({
        "message": "Personal Expense Tracker API is running"
    })
@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/expenses", methods=["POST"])
def add_expense():
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    amount = data.get("amount")
    category = data.get("category")


    if not title or not category or amount is None:
        return jsonify({"error": "All fields are required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be positive"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO expenses (title, amount, category)
               VALUES (?, ?, ?)""",
            (title, amount, category)
        )
        expense_id = cursor.lastrowid

    return jsonify({
        "id": expense_id,
        "title": title,
        "amount": amount,
        "category": category
    }), 201


@app.route("/expenses", methods=["GET"])
def get_expenses():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM expenses ORDER BY id"
        ).fetchall()

    return jsonify([dict(row) for row in rows])


@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    amount = data.get("amount")
    category = data.get("category")

    if not title or not category or amount is None:
        return jsonify({"error": "All fields are required"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Amount must be positive"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            """UPDATE expenses
               SET title = ?, amount = ?, category = ?
               WHERE id = ?""",
            (title, amount, category, expense_id)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify({"message": "Expense updated successfully"})


@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )

    if cursor.rowcount == 0:
        return jsonify({"error": "Expense not found"}), 404

    return jsonify({"message": "Expense deleted successfully"})


@app.route("/total", methods=["GET"])
def total_expenses():
    with get_db() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
        ).fetchone()

    return jsonify({"total": row["total"]})


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
