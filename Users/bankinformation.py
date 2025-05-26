from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as st
from .models import BankInformation
from .serializers import BankInformationSerializer
from Authentication.decorators import authentication_required
from Authentication.views import *


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve bank information for the authenticated user.",
    responses={
        200: openapi.Response('Successful retrieval of bank information.', BankInformationSerializer(many=True)),
        400: openapi.Response('User ID not found in request.'),
        500: openapi.Response('An unexpected error occurred.')
    }
)
@api_view(['GET'])
@authentication_required()
def get_bank_information(request):
    try:
        user_id = request.user.get('id')
        if not user_id:
            return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

        bank_information = BankInformation.objects.filter(user_id=user_id, is_deleted=False)
        
        serializer = BankInformationSerializer(bank_information, many=True)
        
        return Response(serializer.data, status=st.HTTP_200_OK)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        return Response({'error': 'An unexpected error occurred'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve bank information for a specific bank ID for the authenticated user.",
    manual_parameters=[
        openapi.Parameter('bank_id', openapi.IN_QUERY, description="The ID of the bank information to retrieve.", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={
        200: openapi.Response('Successful retrieval of bank information.', BankInformationSerializer),
        400: openapi.Response('Error due to missing parameters or invalid request.'),
        404: openapi.Response('Bank information record not found or does not belong to the user.'),
    }
)
@api_view(['GET'])
@authentication_required()
def get_bank_information_by_id(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    bank_id = request.query_params.get('bank_id')
    
    if not bank_id:
        return Response({'error': 'Bank ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        bank_info = BankInformation.objects.get(bank_id=bank_id, user_id=user_id, is_deleted=False)
    except BankInformation.DoesNotExist:
        return Response({'error': 'Bank information record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)

    serializer = BankInformationSerializer(bank_info)
    return Response(serializer.data, status=st.HTTP_200_OK)

# custom_request_body_schema = openapi.Schema(
#     title='BankInformationSerializer',
#     type=openapi.TYPE_OBJECT,
#     properties={
#         'bank_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the bank'),
#         'bank_accout_number': openapi.Schema(type=openapi.TYPE_STRING, description='Bank account number'),
#         'ifsc_code': openapi.Schema(type=openapi.TYPE_STRING, description='IFSC code'),
#         'branch_name': openapi.Schema(type=openapi.TYPE_STRING, description='Branch name'),
#         'pan_number': openapi.Schema(type=openapi.TYPE_STRING, description='Pan number'),
#     },
#     required=['bank_name', 'bank_accout_number']
# )
@swagger_auto_schema(
    method='post',
    operation_description="Create a new bank information record for the authenticated user.",
    request_body=BankInformationSerializer,
    responses={
        201: openapi.Response('Bank information created successfully.', BankInformationSerializer),
        400: openapi.Response('Validation error or bad request.')
    }
)
@api_view(['POST'])
@authentication_required()
def create_bank_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)
    email = get_user_email(user_id)
    data = request.data
    data['user_id'] = user_id

    serializer = BankInformationSerializer(data=data)
    if serializer.is_valid():
        try:
            add_additional_information = serializer.save()
            add_additional_information.created_by = email
            add_additional_information.created_on  = datetime.now(timezone.utc)
            add_additional_information.save()

            response = serializer.data
            response['created_on'] = add_additional_information.created_on
            return Response(response, status=st.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=st.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=st.HTTP_400_BAD_REQUEST)


custom_request_body_schema_with_bank_id = openapi.Schema(
    title='BankInformationSerializer',
    type=openapi.TYPE_OBJECT,
    properties={
        'bank_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id of the bank'),
        'bank_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the bank'),
        'bank_accout_number': openapi.Schema(type=openapi.TYPE_STRING, description='Bank account number'),
        'ifsc_code': openapi.Schema(type=openapi.TYPE_STRING, description='IFSC code'),
        'branch_name': openapi.Schema(type=openapi.TYPE_STRING, description='Branch name'),
        'pan_number': openapi.Schema(type=openapi.TYPE_STRING, description='Pan number'),

    },
)    
  
@swagger_auto_schema(
    method='patch',
    operation_description="Update a bank information record for the authenticated user.",
    request_body=custom_request_body_schema_with_bank_id,
    responses={
        200: openapi.Response('Bank information updated successfully.', BankInformationSerializer),
        400: openapi.Response('Validation error or bad request.'),
        404: openapi.Response('Bank information record not found or does not belong to the user.')
    }
)    
@api_view(['PATCH'])
@authentication_required()
def update_bank_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)
    
    email = get_user_email(user_id)
    data = request.data
    bank_id = data.get('bank_id')
    
    if not bank_id:
        return Response({'error': 'Bank information ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        bank_info = BankInformation.objects.get(bank_id=bank_id)
    except BankInformation.DoesNotExist:
        return Response({'error': 'Bank information record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)

    serializer = BankInformationSerializer(bank_info, data=data, partial=True) 
    if serializer.is_valid():
        try:
            updated_info = serializer.save()
            updated_info.updated_by = email
            updated_info.updated_on =  datetime.now(timezone.utc)
            updated_info.save()

            return Response(serializer.data, status=st.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=st.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=st.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a bank information record for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'bank_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the bank information record to delete'),
        },
    ),
    responses={
        200: openapi.Response('Bank information successfully deleted.'),
        400: openapi.Response('Bad request, bank ID is required.'),
        404: openapi.Response('Bank information record not found.')
    }
)
@api_view(['DELETE'])
@authentication_required()
def delete_bank_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    data = request.data
    bank_id = data.get('bank_id')
    
    if not bank_id:
        return Response({'error': 'Bank information ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        bank_info = BankInformation.objects.get(bank_id=bank_id, is_deleted=False, user_id=user_id)
        bank_info.is_deleted = True
        bank_info.updated_on = datetime.now(timezone.utc)

        bank_info.save()
        return Response({'message': 'Bank information successfully deleted'}, status=st.HTTP_200_OK)
    except BankInformation.DoesNotExist:
        return Response({'error': 'Bank information record not found'}, status=st.HTTP_404_NOT_FOUND)