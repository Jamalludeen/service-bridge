# Service Module Documentation

## Overview

The **ServiceBridge Service Module** manages the services offered by professionals. It allows professionals to create, update, and manage their service listings, while customers and guests can browse and search available services.

Key Features:

- **Service Catalog**: Professionals create detailed service listings with pricing and descriptions.
- **Category-Based Organization**: Services are organized by categories (e.g., Plumbing, Electrical, Carpentry).
- **Flexible Pricing Models**: Supports `HOURLY`, `DAILY`, `FIXED`, and `PER_UNIT` pricing.
- **Image Support**: Service images with automatic upload path organization.
- **Advanced Filtering**: Search, filter by category, pricing type, and price range.
- **Activation Controls**: Professionals and admins can activate/disable services.

## Base URL

`/available-services/`

## Authentication

- **Public Endpoints**: `list`, `retrieve` (read-only access for unauthenticated users).
- **Protected Endpoints**: `create`, `update`, `delete`, `active`, `disable` require Token Authentication.

Headers: `Authorization: Token <your_token>`

## Service Model

### Fields

| Field            | Type         | Description                                           |
| :--------------- | :----------- | :---------------------------------------------------- |
| `id`             | Integer      | Auto-generated primary key                            |
| `professional`   | ForeignKey   | Reference to the Professional who offers this service |
| `category`       | ForeignKey   | Service category (e.g., Plumbing, Electrical)         |
| `title`          | String (255) | Service title                                         |
| `description`    | TextField    | Detailed service description                          |
| `image`          | ImageField   | Service image (jpg, jpeg, png) - Optional             |
| `pricing_type`   | String       | One of: `HOURLY`, `DAILY`, `FIXED`, `PER_UNIT`        |
| `price_per_unit` | Decimal      | Price amount (10 digits, 2 decimal places)            |
| `is_active`      | Boolean      | Whether service is active and visible (default: True) |
| `created_at`     | DateTime     | Auto-generated creation timestamp                     |

### Pricing Types

| Type       | Description           |
| :--------- | :-------------------- |
| `HOURLY`   | Charged per hour      |
| `DAILY`    | Charged per day       |
| `FIXED`    | One-time fixed price  |
| `PER_UNIT` | Charged per unit/item |

## API Endpoints

### 1. List Services

**GET** `/available-services/`

**Permissions**: Public (AllowAny)

**Query Parameters**:
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `category` | Integer | Filter by category ID |
| `pricing_type` | String | Filter by pricing type (HOURLY, DAILY, etc.) |
| `price_per_unit__lt` | Decimal | Price less than |
| `price_per_unit__gt` | Decimal | Price greater than |
| `search` | String | Search in title and category name |
| `ordering` | String | Order by: title, category\_\_name, price_per_unit |

**User-Specific Behavior**:

- **Unauthenticated/Customer**: See only `is_active=True` services
- **Professional**: See only their own services
- **Admin**: See all services

**Example Request**:

```bash
GET /available-services/?category=3&price_per_unit__lt=1000&search=plumbing
```

**Response (200 OK)**:

```json
[
  {
    "id": 5,
    "professional": {
      "user": 12,
      "username": "john_plumber",
      "first_name": "John",
      "last_name": "Smith"
    },
    "category": 3,
    "category_name": "Plumbing",
    "title": "Emergency Pipe Repair",
    "description": "24/7 emergency plumbing services...",
    "image": "/media/service_images/john_plumber/pipe_repair.jpg",
    "pricing_type": "HOURLY",
    "price_per_unit": "750.00",
    "is_active": true
  }
]
```

---

### 2. Retrieve Service Detail

**GET** `/available-services/{id}/`

**Permissions**: Public (AllowAny)

**Response (200 OK)**:

```json
{
  "id": 5,
  "professional": {
    "user": 12,
    "username": "john_plumber",
    "first_name": "John",
    "last_name": "Smith"
  },
  "category": 3,
  "category_name": "Plumbing",
  "title": "Emergency Pipe Repair",
  "description": "Specialized in fixing burst pipes, leaks, and drainage issues. Available 24/7 for emergency calls.",
  "image": "/media/service_images/john_plumber/pipe_repair.jpg",
  "pricing_type": "HOURLY",
  "price_per_unit": "750.00",
  "is_active": true
}
```

---

### 3. Create Service

**POST** `/available-services/`

**Permissions**: Professional Only

**Body Parameters**:
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `category` | Integer | **Yes** | Category ID |
| `title` | String | **Yes** | Service title (max 255 chars) |
| `description` | String | **Yes** | Detailed description |
| `image` | File | No | Service image (jpg, jpeg, png) |
| `pricing_type` | String | **Yes** | One of: HOURLY, DAILY, FIXED, PER_UNIT |
| `price_per_unit` | Decimal | **Yes** | Price amount |

**Example Request**:

```json
{
  "category": 3,
  "title": "Emergency Pipe Repair",
  "description": "24/7 emergency plumbing services for residential and commercial properties.",
  "pricing_type": "HOURLY",
  "price_per_unit": "750.00"
}
```

**Response (201 Created)**:

