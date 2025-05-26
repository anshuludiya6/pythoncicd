from datetime import date
from django.db import models
from django.utils.timezone import now
from Authentication.models import Users

class BankInformation(models.Model):
    bank_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('Authentication.Users', on_delete=models.CASCADE, db_column='user_id')
    bank_name = models.CharField(max_length=100, null=True)
    bank_accout_number = models.CharField(max_length=30, null=True)
    ifsc_code = models.CharField(max_length=20, null=True)
    pan_number = models.CharField(max_length=30, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_by = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'BankInformation'


class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('Authentication.Users', on_delete=models.CASCADE, db_column='user_id')
    college_name = models.CharField(max_length=100, null=True)
    admission_year = models.CharField(max_length=4, null=True)
    passout_year = models.CharField(max_length=4, null=True)
    course = models.CharField(max_length=30, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True,)
    updated_by = models.CharField(max_length=50, null=True,)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Education'


class ExperienceInformation(models.Model):
    experience_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('Authentication.Users', on_delete=models.CASCADE, db_column='user_id')
    position = models.CharField(max_length=100, null=True)
    date_of_joining = models.CharField(null=True)
    date_of_relieving = models.CharField(null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True,)
    updated_by = models.CharField(max_length=50, null=True,)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ExperienceInformation'

class Holiday(models.Model):
    holiday_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, null=True)
    holiday_date = models.DateField(null=True)
    day = models.CharField(max_length=20, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True,)
    updated_by = models.CharField(max_length=50, null=True,)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Holiday'

    

    