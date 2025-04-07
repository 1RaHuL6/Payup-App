import threading
import thriftpy2
from thriftpy2.rpc import make_server
import time

# Load the Timestamp thrift definition
timestamp_thrift = thriftpy2.load("timestamp.thrift", module_name="timestamp_thrift")
Timestamp = timestamp_thrift.TimestampService


# Define the handler class
class TimestampHandler:

    # To get the current system timestamp
    def getCurrentTimestamp(self):
        return int(time.time())

    # To echo the provided timestamp
    def echoTimestamp(self, timestamp):
        return timestamp


def run_server():
    handler = TimestampHandler()
    server = make_server(Timestamp, handler, '127.0.0.1', 10000)
    print("Thrift server started. Listening on port 10000...")
    server.serve()


if __name__ == "__main__":
    # Create a separate thread to run the Thrift server
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Do other tasks here if necessary
    try:
        while True:
            pass  # Keep the main thread alive if needed
    except KeyboardInterrupt:
        print("Server stopped.")
