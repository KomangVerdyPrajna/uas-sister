import os
import json
import sqlite3
import pika
from flask_cors import CORS
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)
CORS(app)

DB_FILE = 'db/appointments.db'
RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
REQ_QUEUE = os.getenv("REQ_QUEUE", "booking_requests")

def init_db():
    os.makedirs('db', exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            doctor_id TEXT,
            date TEXT,
            time TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def publish_to_rabbitmq(payload):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, connection_attempts=5, retry_delay=2))
        channel = connection.channel()
        channel.queue_declare(queue=REQ_QUEUE, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=REQ_QUEUE,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2) # make message persistent
        )
        connection.close()
        return True
    except Exception as e:
        print(f"Failed to publish to RabbitMQ: {e}")
        return False

@app.route('/')
def index():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(current_dir, 'index.html')

@app.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    
    patient_name = data.get('patient_name')
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    time = data.get('time')
    notes = data.get('notes', '')

    # 1. Save to Database
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('INSERT INTO appointments (patient_name, doctor_id, date, time, notes) VALUES (?, ?, ?, ?, ?)',
                  (patient_name, doctor_id, date, time, notes))
        appointment_id = c.lastrowid
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

    payload = {
        "id": appointment_id,
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "date": date,
        "time": time,
        "notes": notes
    }

    # 2. Publish to RabbitMQ
    success = publish_to_rabbitmq(payload)
    rabbitmq_status = "Sent to cluster-queue successfully" if success else "Failed to send to cluster-queue"

    return jsonify({
        "status": "success",
        "message": "Appointment successfully scheduled",
        "rabbitmq_status": rabbitmq_status,
        "data": payload
    }), 201

import requests
CLUSTER_NODES = ["node-1", "node-2", "node-3"]

@app.route('/cluster-status', methods=['GET'])
def cluster_status():
    leader_id = None
    active_nodes = []
    
    for node in CLUSTER_NODES:
        try:
            r = requests.post(f"http://{node}:9000/rpc", json={"method": "who_is_leader", "params": {}}, timeout=0.5)
            if r.status_code == 200:
                active_nodes.append(node)
                data = r.json()
                l_id = data.get("result", {}).get("leader_id")
                if l_id and not leader_id:
                    leader_id = str(l_id)
        except Exception:
            continue
            
    return jsonify({
        "leader_id": leader_id,
        "active_nodes": active_nodes
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)