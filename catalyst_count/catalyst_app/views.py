# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import Company
from django.shortcuts import render
from django.http import JsonResponse
import os
from .task import process_csv_file
from django.conf import settings
import pandas as pd
from django.core.cache import cache


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('account/signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('account/signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('account/signup')

        # Create and save the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Automatically log the user in
        login(request, user)

        messages.success(request, "You have successfully signed up!")
        return redirect('login')

    return render(request, 'account/signup.html')


def user_login(request):
    
    if request.method == "POST":
        username = request.POST.get('login')  # Using 'login' to capture username or email
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect('upload_file')
        else:
            messages.error(request, "Invalid credentials.")
            return render(request,'account/login.html')

    return render(request, 'account/login.html')



@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        
        if uploaded_file.name.endswith('.csv'):
            
        
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
            
            file_path = os.path.join(fs.location, uploaded_file.name)
            print('current_file_path',file_path)
            if os.path.exists(file_path):
                # If the file exists, delete it first
                print('removeing file')
                os.remove(file_path)
            
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)
            print('saved file path',file_path)
            # csv_data = uploaded_file.read().decode('utf-8').splitlines()
            
            # Call the Celery task asynchronously
            process_csv_file.delay(file_path)

            return JsonResponse({
                'status': 'success',
                'message': 'File has been uploaded successfully!',
                'redirect_url': 'query-builder/'  # You can adjust this URL if necessary
            })
            # return JsonResponse({'status': 'success'})

        return JsonResponse({'status': 'error', 'message': 'File format not supported'})
    
    

    return render(request, 'upload.html')


def query_builder(request):
   
    
    # df = pd.read_csv('../catalyst_count/uploads/companies_sorted.csv', encoding='utf8')
    # # print(df.columns)
    # names = df['name'].head(10).unique().tolist()
    # domains = df['domain'].head(10).unique().tolist()
    # df['year founded'] = df['year founded'].fillna(0).astype(int)
    # print(df['year founded'].head(30))
    # years = df['year founded'].head(10).unique().tolist()
    # industries = df['industry'].head(10).unique().tolist()
    # sizes = df['size range'].head(10).unique().tolist()
    # localities = df['locality'].head(10).unique().tolist()
    # countries = df['country'].head(10).unique().tolist()
    # urls = df['linkedin url'].head(10).unique().tolist()
    # current_employee_estimate = df['current employee estimate'].head(10).unique().tolist()
    # total_employee_estimate = df['total employee estimate'].head(10).unique().tolist()
    # print(names)   
    # names = Company.objects.values_list('name', flat=True).distinct()[:10]
    # domains = Company.objects.values_list('domain', flat=True).distinct()[:10]
    # years = Company.objects.values_list('year_founded', flat=True).distinct()[:10]
    # industries = Company.objects.values_list('industry', flat=True).distinct()[:10]
    # sizes = Company.objects.values_list('size_range', flat=True).distinct()[:10]
    # localities = Company.objects.values_list('locality', flat=True).distinct()[:10]
    # countries = Company.objects.values_list('country', flat=True).distinct()[:10]
    # urls = Company.objects.values_list('linkedin_url', flat=True).distinct()[:10]
    # current_employee_estimate = Company.objects.values_list('current_employee_estimate', flat=True).distinct()[:10]
    # total_employee_estimate = Company.objects.values_list('total_employee_estimate', flat=True).distinct()[:10]

    # context = {
    #     'names': names,
    #     'domains': domains,
    #     'years': years,
    #     'industries': industries,
    #     'sizes': sizes,
    #     'localities': localities,
    #     'countries': countries,
    #     'urls': urls,
    #     'current_employee_estimate': current_employee_estimate,
    #     'total_employee_estimate': total_employee_estimate,
    # }

    return render(request, 'query_builder.html')

# def get_dropdown_data(request):
    
