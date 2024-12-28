from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch
from django.test import TestCase
from rest_framework import status


class CDRStatsViewTest(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a test user and obtaining a JWT token.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.url = '/api/cdr/stats/'

    @patch('apps.cdr.views.cdr_stats.es.search')
    def test_cdr_stats_success(self, mock_es_search):
        """
        Test when Elasticsearch returns data correctly.
        """
        mock_es_search.return_value = {
            'aggregations': {
                'avg_duration': {'value': 150.0},
                'successful_calls': {'doc_count': 120},
                'failed_calls': {'doc_count': 30}
            }
        }
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['average_call_duration'], 150.0)
        self.assertEqual(response.data['successful_calls'], 120)
        self.assertEqual(response.data['failed_calls'], 30)

    @patch('apps.cdr.views.cdr_stats.es.search')
    def test_cdr_stats_es_exception(self, mock_es_search):
        """
        Test when Elasticsearch throws an exception.
        """
        mock_es_search.side_effect = Exception("Elasticsearch is down")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Elasticsearch is down")

    @patch('apps.cdr.views.cdr_stats.es.search')
    def test_cdr_stats_empty_data(self, mock_es_search):
        """
        Test when Elasticsearch returns no data (empty aggregation results).
        """
        mock_es_search.return_value = {
            'aggregations': {
                'avg_duration': {'value': 0.0},
                'successful_calls': {'doc_count': 0},
                'failed_calls': {'doc_count': 0}
            }
        }

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['average_call_duration'], 0.0)
        self.assertEqual(response.data['successful_calls'], 0)
        self.assertEqual(response.data['failed_calls'], 0)
