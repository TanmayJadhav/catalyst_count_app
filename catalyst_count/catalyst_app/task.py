# tasks.py
from celery import shared_task
import csv
from io import StringIO
from itertools import islice
import time
from .models import Company

from django.db import connection

# give me a beautiful html page with bootstrap4 which will have a heading Query Builder and multiple drop downs same number as I have columns in db .with same placeholder and it should be populated with the data from the db in each dropdown. I want 2 buttons one or submit data and one for reset all dropdown. Once I submit, on backend it should fetch and return the count of the rows which matches the dropdown values in respected columns in table
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
    
        # Read the CSV in chunks to avoid memory overload
    # batch_size = 100000
    # while True:
    #     batch = list(islice(csv_reader, batch_size))
    #     if not batch:
    #         break
        
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
                
    
    # Once the batch size is reached, insert into the database
    # if len(company_list) >= batch_size:
    #     Company.objects.bulk_create(company_list)
    #     company_list = []  # Clear the batch list after insertion

    # Insert any remaining companies
    # if company_list:
    #     Company.objects.bulk_create(company_list)
    Company.objects.bulk_create(company_list)
    # Reset the primary key sequence to avoid conflicts for future inserts
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         "SELECT setval(pg_get_serial_sequence('catalyst_app_company', 'id'), coalesce(max(id), 1), max(id) IS NOT NULL) FROM catalyst_app_company"
    #     )
    end = time.process_time()
    # print(f"end time {end}")
    print(f"total time {end-start}")
    return f"Batch of {len(batch)} inserted successfully"
    

# @shared_task
# def process_csv_file(file_path):
#     # csv_file = StringIO("\n".join(csv_data))
#     with open(file_path, mode='r', encoding='utf-8') as f:
#         csv_reader = csv.reader(f)
#         next(csv_reader, None)  # Skip the header
        
#         # Prepare a list to store Company objects to be created
#         company_list = []
        
#             # Read the CSV in chunks to avoid memory overload
#         batch_size = 100000
#         while True:
#             batch = list(islice(csv_reader, batch_size))
#             if not batch:
#                 break
            
#             company_list = [
#                 Company(
#                     name=row[1],         # Assuming 'name' is the 2nd column (index 1)
#                     domain=row[2],       # Assuming 'domain' is the 3rd column (index 2)
#                     year_founded=int(float(row[3].strip())) if row[3] != '' else 0,
#                     industry=row[4],
#                     size_range=row[5],
#                     locality=row[6],
#                     country=row[7],
#                     linkedin_url=row[8],
#                     current_employee_estimate=row[9],
#                     total_employee_estimate=row[10]
#                 ) for row in batch
#             ]
#             Company.objects.bulk_create(company_list)
                

#             # Bulk insert in batches
#             if len(company_list) >= batch_size:
#                 Company.objects.bulk_create(company_list)
#                 company_list = []  # Clear the list for the next batch
#                 reset_sequence()

#         if company_list:
#             Company.objects.bulk_create(company_list)
#             reset_sequence()




# celery -A catalyst_count worker --loglevel=info -P eventlet
# celery -A catalyst_count worker --concurrency=6 --loglevel=info -P eventlet