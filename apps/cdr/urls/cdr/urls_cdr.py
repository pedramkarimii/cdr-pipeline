from django.urls import path

from apps.cdr.views.cdr_search import CDRSearchView
from apps.cdr.views.cdr_stats import CDRStatsView
from apps.cdr.views.cdr_sync_tatus import CDRSyncStatusView

"""
    URL patterns for the CDR API:
    1. 'cdr/search/': Endpoint to search for CDRs with various filtering options (source, destination, call success,
         duration, etc.).
    2. 'cdr/stats/': Endpoint to get aggregated statistics about CDRs such as average call duration, successful 
         and failed calls.
    3. 'cdr/sync-status/': Endpoint to check if the CDRs are in sync between the Django database and Elasticsearch.
    """
urlpatterns = [
    path('cdr/search/', CDRSearchView.as_view(), name='cdr_search'),
    path('cdr/stats/', CDRStatsView.as_view(), name='cdr_stats'),
    path('cdr/sync-status/', CDRSyncStatusView.as_view(), name='cdr_sync_status'),
]
