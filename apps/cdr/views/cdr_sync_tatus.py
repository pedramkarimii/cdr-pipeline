from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.cdr.models import Cdr
from apps.core.os_setting_elastic import es


class CDRSyncStatusView(APIView):
    """
    This view checks if the CDRs are in sync between the Django database and Elasticsearch.

    Parameters (via GET request):
    - None. This view compares the count of CDRs in the database and Elasticsearch.

    Returns:
    - Response: A status message indicating whether the data is synced or not, along with the counts
                from both the database and Elasticsearch.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'default'

    def get(self, request):
        """
        Handles the GET request to check if the CDRs are in sync between the database and Elasticsearch.

        Returns:
        - Response: A message indicating the sync status, and counts from the database and Elasticsearch.
        """

        try:
            cdr_count_db = Cdr.objects.count()
            cdr_count_es = es.count(index="cdrs")['count']

            # Check if counts match
            if cdr_count_db == cdr_count_es:
                return Response({"status": "synced"}, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "out_of_sync",
                    "db_count": cdr_count_db,
                    "es_count": cdr_count_es
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
