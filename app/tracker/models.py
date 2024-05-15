from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
import uuid
import bcrypt
import random

from django.db import models


keyspace_name = 'stock_watcher_keyspace'

class CustomUser(Model):
    email = columns.Text(primary_key=True) # So we can make some sort of relations between the two tables
    password_hash = columns.Text()  # Store hashed password instead of plain text
    
    def set_password(self, raw_password):
        # Hash the raw password and store the hash
        self.password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, raw_password):
        # Check if the raw password matches the stored hashed password
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password_hash.encode('utf-8'))


# Further down in requirements token generation, token expiry, token refresh, and other features to enhance security and usability.
class Token(Model):
    token = columns.Text(primary_key=True) # So we can make some sort of relations between the two tables
    user_email = columns.Text(index=True)
    
    # Cassandra has no built-in to_dict  :((( 
    def to_dict(self):
        return {
            'user_email': self.user_email,
            'token': self.token,
        }


class TrackingRecord(Model):
    id = columns.Integer(primary_key=True, default=random.randint(1, 1000000))
    user_email = columns.Text(primary_key=True) # So we can make some sort of relations between the two tables
    product_url = columns.Text(index=True)
    tracked_word = columns.Text(index=True)
    stock_check_interval = columns.Integer(index=True, default=60)
    last_checked = columns.DateTime(index=True)
    is_active = columns.Boolean(default=True, index=True)
