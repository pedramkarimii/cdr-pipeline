from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.cdr.serializers.cdr_serializer import CdrSearchSerializer
from apps.core.os_setting_elastic import es


class CDRSearchView(APIView):
    """
    This view allows querying of Call Detail Records (CDRs) in Elasticsearch.
    Filters include date range, source/destination numbers, call success status, call duration, and timestamp.

    Parameters (via GET request):
    - src_number: (str) The source phone number to filter by.
    - dest_number: (str) The destination phone number to filter by.
    - call_successful: (str) Whether the call was successful, should be 'true' or 'false'.
    - timestamp: (str) The timestamp to filter CDRs.
    - call_duration: (int) The minimum call duration (in seconds) to filter CDRs.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'default'

    def get(self, request):
        """
        Handles the GET request to search CDRs based on query parameters.

        Parameters:
        - src_number (str): Source number for filtering CDRs.
        - dest_number (str): Destination number for filtering CDRs.
        - call_successful (str): Whether the call was successful ('true' or 'false').
        - timestamp (str): Timestamp for filtering CDRs.
        - call_duration (int): The minimum call duration to filter CDRs.

        Returns:
        - Response: A list of filtered CDRs or error message.
        """
        serializer = CdrSearchSerializer(data=request.GET)

        if serializer.is_valid():
            src_number = serializer.validated_data.get('src_number')
            dest_number = serializer.validated_data.get('dest_number')
            call_successful = serializer.validated_data.get('call_successful')
            timestamp = serializer.validated_data.get('timestamp')
            call_duration = serializer.validated_data.get('call_duration')

            query = self.build_query(src_number, dest_number, call_successful, timestamp, call_duration)
            try:
                response = es.search(index="cdrs", body=query)
                cdrs = [hit["_source"] for hit in response['hits']['hits']]
                return Response(cdrs, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def build_query(self, src_number, dest_number, call_successful, timestamp, call_duration):
        """
        Builds the Elasticsearch query based on provided filters.

        Parameters:
        - src_number (str): Source phone number to filter by.
        - dest_number (str): Destination phone number to filter by.
        - call_successful (str): 'true' or 'false' to filter by call success status.
        - timestamp (str): Timestamp for filtering CDRs.
        - call_duration (int): The minimum call duration (in seconds) to filter CDRs.

        Returns:
        - dict: The Elasticsearch query with appropriate filters.
        """
        query = {"query": {"bool": {"filter": []}}}

        # Add filters to the query
        if src_number:
            query["query"]["bool"]["filter"].append({"match": {"src_number": src_number}})
        if dest_number:
            query["query"]["bool"]["filter"].append({"match": {"dest_number": dest_number}})
        if call_successful is not None:
            query["query"]["bool"]["filter"].append(self.call_successful_filter(call_successful))
        if timestamp:
            query["query"]["bool"]["filter"].append(self.date_range_filter(timestamp))
        if call_duration:
            query["query"]["bool"]["filter"].append(self.call_duration_filter(call_duration))

        return query

    def date_range_filter(self, timestamp):
        """
        Returns a filter for the 'timestamp' field based on the provided timestamp.

        Parameters:
        - timestamp (str): The timestamp to filter CDRs.

        Returns:
        - dict: The filter for the 'timestamp' field.
        """
        parsed_timestamp = parse_datetime(timestamp)

        if parsed_timestamp:
            if timezone.is_naive(parsed_timestamp):
                parsed_timestamp = timezone.make_aware(parsed_timestamp)
            return {"range": {"timestamp": {"gte": parsed_timestamp.isoformat()}}}
        return {}

    def call_successful_filter(self, call_successful):
        """
        Returns a filter for the 'call_successful' field, either True or False.

        Parameters:
        - call_successful (str): 'true' or 'false' to filter by the success status.

        Returns:
        - dict: The filter for the 'call_successful' field.
        """
        return {"match": {"call_successful": call_successful.lower() == 'true'}}

    def call_duration_filter(self, call_duration):
        """
        Returns a filter for the 'call_duration' field, where the call duration matches exactly the specified value.

        Parameters:
        - call_duration (int): The exact call duration to filter CDRs.

        Returns:
        - dict: The filter for the 'call_duration' field.
        """
        try:
            call_duration = int(call_duration)
            return {"term": {"call_duration": call_duration}}
        except ValueError:
            return {}
