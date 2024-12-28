from unittest.mock import patch

from apps.cdr.models import Cdr
from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


class CDRSyncStatusViewTest(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a test user and obtaining a JWT token.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.url = '/api/cdr/sync-status/'

    @patch('apps.cdr.views.cdr_sync_tatus.es.count')
    def test_cdr_sync_status_success(self, mock_es_count):
        """
        Test when the CDR counts in the Django DB and Elasticsearch are synced.
        """
        mock_es_count.return_value = {'count': 100}

        cdrs = [Cdr(src_number=f"src_{i:02d}", dest_number=f"dest_{i:02d}") for i in range(100)]
        Cdr.objects.bulk_create(cdrs)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'synced')

    @patch('apps.cdr.views.cdr_sync_tatus.es.count')
    def test_cdr_sync_status_out_of_sync(self, mock_es_count):
        """
        Test when the CDR counts in the Django DB and Elasticsearch are out of sync.
        """
        mock_es_count.return_value = {'count': 120}
        cdrs = [Cdr(src_number=f"src_{i:02d}", dest_number=f"dest_{i:02d}") for i in range(100)]
        Cdr.objects.bulk_create(cdrs)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'out_of_sync')
        self.assertEqual(response.data['db_count'], 100)
        self.assertEqual(response.data['es_count'], 120)

    @patch('apps.cdr.views.cdr_sync_tatus.es.count')
    def test_cdr_sync_status_es_exception(self, mock_es_count):
        """
        Test when Elasticsearch throws an exception (e.g., down).
        """
        mock_es_count.side_effect = Exception("Elasticsearch is down")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Elasticsearch is down")
