# host.py

import uuid
import time
from utils import get_redis_connection, serialize_message, deserialize_message, INVITATION_STREAM, HOST_SUMMARIES_STREAM

def main():
    redis_conn = get_redis_connection()

    # Step 1: Create and publish the invitation
    invitation_id = str(uuid.uuid4())
    invitation = {
        "invitation_id": invitation_id,
        "host_name": "Alice",
        "event_name": "Python Party",
        "event_time": "2025-06-20 18:00",
        "message": "You're invited to a fun evening with pizza and code!"
    }

    redis_conn.xadd(INVITATION_STREAM, {"data": serialize_message(invitation)})
    print(f"[Host] Published invitation {invitation_id} to '{INVITATION_STREAM}'")

    # Step 2: Listen for the summary
    print(f"[Host] Waiting for summary on '{HOST_SUMMARIES_STREAM}'...")
    last_id = '0-0'

    while True:
        responses = redis_conn.xread({HOST_SUMMARIES_STREAM: last_id}, block=0, count=1)
        if responses:
            for stream, messages in responses:
                for msg_id, data in messages:
                    last_id = msg_id
                    summary_data = deserialize_message(data.get("data", ""))
                    if summary_data and summary_data.get("invitation_id") == invitation_id:
                        print(f"\n[Host] Received Summary for Event '{invitation['event_name']}':")
                        for guest, response in summary_data.get("responses", {}).items():
                            print(f"  - {guest}: {response}")
                        return

if __name__ == "__main__":
    main()
