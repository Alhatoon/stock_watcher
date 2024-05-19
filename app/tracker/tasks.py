
from celery import shared_task
from .models import TrackingRecord 
# from . import check_stock_availability


@shared_task
def check_all_stock_availability():
    tracking_records = TrackingRecord.objects.filter(is_active=True)
    for tracking_record in tracking_records:
        check_stock_availability.delay(tracking_record.id)