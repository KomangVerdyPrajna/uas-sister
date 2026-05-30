import os
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# 1. ROUTE UNTUK MENAMPILKAN HALAMAN WEB KLINIK
@app.route('/')
def index():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return send_from_directory(current_dir, 'index.html')

# 2. ROUTE APPOINTMENT SESUAI PARAMETER TEMA BARU (POST /appointments)
@app.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    
    # Validasi input data dari gambar parameter
    patient_name = data.get('patient_name')
    doctor_id = data.get('doctor_id')
    date = data.get('date')
    time = data.get('time')
    notes = data.get('notes', '')

    # Mengembalikan response sukses berformat JSON
    return jsonify({
        "status": "success",
        "message": "Appointment successfully scheduled",
        "appointment_details": {
            "patient_name": patient_name,
            "doctor_id": doctor_id,
            "date": date,
            "time": time,
            "notes": notes
        }
    }), 201

if __name__ == '__main__':
    # Server berjalan di port 8000
    app.run(host='0.0.0.0', port=8000)