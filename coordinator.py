# coordinator.py

import time
from utils import (
    get_redis_connection,
    serialize_message,
    deserialize_message,
    INVITATION_STREAM,
    GUEST_INVITATIONS_STREAM,
    HOST_SUMMARIES_STREAM
)

GUEST_LIST = ["guest1", "guest2", "guest3"]

def main():
    redis_conn = get_redis_connection()
    print(f"[Coordinator] Listening on '{INVITATION_STREAM}' for new invitations...")
    last_id = '0-0'

    while True:
        # Step 1: Wait for an invitation from Host
        invitations = redis_conn.xread({INVITATION_STREAM: last_id}, block=0, count=1)
        if not invitations:
            continue

        for stream, messages in invitations:
            for msg_id, data in messages:
                last_id = msg_id
                invitation = deserialize_message(data.get("data", ""))
                if not invitation:
                    continue

                invitation_id = invitation["invitation_id"]
                print(f"[Coordinator] Received invitation '{invitation_id}' - forwarding to guests...")

                # Step 2: Forward to guests via guest_invitations_stream
                for guest in GUEST_LIST:
                    guest_invite = {
                        "guest": guest,
                        "invitation": invitation
                    }
                    redis_conn.xadd(GUEST_INVITATIONS_STREAM, {"data": serialize_message(guest_invite)})
                
                print(f"[Coordinator] Waiting for responses for invitation '{invitation_id}'...")

                # Step 3: Collect responses
                expected = set(GUEST_LIST)
                received = {}
                last_response_id = '0-0'
                response_stream = f"responses_{invitation_id}_stream"

                while expected:
                    response_msgs = redis_conn.xread({response_stream: last_response_id}, block=10000, count=1)
                    if not response_msgs:
                        continue

                    for stream_name, response_data in response_msgs:
                        for resp_id, msg_data in response_data:
                            last_response_id = resp_id
                            response = deserialize_message(msg_data.get("data", ""))
                            guest = response.get("guest")
                            decision = response.get("response")

                            if guest in expected:
                                received[guest] = decision
                                expected.remove(guest)
                                print(f"[Coordinator] Received response from {guest}: {decision}")

                # Step 4: Send summary back to host
                summary = {
                    "invitation_id": invitation_id,
                    "responses": received
                }

                redis_conn.xadd(HOST_SUMMARIES_STREAM, {"data": serialize_message(summary)})
                print(f"[Coordinator] Sent summary to Host for invitation '{invitation_id}'.")

if __name__ == "__main__":
    main()
