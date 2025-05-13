from flask import Flask, request, jsonify
from pymongo import MongoClient
from web3 import Web3
from datetime import datetime
from flask_cors import CORS
import os
app = Flask(__name__)
CORS(app)  # Enable CORS


# MongoDB connection
MONGO_URI=os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["car-rentals"]
payments = db["payments"]

# Web3 setup (if needed)
w3 = Web3(Web3.HTTPProvider("https://eth-sepolia.g.alchemy.com/v2/aQnLO-2ymtuqeI4Pys3cmlyO2vFp9acP"))  # e.g., Infura

@app.route("/log", methods=["POST"])
def log_transaction_from_metamask():
    try:
        data = request.json
        print("Received /log data:", data)

        required_fields = ["from", "to", "amount", "tx_hash"]
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        payment_record = {
            "from": Web3.to_checksum_address(data["from"]),
            "to": Web3.to_checksum_address(data["to"]),
            "amount_ether": float(data["amount"]),
            "tx_hash": data["tx_hash"],
            "block_number": data.get("block_number", None),
            "timestamp": datetime.utcnow()
        }

        try:
            result = payments.insert_one(payment_record)
            print(f"✅ MetaMask payment logged with ID: {result.inserted_id}")
            print("Inserted document:", payments.find_one({"_id": result.inserted_id}))
            return jsonify({"message": "Transaction logged"}), 200
        except Exception as mongo_err:
            print(f"❌ MongoDB insert error: {str(mongo_err)}")
            return jsonify({"status": "error", "message": f"MongoDB error: {str(mongo_err)}"}), 500

    except Exception as e:
        print("❌ Error in /log route:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Flask server is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)