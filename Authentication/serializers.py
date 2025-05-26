from rest_framework import serializers
from .models import Users

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['name', 'email', 'password']

class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        # fields = '__all__'
        exclude = ['password', 'is_deleted', 'is_verified', 'is_google_register', 'is_linkedin_register', 'terms_and_conditions', 'created_by', 'updated_by', 'updated_on']


class UsersUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        # fields = '__all__'
        exclude = ['emp_id', 'email', 'password', 'is_deleted', 'is_verified', 'created_by', 'updated_by', 'updated_on', 'terms_and_conditions', 'is_google_register', 'is_linkedin_register', 'created_on']

# class SignUpSerializer(serializers.Serializer):
#     emp_id = serializers.CharField(max_length=50)
    # name = serializers.CharField(max_length=100)
    # email = serializers.EmailField(max_length=255, required=True)
    # password = serializers.CharField(max_length=128, required=False)
#     status = serializers.CharField(max_length=50, required=False, allow_null=True)
#     role = serializers.CharField(max_length=100, required=False, allow_null=True)
#     phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
#     emergency_contact = serializers.CharField(max_length=20, required=False, allow_null=True)
#     blood_group = serializers.CharField(max_length=10, required=False, allow_null=True)
#     nationality = serializers.CharField(max_length=50, required=False, allow_null=True)
#     religion = serializers.CharField(max_length=50, required=False, allow_null=True)
#     marital_status = serializers.CharField(max_length=20, required=False, allow_null=True)
#     address = serializers.CharField(required=False, allow_blank=True)
#     country = serializers.CharField(max_length=50, required=False, allow_null=True)
#     state = serializers.CharField(max_length=50, required=False, allow_null=True)
#     zipcode = serializers.CharField(max_length=20, required=False, allow_null=True)
#     emergency_contact_details = serializers.JSONField(required=False)



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,required=True)
    password = serializers.CharField(max_length=255,required=True)
 

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    # class Meta:
    #     model = Users
    #     # fields = '__all__'
    #     include = ['token']

class OTPSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    otp = serializers.CharField(max_length=6)
    created_on = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    # class Meta:
        # model = Users
        # fields = '__all__'
        # exclude = ['updated_on', 'otp_expires_at']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()


