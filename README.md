# CDR Pipeline

**CDR Pipeline** is a scalable, reliable, and efficient system for ingesting, processing, storing, and querying Call Detail Records (CDRs). The system utilizes RabbitMQ for handling high-throughput message queuing, Django and PostgreSQL for data storage, and Elasticsearch for fast search and analytics. It’s designed to process up to 500 CDRs per second with minimal delay between ingestion and availability for querying.

## Features

- High Throughput Ingestion: The system can handle 500 CDRs per second, ensuring no data loss with message queuing via RabbitMQ.
- Real-Time Data Processing: CDRs are processed and validated asynchronously through RabbitMQ and stored in a PostgreSQL database.
- Efficient Searching: Elasticsearch is used for fast querying of large datasets, with support for filtering by source and destination numbers, date ranges, and call duration.
- Scalability and Fault Tolerance: The system can be scaled horizontally, and RabbitMQ ensures message durability and reliable delivery.
- REST API: Provides endpoints for querying CDR data stored in Elasticsearch.

## Architecture Overview

The system is built with the following components:

1. RabbitMQ: A message broker that facilitates the asynchronous and fault-tolerant processing of CDRs.
2. Django: A web framework that provides API endpoints for querying CDRs, handles data validation, and interacts with PostgreSQL for storage.
3. PostgreSQL: A relational database used to store the validated CDRs.
4..md for your cdr-pi A distributed search and analytics engine used to index and search CDR data in real-time.
5. API Layer: Provides endpoints to query CDRs, supporting various filters and sorting.


Project Structure
```bash
 .
├──  apps
│  ├──  cdr
│  │  ├──  serializers
│  │  │  ├──  __init__.py
│  │  │  └──  cdr_serializer.py
│  │  ├──  tasks
│  │  │  ├──  __init__.py
│  │  │  ├──  tasks_consumer.py
│  │  │  ├──  tasks_main.py
│  │  │  └──  tasks_producer.py
│  │  ├──  tests
│  │  │  ├──  __init__.py
│  │  │  ├──  test_model.py
│  │  │  └──  test_view.py
│  │  ├──  urls
│  │  │  ├──  cdr
│  │  │  │  ├──  __init__.py
│  │  │  │  └──  urls_cdr.py
│  │  │  └──  __init__.py
│  │  ├──  views
│  │  │  ├──  __init__.py
│  │  │  ├──  cdr_search.py
│  │  │  ├──  cdr_stats.py
│  │  │  └──  cdr_sync_tatus.py
│  │  ├──  __init__.py
│  │  ├──  admin.py
│  │  ├──  apps.py
│  │  └──  models.py
│  ├──  core
│  │  ├──  management
│  │  │  ├──  commands
│  │  │  │  ├──  __init__.py
│  │  │  │  ├──  create_consumer.py
│  │  │  │  ├──  create_producer.py
│  │  │  │  ├──  create_producer_consumer.py
│  │  │  │  ├──  delete_logs.py
│  │  │  │  ├──  wait_for_db.py
│  │  │  │  ├──  wait_for_rabbitmq.py
│  │  │  │  └──  wait_for_redis.py
│  │  │  └──  __init__.py
│  │  ├──  __init__.py
│  │  ├──  documents.py
│  │  ├──  middlewares.py
│  │  ├──  os_setting_elastic.py
│  │  └──  validators.py
│  └──  __init__.py
├──  config
│  ├──  __init__.py
│  ├──  asgi.py
│  ├──  celery.py
│  ├──  conf.py
│  ├──  settings.py
│  ├──  urls.py
│  └──  wsgi.py
├──  utility
│  ├──  bin
│  │  └──  setup.sh
│  ├──  cache
│  │  └──  f4b2ae60a662bd58f1d94cecdd5c5f5a.djcache
│  ├──  __init__.py
│  └──  cache.py
├──  .env.local.sample
├──  .pre-commit-config.yaml
├──  LICENSE
├──  manage.py
├──  pyproject.toml
├──  README.md
└──  requirements.txt
```
#### System Design Diagram
```
                            +-------------------+
                            |   Producer/API    |
                            |  (Sends CDR data) |
                            +-------------------+
                                      |
                                      v
                          +-----------------------+
                          |     RabbitMQ Queue    |
                          | (Persistent Queue)    |
                          +-----------------------+
                                      |
                        +-------------+-------------+
                        |                           |
               +-------------------+        +---------------------+
               | RabbitMQ Consumer  |       |Database (Postgres)  |
               | (Process CDR)      |       |(Store CDR data)     |
               +-------------------+        +---------------------+
                         |                              |
                         v                              v
                 +-----------------+              +---------------------+
                 | Elasticsearch   |              | Sync Service        |
                 | (Index CDR data)|  <-------->  | (Synchronize CDR)   |
                 +-----------------+              +---------------------+




```


## Technologies Used

This project uses a variety of tools and technologies to ensure scalability, performance, and reliability:

