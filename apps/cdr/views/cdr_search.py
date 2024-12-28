from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.cdr.serializers.cdr_serializer import CdrSearchSerializer
from apps.core.os_setting_elastic import es


class CDRSearchView(APIView):
    """
    This view allows querying of Call Detail Records (CDRs) in Elasticsearch.
    Filters include date range, source/destination numbers, call success status and call duration,.

    Parameters (via GET request):
    - src_number: (str) The source phone number to filter by.
    - dest_number: (str) The destination phone number to filter by.
    - call_successful: (str) Whether the call was successful, should be 'true' or 'false'.
    - call_duration: (int) The minimum call duration (in seconds) to filter CDRs.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'default'

    ALLOWED_PARAMETERS = ['src_number', 'dest_number', 'call_successful', 'call_duration']

    def get(self, request):
        """
        Handles the GET request to search CDRs based on query parameters.

        Parameters:
        - src_number (str): Source number for filtering CDRs.
        - dest_number (str): Destination number for filtering CDRs.
        - call_successful (str): Whether the call was successful ('true' or 'false').
        - call_duration (int): The minimum call duration to filter CDRs.

        Returns:
        - Response: A list of filtered CDRs or error message.
        """
        params = request.GET.dict()
        print(params)
        invalid_params = [key for key in params.keys() if key not in self.ALLOWED_PARAMETERS]
        print(invalid_params)
        if invalid_params:
            return Response(
                {"error": f"Invalid parameter(s): {', '.join(invalid_params)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CdrSearchSerializer(data=request.GET)
        if serializer.is_valid():
            validated_data = serializer.validated_data

            if not validated_data:
                return Response(
                    {"error": "No valid parameters provided for search"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            src_number = validated_data.get('src_number')
            dest_number = validated_data.get('dest_number')
            call_successful = validated_data.get('call_successful')
            call_duration = validated_data.get('call_duration')

            query = self.build_query(src_number, dest_number, call_successful, call_duration)

            try:
                response = es.search(index="cdrs", body=query)
                hits = response.get("hits", {}).get("hits", [])
                if not hits:
                    return Response({"message": "No results found."}, status=status.HTTP_404_NOT_FOUND)
                cdrs = [hit["_source"] for hit in hits]
                return Response(cdrs, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def build_query(self, src_number, dest_number, call_successful, call_duration):
        """
        Builds the Elasticsearch query based on provided filters.

        Parameters:
        - src_number (str): Source phone number to filter by.
        - dest_number (str): Destination phone number to filter by.
        - call_successful (str): 'true' or 'false' to filter by call success status.
        - call_duration (int): The minimum call duration (in seconds) to filter CDRs.

        Returns:
        - dict: The Elasticsearch query with appropriate filters.
        """
        query = {"query": {"bool": {"filter": []}}}

        if src_number:
            query["query"]["bool"]["filter"].append({"match": {"src_number": src_number}})
        if dest_number:
            query["query"]["bool"]["filter"].append({"match": {"dest_number": dest_number}})
        if call_successful is not None:
            query["query"]["bool"]["filter"].append({"term": {"call_successful": call_successful}})
        if call_duration:
            query["query"]["bool"]["filter"].append({"term": {"call_duration": call_duration}})

        return query
