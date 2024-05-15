from django.core.management.base import BaseCommand
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Cassandra connection settings
CASSANDRA_HOSTS = ['db', 'localhost','172.25.0.2', '127.0.0.1', '::1']
CASSANDRA_KEYSPACE = 'stock_watcher_keyspace'
CASSANDRA_USERNAME = 'cassandra'
CASSANDRA_PASSWORD = 'cassandra'

class Command(BaseCommand):
    help = 'Sets up the test keyspace'

    def handle(self, *args, **options):
        # Connect to Cassandra cluster
        auth_provider = PlainTextAuthProvider(username=CASSANDRA_USERNAME, password=CASSANDRA_PASSWORD)
        cluster = Cluster(CASSANDRA_HOSTS, auth_provider=auth_provider)
        session = cluster.connect()

        # Create test keyspace with the same schema as production
        session.execute(f"CREATE KEYSPACE IF NOT EXISTS {CASSANDRA_KEYSPACE} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}")
        self.stdout.write(self.style.SUCCESS(f"Keyspace {CASSANDRA_KEYSPACE} setup completed."))

        # Close connection
        cluster.shutdown()