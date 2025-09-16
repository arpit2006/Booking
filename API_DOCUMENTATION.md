# BookingMVP API Documentation

## Overview

The BookingMVP API provides comprehensive endpoints for hotel booking operations, user management, and administrative functions. The API follows REST conventions and supports both JSON and browsable HTML formats.

## Base URL

- Development: `http://localhost:8000/api/`
- Production: `https://yourdomain.com/api/`

## Authentication

The API supports multiple authentication methods:

### 1. Token Authentication
```http
Authorization: Token your_token_here
```

### 2. Session Authentication
Use Django's built-in session authentication for web applications.

### Getting an API Token

**Endpoint:** `POST /api-auth/token/`

**Request:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "token": "your_api_token_here"
}
```

## Rate Limiting

API endpoints are rate-limited to ensure fair usage:

- **Anonymous users**: 100 requests/hour
- **Authenticated users**: 1000 requests/hour
- **Login endpoint**: 5 requests/minute
- **Booking endpoint**: 10 requests/minute

## Response Format

All API responses follow a consistent format:

**Success Response:**
```json
{
    "data": { ... },
    "message": "Success message",
    "status": "success"
}
```

**Error Response:**
```json
{
    "error": "Error description",
    "message": "Detailed error message",
    "status": "error"
}
```

**Paginated Response:**
```json
{
    "count": 150,
    "next": "http://api.example.org/accounts/?page=4",
    "previous": "http://api.example.org/accounts/?page=2",
    "results": [ ... ]
}
```

## Endpoints

### Hotels

#### List Hotels
**GET** `/api/hotels/`

List all active hotels with filtering and pagination.

**Query Parameters:**
- `city` (integer): Filter by city ID
- `star_rating` (integer): Filter by star rating (1-5)
- `star_rating__gte` (integer): Minimum star rating
- `star_rating__lte` (integer): Maximum star rating
- `price_per_night__gte` (decimal): Minimum price per night
- `price_per_night__lte` (decimal): Maximum price per night
- `guest_rating__gte` (decimal): Minimum guest rating
- `is_featured` (boolean): Filter featured hotels
- `search` (string): Search in name, description, address, city
- `ordering` (string): Sort by fields (name, price_per_night, guest_rating, star_rating)

**Example Request:**
```http
GET /api/hotels/?city=1&star_rating__gte=4&price_per_night__lte=200&ordering=price_per_night
```

**Response:**
```json
{
    "count": 25,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Grand Hotel",
            "slug": "grand-hotel",
            "city": {
                "id": 1,
                "name": "New York",
                "country": "USA",
                "is_popular": true
            },
            "address": "123 Main Street",
            "description": "Luxury hotel in the heart of the city",
            "price_per_night": "150.00",
            "star_rating": 5,
            "guest_rating": "4.5",
            "is_featured": true,
            "featured_image": "/media/hotels/hotel1.jpg",
            "amenities": [
                {
                    "id": 1,
                    "name": "Free WiFi",
                    "icon": "wifi",
                    "category": "connectivity"
                }
            ],
            "average_rating": 4.5,
            "review_count": 50
        }
    ]
}
```

#### Get Hotel Details
**GET** `/api/hotels/{id}/`

Get detailed information about a specific hotel.

**Response:**
```json
{
    "id": 1,
    "name": "Grand Hotel",
    "slug": "grand-hotel",
    "city": {
        "id": 1,
        "name": "New York",
        "country": "USA",
        "is_popular": true
    },
    "address": "123 Main Street",
    "description": "Luxury hotel in the heart of the city",
    "price_per_night": "150.00",
    "star_rating": 5,
    "guest_rating": "4.5",
    "is_featured": true,
    "featured_image": "/media/hotels/hotel1.jpg",
    "amenities": [...],
    "phone": "+1-555-123-4567",
    "email": "info@grandhotel.com",
    "website": "https://grandhotel.com",
    "check_in_time": "15:00:00",
    "check_out_time": "11:00:00",
    "cancellation_policy": "Free cancellation until 24 hours before check-in",
    "average_rating": 4.5,
    "review_count": 50,
    "images": [],
    "latitude": "40.7128",
    "longitude": "-74.0060"
}
```

#### Get Featured Hotels
**GET** `/api/hotels/featured/`

Get a list of featured hotels (limited to 6).

#### Advanced Hotel Search
**GET** `/api/hotels/search/`

Perform advanced hotel search with custom parameters.

**Query Parameters:**
- `location` (string): Search by location name
- `check_in` (date): Check-in date (YYYY-MM-DD)
- `check_out` (date): Check-out date (YYYY-MM-DD)
- `guests` (integer): Number of guests

**Example:**
```http
GET /api/hotels/search/?location=New York&check_in=2024-01-15&check_out=2024-01-20&guests=2
```

### Bookings

#### List User Bookings
**GET** `/api/bookings/`

**Authentication Required:** Yes

List all bookings for the authenticated user. Staff users can see all bookings.

**Query Parameters:**
- `status` (string): Filter by booking status (confirmed, pending, cancelled, completed)
- `check_in__gte` (date): Bookings from this check-in date
- `check_in__lte` (date): Bookings until this check-in date
- `check_out__gte` (date): Bookings from this check-out date
- `check_out__lte` (date): Bookings until this check-out date
- `created_at__gte` (datetime): Bookings created after this date
- `created_at__lte` (datetime): Bookings created before this date
- `ordering` (string): Sort by fields (created_at, check_in, check_out, total_amount)

**Response:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "booking_id": "BK123456",
            "hotel": {
                "id": 1,
                "name": "Grand Hotel",
                "slug": "grand-hotel",
                "city": {...},
                "address": "123 Main Street",
                "featured_image": "/media/hotels/hotel1.jpg",
                "price_per_night": "150.00",
                "star_rating": 5
            },
            "user": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "check_in": "2024-01-15",
            "check_out": "2024-01-20",
            "guests": 2,
            "total_amount": "750.00",
            "status": "confirmed",
            "created_at": "2024-01-10T10:30:00Z",
            "nights": 5
        }
    ]
}
```

