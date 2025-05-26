import re
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status as st
from .decorators import authentication_required
from .models import *
from .serializers import  ResetPasswordSerializer, SignUpSerializer, LoginSerializer, TokenSerializer, OTPSerializer, ForgotPasswordSerializer,UsersSerializer, UsersUpdateSerializer
from .utils import *
from django.utils.timezone import now as get_current_pst_time
from datetime import timedelta
from django.core.exceptions import ValidationError
import bcrypt  
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from Users.serializers import *

@api_view(['GET'])
def status(request):
    return Response({"message": "Django is running"})

@swagger_auto_schema(
    method='post',
    operation_description="Register a new user",
    request_body=SignUpSerializer,
    responses={
        200: openapi.Response('User registered. Verification email sent.'),
        400: openapi.Response('Validation failed.'),
        401: openapi.Response('Your account has been deleted.'),
        500: openapi.Response('An error occurred while registering user.'),
    }
)
@api_view(['POST'])
def signup(request):
    try:
        print("request",request)
        serializer = SignUpSerializer(data=request.data)
        print(serializer)
        if not serializer.is_valid():
            return Response({'message': 'Validation failed.', 'errors': serializer.errors}, status=st.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        email = data.get('email').lower()
        password = data.get('password')

        if not email:
            return Response({"error": "Email is required"}, status=st.HTTP_400_BAD_REQUEST)
 
        existing_user = Users.objects.filter(email=email).first()
        if existing_user:
            if existing_user.is_deleted != False:
                return Response({'message': 'Your account has been deleted. To reactivate, please contact the administrator at hello@heyloops.com.'}, status=st.HTTP_401_UNAUTHORIZED)
            if not existing_user.is_verified:
                send_verification_email(existing_user)
                return Response({'message': 'you are not verified, email is send to this email address please verify your email.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Email already registered.'}, status=st.HTTP_400_BAD_REQUEST)

        hashed_password = None
        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        total_users = Users.objects.count()
        if total_users == 0:
            emp_id = f"ATPL_{total_users + 1001}"
        else:
            latest_user = Users.objects.order_by('-user_id').first()
            latest_user_id = latest_user.user_id
            emp_id = f"ATPL_{latest_user_id + 1001}"
 

        new_user = Users(
            emp_id=emp_id,
            name=data.get('name'),
            email=email,
            password=hashed_password,
            user_status=data.get('user_status'),
            role=data.get('role'),
            contact=data.get('contact'),
            emergency_contact=data.get('emergency_contact'),
            blood_group=data.get('blood_group'),
            nationality=data.get('nationality'),
            religion=data.get('religion'),
            marital_status=data.get('marital_status'),
            address=data.get('address'),
            country=data.get('country'),
            state=data.get('state'),
            zipcode=data.get('zipcode'),
            emergency_contact_details=data.get('emergency_contact_details'),
            is_deleted=data.get('is_deleted', False),
            is_verified=data.get('is_verified', False),
            is_google_register=data.get('is_google_register', False),
            is_linkedin_register=data.get('is_linkedin_register', False),
            terms_and_conditions=data.get('terms_and_conditions', False),
            created_by=email,
            created_on=current_pst_to_utc(),
        )
        # if profile_photo:
        #     new_user.profile_photo = profile_photo

        new_user.save()

        send_verification_email(new_user)
        return Response({"message": "User registered. Verification email sent."}, status=st.HTTP_200_OK)
 
    except ValidationError as error:
        return Response({'message': 'Validation failed.', 'errors': error.message_dict}, status=st.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'message': 'An error occurred while registering user.', 'error': str(e)}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    operation_description="send otp to the user.",
    request_body=LoginSerializer,
    responses={
        200: openapi.Response('User registered. Verification email sent.'),
        400: openapi.Response('Validation failed.'),
        401: openapi.Response('Your account has been deleted.'),
        500: openapi.Response('An error occurred while registering user.'),
    }
)
@api_view(['POST'])
def login(request): 
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data.get('email').lower()
        password = serializer.validated_data.get('password')  
        provided_password_bytes = password.encode('utf-8')   
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:  # Use 'Users' here instead of 'user'
            return Response({'message': 'Sorry, no account found. Please check your credentials or sign up to create an account.'}, status=st.HTTP_404_NOT_FOUND)
        
        if user:
            if user.is_deleted:
                return Response({'message': 'Your account has been Deactivated. To reactivate, please contact the administrator at hello@heyloops.com.'}, status=st.HTTP_401_UNAUTHORIZED)

            if user.is_linkedin_register:
                return Response({'message': 'Your account is registered using LinkedIn. Please log in with LinkedIn to access your account.'}, status=st.HTTP_403_FORBIDDEN)

            if user.is_google_register:
                return Response({'message': 'Your account is registered using Google. Please log in with Google to access your account.'}, status=st.HTTP_403_FORBIDDEN)

            if bcrypt.checkpw(provided_password_bytes, user.password.encode('utf-8')):
                if user.is_verified:
                    otp = set_user_otp(user)
                    print(otp)
                    send_otp_email(user, otp)


                    return Response({
                        'message': 'OTP is sent to your email. Please verify.',
                        'user_id': user.user_id
                    }, status=st.HTTP_200_OK)
                else:
                    return Response({'message': 'Invalid credentials. Please check and try again.'}, status=st.HTTP_401_UNAUTHORIZED)
            else:  
                return Response({'message': 'email or password is incorrect.', 'errors': serializer.errors}, status=st.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'Invalid data', 'errors': serializer.errors}, status=st.HTTP_400_BAD_REQUEST)
  
 
