import json
import logging
import asyncio
import threading
from typing import Dict

import redis
from fastapi import WebSocket

from app.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.employee_connections: Dict[int, WebSocket] = {}
        self.employee_shop_mapping: Dict[int, int] = {}
        self.customer_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[int, WebSocket] = {}
        self.main_loop = None

        self.use_redis = False
        try:
            self.redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
            )
            self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(
                ["chat_messages", "session_notifications", "employee_notifications"]
            )
            self.use_redis = True
            logger.info("Redis connected at %s:%s", settings.redis_host, settings.redis_port)
        except Exception as exc:
            logger.error("Redis connection failed. Falling back to local in-memory delivery. Error: %s", exc)

        if self.use_redis:
            self._start_listener()

    def _ensure_main_loop(self):
        try:
            self.main_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

    def _start_listener(self):
        def _listen():
            try:
                for message in self.pubsub.listen():
                    if message["type"] == "message":
                        loop = self.main_loop
                        if not loop or not loop.is_running():
                            try:
                                loop = asyncio.get_event_loop()
                            except Exception:
                                pass
                        if loop and loop.is_running():
                            asyncio.run_coroutine_threadsafe(
                                self._handle_message(message), loop
                            )
                        else:
                            # Fallback if no loop threadsafe, attempt local execution
                            logger.warning("Main loop unavailable for Redis message dispatch")
            except Exception as exc:
                logger.error("Redis listener error: %s", exc)

        thread = threading.Thread(target=_listen, daemon=True)
        thread.start()

    async def _handle_message(self, message):
        try:
            channel = message["channel"]
            data = json.loads(message["data"])

            if channel == "chat_messages":
                await self._deliver_chat(data)
            elif channel == "session_notifications":
                if data.get("notification_type") == "broadcast_to_shop":
                    await self._broadcast_shop_local(
                        data["message"],
                        data["shop_id"],
                        exclude_employee_id=data.get("exclude_employee_id"),
                    )
            elif channel == "employee_notifications":
                await self._broadcast_employees_local(data.get("message", ""))
        except Exception as exc:
            logger.exception("Error handling Redis message: %s", exc)

    async def _deliver_chat(self, data):
        target_type = data.get("target_type")
        target_id = data.get("target_id")
        content = data.get("message")

        if target_type == "employee":
            emp_id = int(target_id)
            if emp_id in self.employee_connections:
                try:
                    await self.employee_connections[emp_id].send_text(content)
                except Exception:
                    self.disconnect_employee(emp_id)

        elif target_type == "customer":
            email = str(target_id)
            if email in self.customer_connections:
                try:
                    await self.customer_connections[email].send_text(content)
                except Exception:
                    self.disconnect_customer(email)

        elif target_type == "session":
            sid = int(target_id)
            delivered = False

            if sid in self.session_connections:
                try:
                    await self.session_connections[sid].send_text(content)
                    delivered = True
                except Exception:
                    self.session_connections.pop(sid, None)

            # Fallback to customer connection if available
            if not delivered and "customer_email" in data:
                email = data["customer_email"]
                if email in self.customer_connections:
                    try:
                        await self.customer_connections[email].send_text(content)
                    except Exception:
                        self.disconnect_customer(email)

    async def _broadcast_employees_local(self, message: str):
        for emp_id, ws in list(self.employee_connections.items()):
            try:
                await ws.send_text(message)
            except Exception:
                self.disconnect_employee(emp_id)

    async def _broadcast_shop_local(self, message: str, shop_id: int, exclude_employee_id: int = None):
        for emp_id, ws in list(self.employee_connections.items()):
            if exclude_employee_id is not None and emp_id == exclude_employee_id:
                continue
            if self.employee_shop_mapping.get(emp_id) == shop_id:
                try:
                    await ws.send_text(message)
                except Exception:
                    self.disconnect_employee(emp_id)

    # Connection lifecycle
    async def connect_employee(self, ws: WebSocket, employee_id: int, shop_id: int):
        self._ensure_main_loop()
        await ws.accept()
        self.employee_connections[employee_id] = ws
        self.employee_shop_mapping[employee_id] = shop_id

    async def connect_customer(self, ws: WebSocket, email: str, session_id: int = None):
        self._ensure_main_loop()
        await ws.accept()
        self.customer_connections[email] = ws
        if session_id:
            self.session_connections[session_id] = ws

    def disconnect_employee(self, employee_id: int):
        self.employee_connections.pop(employee_id, None)
        self.employee_shop_mapping.pop(employee_id, None)

    def disconnect_customer(self, email: str, session_id: int = None):
        self.customer_connections.pop(email, None)
        if session_id:
            self.session_connections.pop(session_id, None)

    # Publishing via Redis with fallback
    async def send_to_employee(self, message: str, employee_id: int):
        if self.use_redis:
            self.redis_client.publish(
                "chat_messages",
                json.dumps({"target_type": "employee", "target_id": employee_id, "message": message}),
            )
        else:
            await self._deliver_chat({"target_type": "employee", "target_id": employee_id, "message": message})

    async def send_to_customer(self, message: str, email: str):
        if self.use_redis:
            self.redis_client.publish(
                "chat_messages",
                json.dumps({"target_type": "customer", "target_id": email, "message": message}),
            )
        else:
            await self._deliver_chat({"target_type": "customer", "target_id": email, "message": message})

    async def send_to_session(self, message: str, session_id: int, customer_email: str = None):
        if self.use_redis:
            payload = {"target_type": "session", "target_id": session_id, "message": message}
            if customer_email:
                payload["customer_email"] = customer_email
            self.redis_client.publish("chat_messages", json.dumps(payload))
        else:
            await self._deliver_chat({
                "target_type": "session",
                "target_id": session_id,
                "customer_email": customer_email,
                "message": message,
            })

    async def broadcast_to_employees(self, message: str):
        if self.use_redis:
            self.redis_client.publish(
                "employee_notifications", json.dumps({"message": message})
            )
        else:
            await self._broadcast_employees_local(message)

    async def broadcast_to_shop_employees(self, message: str, shop_id: int, exclude_employee_id: int = None):
        if self.use_redis:
            self.redis_client.publish(
                "session_notifications",
                json.dumps(
                    {
                        "notification_type": "broadcast_to_shop",
                        "shop_id": shop_id,
                        "message": message,
                        "exclude_employee_id": exclude_employee_id,
                    }
                ),
            )
        else:
            await self._broadcast_shop_local(message, shop_id, exclude_employee_id)
