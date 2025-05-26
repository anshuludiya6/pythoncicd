# Authentication/urls.py

from django.urls import path
from .bankinformation import *
from .Education import *
from .Experience import *
from .Holiday import *

urlpatterns = [
    path('get_bank_information/', get_bank_information, name='get_bank_information'),
    path('get_bank_information_by_id/', get_bank_information_by_id, name='get_bank_information_by_id'),
    path('create_bank_information/', create_bank_information, name='create_bank_information'),
    path('update_bank_information/', update_bank_information, name='update_bank_information'),
    path('delete_bank_information/', delete_bank_information, name='delete_bank_information'),

    path('get_education_information/', get_education_information, name='get_education_information'),
    path('get_education_by_id/', get_education_by_id, name='get_education_by_id'),
    path('create_education_information/', create_education_information, name='create_education_information'),
    path('update_education_information/', update_education_information, name='update_education_information'),
    path('delete_education_information/', delete_education_information, name='delete_education_information'),

    path('get_experience_information/', get_experience_information, name='get_experience_information'),
    path('get_experience_by_id/', get_experience_by_id, name='get_experience_by_id'),
    path('create_experience_information/', create_experience_information, name='create_experience_information'),
    path('update_experience_information/', update_experience_information, name='update_experience_information'),
    path('delete_experience_information/', delete_experience_information, name='delete_experience_information'),

    path('get_holiday_information/', get_holiday_information, name='get_holiday_information'),
]
