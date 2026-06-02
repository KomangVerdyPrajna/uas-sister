import os, json, time
import pika
import requests

RABBIT_HOST = os.getenv("RABBIT_HOST", "rabbitmq")
REQ_QUEUE = os.getenv("REQ_QUEUE", "booking_requests")
CLUSTER_NODES = os.getenv("ALL_NODES", "node-1:9000,node-2:9000,node-3:9000").split(",")

def call_cluster_rpc(payload):
    leader_url = None
    for node in CLUSTER_NODES:
        host = node.split(":")[0]
        try:
            r = requests.post(f"http://{host}:9000/rpc", json={"method": "who_is_leader", "params": {}}, timeout=1.0)
            if r.status_code == 200:
                data = r.json()
                leader_url = data.get("result", {}).get("leader_url")
                if leader_url:
                    break
        except Exception:
            continue
    
    if not leader_url:
        print("[worker] Could not find leader. Nodes might be down.")
        return False
        
    try:
        r = requests.post(f"{leader_url}/rpc", json={"method": "process_notification", "params": {"appointment": payload}}, timeout=2.0)
        if r.status_code == 200:
            print(f"[worker] Successfully processed by leader: {r.json()}")
            return True
        elif r.status_code == 409:
            # Not leader anymore? 
            print("[worker] Node is not leader, will retry.")
            return False
        else:
            print(f"[worker] Leader returned status {r.status_code}: {r.text}")
            return False
    except Exception as e:
        print(f"[worker] Error communicating with leader {leader_url}: {e}")
        return False

def main():
    print("[worker] Starting and waiting for RabbitMQ...", flush=True)
    time.sleep(5) 
    conn = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, connection_attempts=15, retry_delay=2))
    ch = conn.channel()
    ch.queue_declare(queue=REQ_QUEUE, durable=True)
    ch.basic_qos(prefetch_count=1)

    def on_message(ch, method, properties, body):
        req = json.loads(body.decode("utf-8"))
        print(f"[worker] Received booking request: {req}", flush=True)

        success = call_cluster_rpc(req)
        if success:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            print("[worker] Requeueing message due to failure")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            time.sleep(2)

    ch.basic_consume(queue=REQ_QUEUE, on_message_callback=on_message, auto_ack=False)
    print("[worker] Waiting for booking requests...", flush=True)
    ch.start_consuming()

if __name__ == "__main__":
    main()
