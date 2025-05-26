from datetime import datetime, timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status as st
from .models import *
from .serializers import *
from Authentication.decorators import authentication_required
from Authentication.views import *



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve holiday information for the authenticated user.",
    responses={
        200: openapi.Response('Successfully retrieved holiday information.', HolidaySerializer(many=True)),
        400: openapi.Response('Bad Request'),
        404: openapi.Response('No holiday records found for the user.'),
        500: openapi.Response('Internal Server Error')
    }
)
@api_view(['GET'])
@authentication_required()
def get_holiday_information(request):
    try:
        holidays = Holiday.objects.filter(is_deleted=False)
        
        serializer = HolidaySerializer(holidays, many=True)
        
        return Response(serializer.data, status=st.HTTP_200_OK)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return Response({'error': 'An unexpected error occurred'}, status=st.HTTP_500_INTERNAL_SERVER_ERROR)