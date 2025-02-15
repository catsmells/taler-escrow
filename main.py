from flask import Flask, request, jsonify
import sqlite3
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("escrow.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer TEXT,
            seller TEXT,
            amount REAL,
            status TEXT DEFAULT 'pending',
            taler_contract_id TEXT
        )
    ''')
    conn.commit()
    conn.close()
  
@app.route("/create_escrow", methods=["POST"])
def create_escrow():
    data = request.json
    buyer = data["buyer"]
    seller = data["seller"]
    amount = data["amount"]
    taler_contract_id = "" #contract API call here
    conn = sqlite3.connect("escrow.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (buyer, seller, amount, taler_contract_id)
        VALUES (?, ?, ?, ?)""", (buyer, seller, amount, taler_contract_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Escrow created", "contract_id": taler_contract_id})
  
@app.route("/release_funds", methods=["POST"])
def release_funds():
    data = request.json
    contract_id = data["contract_id"]
    conn = sqlite3.connect("escrow.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status='released' WHERE taler_contract_id=?", (contract_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Funds released successfully"})
@app.route("/dispute", methods=["POST"])
def dispute_transaction():
    data = request.json
    contract_id = data["contract_id"]
    conn = sqlite3.connect("escrow.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE transactions SET status='disputed' WHERE taler_contract_id=?", (contract_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Transaction marked as disputed"})
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
