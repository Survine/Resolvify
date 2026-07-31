import asyncio
import json
import urllib.request
import urllib.parse
import sys

FRONTEND_BASE = "http://localhost:5173"
WS_BASE = "ws://localhost:5173"

def http_post(url, data_dict=None, headers=None):
    if headers is None:
        headers = {}
    if data_dict is not None:
        data_bytes = json.dumps(data_dict).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        data_bytes = None
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def http_post_form(url, form_dict):
    data_bytes = urllib.parse.urlencode(form_dict).encode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def http_get(url, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def http_put(url, data_dict=None, headers=None):
    if headers is None:
        headers = {}
    data_bytes = json.dumps(data_dict).encode('utf-8') if data_dict else None
    if data_bytes:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method='PUT')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

async def run_test():
    print("=== Step 1: Fetch Available Shops via Frontend Proxy ===")
    shops = http_get(f"{FRONTEND_BASE}/chat/shops/")
    print(f"Shops found: {len(shops)}")
    for shop in shops:
        print(f" - [{shop['id']}] {shop['name']} ({shop['location']})")
    assert len(shops) > 0, "No shops found!"

    shop_id = shops[0]['id']

    print("\n=== Step 2: Register Customer ===")
    customer_email = "test.user@resolvify.in"
    customer_name = "Test Customer"
    cust_res = http_post(f"{FRONTEND_BASE}/customers/", {"name": customer_name, "email": customer_email})
    print(f"Customer registered/found: {cust_res}")

    print("\n=== Step 3: Create Chat Session ===")
    encoded_email = urllib.parse.quote(customer_email)
    session_res = http_post(f"{FRONTEND_BASE}/chat/sessions/?customer_email={encoded_email}&shop_id={shop_id}")
    session_id = session_res['id']
    print(f"Chat Session Created! Session ID: {session_id}, Status: {session_res['status']}")

    print("\n=== Step 4: Login as Support Employee ===")
    login_res = http_post_form(f"{FRONTEND_BASE}/auth/token", {
        "username": "support1",
        "password": "support123"
    })
    token = login_res['access_token']
    auth_headers = {"Authorization": f"Bearer {token}"}
    print(f"Login successful! Employee token acquired.")

    print("\n=== Step 5: Check Employee Profile & Waiting Queue ===")
    emp_profile = http_get(f"{FRONTEND_BASE}/employees/me", headers=auth_headers)
    print(f"Employee Profile: {emp_profile['first_name']} {emp_profile['last_name']} ({emp_profile['username']})")
    
    waiting_queue = http_get(f"{FRONTEND_BASE}/chat/sessions/waiting", headers=auth_headers)
    print(f"Waiting Sessions in Queue: {[s['id'] for s in waiting_queue]}")
    assert any(s['id'] == session_id for s in waiting_queue), f"Session {session_id} not in waiting queue!"

    print("\n=== Step 6: Assign Session to Support Agent ===")
    assign_res = http_put(f"{FRONTEND_BASE}/chat/sessions/{session_id}/assign", headers=auth_headers)
    print(f"Assign response: {assign_res}")

    active_sessions = http_get(f"{FRONTEND_BASE}/chat/sessions/active", headers=auth_headers)
    print(f"Employee Active Sessions: {[s['id'] for s in active_sessions]}")
    assert any(s['id'] == session_id for s in active_sessions), f"Session {session_id} not active!"

    print("\n=== Step 7: Test Real-Time WebSocket Chat Flow via Vite WS Proxy ===")
    import websockets
    
    cust_ws_url = f"{WS_BASE}/chat/ws/customer/{encoded_email}"
    emp_ws_url = f"{WS_BASE}/chat/ws/employee/{emp_profile['id']}"

    async with websockets.connect(cust_ws_url) as cust_ws, websockets.connect(emp_ws_url) as emp_ws:
        print("Both Customer and Employee WebSockets connected successfully!")

        # Customer sends a message
        cust_msg = {"type": "chat_message", "session_id": session_id, "message": "Hello, I need help with my order!"}
        await cust_ws.send(json.dumps(cust_msg))
        print("Customer sent message:", cust_msg['message'])

        # Employee receives message
        received_by_emp = False
        for _ in range(3):
            msg_raw = await asyncio.wait_for(emp_ws.recv(), timeout=3.0)
            msg_data = json.loads(msg_raw)
            print("Employee received WS event:", msg_data)
            if msg_data.get("type") == "message" and msg_data.get("from") == "customer":
                assert msg_data["message"] == "Hello, I need help with my order!"
                received_by_emp = True
                break
        assert received_by_emp, "Employee did not receive customer message!"

        # Employee sends a response
        emp_reply = {"type": "chat_message", "session_id": session_id, "message": "Hi! I am happy to assist you. What is your order ID?"}
        await emp_ws.send(json.dumps(emp_reply))
        print("Employee sent message:", emp_reply['message'])

        # Customer receives message
        received_by_cust = False
        for _ in range(3):
            msg_raw = await asyncio.wait_for(cust_ws.recv(), timeout=3.0)
            msg_data = json.loads(msg_raw)
            print("Customer received WS event:", msg_data)
            if msg_data.get("type") == "message" and msg_data.get("from") == "support":
                assert msg_data["message"] == "Hi! I am happy to assist you. What is your order ID?"
                received_by_cust = True
                break
        assert received_by_cust, "Customer did not receive employee response!"

    print("\n=== Step 8: Verify Session History ===")
    messages_history = http_get(f"{FRONTEND_BASE}/chat/sessions/{session_id}/messages")
    print(f"Stored Messages Count: {len(messages_history)}")
    for m in messages_history:
        sender = "Customer" if m['is_from_customer'] else "Support Agent"
        print(f" - [{sender}]: {m['message']}")

    print("\n=== Step 9: Close Chat Session ===")
    close_res = http_put(f"{FRONTEND_BASE}/chat/sessions/{session_id}/close", headers=auth_headers)
    print(f"Close response: {close_res}")

    session_final = http_get(f"{FRONTEND_BASE}/chat/sessions/{session_id}")
    print(f"Final session status: {session_final['status']}")
    assert session_final['status'] == 'closed', "Session is not closed!"

    print("\n✅ ALL FRONTEND & BACKEND CHAT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_test())
