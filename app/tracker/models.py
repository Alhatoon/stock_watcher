from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
import uuid

keyspace_name = 'stock_watcher_keyspace'

class TrackingRecord(Model):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_id = columns.UUID(primary_key=True)
    product_url = columns.Text()
    tracked_word = columns.Text()
    stock_check_interval = columns.Integer(default=60)
    last_checked = columns.DateTime()
    is_active = columns.Boolean(default=True)
