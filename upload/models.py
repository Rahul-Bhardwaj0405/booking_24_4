from django.db import models

class BookingData(models.Model):
    txn_date = models.DateField(null=True, blank=True)  # Allow null dates if missing
    credited_on_date = models.DateField(null=True, blank=True)  # Credited on date from the file
    booking_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # booking amount
    irctc_order_no = models.BigIntegerField(null=True, blank=True)  # Removed default value to prevent unintentional duplicates
    bank_booking_ref_no = models.BigIntegerField(null=True, blank=True)  # Same for bank booking reference number

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['txn_date', 'credited_on_date', 'irctc_order_no', 'bank_booking_ref_no'], name='unique_bookingdata_constraint')
        ]

    def __str__(self):
        return f"{self.id}, {self.txn_date}, {self.irctc_order_no}, {self.bank_booking_ref_no}"

class RefundData(models.Model):
    refund_date = models.DateField(null=True, blank=True)  # Allow null dates if missing
    debited_on_date = models.DateField(null=True, blank=True)  # Debited on date from the file
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # refund amount
    irctc_order_no = models.BigIntegerField(null=True, blank=True)  # Removed default to avoid unintentional duplicates
    bank_booking_ref_no = models.BigIntegerField(null=True, blank=True)  # Same for bank booking reference number
    bank_refund_ref_no = models.BigIntegerField(null=True, blank=True)  # Same for bank refund reference number

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['refund_date', 'debited_on_date', 'irctc_order_no', 'bank_booking_ref_no', 'bank_refund_ref_no'], name='unique_refunddata_constraint')
        ]

    def __str__(self):
        return f"{self.id}, {self.refund_date}, {self.irctc_order_no}, {self.bank_booking_ref_no}, {self.bank_refund_ref_no}"
