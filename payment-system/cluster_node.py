import os, time, threading, logging
from typing import Dict, Optional
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
log_werkzeug = logging.getLogger('werkzeug')
log_werkzeug.setLevel(logging.ERROR)

NODE_NAME = os.getenv("NODE_NAME", "node-1")
NODE_ID = int(os.getenv("NODE_ID", "1"))
ALL_NODES_RAW = os.getenv("ALL_NODES", "node-1:1,node-2:2,node-3:3")

NODES: Dict[int, str] = {}
for item in [x.strip() for x in ALL_NODES_RAW.split(",") if x.strip()]:
    host, sid = item.split(":")
    NODES[int(sid)] = host

# SORTED nodes for ring topology
RING = sorted(NODES.keys()) # e.g. [1, 2, 3]
my_index = RING.index(NODE_ID)

SELF_URL = f"http://{NODE_NAME}:9000"

state_lock = threading.Lock()
leader_id: Optional[int] = None
leader_url: Optional[str] = None
is_leader = False
election_in_progress = False
participant = False # For LCR election
last_heartbeat = time.time()

def log(msg: str):
    print(f"[{NODE_NAME} id={NODE_ID}] {msg}", flush=True)

def rpc_call(url: str, method: str, params: dict, timeout=1.0):
    r = requests.post(f"{url}/rpc", json={"method": method, "params": params}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def get_next_active_node():
    # Find the next node in the ring that is active
    for offset in range(1, len(RING)):
        next_idx = (my_index + offset) % len(RING)
        next_id = RING[next_idx]
        host = NODES[next_id]
        # simple ping/healthcheck
        try:
            r = requests.get(f"http://{host}:9000/health", timeout=0.5)
            if r.status_code == 200:
                return next_id, host
        except Exception:
            continue
    return None, None

def forward_election(msg_id: int):
    next_id, next_host = get_next_active_node()
    if not next_id:
        # I am the only one alive
        become_leader()
        return
    try:
        rpc_call(f"http://{next_host}:9000", "ring_election", {"msg_id": msg_id}, timeout=1.0)
    except Exception as e:
        log(f"Failed to forward election to {next_id}: {e}")

def forward_coordinator(l_id: int, l_url: str):
    next_id, next_host = get_next_active_node()
    if not next_id:
        return
    try:
        rpc_call(f"http://{next_host}:9000", "ring_coordinator", {"leader_id": l_id, "leader_url": l_url}, timeout=1.0)
    except Exception as e:
        log(f"Failed to forward coordinator to {next_id}: {e}")

def become_leader():
    global leader_id, leader_url, is_leader, election_in_progress, participant, last_heartbeat
    with state_lock:
        leader_id = NODE_ID
        leader_url = SELF_URL
        is_leader = True
        election_in_progress = False
        participant = False
        last_heartbeat = time.time()
    log("BECOME LEADER -> circulate coordinator")
    forward_coordinator(leader_id, leader_url)

def start_election():
    global election_in_progress, participant
    with state_lock:
        if election_in_progress:
            return
        election_in_progress = True
        participant = True
        leader_id = None
        is_leader = False

    log("ELECTION started (Token Ring)")
    forward_election(NODE_ID)
    
    # Wait and retry if no coordinator received
    def wait_and_retry():
        global election_in_progress, participant
        time.sleep(3.0)
        with state_lock:
            still_waiting = election_in_progress
        if still_waiting:
            log("Election timeout, retrying...")
            with state_lock:
                election_in_progress = False
                participant = False
            start_election()
            
    threading.Thread(target=wait_and_retry, daemon=True).start()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "up"})

@app.post("/rpc")
def rpc():
    global last_heartbeat, leader_id, leader_url, is_leader, election_in_progress, participant

    body = request.get_json(force=True, silent=True) or {}
    method = body.get("method")
    params = body.get("params") or {}

    if method == "who_is_leader":
        with state_lock:
            return jsonify({"result": {"leader_id": leader_id, "leader_url": leader_url, "i_am_leader": is_leader}})

    if method == "heartbeat":
        with state_lock:
            l_id = params.get("leader_id")
            if l_id is not None:
                leader_id = int(l_id)
                leader_url = params.get("leader_url")
                is_leader = (leader_id == NODE_ID)
            last_heartbeat = time.time()
            election_in_progress = False
        return jsonify({"result": "OK"})

    if method == "ring_election":
        msg_id = int(params.get("msg_id"))
        log(f"Received ring_election(msg_id={msg_id})")
        
        with state_lock:
            if msg_id > NODE_ID:
                participant = True
                threading.Thread(target=forward_election, args=(msg_id,), daemon=True).start()
            elif msg_id < NODE_ID:
                if not participant:
                    participant = True
                    threading.Thread(target=forward_election, args=(NODE_ID,), daemon=True).start()
            else:
                threading.Thread(target=become_leader, daemon=True).start()
        return jsonify({"result": "OK"})

    if method == "ring_coordinator":
        l_id = int(params.get("leader_id"))
        l_url = params.get("leader_url")
        log(f"Received ring_coordinator(leader_id={l_id})")
        
        with state_lock:
            if l_id != NODE_ID:
                leader_id = l_id
                leader_url = l_url
                is_leader = False
                election_in_progress = False
                participant = False
                last_heartbeat = time.time()
                threading.Thread(target=forward_coordinator, args=(l_id, l_url), daemon=True).start()
            else:
                election_in_progress = False
                participant = False
                is_leader = True
                last_heartbeat = time.time()
                log("Election Complete. I am the confirmed leader.")
        return jsonify({"result": "OK"})

    if method == "process_notification":
        with state_lock:
            local_is_leader = is_leader
            l_id = leader_id
            l_url = leader_url

        if not local_is_leader:
            return jsonify({"error": {"code": "NOT_LEADER", "leader_id": l_id, "leader_url": l_url}}), 409

        appointment_data = params.get("appointment", {})
        log(f"Leader processing notification for: {appointment_data.get('patient_name')}")
        time.sleep(0.5) 
        result = {
            "status": "Notification Sent",
            "processed_by_node": NODE_NAME,
            "processed_at": time.time()
        }
        return jsonify({"result": result})

    return jsonify({"error": {"code": "NO_SUCH_METHOD"}}), 400

def heartbeat_loop():
    while True:
        time.sleep(1.0)
        with state_lock:
            if not is_leader:
                continue
            hb = {"leader_id": leader_id, "leader_url": leader_url}
            
        for nid, host in NODES.items():
            if nid == NODE_ID:
                continue
            try:
                rpc_call(f"http://{host}:9000", "heartbeat", hb, timeout=1.0)
            except Exception:
                pass

def monitor_loop():
    while True:
        time.sleep(0.5)
        with state_lock:
            if is_leader or election_in_progress:
                continue
            lh = last_heartbeat
        
        if (time.time() - lh) > 5.0:
            start_election()

def bootstrap():
    time.sleep(1.0 + 0.2 * NODE_ID)
    start_election()

if __name__ == "__main__":
    threading.Thread(target=heartbeat_loop, daemon=True).start()
    threading.Thread(target=monitor_loop, daemon=True).start()
    threading.Thread(target=bootstrap, daemon=True).start()
    log("starting cluster node on :9000")
    app.run(host="0.0.0.0", port=9000, threaded=True)
