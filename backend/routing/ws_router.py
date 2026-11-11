import asyncio

import json

import queue

import threading

from typing import Optional



import redis

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from jose import JWTError, jwt



from core.config import configs

from core.logging_config import logger

from core.redis_pubsub import user_channel

from core.database import async_session

from repositories.users_repository import UserRepository



router = APIRouter(tags=["WebSocket"])



_REDIS_PUBSUB_TIMEOUT_SEC = 1.0





def _redis_listener_thread(

    channel: str,

    out_queue: queue.Queue,

    stop_event: threading.Event,

) -> None:

    """Синхронный pubsub в отдельном потоке — не блокирует event loop FastAPI."""

    client = redis.from_url(

        configs.REDIS_URL,

        decode_responses=True,

        socket_timeout=_REDIS_PUBSUB_TIMEOUT_SEC,

        socket_connect_timeout=5,

    )

    pubsub = client.pubsub(ignore_subscribe_messages=True)

    try:

        pubsub.subscribe(channel)

        while not stop_event.is_set():

            message = pubsub.get_message(timeout=_REDIS_PUBSUB_TIMEOUT_SEC)

            if not message or message.get("type") != "message":

                continue

            data = message.get("data")

            if data is not None:

                out_queue.put(data)

    except Exception:

        logger.exception("Redis pubsub thread failed for channel {}", channel)

    finally:

        try:

            pubsub.unsubscribe(channel)

            pubsub.close()

        except Exception:

            pass

        client.close()





async def _resolve_user_id_from_token(token: str) -> Optional[int]:

    try:

        payload = jwt.decode(token, configs.SECRET_KEY, algorithms=[configs.ALGORITHM])

        user_identifier: str = payload.get("sub")

        if not user_identifier:

            return None

    except JWTError:

        return None



    async with async_session() as session:

        repo = UserRepository(session)

        user = None

        if user_identifier.isdigit():

            user = await repo.get_by_id(int(user_identifier))

        if user is None:

            user = await repo.find_one_or_none(user_identifier)

        return user.id if user else None





def _token_from_subprotocol(websocket: WebSocket) -> tuple[Optional[str], Optional[str]]:
    """Токен из Sec-WebSocket-Protocol вида 'bearer.<jwt>' — не попадает в access-логи."""
    header = websocket.headers.get("sec-websocket-protocol", "")
    for part in header.split(","):
        part = part.strip()
        if part.startswith("bearer."):
            return part[len("bearer.") :], part
    return None, None


@router.websocket("/ws/notifications")

async def websocket_notifications(

    websocket: WebSocket,

    token: Optional[str] = Query(None, description="JWT access token"),

):

    subprotocol = None

    if not token:

        token, subprotocol = _token_from_subprotocol(websocket)

    if not token:

        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

        return

    user_id = await _resolve_user_id_from_token(token)

    if not user_id:

        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)

        return



    await websocket.accept(subprotocol=subprotocol)

    channel = user_channel(user_id)

    msg_queue: queue.Queue = queue.Queue()

    stop_event = threading.Event()

    listener = threading.Thread(

        target=_redis_listener_thread,

        args=(channel, msg_queue, stop_event),

        name=f"ws-redis-{user_id}",

        daemon=True,

    )

    listener.start()



    try:

        await websocket.send_json(

            {"type": "connected", "message": "Подключено к уведомлениям"}

        )



        while True:

            while True:

                try:

                    raw = msg_queue.get_nowait()

                except queue.Empty:

                    break

                if isinstance(raw, str):

                    try:

                        payload = json.loads(raw)

                    except json.JSONDecodeError:

                        payload = {"type": "raw", "message": raw}

                else:

                    payload = raw

                await websocket.send_json(payload)



            try:

                incoming = await asyncio.wait_for(

                    websocket.receive_text(), timeout=_REDIS_PUBSUB_TIMEOUT_SEC

                )

            except asyncio.TimeoutError:

                continue



            if incoming == "ping":

                await websocket.send_json({"type": "pong"})



    except WebSocketDisconnect:

        pass

    finally:

        stop_event.set()

        listener.join(timeout=3)