#     df = pd.read_csv('../catalyst_count/uploads/companies_sorted.csv', encoding='utf8')
#     # print(df.columns)
#     names = df['name'].head(10).unique().tolist()
#     domains = df['domain'].head(10).unique().tolist()
#     df['year founded'] = df['year founded'].fillna(0).astype(int)
#     years = df['year founded'].head(10).unique().tolist()
#     industries = df['industry'].head(10).unique().tolist()
#     sizes = df['size range'].head(10).unique().tolist()
#     localities = df['locality'].head(10).unique().tolist()
#     countries = df['country'].head(10).unique().tolist()
#     urls = df['linkedin url'].head(10).unique().tolist()
#     current_employee_estimate = df['current employee estimate'].head(10).unique().tolist()
#     total_employee_estimate = df['total employee estimate'].head(10).unique().tolist()
    
#     return JsonResponse({
#         'names': names,
#         'domains': domains,
#         'years': years,
#         'industries': industries,
#         'sizes': sizes,
#         'localities': localities,
#         'countries': countries,
#         'urls': urls,
#         'current_employee_estimate': current_employee_estimate,
#         'total_employee_estimate': total_employee_estimate,
#     })


def get_dropdown_data(request):
    # Define the cache key
    cache_key = 'dropdown_data'
    
    # Try to get data from the cache
    cached_data = cache.get(cache_key)
    if cached_data:
        # If data is found in cache, return it
        return JsonResponse(cached_data)

    # If data is not found in cache, read from CSV
    df = pd.read_csv('../catalyst_count/uploads/companies_sorted.csv', encoding='utf8')
    
    # Extract unique values for each field
    names = df['name'].head(10).unique().tolist()
    domains = df['domain'].head(10).unique().tolist()
    df['year founded'] = df['year founded'].fillna(0).astype(int)
    years = df['year founded'].head(10).unique().tolist()
    industries = df['industry'].head(10).unique().tolist()
    sizes = df['size range'].head(10).unique().tolist()
    localities = df['locality'].head(10).unique().tolist()
    countries = df['country'].head(10).unique().tolist()
    urls = df['linkedin url'].head(10).unique().tolist()
    current_employee_estimate = df['current employee estimate'].head(10).unique().tolist()
    total_employee_estimate = df['total employee estimate'].head(10).unique().tolist()

    # Create the data to be cached
    data_to_cache = {
        'names': names,
        'domains': domains,
        'years': years,
        'industries': industries,
        'sizes': sizes,
        'localities': localities,
        'countries': countries,
        'urls': urls,
        'current_employee_estimate': current_employee_estimate,
        'total_employee_estimate': total_employee_estimate,
    }

    # Store the data in the cache for 10 minutes (600 seconds)
    cache.set(cache_key, data_to_cache, timeout=600)

    # Return the newly fetched data
    return JsonResponse(data_to_cache)

def get_filtered_record_count(request):
    if request.method == "POST":
        name = request.POST.get('name', None)
        domain = request.POST.get('domain', None)
        year_founded = request.POST.get('year_founded', None)
        industry = request.POST.get('industry', None)
        size_range = request.POST.get('size_range', None)
        locality = request.POST.get('locality', None)
        country = request.POST.get('country', None)
        linkedin_url = request.POST.get('linkedin_url', None)
        current_employee_estimate = request.POST.get('current_employee_estimate', None)
        total_employee_estimate = request.POST.get('total_employee_estimate', None)

        # Build the queryset by filtering based on the dropdown values
        queryset = Company.objects.all()

        if name:
            queryset = queryset.filter(name=name)
        if domain:
            queryset = queryset.filter(domain=domain)
        if year_founded:
            queryset = queryset.filter(year_founded=year_founded)
        if industry:
            queryset = queryset.filter(industry=industry)
        if size_range:
            queryset = queryset.filter(size_range=size_range)
        if locality:
            queryset = queryset.filter(locality=locality)
        if country:
            queryset = queryset.filter(country=country)
        if linkedin_url:
            queryset = queryset.filter(linked_url=linkedin_url)
        if current_employee_estimate:
            queryset = queryset.filter(current_employee_estimate=current_employee_estimate)
        if total_employee_estimate:
            queryset = queryset.filter(total_employee_estimate=total_employee_estimate)

        # Get the total count of matching records
        record_count = queryset.count()
        

        # Return the record count as JSON
        return JsonResponse({'record_count': record_count})

    return JsonResponse({'error': 'Invalid request'}, status=400)
    
       
       