@swagger_auto_schema(
    method='get',
    operation_description="Verify email using token",
    manual_parameters=[
        openapi.Parameter(
            'token',
            openapi.IN_QUERY,
            description="Token for email verification",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response('Email verified successfully.'),
        400: openapi.Response('Invalid token or validation error.'),
        404: openapi.Response('No account found with the provided token.'),
    }
)
@api_view(['GET'])
def verify_email(request, token):
    try:
        is_valid, error = is_token_valid(token)
        if not is_valid:
            return redirect('failure_page')
 
        user = get_user_by_token(token)
        if not user:
            return redirect('failure_page')
       
        user.is_verified = True
        user.save()
 
        token_record = Token.objects.filter(token=token).first()
        if token_record:
            token_record.used = True
            token_record.save()
 
        return redirect('success_page')
   
    except Token.DoesNotExist:
        return redirect('failure_page')
 

@swagger_auto_schema(
    method='post',
    operation_description="Verify OTP and log in the user",
    request_body=OTPSerializer,
    responses={
        200: openapi.Response(
            'Your OTP is correct. Login Successful',
            openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'response': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'success_message': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                }
            )
        ),
        400: openapi.Response('Invalid OTP or validation error.'),
        404: openapi.Response('User not found.'),
    }
)
@api_view(['POST'])
def verify_otp(request):
    serializer = OTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=st.HTTP_400_BAD_REQUEST)
    
    user_id = serializer.validated_data.get('user_id')
    otp_input = serializer.validated_data.get('otp')
    
    is_valid, message = verify(user_id, otp_input)
    
    if is_valid:
        try:
            user = Users.objects.get(user_id=user_id)
        except Users.DoesNotExist:
            return Response({'message': 'User not found.'}, status=st.HTTP_404_NOT_FOUND)

        access_token = generate_jwt_token(user_id)
        request.session['jwt_token'] = access_token
        response_data = {
            'access_token': access_token,
            'name': user.name,
            'email': user.email,
            'success_message': 'Your OTP is correct. Login Successful'
        }
        return Response({'response': response_data}, status=st.HTTP_200_OK)
    else:
        return Response({'message': message}, status=st.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    method='post',
    operation_description="Send a password reset email",
    request_body=ForgotPasswordSerializer,
    security=[{'Bearer': []}],
    responses={
        200: openapi.Response('Password reset email sent.'),
        400: openapi.Response('Validation error.'),
        404: openapi.Response('User with this email address does not exist.'),
        500: openapi.Response('Failed to send email.')
    }
)
@api_view(['POST'])
# @authentication_required()
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': serializer.errors}, status=st.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data['email'].lower()
    try:
        user = Users.objects.get(email=email)
    except Users.DoesNotExist:
        return Response({'error': 'User with this email address does not exist.'}, status=st.HTTP_404_NOT_FOUND)

    token = generate_secure_token(user.user_id)

    reset_url = f'http://122.168.125.73:8080/authentication/check-reset-token/{token}'
    email_subject = 'Password Reset Request'
    email_body = render_to_string('forgot_password_email.html', {'user': user.name, 'reset_url': reset_url})

    try:
        send_mail(
            email_subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_body,
            fail_silently=False,
        )
        return Response({'success': 'Password reset email sent.'}, status=st.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Failed to send email. Error: {str(e)}'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="Validate a reset token.",
    manual_parameters=[
        openapi.Parameter('token', openapi.IN_QUERY, description="The token used to verify email", type=openapi.TYPE_STRING)
    ],
    responses={
        200: openapi.Response('Reset token is valid.'),
        400: openapi.Response('Invalid token or validation error.')
    }
)    
@api_view(['GET'])
def check_reset_token_for_user(request,token):
    is_valid, error_message = is_token_valid(token)
    if not is_valid:
        context = {'error_message': error_message}
        return render(request, 'reset_password.html', context)
    context = {'token': token}
    return render(request, 'reset_password.html', context)

