# guest.py

import os
import random
import time
from utils import (
    get_redis_connection,
    serialize_message,
    deserialize_message,
    validate_guest_token,
    GUEST_INVITATIONS_STREAM
)

GUEST_ID = os.getenv("GUEST_ID", "")
GUEST_TOKEN = os.getenv("GUEST_TOKEN", "")
if not validate_guest_token(GUEST_ID, GUEST_TOKEN):
    print(f"[{GUEST_ID}] Invalid or missing GUEST_TOKEN. Exiting.")
    exit(1)

redis_conn = get_redis_connection()
print(f"[{GUEST_ID}] Listening for invitations on '{GUEST_INVITATIONS_STREAM}'...")


def main():
    redis_conn = get_redis_connection()

    guest_id = os.getenv("GUEST_ID")
    if not guest_id:
        print("Error: GUEST_ID environment variable not set.")
        return

    print(f"[{guest_id}] Listening for invitations on '{GUEST_INVITATIONS_STREAM}'...")
    last_id = '0-0'

    while True:
        messages = redis_conn.xread({GUEST_INVITATIONS_STREAM: last_id}, block=0, count=1)
        if not messages:
            continue

        for stream_name, msgs in messages:
            for msg_id, data in msgs:
                last_id = msg_id
                payload = deserialize_message(data.get("data", ""))
                if not payload:
                    continue

                target_guest = payload.get("guest")
                invitation = payload.get("invitation")
                invitation_id = invitation.get("invitation_id")

                if target_guest != guest_id:
                    continue  # Skip if not meant for this guest

                print(f"[{guest_id}] Received invitation: '{invitation['event_name']}' from {invitation['host_name']}")

                # Simulate decision-making
                decision = random.choice(["Yes", "No", "Maybe"])
                print(f"[{guest_id}] Responding: {decision}")

                response = {
                    "invitation_id": invitation_id,
                    "guest": guest_id,
                    "response": decision
                }

                response_stream = f"responses_{invitation_id}_stream"
                redis_conn.xadd(response_stream, {"data": serialize_message(response)})

if __name__ == "__main__":
    main()
