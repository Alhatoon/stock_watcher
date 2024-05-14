# setup_test_keyspace.py

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Cassandra connection settings
CASSANDRA_HOSTS = ['db', 'localhost','172.25.0.2', '127.0.0.1', '::1']
CASSANDRA_KEYSPACE = 'stock_watcher_keyspace'
CASSANDRA_USERNAME = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra'

def setup_test_keyspace():
    # Connect to Cassandra cluster
    auth_provider = PlainTextAuthProvider(username=CASSANDRA_USERNAME, password=CASSANDRA_PASSWORD)
    cluster = Cluster(CASSANDRA_HOSTS, auth_provider=auth_provider)
    session = cluster.connect()

    # Create test keyspace with the same schema as production
    session.execute(f"CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}")
    print(f"Keyspace {CASSANDRA_KEYSPACE} setup completed.")

    # Close connection
    cluster.shutdown()

if __name__ == "__main__":
    setup_test_keyspace()
