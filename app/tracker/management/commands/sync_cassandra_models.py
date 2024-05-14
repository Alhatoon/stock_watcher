from django.core.management.base import BaseCommand
from cassandra.cqlengine.management import sync_table, drop_table
from cassandra.cqlengine import CQLEngineException
from cassandra.cqlengine import connection
from tracker.models import TrackedProduct, TrackingRecord

class Command(BaseCommand):
    help = 'Synchronize Django models with Cassandra database schema'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Dropping and synchronizing models with Cassandra schema...'))

        # Attempt to drop and sync each model with the database schema
        try:
            drop_table(TrackingRecord)
            sync_table(TrackingRecord)
            self.stdout.write(self.style.SUCCESS('Synchronization complete'))
        except CQLEngineException as e:
            if 'Keyspace' in str(e) and 'does not exist' in str(e):
                # Handle missing keyspace by creating it
                self.stdout.write(self.style.WARNING('Keyspace does not exist. Creating keyspace...'))
                from cassandra.cluster import Cluster
                cluster = Cluster(['db'])
                session = cluster.connect()
                session.execute("CREATE KEYSPACE IF NOT EXISTS stock_watcher_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
                cluster.shutdown()

                # Establish a new connection to the Cassandra cluster
                connection.setup(['db'], "stock_watcher_keyspace")

                # Retry dropping and syncing models
                self.stdout.write(self.style.WARNING('Retrying synchronization...'))
                drop_table(TrackedProduct)
                drop_table(TrackingRecord)
                sync_table(TrackedProduct)
                sync_table(TrackingRecord)
                self.stdout.write(self.style.SUCCESS('Synchronization complete'))
            else:
                raise e