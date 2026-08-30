"""
Event Bus
=========

WHY: The backend needs to TELL the frontend what's happening.
     "Hey, I just pulled the Node image!"
     "Oops, Postgres failed to start."

WHAT: A simple pub/sub system. Components SUBSCRIBE to listen.
     The coordinator EMITS events when things happen.
     The WebSocket handler forwards events to the browser.

HOW:
     1. WebSocket handler calls subscribe(ws) when browser connects
     2. Coordinator calls emit("step_done", {...}) when a step finishes
     3. Bus sends the event to ALL subscribed WebSockets
     4. If a WebSocket is dead, we remove it (don't crash)

THINK OF IT LIKE:
     A newspaper delivery system.
     - Subscribers = people who want the newspaper
     - Events = the newspaper articles
     - The bus delivers the newspaper to everyone on the list
"""

import json
from typing import List, Any
from app.utils.logger import get_logger

logger = get_logger("bus")

subscribers: List[Any] = []


def subscribe(client: Any) -> None:
    """Register a WebSocket client to receive events."""
    subscribers.append(client)
    logger.info("client subscribed (%d total)", len(subscribers))


def unsubscribe(client: Any) -> None:
    """Remove a WebSocket client from the list."""
    if client in subscribers:
        subscribers.remove(client)
        logger.info("client unsubscribed (%d total)", len(subscribers))


async def emit(event_type: str, data: dict) -> None:
    """Send an event to ALL connected clients.

    If a client's WebSocket is dead, we remove it silently.
    We don't let one broken connection crash the whole system.
    """
    message = json.dumps({"type": event_type, "data": data})

    # WHY list(subscribers)? We must iterate over a SNAPSHOT (copy) of the list.
    # During `await sub.send_text(message)`, the event loop yields.
    # If a WebSocket disconnects during that yield, ws.py's finally block
    # calls unsubscribe() which mutates the live `subscribers` list.
    # Iterating a live list while it's being mutated causes:
    #   - Skipped clients (events never reach them)
    #   - RuntimeError: list changed size during iteration
    dead = []
    for sub in list(subscribers):
        try:
            await sub.send_text(message)
        except Exception:
            dead.append(sub)

    for client in dead:
        unsubscribe(client)

    if dead:
        logger.warning("removed %d dead clients", len(dead))