- **Python**: The programming language used for developing the system (version 3.12+).
- **Django**: A high-level Python web framework for building the API and backend services (version 5.1+).
- **RabbitMQ**: A message broker that handles high-throughput message ingestion and delivery to consumers.
- **Celery**: An asynchronous task queue used for managing background tasks like Elasticsearch indexing.
- **PostgreSQL/MySQL**: Relational databases for storing and managing Call Detail Records (CDRs).
- **Elasticsearch**: A distributed search and analytics engine for fast querying and indexing of CDR data.
- **Pika**: A Python library for interacting with RabbitMQ.
- **Django Elasticsearch DSL**: A library that integrates Elasticsearch with Django for indexing models and searching efficiently.
- **Celery Results**: A Django extension for storing the results of Celery tasks.
- **drf-spectacular**: A tool to generate OpenAPI specifications for the Django REST API.
- **Django Rest Framework**: A toolkit for building Web APIs in Django.
- **Python Decouple**: A library for separating settings from code to keep sensitive data secure and configurable.

## API Documentation

The API documentation is available through the following interactive interfaces:

- **ReDoc**: Provides a user-friendly interface for exploring the API endpoints and their details.
- **Swagger UI**: Allows you to interact with the API directly from your browser, testing endpoints and viewing
  responses.

### Accessing API Documentation

Ensure that your Django server is running. You can access the API documentation at the following URLs:

- **API Schema**: [http://localhost:8000/schema/](http://localhost:8000/schema/)
    - This endpoint provides the raw OpenAPI schema for the API, which can be used for various tools and integrations.

- **ReDoc**: [http://localhost:8000/schema/redoc/](http://localhost:8000/schema/redoc/)
    - ReDoc offers a comprehensive, interactive documentation view of the API endpoints. It displays details about each
      operation, parameters, and responses in a clean interface.

- **Swagger UI**: [http://localhost:8000/schema/swagger-ui/](http://localhost:8000/schema/swagger-ui/)
    - Swagger UI provides an interactive API explorer where you can test API endpoints, see request and response
      formats, and execute API calls directly.
## Installation Guide

### 1. Install RabbitMQ

To run RabbitMQ using Docker:

```bash
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
```
You can access the RabbitMQ Management UI at http://localhost:15672 using the default username and password guest.

2. Install Elasticsearch

To run Elasticsearch using Docker:
```bash
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 docker.elastic.co/elasticsearch/elasticsearch:7.10.0
```
Elasticsearch will be available at http://localhost:9200.

3. Install PostgreSQL

To run PostgreSQL using Docker:
```bash
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=mysecretpassword postgres:latest
```
4. Clone the Repository and Install Dependencies

Clone the repository and install Python dependencies:
```bash
git clone https://github.com/pedramkarimii/cdr-pipeline.git

cd cdr-pipeline

poetry install

cp .env.local.sample .env

chmod +x ./utility/bin/setup.sh

./utility/bin/setup.sh

pip install -r requirements.txt
```
5. Configure Django

Edit the settings.py file to configure(.env) the PostgreSQL and Elasticsearch connections


Running the Pipeline

1. Start the Produce CDRs and RabbitMQ Consumer

simulate the generation of 500 CDRs per second by running the producer script, which sends CDRs to RabbitMQ
The consumer listens for messages from RabbitMQ, processes them, and stores the validated CDRs in PostgreSQL
```bash
python manage.py create_producer_consumer --queue_prefix cdr_queue --shard_count 4 --num_messages 500 
      
```
2. Csearch Index CDRs

```bash
python manage.py csearch_index --rebuild 
```
3. Querying the CDRs

You can query the CDR data using the provided API endpoints.

Example API Request:

 • Search for CDRs by Source and Destination Numbers:
Example request to search for calls between two numbers:
```bash
GET http://localhost:8000/api/search/?src_number=1234567890&dest_number=0987654321
```

 • Search for CDRs by Date Range:
Example request to search CDRs between two dates:
```bash
GET http://localhost:8000/api/search/?start_date=2024-01-01&end_date=2024-12-31
```


API Response:

The response will return a JSON object containing the matching CDR records:
```bash
[
  {
    "src_number": "09124526529",
    "dest_number": "09125365540",
    "call_duration": 41310,
    "call_successful": false
  },
  ...
]
```

Testing the System

To ensure the system is functioning correctly, you can run the tests:
```bash
python manage.py test
```
This will run the unit tests for the system, ensuring that all components are working as expected under different conditions.


### Fork and Contribute

To contribute to the project, you can fork it and submit a pull request. Here’s how:

1. **Fork the repository from GitHub**: [Fork Repository](https://github.com/pedramkarimii/cdr-pipeline)

2. **Clone your forked repository**:

   ```bash
   git clone https://github.com/pedramkarimii/cdr-pipeline.git
   ```
3. **Navigate to the Project Directory**:

   ```bash
   cd cdr-pipeline
   ```
4. **Create a new branch for your changes**:

   ```bash
   git checkout -b my-feature-branch
   ```
5. **Make your changes and commit them**:

   ```bash
   git add .
   git commit -m "Description of your changes"
   ```
6. **Push your changes to your fork**:

   ```bash
   git push origin master
   ```

#### 7. Create a pull request on GitHub:

Go to your forked repository on GitHub and click the "New pull request" button. Follow the prompts to create a pull
request from your fork and branch to the original repository.

### Author

#### This project is developed and maintained by Pedram Karimi.

### License

This project is licensed under the MIT License - see the LICENSE file for details.