```json
{
  "id": 5,
  "professional": {
    "user": 12,
    "username": "john_plumber",
    "first_name": "John",
    "last_name": "Smith"
  },
  "category": 3,
  "category_name": "Plumbing",
  "title": "Emergency Pipe Repair",
  "description": "24/7 emergency plumbing services...",
  "image": null,
  "pricing_type": "HOURLY",
  "price_per_unit": "750.00",
  "is_active": true
}
```

**Error Responses**:

- **403 Forbidden** - User is not a professional

  ```json
  {
    "detail": "Only professional users can create services."
  }
  ```

- **400 Bad Request** - Professional profile not found
  ```json
  {
    "detail": "Professional profile not found. Please create your profile first."
  }
  ```

---

### 4. Update Service

**PUT/PATCH** `/available-services/{id}/`

**Permissions**: Professional (owner) or Admin

**Body Parameters**: Same as Create (all fields optional for PATCH)

**Response (200 OK)**: Updated service data

---

### 5. Delete Service

**DELETE** `/available-services/{id}/`

**Permissions**: Professional (owner) or Admin

**Response (204 No Content)**

---

### 6. Activate Service

**POST** `/available-services/{id}/active/`

**Permissions**: Professional (owner) or Admin

Makes an inactive service visible to customers.

**Response (200 OK)**:

```json
{
  "message": "Service activated",
  "data": { ... }
}
```

**If already active**:

```json
{
  "message": "Service is already active",
  "data": { ... }
}
```

---

### 7. Disable Service

**POST** `/available-services/{id}/disable/`

**Permissions**: Professional (owner) or Admin

Hides a service from customers without deleting it.

**Response (200 OK)**:

```json
{
  "message": "Service deactivated",
  "data": { ... }
}
```

**If already disabled**:

```json
{
  "message": "Service is already disabled",
  "data": { ... }
}
```

---

### 8. Search Services (Advanced)

**GET** `/available-services/search/`

**Permissions**: Public (AllowAny)

This endpoint is an extended search compared to `GET /available-services/?search=...`.
It supports keyword search across multiple fields, price/rating filters, optional geo filtering, and custom sorting.

**Query Parameters**:

| Parameter    | Type    | Required | Description                                                       |
| :----------- | :------ | :------: | :---------------------------------------------------------------- |
| `q`          | String  |    No    | Keyword search in `title`, `category.name`, `description`         |
| `category`   | Integer |    No    | Category ID filter                                                |
| `min_price`  | Decimal |    No    | Minimum `price_per_unit`                                          |
| `max_price`  | Decimal |    No    | Maximum `price_per_unit`                                          |
| `min_rating` | Float   |    No    | Minimum professional average rating                               |
| `lat`        | Float   |    No    | User latitude (enables geo filtering)                             |
| `lng`        | Float   |    No    | User longitude (enables geo filtering)                            |
| `radius`     | Float   |    No    | Radius (km). Default: `10`                                        |
| `sort_by`    | String  |    No    | One of: `distance` (default), `rating`, `price_low`, `price_high` |

**Behavior**:

- If `lat` and `lng` are provided, results are filtered to professionals within `radius` km.
- If `lat`/`lng` are present and valid, each result may include:
  - `distance_km`: calculated distance
  - `is_nearby`: `true` if `distance_km <= 5`
- If `lat`/`lng` are missing, no distance fields are added.

**Example Request**:

```bash
GET /available-services/search/?q=plumbing&min_price=200&max_price=1500&min_rating=4&lat=34.528&lng=69.171&radius=10&sort_by=distance
```

**Response (200 OK)**:

```json
{
  "count": 2,
  "filters_applied": {
    "query": "plumbing",
    "category": null,
    "location": "34.528, 69.171",
    "radius_km": 10.0
  },
  "results": [
    {
      "id": 5,
      "title": "Emergency Pipe Repair",
      "category": 3,
      "category_name": "Plumbing",
      "price_per_unit": "750.00",
      "distance_km": 2.31,
      "is_nearby": true
    }
  ]
}
```

**Error Response**:

- **400 Bad Request** (invalid `lat`/`lng`)

```json
{
  "message": "Invalid latitude or longitude"
}
```

---

### 9. Nearby Services

**GET** `/available-services/nearby/`

**Permissions**: Public (AllowAny)

This is a convenience endpoint that delegates to `GET /available-services/search/` with:

- `radius` defaulting to `5`
- `sort_by=distance`

**Query Parameters**:

| Parameter | Type  | Required | Description               |
| :-------- | :---- | :------: | :------------------------ |
| `lat`     | Float | **Yes**  | User latitude             |
| `lng`     | Float | **Yes**  | User longitude            |
| `radius`  | Float |    No    | Radius (km). Default: `5` |

**Example Request**:

```bash
GET /available-services/nearby/?lat=34.528&lng=69.171&radius=5
```

**Error Response**:

- **400 Bad Request** (missing `lat`/`lng`)

```json
{
  "error": "Latitude and longitude are required"
}
```

---

## Permissions

### IsProfessionalOwnerOrIsAdmin

