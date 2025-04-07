import thriftpy2
from thriftpy2.rpc import make_client

# Load the Thrift file
timestamp_thrift = thriftpy2.load("timestamp.thrift", module_name="timestamp_thrift")
Timestamp = timestamp_thrift.TimestampService

# Create a client to call the Thrift server (running on port 10000)
def get_timestamp_from_thrift():
    client = make_client(Timestamp, '127.0.0.1', 10000)  # Connect to Thrift server on port 10000
    return client.getCurrentTimestamp()  # Call the service method to get the current timestamp
