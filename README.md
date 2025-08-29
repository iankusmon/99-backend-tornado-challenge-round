# 99 Backend Tech Challenge – Tornado

This repository contains a backend tech challenge submission for 99 Group. The task is to build a **microservices-based system** that stores information about users and property listings. This solution uses **Python 3 and Tornado framework**.

## Architecture Overview

The system comprises three services:

1. **Listing Service** – stores property listings (`listing_service.py`)  
2. **User Service** – stores users (`user_service.py`)  
3. **Public API Layer** – exposes APIs to the public, aggregating user & listing services (`public_api.py`)  

All services are REST-based and communicate via **JSON payloads**.

## Listing Service

### Listing Object

| Field        | Type | Description |
|--------------|------|------------|
| id           | int  | Auto-generated listing ID |
| user_id      | int  | User who created the listing |
| listing_type | str  | `rent` or `sale` |
| price        | int  | Must be > 0 |
| created_at   | int  | Timestamp in microseconds |
| updated_at   | int  | Timestamp in microseconds |

### Endpoints

**Get all listings**

GET /listings




**Query Parameters**

- `page_num` (int, default=1)  
- `page_size` (int, default=10)  
- `user_id` (int, optional)  

**Response**

```json
{
  "result": true,
  "listings": [
    {
      "id": 1,
      "user_id": 1,
      "listing_type": "rent",
      "price": 6000,
      "created_at": 1675820997000000,
      "updated_at": 1675820997000000
    }
  ]
}
Create a listing

bash

POST /listings
Content-Type: application/x-www-form-urlencoded
Parameters

user_id (int, required)

listing_type (str, required, rent or sale)

price (int, required)

Response

json

{
  "result": true,
  "listing": {
    "id": 1,
    "user_id": 1,
    "listing_type": "rent",
    "price": 6000,
    "created_at": 1675820997000000,
    "updated_at": 1675820997000000
  }
}
User Service
User Object
Field	Type	Description
id	int	Auto-generated
name	str	Full name
created_at	int	Timestamp
updated_at	int	Timestamp

Endpoints
Get all users

bash

GET /users?page_num=1&page_size=10
Get specific user

bash

GET /users/{id}
Create user

bash

POST /users
Content-Type: application/x-www-form-urlencoded
Parameters

name (str, required)

Public API Layer
Aggregates data from Listing and User services.

Endpoints
Get listings

vbnet

GET /public-api/listings
Query Parameters

page_num (int, default=1)

page_size (int, default=10)

user_id (optional)

Response

json

{
  "result": true,
  "listings": [
    {
      "id": 1,
      "listing_type": "rent",
      "price": 6000,
      "created_at": 1675820997000000,
      "updated_at": 1675820997000000,
      "user": {
        "id": 1,
        "name": "Suresh Subramaniam",
        "created_at": 1675820997000000,
        "updated_at": 1675820997000000
      }
    }
  ]
}
Create user

pgsql

POST /public-api/users
Content-Type: application/json
Body

json

{
  "name": "Lorel Ipsum"
}
Create listing

pgsql

POST /public-api/listings
Content-Type: application/json
Body

json

{
  "user_id": 1,
  "listing_type": "rent",
  "price": 6000
}
Testing with CURL
Create a user

bash

curl -X POST http://localhost:8000/public-api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
Create a listing

bash

curl -X POST http://localhost:8000/public-api/listings \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "listing_type": "rent", "price": 4500}'
Get listings

bash

curl "http://localhost:8000/public-api/listings?page_num=1&page_size=5"
Ping service

bash

curl http://localhost:6000/listings/ping
Running the Services
1. Install dependencies

bash

pip install -r python-libs.txt
2. Run Listing Service

bash

python listing_service.py --port=6000 --debug=true
3. Run User Service

bash

python user_service.py --port=7000 --debug=true
4. Run Public API Layer

bash

python public_api.py --port=8000 --debug=true
Submission Repository
https://github.com/iankusmon/99-backend-tornado-challenge-round
