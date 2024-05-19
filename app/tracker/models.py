import datetime
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
    password_hash = columns.Text(max_length=128) # Security Store hashed password instead of plain text
    otp = columns.Text(max_length=6, required=False) # Store OTP for user temporary with a short expiration
    otp_url = columns.Text(required=False) # Store URL associated with the OTP
    otp_expiration = columns.DateTime(required=False) # Store the expiration time of the OTP
    
    
    def set_password(self, raw_password):
        self.password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def set_otp(self, otp, url):
        self.otp = otp
        self.otp_expiration = datetime.datetime.now() + datetime.timedelta(minutes=10)
        self.otp_url = url
    
    def check_otp(self, otp):
        return self.otp == otp and self.otp_expiration > datetime.datetime.now()


# Further down in requirements token generation, token expiry, token refresh, and other features to enhance security and usability.
# User based Token 
class Token(Model):
    user_email = columns.Text(primary_key=True) # So we can make some sort of relations between the two tables
    token = columns.Text(index=True) 
    
    # Cassandra has no built-in to_dict  :((( 
    def to_dict(self):
        return {
            'user_email': self.user_email,
            'token': self.token,
        }


class TrackingRecord(Model):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    user_email = columns.Text(index=True) # So we can make some sort of relations between the two tables
    product_url = columns.Text(index=True)
    tracked_word = columns.Text(index=True)
    stock_check_interval = columns.Integer(index=True, default=60)
    last_checked = columns.DateTime(index=True)
    is_active = columns.Boolean(default=True, index=True)
