import boto3
import pandas as pd
import os
import email
import imaplib

# AWS S3 Configuration
BUCKET_NAME = "your-s3-bucket-name"
FILE_KEY = "cleaned_data.csv"

# Gmail Configuration
EMAIL = "your-email@gmail.com"
PASSWORD = "your-app-password"
IMAP_SERVER = "imap.gmail.com"

def extract_latest_csv():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    
    result, data = mail.search(None, "ALL")
    email_ids = data[0].split()
    
    latest_email_id = email_ids[-1]  # Get latest email
    result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    
    raw_email = msg_data[0][1]
    msg = email.message_from_bytes(raw_email)
    
    for part in msg.walk():
        if part.get_content_type() == "text/csv":
            return part.get_payload(decode=True)
    
    return None  # No CSV found

def process_and_store_csv():
    csv_data = extract_latest_csv()
    if csv_data:
        df = pd.read_csv(pd.io.common.BytesIO(csv_data))

        # Cleaning
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
        df = df.dropna()

        # Upload to S3
        s3 = boto3.client("s3")
        csv_buffer = pd.io.common.StringIO()
        df.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=BUCKET_NAME, Key=FILE_KEY, Body=csv_buffer.getvalue())

def lambda_handler(event, context):
    process_and_store_csv()
    return {"statusCode": 200, "body": "CSV processed and stored in S3"}
