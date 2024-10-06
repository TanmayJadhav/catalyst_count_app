# tasks.py
from celery import shared_task
import csv
from io import StringIO
from itertools import islice
import time
from .models import Company

from django.db import connection

@shared_task
def process_csv_file(csv_file_path):
   
    with open(csv_file_path, 'r',encoding="utf8") as csvfile:
        start = time.process_time()
        csv_reader = csv.reader(csvfile)
        
        # Skip the header (optional, if your CSV contains headers)
        next(csv_reader, None)  # Skip the header row

        batch = []
        batch_size = 50000
        
        for row in csv_reader:
            batch.append(row)
            
            # When batch size is reached, send batch to a new worker
            if len(batch) >= batch_size:
                end = time.process_time()
                print("time for reading file ",end-start)
                insert_batch.delay(batch)  # Send to a new Celery worker
                batch = []  # Reset the batch

    # Handle the remaining rows (if any)
        if batch:
            print("running for remaining batch")
            insert_batch.delay(batch)
    
    return "All batches submitted to workers"

        
@shared_task
def insert_batch(batch):
    # Prepare a list to store Company objects to be created
    start = time.process_time()
    # print(f"start time {start}")
    company_list = []
    
       
        
    company_list = [
        Company(
            name=row[1],         # Assuming 'name' is the 2nd column (index 1)
            domain=row[2],       # Assuming 'domain' is the 3rd column (index 2)
            year_founded=int(float(row[3].strip())) if row[3] != '' else 0,
            industry=row[4],
            size_range=row[5],
            locality=row[6],
            country=row[7],
            linkedin_url=row[8],
            current_employee_estimate=row[9],
            total_employee_estimate=row[10]
        ) for row in batch
    ]
                
    
    
    Company.objects.bulk_create(company_list)
    
    end = time.process_time()
    # print(f"end time {end}")
    print(f"total time {end-start}")
    return f"Batch of {len(batch)} inserted successfully"
    

#celery run commands
# celery -A catalyst_count worker --loglevel=info -P eventlet
# celery -A catalyst_count worker --concurrency=6 --loglevel=info -P eventlet