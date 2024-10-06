from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    # path('accounts/logout/', views.user_login, name='signup'),
    path('accounts/login/', views.user_login, name='signup'),
    path('upload/', views.upload_file, name='upload_file'),
    path('query-builder/', views.query_builder, name='query_builder'),
    path('get-filtered-record-count/', views.get_filtered_record_count, name='get_filtered_record_count'),
    path('get-dropdown-data/', views.get_dropdown_data, name='get_dropdown_data')

    
]