Used for create, update, delete operations.

**Rules**:

- **Unauthenticated/Customer**: Read-only access (GET)
- **Professional**: Full access to own services
- **Admin**: Full access to all services

### IsAdminUserOrProfessionalOwner

Used for activate/disable actions.

**Rules**:

- **Professional**: Can activate/disable own services
- **Admin**: Can activate/disable any service

---

## Serializers

### AdminServiceSerializer

Used when the requesting user is an Admin.

**Fields**:

- `id`, `professional` (ID only), `category`, `category_name`, `title`, `image`, `description`, `pricing_type`, `price_per_unit`, `is_active`

### ProfessionalServiceSerializer

Used for Professionals and other users.

**Fields**:

- `id`, `professional` (nested with username, first_name, last_name), `category`, `category_name`, `title`, `image`, `description`, `pricing_type`, `price_per_unit`, `is_active`

**Read-only**: `professional` (auto-set to current user)

---

## Filtering and Search

### Available Filters (DjangoFilterBackend)

- `category` (exact match): `/available-services/?category=3`
- `pricing_type` (exact match): `/available-services/?pricing_type=HOURLY`
- `price_per_unit__lt` (less than): `/available-services/?price_per_unit__lt=1000`
- `price_per_unit__gt` (greater than): `/available-services/?price_per_unit__gt=500`

### Search (SearchFilter)

Searches in: `title`, `category__name`

Example: `/available-services/?search=plumbing`

**Note**: `search` here is DRF's `SearchFilter` on the list endpoint.
For advanced search (price/rating/geo + distance sorting), use `GET /available-services/search/`.

### Ordering (OrderingFilter)

Available fields: `title`, `category__name`, `price_per_unit`

Example: `/available-services/?ordering=-price_per_unit` (descending)

---

## Image Upload

### Upload Path Structure

```
media/
  service_images/
    {professional_username}/
      {filename}
```

### Allowed Extensions

- jpg, jpeg, png

### Example Path

```
/media/service_images/john_plumber/emergency_repair.jpg
```

---

## Business Logic

### Service Creation Flow

1. User must be authenticated with role `professional`
2. Professional profile must exist (raises error if not)
3. Service is automatically assigned to the authenticated professional
4. Service is created with `is_active=True` by default
5. `created_at` timestamp is auto-generated

### Visibility Rules

| User Role           | Can See                                     |
| :------------------ | :------------------------------------------ |
| **Unauthenticated** | Only `is_active=True` services              |
| **Customer**        | Only `is_active=True` services              |
| **Professional**    | Only their own services (active & inactive) |
| **Admin**           | All services (active & inactive)            |

---

## Diagrams

### Service Data Model

See [Service Model UML](service_model.puml)

### Service Workflow

See [Service Workflow UML](service_workflow.puml)

---

## Related Models

### ServiceCategory

Defined in `professional.models`

**Fields**:

- `id`: Primary key
- `name`: Unique category name (e.g., "Plumbing", "Electrical")

**Example Categories**:

- Plumbing
- Electrical Work
- Carpentry
- Painting
- Cleaning Services
- HVAC Repair

### Professional

Defined in `professional.models`

**Key Fields**:

- `user`: OneToOne with User model
- `services`: ManyToMany with ServiceCategory
- `verification_status`: PENDING, VERIFIED, REJECTED
- `is_active`: Boolean
- `avg_rating`: Float
- `city`: CharField

---

## Usage Examples

### Create a Service (cURL)

```bash
curl -X POST https://api.servicebridge.com/available-services/ \
  -H "Authorization: Token abc123xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 3,
    "title": "Emergency Pipe Repair",
    "description": "24/7 plumbing services",
    "pricing_type": "HOURLY",
    "price_per_unit": "750.00"
  }'
```

### Search and Filter Services (cURL)

```bash
curl -X GET "https://api.servicebridge.com/available-services/?search=plumbing&category=3&price_per_unit__lt=1000&ordering=price_per_unit"
```

### Advanced Search (cURL)

```bash
curl -X GET "https://api.servicebridge.com/available-services/search/?q=plumbing&min_price=200&max_price=1500&min_rating=4&lat=34.528&lng=69.171&radius=10&sort_by=distance"
```

### Nearby Services (cURL)

```bash
curl -X GET "https://api.servicebridge.com/available-services/nearby/?lat=34.528&lng=69.171&radius=5"
```

### Deactivate a Service (cURL)

```bash
curl -X POST https://api.servicebridge.com/available-services/5/disable/ \
  -H "Authorization: Token abc123xyz"
```

---

## Notes

- Services cannot be created without a valid Professional profile
- Deleted services are removed permanently (consider implementing soft delete in future)
- Image uploads are validated for file extensions (jpg, jpeg, png only)
- Service title and description should follow content guidelines
- Price must be a positive decimal value
- Services are ordered by `created_at` (newest first) by default

---

## Future Enhancements

- Add service reviews/ratings
- Implement service availability schedule
- Improve geo search accuracy/performance (e.g., PostGIS + geo indexes)
- Service packages (bundled services)
- Promotional pricing
- Service request history
