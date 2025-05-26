# Authentication/models.py

from django.db import models
from django.utils.timezone import now

class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    emp_id = models.CharField(max_length=50, unique=True, null=False)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=128, null=True)
    profile_photo = models.ImageField(null=True)
    user_status = models.CharField(max_length=50, null=True)
    role = models.CharField(max_length=100, null=True)
    contact = models.CharField(max_length=20, null=True)
    emergency_contact = models.CharField(max_length=20, null=True)
    blood_group = models.CharField(max_length=10, null=True)
    nationality = models.CharField(max_length=50, null=True)
    religion = models.CharField(max_length=50, null=True)
    marital_status = models.CharField(max_length=20, null=True)
    address = models.TextField(null=True)
    country = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    zipcode = models.CharField(max_length=20, null=True)
    emergency_contact_details = models.JSONField(null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    is_verified = models.BooleanField(default=False, null=True)
    is_google_register = models.BooleanField(default=False, null=True)
    is_linkedin_register = models.BooleanField(default=False, null=True)
    terms_and_conditions = models.BooleanField(default=False, null=True)
    created_by = models.CharField(max_length=50, null=True)
    updated_by = models.CharField(max_length=50, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Users'


class Token(models.Model):
    token_id = models.AutoField(primary_key=True)
    token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey('Users', on_delete=models.CASCADE) 
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Token'


class OTP(models.Model):
    otp_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('Users', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, null=True)
    otp_expires_at = models.DateTimeField(null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'OTP'