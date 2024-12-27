import os
from django.core.wsgi import get_wsgi_application

# Set the default Django settings module for the 'django' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Get the WSGI application callable for the Django application
application = get_wsgi_application()

# Import the Elasticsearch client
from elasticsearch import Elasticsearch

# Create an Elasticsearch client instance connecting to localhost on port 9200
es = Elasticsearch([{'scheme': 'http', 'host': 'localhost', 'port': 9200}])
