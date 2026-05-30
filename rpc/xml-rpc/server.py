from xmlrpc.server import SimpleXMLRPCServer
# Tambahkan library database kalian nanti di sini (misal: mysql.connector)

def check_slot_availability(slot_id):
    """
    Fungsi RPC untuk mengecek apakah sebuah slot tempat masih kosong.
    Nanti di sini kalian hubungkan ke database asli kelompok kalian!
    """
    # ---- INI SIMULASI DATABASE JADWAL/TEMPAT ----
    # 0 berarti penuh, 1 berarti tersedia
    daftar_slot = {"slot_pagi": 1, "slot_siang": 0, "slot_sore": 1}
    
    # Ambil status berdasarkan slot_id yang dikirim client
    status = daftar_slot.get(slot_id.lower(), "Slot tidak ditemukan")
    
    if status == 1:
        return "Tersedia"
    elif status == 0:
        return "Penuh"
    else:
        return status

# Initialize the server pada port 8000
server = SimpleXMLRPCServer(("localhost", 8000))

# Daftarkan fungsi baru kalian dengan nama RPC "verify_slot"
server.register_function(check_slot_availability, "verify_slot")

print("Service Slot Checker (RPC) sudah aktif. Menunggu panggilan...")
server.serve_forever()