# <div class="form-row">
#                 <div class="form-group col-md-4">
#                     <label for="name">Name</label>
#                     <select id="name" class="form-control" name="name">
#                         <option value="" selected>-- Select Name --</option>
#                         {% for name in names %}
#                             <option value="{{ name }}">{{ name }}</option>
#                         {% endfor %}
#                     </select>
#                 </div>

#                 <div class="form-group col-md-4">
#                     <label for="domain">Domain</label>
#                     <select id="domain" class="form-control" name="domain">
#                         <option value="" selected>-- Select Domain --</option>
#                         {% for domain in domains %}
#                             <option value="{{ domain }}">{{ domain }}</option>
#                         {% endfor %}
#                     </select>
#                 </div>

#                 <div class="form-group col-md-4">
#                     <label for="year_founded">Year Founded</label>
#                     <select id="year_founded" class="form-control" name="year_founded">
#                         <option value="" selected>-- Select Year --</option>
#                         {% for year in years %}
#                             <option value="{{ year }}">{{ year }}</option>
#                         {% endfor %}
#                     </select>
#                 </div>
#             </div>

            # <div class="form-row">
            #     <div class="form-group col-md-4">
            #         <label for="industry">Industry</label>
            #         <select id="industry" class="form-control" name="industry">
            #             <option value="" selected>-- Select Industry --</option>
            #             {% for industry in industries %}
            #                 <option value="{{ industry }}">{{ industry }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>

            #     <div class="form-group col-md-4">
            #         <label for="size_range">Size Range</label>
            #         <select id="size_range" class="form-control" name="size_range">
            #             <option value="" selected>-- Select Size Range --</option>
            #             {% for size in sizes %}
            #                 <option value="{{ size }}">{{ size }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>

            #     <div class="form-group col-md-4">
            #         <label for="locality">Locality</label>
            #         <select id="locality" class="form-control" name="locality">
            #             <option value="" selected>-- Select Locality --</option>
            #             {% for locality in localities %}
            #                 <option value="{{ locality }}">{{ locality }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>
            # </div>

            # <div class="form-row">
            #     <div class="form-group col-md-4">
            #         <label for="country">Country</label>
            #         <select id="country" class="form-control" name="country">
            #             <option value="" selected>-- Select Country --</option>
            #             {% for country in countries %}
            #                 <option value="{{ country }}">{{ country }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>

            #     <div class="form-group col-md-4">
            #         <label for="linkedin_url">Linkedin URL</label>
            #         <select id="linkedin_url" class="form-control" name="linkedin_url">
            #             <option value="" selected>-- Select URL --</option>
            #             {% for url in urls %}
            #                 <option value="{{ url }}">{{ url }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>
            #     <div class="form-group col-md-4">
            #         <label for="current_employee_estimate">Current Employee Estimate</label>
            #         <select id="current_employee_estimate" class="form-control" name="current_employee_estimate">
            #             <option value="" selected>-- Select Current Employee Estimate --</option>
            #             {% for employee_estimate in current_employee_estimate %}
            #                 <option value="{{ employee_estimate }}">{{ employee_estimate }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>

            # </div>

            # <div class="form-row">
            #     <div class="form-group col-md-4">
            #         <label for="total_employee_estimate">Total Employee Estimate</label>
            #         <select id="total_employee_estimate" class="form-control" name="total_employee_estimate">
            #             <option value="" selected>-- Select Total Employee Estimate --</option>
            #             {% for employee_estimate in total_employee_estimate %}
            #                 <option value="{{ employee_estimate }}">{{ employee_estimate }}</option>
            #             {% endfor %}
            #         </select>
            #     </div>
            # </div>
