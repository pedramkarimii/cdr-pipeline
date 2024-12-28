from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.core.os_setting_elastic import es


class CDRStatsView(APIView):
    """
    This view provides statistics about CDRs, such as average call duration,
    and the number of successful and failed calls.

    Parameters (via GET request):
    - None. This view only aggregates data from Elasticsearch.

    Returns:
    - Response: A dictionary containing average call duration, number of successful calls,
                and number of failed calls.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'default'

    def get(self, request):
        """
        Handles the GET request to retrieve statistics about CDRs.

        Returns:
        - Response: A dictionary with statistics on average call duration, successful and failed calls.
        """

        try:
            response = es.search(
                index="cdrs",
                body={
                    "aggs": {
                        "avg_duration": {
                            "avg": {
                                "field": "call_duration"
                            }
                        },
                        "successful_calls": {
                            "filter": {
                                "term": {
                                    "call_successful": True
                                }
                            }
                        },
                        "failed_calls": {
                            "filter": {
                                "term": {
                                    "call_successful": False
                                }
                            }
                        }
                    }
                }
            )

            stats = {
                "average_call_duration": response['aggregations']['avg_duration']['value'],
                "successful_calls": response['aggregations']['successful_calls']['doc_count'],
                "failed_calls": response['aggregations']['failed_calls']['doc_count']
            }

            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