#### Create Booking
**POST** `/api/bookings/`

**Authentication Required:** Yes

Create a new hotel booking.

**Request:**
```json
{
    "hotel": 1,
    "check_in": "2024-01-15",
    "check_out": "2024-01-20",
    "guests": 2
}
```

**Response:**
```json
{
    "id": 1,
    "booking_id": "BK123456",
    "hotel": 1,
    "check_in": "2024-01-15",
    "check_out": "2024-01-20",
    "guests": 2,
    "nights": 5
}
```

**Validation Errors:**
```json
{
    "check_out": ["Check-out date must be after check-in date."],
    "guests": ["Number of guests must be greater than 0."],
    "check_in": ["Check-in date cannot be in the past."]
}
```

#### Get Booking Details
**GET** `/api/bookings/{id}/`

**Authentication Required:** Yes

Get detailed information about a specific booking.

#### Cancel Booking
**POST** `/api/bookings/{id}/cancel/`

**Authentication Required:** Yes

Cancel a specific booking.

**Response:**
```json
{
    "id": 1,
    "booking_id": "BK123456",
    "status": "cancelled",
    "message": "Booking cancelled successfully"
}
```

**Error Response:**
```json
{
    "error": "Booking is already cancelled"
}
```

#### Get Upcoming Bookings
**GET** `/api/bookings/upcoming/`

**Authentication Required:** Yes

Get upcoming bookings for the authenticated user.

#### Get Booking History
**GET** `/api/bookings/history/`

**Authentication Required:** Yes

Get past bookings for the authenticated user.

### Cities

#### List Cities
**GET** `/api/cities/`

List all cities in the system.

**Query Parameters:**
- `country` (string): Filter by country name
- `is_popular` (boolean): Filter popular cities
- `search` (string): Search in name and country
- `ordering` (string): Sort by name or country

**Response:**
```json
{
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "New York",
            "country": "USA",
            "is_popular": true
        }
    ]
}
```

#### Get City Details
**GET** `/api/cities/{id}/`

Get details about a specific city.

### Amenities

#### List Amenities
**GET** `/api/amenities/`

List all hotel amenities.

**Query Parameters:**
- `category` (string): Filter by amenity category
- `search` (string): Search in amenity name

**Response:**
```json
{
    "count": 20,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Free WiFi",
            "icon": "wifi",
            "category": "connectivity"
        }
    ]
}
```

## Error Codes

| HTTP Status | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

## Common Error Responses

### Authentication Required
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Permission Denied
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### Rate Limit Exceeded
```json
{
    "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### Validation Error
```json
{
    "field_name": [
        "This field is required."
    ],
    "non_field_errors": [
        "Custom validation error message."
    ]
}
```

## Examples

### Python with requests

```python
import requests

# Get API token
response = requests.post('http://localhost:8000/api-auth/token/', {
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['token']

# Use token for authenticated requests
headers = {'Authorization': f'Token {token}'}

# Search hotels
hotels = requests.get(
    'http://localhost:8000/api/hotels/search/',
    params={
        'location': 'New York',
        'check_in': '2024-01-15',
        'check_out': '2024-01-20',
        'guests': 2
    },
    headers=headers
)

# Create booking
booking = requests.post(
    'http://localhost:8000/api/bookings/',
    json={
        'hotel': 1,
        'check_in': '2024-01-15',
        'check_out': '2024-01-20',
        'guests': 2
    },
    headers=headers
)
```

### JavaScript with fetch

```javascript
// Get API token
const tokenResponse = await fetch('http://localhost:8000/api-auth/token/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});
const { token } = await tokenResponse.json();

// Use token for authenticated requests
const headers = {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
};

// Search hotels
const hotelsResponse = await fetch(
    'http://localhost:8000/api/hotels/search/?location=New York&check_in=2024-01-15&check_out=2024-01-20&guests=2',
    { headers }
);
const hotels = await hotelsResponse.json();

// Create booking
const bookingResponse = await fetch('http://localhost:8000/api/bookings/', {
    method: 'POST',
    headers,
    body: JSON.stringify({
        hotel: 1,
        check_in: '2024-01-15',
        check_out: '2024-01-20',
        guests: 2
    })
});
const booking = await bookingResponse.json();
```

### cURL Examples

```bash
# Get API token
curl -X POST http://localhost:8000/api-auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Search hotels
curl -X GET "http://localhost:8000/api/hotels/search/?location=New York&check_in=2024-01-15&check_out=2024-01-20&guests=2" \
  -H "Authorization: Token your_token_here"

# Create booking
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Token your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"hotel": 1, "check_in": "2024-01-15", "check_out": "2024-01-20", "guests": 2}'
```

## API Browser

The API includes a browsable interface for development and testing:

- **Development**: http://localhost:8000/api/
- **Production**: https://yourdomain.com/api/

The browsable API allows you to:
- Explore available endpoints
- Test API calls interactively
- View response formats
- Understand request/response schemas

## Webhooks (Future Feature)

Planned webhook support for:
- Booking confirmations
- Booking cancellations
- Payment updates
- Hotel availability changes

## SDK and Libraries

Official SDKs planned for:
- Python
- JavaScript/Node.js
- PHP
- Ruby

## Support

For API support and questions:
- Email: api-support@bookingmvp.com
- Documentation: Check the main README.md
- Issues: Create GitHub issues for bugs

---

**BookingMVP API** - Powering modern hotel booking experiences! 🏨🚀