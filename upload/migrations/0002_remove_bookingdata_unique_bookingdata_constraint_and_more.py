# Generated by Django 5.1.1 on 2024-09-24 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upload', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='bookingdata',
            name='unique_bookingdata_constraint',
        ),
        migrations.RemoveField(
            model_name='bookingdata',
            name='bank_booking_ref_no',
        ),
        migrations.RemoveField(
            model_name='bookingdata',
            name='booking_amount',
        ),
        migrations.RemoveField(
            model_name='bookingdata',
            name='credited_on_date',
        ),
        migrations.RemoveField(
            model_name='bookingdata',
            name='irctc_order_no',
        ),
        migrations.RemoveField(
            model_name='bookingdata',
            name='txn_date',
        ),
        migrations.AddField(
            model_name='refunddata',
            name='bank_booking_ref_no',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='refunddata',
            name='bank_refund_ref_no',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='refunddata',
            name='debited_on_date',
            field=models.DateField(default='2024-01-01'),
        ),
        migrations.AddField(
            model_name='refunddata',
            name='irctc_order_no',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='refunddata',
            name='refund_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='refunddata',
            name='refund_date',
            field=models.DateField(default='2024-01-01'),
        ),
        migrations.AddConstraint(
            model_name='refunddata',
            constraint=models.UniqueConstraint(fields=('refund_date', 'debited_on_date', 'irctc_order_no', 'bank_booking_ref_no', 'bank_refund_ref_no'), name='unique_refunddata_constraint'),
        ),
    ]
