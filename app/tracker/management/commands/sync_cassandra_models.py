from django.core.management.base import BaseCommand
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine import CQLEngineException
from cassandra import InvalidRequest
from cassandra.cqlengine import connection
from tracker.models import TrackingRecord, CustomUser, Token
from cassandra.cluster import Cluster

class Command(BaseCommand):
    help = 'Synchronize Django models with Cassandra database schema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Dropping and synchronizing models with Cassandra schema...'))

        # Establish a connection to the Cassandra cluster
        cluster = Cluster(['db'])
        session = cluster.connect()

        # Attempt to drop the keyspace
        try:
            session.execute("DROP KEYSPACE IF EXISTS stock_watcher_keyspace")
            self.stdout.write(self.style.SUCCESS('Dropping complete'))
        except InvalidRequest as e:
            if 'unconfigured' in str(e):
                self.stdout.write(self.style.WARNING('Keyspace does not exist. Skipping drop...'))
            else:
                raise e

        # Create the keyspace if it doesn't exist
        session.execute("CREATE KEYSPACE IF NOT EXISTS stock_watcher_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")

        # Establish a new connection to the Cassandra cluster
        connection.setup(['db'], "stock_watcher_keyspace")

        # Retry syncing models
        self.stdout.write(self.style.WARNING('Retrying synchronization...'))
        try:
            sync_table(TrackingRecord)
            sync_table(CustomUser)
            sync_table(Token)
            self.stdout.write(self.style.SUCCESS('Synchronization complete'))
        except CQLEngineException as e:
            raise e