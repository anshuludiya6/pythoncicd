from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as st
from .models import *
from .serializers import *
from Authentication.decorators import authentication_required
from Authentication.views import *


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve experience information for the authenticated user.",
    responses={
        200: openapi.Response('Successfully retrieved experience information.', ExperienceInformationSerializer(many=True)),
        400: openapi.Response('Bad Request'),
        404: openapi.Response('No experience records found for the user.'),
        500: openapi.Response('Internal Server Error')
    }
)
@api_view(['GET'])
@authentication_required()
def get_experience_information(request):
    try:
        user_id = request.user.get('id')
        if not user_id:
            return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

        experience_information = ExperienceInformation.objects.filter(user_id=user_id, is_deleted=False)
        
        serializer = ExperienceInformationSerializer(experience_information, many=True)
        
        return Response(serializer.data, status=st.HTTP_200_OK)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve experience information for a specific experience ID for the authenticated user.",
    manual_parameters=[
        openapi.Parameter('experience_id', openapi.IN_QUERY, description="The ID of the experience information to retrieve.", type=openapi.TYPE_INTEGER, required=True),
    ],
    responses={
        200: openapi.Response('Successful retrieval of experience information.', ExperienceInformationSerializer),
        400: openapi.Response('Error due to missing parameters or invalid request.'),
        404: openapi.Response('Experience information record not found or does not belong to the user.'),
    }
) 
@api_view(['GET'])
@authentication_required()
def get_experience_by_id(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    experience_id = request.query_params.get('experience_id')
    
    if not experience_id:
        return Response({'error': 'Experience ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        experience_info = ExperienceInformation.objects.get(experience_id=experience_id, user_id=user_id, is_deleted=False)
    except ExperienceInformation.DoesNotExist:
        return Response({'error': 'Experience record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)

    serializer = ExperienceInformationSerializer(experience_info)
    return Response(serializer.data, status=st.HTTP_200_OK)



custom_request_body_schema = openapi.Schema(
    title='ExperienceInformationSerializer',
    type=openapi.TYPE_OBJECT,
    properties={
        'position': openapi.Schema(type=openapi.TYPE_STRING, description='Position in a Company'),
        'date_of_joining': openapi.Schema(type=openapi.TYPE_STRING, description='Date of Joining'),
        # 'date_of_relieving': openapi.Schema(type=openapi.TYPE_STRING, description='Date of Relieving'),
    },
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new experience information record for the authenticated user.",
    request_body=custom_request_body_schema,
    responses={
        201: openapi.Response('Experience information created successfully.', ExperienceInformationSerializer),
        400: openapi.Response('Validation error or bad request.')
    }
)
@api_view(['POST'])
@authentication_required()
def create_experience_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    email = get_user_email(user_id)
    data = request.data
    data['user_id'] = user_id

    serializer = ExperienceInformationSerializer(data=data)
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
    title='ExperienceInformationSerializer',
    type=openapi.TYPE_OBJECT,
    properties={
        'experience_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='id of the experience'),
        'position': openapi.Schema(type=openapi.TYPE_STRING, description='Position in a Company'),
        'date_of_joining': openapi.Schema(type=openapi.TYPE_STRING, description='Date of Joining'),
        'date_of_relieving': openapi.Schema(type=openapi.TYPE_STRING, description='Date of Relieving'),
    },
)
@swagger_auto_schema(
    method='patch',
    operation_description="Update a experience information record for the authenticated user.",
    request_body=custom_request_body_schema_update,
    responses={
        200: openapi.Response('Experience information updated successfully.', ExperienceInformationSerializer),
        400: openapi.Response('Validation error or bad request.'),
        404: openapi.Response('Experience information record not found or does not belong to the user.')
    }
)

@api_view(['PATCH'])
@authentication_required()
def update_experience_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    email = get_user_email(user_id)
    data = request.data
    experience_id = data.get('experience_id')
    
    if not experience_id:
        return Response({'error': 'Experience ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        experience_info = ExperienceInformation.objects.get(experience_id=experience_id, user_id=user_id, is_deleted=False)
    except ExperienceInformation.DoesNotExist:
        return Response({'error': 'Experience record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)

    serializer = ExperienceInformationSerializer(experience_info, data=data, partial=True)
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
    operation_description="Delete a experience information record for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'experience_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the experience information record to delete'),
        },
    ),
    responses={
        200: openapi.Response('Experience information successfully deleted.'),
        400: openapi.Response('Bad request, bank ID is required.'),
        404: openapi.Response('Experience information record not found.')
    }
)
@api_view(['DELETE'])
@authentication_required()
def delete_experience_information(request):
    user_id = request.user.get('id')
    if not user_id:
        return Response({'error': 'User ID not found in request'}, status=st.HTTP_400_BAD_REQUEST)

    data = request.data
    experience_id = data.get('experience_id')
    
    if not experience_id:
        return Response({'error': 'Experience ID is required'}, status=st.HTTP_400_BAD_REQUEST)
    
    try:
        experience_info = ExperienceInformation.objects.get(experience_id=experience_id, user_id=user_id, is_deleted=False)
        experience_info.is_deleted = True
        experience_info.updated_on = now()

        experience_info.save()
        return Response({'message': 'Experience information successfully deleted'}, status=st.HTTP_200_OK)
    except ExperienceInformation.DoesNotExist:
        return Response({'error': 'Experience record not found or does not belong to the user'}, status=st.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=st.HTTP_400_BAD_REQUEST)