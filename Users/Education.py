from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as st
from .models import *
from .serializers import *
from Authentication.decorators import authentication_required
from Authentication.views import *


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve education information for the authenticated user.",
    responses={
        200: openapi.Response('Successfully retrieved education information.', EducationSerializer(many=True)),
        400: openapi.Response('Bad Request'),
        404: openapi.Response('No education records found for the user.'),
        500: openapi.Response('Internal Server Error')
    }
)
@api_view(['GET'])
@authentication_required()
def get_education_information(request):
    try:
        user_id = request.user.get('id')
        if not user_id:
            return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

        education_information = Education.objects.filter(user_id=user_id, is_deleted=False)
        
        serializer = EducationSerializer(education_information, many=True)
        
        return Response(serializer.data, status=st.HTTP_200_OK)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)
    

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve education information for a specific education ID for the authenticated user.",
    manual_parameters=[
        openapi.Parameter('education_id', openapi.IN_QUERY, description="The ID of the education information to retrieve.", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={
        200: openapi.Response('Successful retrieval of education information.', EducationSerializer),
        400: openapi.Response('Error due to missing parameters or invalid request.'),
        404: openapi.Response('Education information record not found or does not belong to the user.'),
    }
)
@api_view(['GET'])
@authentication_required()
def get_education_by_id(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    education_id = request.query_params.get('education_id')
    
    if not education_id:
        return Response({'error': 'Education ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        education_info = Education.objects.get(education_id=education_id, user_id=user_id, is_deleted=False)
    except Education.DoesNotExist:
        return Response({'error': 'Education record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)

    serializer = EducationSerializer(education_info)
    return Response(serializer.data, status=st.HTTP_200_OK)


custom_request_body_schema = openapi.Schema(
    title='EducationSerializer',
    type=openapi.TYPE_OBJECT,
    properties={
        'college_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the College'),
        'admission_year': openapi.Schema(type=openapi.TYPE_STRING, description='Admission Year'),
        'passout_year': openapi.Schema(type=openapi.TYPE_STRING, description='Passout Year'),
        'course': openapi.Schema(type=openapi.TYPE_STRING, description='Course'),
    },
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new education information record for the authenticated user.",
    request_body=custom_request_body_schema,
    responses={
        201: openapi.Response('Education information created successfully.', EducationSerializer),
        400: openapi.Response('Validation error or bad request.')
    }
)
@api_view(['POST'])
@authentication_required()
def create_education_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    email = get_user_email(user_id)
    data = request.data
    data['user_id'] = user_id

    serializer = EducationSerializer(data=data)
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
    
custom_request_body_schema_update = openapi.Schema(
    title='EducationSerializer',
    type=openapi.TYPE_OBJECT,
    properties={
        'education_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id of the education'),
        'college_name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the College'),
        'admission_year': openapi.Schema(type=openapi.TYPE_STRING, description='Admission Year'),
        'passout_year': openapi.Schema(type=openapi.TYPE_STRING, description='Passout Year'),
        'course': openapi.Schema(type=openapi.TYPE_STRING, description='Course'),
    },
)
@swagger_auto_schema(
    method='patch',
    operation_description="Update a education information record for the authenticated user.",
    request_body=custom_request_body_schema_update,
    responses={
        200: openapi.Response('Education information updated successfully.', EducationSerializer),
        400: openapi.Response('Validation error or bad request.'),
        404: openapi.Response('Education information record not found or does not belong to the user.')
    }
)

@api_view(['PATCH'])
@authentication_required()
def update_education_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    email = get_user_email(user_id)
    data = request.data
    education_id = data.get('education_id')
    
    if not education_id:
        return Response({'error': 'Education ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        education_info = Education.objects.get(education_id=education_id, user_id=user_id, is_deleted=False)
    except Education.DoesNotExist:
        return Response({'error': 'Education record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)

    serializer = EducationSerializer(education_info, data=data, partial=True)
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
    operation_description="Delete a education information record for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'education_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the education information record to delete'),
        },
    ),
    responses={
        200: openapi.Response('Education information successfully deleted.'),
        400: openapi.Response('Bad request, bank ID is required.'),
        404: openapi.Response('Education information record not found.')
    }
)
@api_view(['DELETE'])
@authentication_required()
def delete_education_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    data = request.data
    education_id = data.get('education_id')
    
    if not education_id:
        return Response({'error': 'Education ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        education_info = Education.objects.get(education_id=education_id, user_id=user_id, is_deleted=False)
        education_info.is_deleted = True
        education_info.updated_on = now()

        education_info.save()
        return Response({'message': 'Education information successfully deleted'}, status=st.HTTP_200_OK)
    except Education.DoesNotExist:
        return Response({'error': 'Education record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=st.HTTP_400_BAD_REQUEST)
    