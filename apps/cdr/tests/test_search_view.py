from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework import status
from apps.cdr.models import Cdr
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class CDRSearchViewTest(TestCase):
    def setUp(self):
        """
        Set up the test environment by creating a test user, obtaining a JWT token,
        and creating some CDR records in the database for testing.
        """
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.cdr1 = Cdr.objects.create(
            src_number="09124567890",
            dest_number="09127654321",
            call_duration=300,
            call_successful=True
        )
        self.cdr2 = Cdr.objects.create(
            src_number="09126543210",
            dest_number="09124509876",
            call_duration=150,
            call_successful=False
        )
        self.url = reverse('cdr_search')

    @patch('apps.cdr.views.cdr_search.es.search')
    def test_cdr_search_with_valid_params(self, mock_es_search):
        """
        Test searching CDRs with valid parameters.
        """
        mock_es_search.return_value = {
            "hits": {
                "hits": [
                    {"_source": {"src_number": "09124567890", "dest_number": "09127654321", "call_duration": 300,
                                 "call_successful": True}}
                ]
            }
        }

        params = {'src_number': '09124567890', 'call_successful': 'true'}
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['src_number'], '09124567890')
        self.assertEqual(response.data[0]['call_successful'], True)

    @patch('apps.cdr.views.cdr_search.es.search')
    def test_cdr_search_with_invalid_param(self, mock_es_search):
        """
        Test when an invalid parameter is passed.
        """
        params = {'invalid_param': 'value'}
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid parameter(s)", response.data['error'])

    @patch('apps.cdr.views.cdr_search.es.search')
    def test_cdr_search_with_no_results(self, mock_es_search):
        """
        Test when no CDRs match the search criteria.
        """
        mock_es_search.return_value = {"hits": {"hits": []}}

        params = {'src_number': '09120000000'}
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No results found.')

    @patch('apps.cdr.views.cdr_search.es.search')
    def test_cdr_search_elasticsearch_error(self, mock_es_search):
        """
        Test when Elasticsearch throws an exception (e.g., down).
        """
        mock_es_search.side_effect = Exception("Elasticsearch is down")

        params = {'src_number': '09124567890'}
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertEqual(response.data['error'], "Elasticsearch is down")
