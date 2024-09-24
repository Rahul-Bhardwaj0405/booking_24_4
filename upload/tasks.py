import pandas as pd
import logging
from io import StringIO, BytesIO
from .models import BookingData, RefundData
from celery import shared_task

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@shared_task
def process_uploaded_files(file_content, file_name):
    logging.info(f"Starting to process file: {file_name}")

    try:
        # Initialize an empty DataFrame
        df = pd.DataFrame()

        # Set possible delimiters for CSV and text files
        possible_delimiters = [',', ';', '\t', '|', ' ', '.', '_']
        logging.info("Attempting to read the file content into a DataFrame.")

        # Read the file content into a DataFrame based on file type
        if file_name.endswith('.csv') or file_name.endswith('.txt'):
            file_str = file_content.decode(errors='ignore')
            delimiter = next((delim for delim in possible_delimiters if delim in file_str), ',')
            
            df = pd.read_csv(StringIO(file_str), delimiter=delimiter, dtype=str)
            logging.info(f"CSV/TXT file read successfully with delimiter '{delimiter}'.")


        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(BytesIO(file_content), engine='openpyxl', dtype={
                'IRCTCORDERNO': str,
                'BANKBOOKINGREFNO': str,
                'BANKREFUNDREFNO': str
            })
            logging.info(f"Excel file read successfully: {file_name}.")

        else:
            logging.error(f"Unsupported file type: {file_name}")
            return

        # Log DataFrame structure
        logging.info(f"DataFrame columns: {df.columns.tolist()}")
        logging.info(f"DataFrame head:\n{df.head()}")

        # Clean the column names
        df.columns = df.columns.str.strip().str.replace(r'\W+', '', regex=True)
        logging.info(f"Cleaned column names: {df.columns.tolist()}")

        # Universal data cleaning step
        df = df.apply(lambda col: col.map(lambda x: str(x).strip() if isinstance(x, str) else x))

        # ***********Refund MPR/MIS ****************************
        # Check for required columns for both booking and refund
        booking_required_columns = ['TXNDATE', 'BOOKINGAMOUNT', 'CREDITEDON', 'IRCTCORDERNO', 'BANKBOOKINGREFNO']
        refund_required_columns = ['REFUNDDATE', 'REFUNDAMOUNT', 'DEBITEDON', 'IRCTCORDERNO', 'BANKBOOKINGREFNO', 'BANKREFUNDREFNO']

        missing_booking_columns = set(booking_required_columns) - set(df.columns)
        missing_refund_columns = set(refund_required_columns) - set(df.columns)

        if missing_booking_columns and missing_refund_columns:
            logging.error(f"Missing required columns: Booking - {missing_booking_columns}, Refund - {missing_refund_columns}")
            return

        # For Booking Data
        if not missing_booking_columns:
            try:
                df['TXNDATE'] = pd.to_datetime(df['TXNDATE'], errors='coerce')
            except Exception as e:
                logging.warning(f"Error converting 'TXNDATE' to datetime: {e}")
                df['TXNDATE'] = pd.NaT

            try:
                df['CREDITEDON'] = pd.to_datetime(df['CREDITEDON'], errors='coerce')
            except Exception as e:
                logging.warning(f"Error converting 'CREDITEDON' to datetime: {e}")
                df['CREDITEDON'] = pd.NaT

            # Convert numeric fields for booking
            df['IRCTCORDERNO'] = df['IRCTCORDERNO'].apply(lambda x: int(float(x)) if pd.notnull(x) else 0)
            df['BANKBOOKINGREFNO'] = df['BANKBOOKINGREFNO'].apply(lambda x: int(float(x)) if pd.notnull(x) else 0)
            df['BOOKINGAMOUNT'] = pd.to_numeric(df['BOOKINGAMOUNT'], errors='coerce')

        # For Refund Data
        if not missing_refund_columns:
            try:
                df['REFUNDDATE'] = pd.to_datetime(df['REFUNDDATE'], errors='coerce')
            except Exception as e:
                logging.warning(f"Error converting 'REFUNDDATE' to datetime: {e}")
                df['REFUNDDATE'] = pd.NaT

            try:
                df['DEBITEDON'] = pd.to_datetime(df['DEBITEDON'], errors='coerce')
            except Exception as e:
                logging.warning(f"Error converting 'DEBITEDON' to datetime: {e}")
                df['DEBITEDON'] = pd.NaT

            # Convert numeric fields for refund
            df['IRCTCORDERNO'] = df['IRCTCORDERNO'].apply(lambda x: int(float(x)) if pd.notnull(x) else 0)
            df['BANKBOOKINGREFNO'] = df['BANKBOOKINGREFNO'].apply(lambda x: int(float(x)) if pd.notnull(x) else 0)
            df['BANKREFUNDREFNO'] = df['BANKREFUNDREFNO'].apply(lambda x: int(float(x)) if pd.notnull(x) else 0)
            df['REFUNDAMOUNT'] = pd.to_numeric(df['REFUNDAMOUNT'], errors='coerce')

        # Iterate through each row to save data and display row-wise details
        for _, row in df.iterrows():
            # Handling Booking Data
            if 'BOOKINGAMOUNT' in row and 'CREDITEDON' in row:
                # Check for duplicate booking data
                booking_exists = BookingData.objects.filter(
                    irctc_order_no=row['IRCTCORDERNO'],
                    bank_booking_ref_no=row['BANKBOOKINGREFNO']
                ).exists()

                if booking_exists:
                    logging.info(f"Duplicate booking found: IRCTCORDERNO {row['IRCTCORDERNO']} - BANKBOOKINGREFNO {row['BANKBOOKINGREFNO']}. Skipping...")
                else:
                    BookingData.objects.create(
                        txn_date=row['TXNDATE'],
                        credited_on_date=row['CREDITEDON'],
                        booking_amount=row['BOOKINGAMOUNT'],
                        irctc_order_no=row['IRCTCORDERNO'],
                        bank_booking_ref_no=row['BANKBOOKINGREFNO']
                    )
                    logging.info(f"Booking data saved for IRCTCORDERNO {row['IRCTCORDERNO']}.")

            # Handling Refund Data
            elif 'REFUNDAMOUNT' in row and 'DEBITEDON' in row:
                # Check for duplicate refund data
                refund_exists = RefundData.objects.filter(
                    irctc_order_no=row['IRCTCORDERNO'],
                    bank_refund_ref_no=row['BANKREFUNDREFNO']
                ).exists()

                if refund_exists:
                    logging.info(f"Duplicate refund found: IRCTCORDERNO {row['IRCTCORDERNO']} - BANKREFUNDREFNO {row['BANKREFUNDREFNO']}. Skipping...")
                else:
                    RefundData.objects.create(
                        refund_date=row['REFUNDDATE'],
                        debited_on_date=row['DEBITEDON'],
                        refund_amount=row['REFUNDAMOUNT'],
                        irctc_order_no=row['IRCTCORDERNO'],
                        bank_booking_ref_no=row['BANKBOOKINGREFNO'],
                        bank_refund_ref_no=row['BANKREFUNDREFNO']
                    )
                    logging.info(f"Refund data saved for IRCTCORDERNO {row['IRCTCORDERNO']}.")

        logging.info("File processed successfully.")

    except Exception as e:
        logging.error(f"Error processing file {file_name}: {e}")