@swagger_auto_schema(
    method='post',
    operation_description="Reset user password using a valid reset token.",
    request_body=ResetPasswordSerializer,
    responses={
        200: openapi.Response('Password reset successful.'),
        400: openapi.Response('Validation error or invalid token.'),
    }
)
# @api_view(['POST'])
# # @authentication_required()
# def reset_password(request):
#     serializer = ResetPasswordSerializer(data=request.data)
#     if not serializer.is_valid():
#         return Response({'error': serializer.errors}, status=st.HTTP_400_BAD_REQUEST)

#     token = serializer.validated_data['token']
#     new_password = serializer.validated_data['new_password']
#     confirm_password = serializer.validated_data['confirm_password']

#     is_valid, error_message = is_token_valid(token)
#     if not is_valid:
#         return Response({'error': error_message}, status=st.HTTP_400_BAD_REQUEST)

#     if new_password != confirm_password:
#         return Response({'error': 'New password does not match confirmation.'}, status=st.HTTP_400_BAD_REQUEST)

#     update_user_password(token, new_password)
#     reset_password_token(token)

#     return Response({'success': 'Password reset successful.'}, status=st.HTTP_200_OK)
@api_view(['POST'])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        confirm_password = serializer.validated_data['confirm_password']

        print(token)
        print(new_password)
        print(confirm_password)
        # Validate the token
        is_valid, error_message = is_token_valid(token)
        if not is_valid:
            return Response({'error': error_message}, status=st.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'New password does not match confirmation.'}, status=st.HTTP_400_BAD_REQUEST)

        update_user_password(token, new_password)

        reset_password_token(token)

        return Response({'success': 'Password reset successful.'}, status=st.HTTP_200_OK)

    return Response({'error': serializer.errors}, status=st.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve user information for the authenticated user.",
    responses={
        200: openapi.Response('Successful retrieval of user information.', UsersSerializer(many=True)),
        400: openapi.Response('User ID not found in request.'),
        500: openapi.Response('An unexpected error occurred.')
    }
)
@api_view(['GET'])
@authentication_required()
def get_user_information(request):
    try:
        user_id = request.user.get('id')
        if not user_id:
            return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)
        
        user_information = Users.objects.get(user_id=user_id, is_deleted=False)
       
        serializer = UsersSerializer(user_information)
        response = serializer.data
        response['profile_photo'] = f"{settings.SERVER_URL}{response['profile_photo']}"
        return Response(response, status=st.HTTP_200_OK)
 
    except Exception as e:
        return Response({'error': 'An unexpected error occurred'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)
    

@swagger_auto_schema(
    method='post',
    operation_description="Update a user record for the authenticated user.",
    request_body=UsersUpdateSerializer,
    responses={
        200: openapi.Response('User information updated successfully.', UsersUpdateSerializer),
        400: openapi.Response('Validation error or bad request.'),
        404: openapi.Response('User record not found.')
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@authentication_required()
def update_user_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    try:
        user = Users.objects.get(user_id=user_id)
    except Users.DoesNotExist:
        return Response({'error': 'User not found'}, status=st.HTTP_404_NOT_FOUND)
    
    try:
        email = get_user_email(user_id)
    except Exception as e:
        return Response({'error': str(e)}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)

    data = request.data
    profile_photo = request.FILES.get('profile_photo')
    if profile_photo:
        data['profile_photo'] = profile_photo

    serializer = UsersUpdateSerializer(user, data=data, partial=True)
    if serializer.is_valid():
        try:
            updated_user = serializer.save()
            updated_user.updated_by = email
            updated_user.updated_on = datetime.now(timezone.utc)
            updated_user.save()
            response = serializer.data
            response['updated_by'] = updated_user.updated_by
            return Response(response, status=st.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=st.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=st.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    method='delete',
    operation_description="Permanently delete a user record based on email for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user record to delete'),
        },
    ),
    responses={
        200: openapi.Response('User successfully deleted.'),
        400: openapi.Response('Bad request, email is required.'),
        404: openapi.Response('User record not found.')
    }
)
@api_view(['DELETE'])
# @authentication_required()
def delete_user(request):
    data = request.data
    email = data.get('email')
    if not email:
        return Response({'error': 'Email is required'}, status=st.HTTP_400_BAD_REQUEST)
    try:
        user = Users.objects.get(email=email)
        user.delete()
        return Response({'message': 'User successfully deleted'}, status=st.HTTP_200_OK)
    except Users.DoesNotExist:
        return Response({'error': 'User record not found'}, status=st.HTTP_404_NOT_FOUND)



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve user information including bank, education, experience and holiday details.",
    responses={
        200: openapi.Response(description="User information retrieved successfully"),
        400: openapi.Response(description="User ID not found in request"),
        404: openapi.Response(description="User not found"),
        500: openapi.Response(description="Internal server error"),
    },
)
@api_view(['GET'])
@authentication_required()
def get_all_user_info(request):
    try:
        user_id = request.user.get('id')
        print(user_id)
        if not user_id:
            return Response({'error': 'User ID not found in request'}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            user = Users.objects.get(user_id=user_id, is_deleted=False)
        except Users.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
       
        try:
            bank_information = BankInformation.objects.filter(user_id=user_id, is_deleted=False)
            education = Education.objects.filter(user_id=user_id, is_deleted=False)
            experience_information = ExperienceInformation.objects.filter(user_id=user_id, is_deleted=False)
            holiday = Holiday.objects.filter(is_deleted=False)
        except Exception as e:
            return Response({'error': 'Error fetching related information', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        user_serializer = UsersSerializer(user)
        bank_serializer = BankInformationSerializer(bank_information, many=True)
        education_serializer = EducationSerializer(education, many=True)
        experience_serializer = ExperienceInformationSerializer(experience_information, many=True)
        holidaySerializer = HolidaySerializer(holiday, many=True)
 
        response_data = {
            'user': user_serializer.data,
            'bank_information': bank_serializer.data,
            'education_information': education_serializer.data,
            'experience_information': experience_serializer.data,
            'holiday_information': holidaySerializer.data,
        }
 
        return Response(response_data, status=status.HTTP_200_OK)
 
    except Exception as e:
        return Response({'error': 'An unexpected error occurred', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

