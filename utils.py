# utils.py
import redis
import json
import os

# --- Configuration ---
# Get Redis connection details from environment variables or use defaults
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Define Redis Stream names

INVITATION_STREAM = "invitations_stream"
GUEST_INVITATIONS_STREAM = "guest_invitations_stream"
HOST_SUMMARIES_STREAM = "host_summaries_stream"
# Guest response streams will be dynamic: responses_<invitation_id>_stream

# --- Redis Connection Function ---
def get_redis_connection():
    """Establishes and returns a Redis connection."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
        r.ping() # Test the connection
        print(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"Could not connect to Redis: {e}")
        print("Please ensure Redis is running and accessible.")
        exit(1) # Exit if we can't connect to Redis

# --- Message Handling Functions ---
def serialize_message(message_dict):
    """Converts a Python dictionary to a JSON string."""
    return json.dumps(message_dict)

def deserialize_message(message_string):
    """Converts a JSON string back to a Python dictionary."""
    try:
        return json.loads(message_string)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON message: {e}")
        print(f"Received string: {message_string}")
        return None
    
# --- Authentication (very basic for simulation) ---
VALID_HOST_TOKENS = {"host123"}  # Set of valid host tokens
VALID_GUEST_TOKENS = {"guest1": "token1", "guest2": "token2", "guest3": "token3"}

def validate_host_token(token):
    return token in VALID_HOST_TOKENS

def validate_guest_token(guest_id, token):
    return VALID_GUEST_TOKENS.get(guest_id) == token


# --- Example Usage (for testing purposes, you can remove later) ---
if __name__ == "__main__":
    # Test Redis connection
    r = get_redis_connection()

    # Test message serialization/deserialization
    test_message = {
        "type": "test",
        "data": "hello world",
        "number": 123
    }
    serialized = serialize_message(test_message)
    print(f"Serialized: {serialized}")

    deserialized = deserialize_message(serialized)
    print(f"Deserialized: {deserialized}")

    # You can also try sending a test message to a stream (optional)
    # try:
    #     r.xadd("test_stream", {"message": serialized})
    #     print("Test message added to 'test_stream'")
    # except Exception as e:
    #     print(f"Error adding message to stream: {e}")