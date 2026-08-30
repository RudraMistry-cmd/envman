"""
WebSocket Handler
=================

WHY: HTTP is like sending a letter.
     You ask a question, get an answer, done.

     But setup takes 30-60 seconds.
     You need LIVE updates. "Step 1 done. Step 2 running..."

     WebSocket is like a phone call.
     The connection STAYS OPEN.
     The server can PUSH updates to the client anytime.

WHAT: Manages WebSocket connections from the frontend.

HOW:
     1. Frontend connects to ws://localhost:8000/ws
     2. We add them to the subscriber list
     3. When coordinator emits events, they get sent to this WebSocket
     4. When the frontend disconnects, we remove them
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.events.bus import subscribe, unsubscribe
from app.utils.logger import get_logger

logger = get_logger("ws")

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle a WebSocket connection from the frontend."""
    await websocket.accept()
    subscribe(websocket)
    logger.info("frontend connected via WebSocket")

    try:
        # Keep the connection open until the frontend disconnects
        # We don't need to receive messages from the frontend
        while True:
            # Wait for any message (or disconnect)
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("frontend disconnected from WebSocket")
    finally:
        unsubscribe(websocket)
