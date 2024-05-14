from django.core.management.base import BaseCommand
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from django.conf import settings


class Command(BaseCommand):
    help = 'Check connection to Cassandra database'

    def handle(self, *args, **kwargs):
        auth_provider = PlainTextAuthProvider(
            username=settings.CASSANDRA_USERNAME,
            password=settings.CASSANDRA_PASSWORD
        )
        cluster = Cluster(settings.CASSANDRA_HOSTS, auth_provider=auth_provider)
        session = cluster.connect()

        try:
            # Check if the connection is successful by executing a query
            session.execute('SELECT key FROM system.local')
            self.stdout.write(self.style.SUCCESS('Connection to Cassandra database successful'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to connect to Cassandra database: {e}'))
            raise e
        finally:
            cluster.shutdown()
