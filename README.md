# Django API Limiter

A Django API rate limiting system using token bucket algorithm with Redis as the backend.

## Overview

Django API Limiter is a Django REST Framework project that demonstrates how to implement a token bucket algorithm for API rate limiting. It includes:

- Unlimited API endpoint with no rate limiting
- Limited API endpoint with token bucket rate limiting
- Periodic tasks using Celery to refill token buckets
- Redis for storing and managing rate limit tokens

## Features

- **Token Bucket Algorithm**: Each client gets a bucket of tokens that are consumed with each request
- **IP-Based Limiting**: Rate limits are applied per client IP address
- **Automatic Refill**: Celery worker automatically refills tokens over time
- **Scheduled Tasks**: Celery Beat scheduler ensures regular token refills at consistent intervals
- **Redis Backend**: Fast, in-memory data store for token management
- **Custom Configuration**: Configurable bucket size and expiry time

## Requirements

- Python 3.8+
- Django 5.1+
- Django REST Framework
- Redis
- Celery

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Oyshik-ICT/django-api-limiter.git

   cd django-api-limiter
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` inside the traffic_shield folder with the following settings (or modify the existing one):
   ```
   MAX_SIZE=10
   RATE_LIMITED_EXPIRY=3600
   ```
   
## Configuration

The token bucket algorithm can be configured through environment variables:

- `MAX_SIZE`: Maximum number of tokens in a bucket (default: 10)
- `RATE_LIMITED_EXPIRY`: Time in seconds before a client's bucket expires (default: 3600)

## Running the Application

### 1. Start Redis server

Make sure Redis is installed and running on your system:

```bash
# On most Linux systems
sudo service redis-server start

# On macOS with Homebrew
brew services start redis

# On Windows, start the Redis server executable
```

### 2. Run Django development server

```bash
python manage.py migrate
python manage.py runserver
```

### 3. Start Celery worker

```bash
celery -A traffic_shield.celery worker --pool=solo -l info
```

### 4. Start Celery beat (scheduler)

```bash
celery -A traffic_shield beat -l INFO
```

## API Endpoints

- **Unlimited API**: `/unlimited/` - No rate limiting applied
- **Limited API**: `/limited/` - Rate limited using token bucket algorithm

## How It Works

1. Each client is identified by their IP address
2. When a client makes their first request, a new token bucket is created with half the maximum capacity
3. Each request to the limited endpoint consumes one token
4. The Celery beat scheduler runs a task every second to refill tokens (one at a time) up to the maximum capacity
5. If a client's bucket is empty (0 tokens), they receive a 429 "Too Many Requests" response
6. Client buckets expire after the configured time period (default: 1 hour)



### Redis Integration

Redis is used to store:
- Client IP addresses as keys
- Number of available tokens as values
- Time-to-live for each bucket based on the expiry setting
