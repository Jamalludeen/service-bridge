# ML App — API Reference

All endpoints are prefixed with `/api/ml/` and require **Token Authentication**.

```
Authorization: Token <user_token>
```

---

## Table of Contents

- [Customer Recommendations](#customer-recommendations)
  - [GET /recommendations/services/](#get-recommendationsservices)
  - [GET /recommendations/professionals/](#get-recommendationsprofessionals)
  - [GET /recommendations/categories/](#get-recommendationscategories)
  - [GET /recommendations/services/:service_id/similar/](#get-recommendationsservicesservice_idsimilar)
- [Professional Recommendations](#professional-recommendations)
  - [GET /professional/suggested-categories/](#get-professionalsuggested-categories)
  - [GET /professional/pricing-suggestion/:service_id/](#get-professionalpricing-suggestionservice_id)
- [Predictive Analytics](#predictive-analytics)
  - [GET /analytics/cancellation-risk/:booking_id/](#get-analyticscancellation-riskbooking_id)
  - [GET /analytics/demand-forecast/](#get-analyticsdemand-forecast)
  - [GET /analytics/peak-hours/](#get-analyticspeak-hours)

---

## Customer Recommendations

> All customer recommendation endpoints require the authenticated user to have `role == "customer"` and a linked `CustomerProfile`.

---

### GET /recommendations/services/

Get personalized service recommendations for the authenticated customer.

**URL:** `/api/ml/recommendations/services/`  
**Method:** `GET`  
**Auth:** Token (Customer only)  
**URL Name:** `recommended-services`

#### Query Parameters

| Parameter | Type | Default | Description                                 |
| --------- | ---- | ------- | ------------------------------------------- |
| `limit`   | int  | `10`    | Maximum number of recommendations to return |

#### Success Response — `200 OK`

```json
{
  "count": 3,
  "recommendations": [
    {
      "id": 12,
      "title": "Deep House Cleaning",
      "description": "Professional deep cleaning service for homes.",
      "price_per_unit": "150.00",
      "pricing_type": "FIXED",
      "category_name": "Cleaning",
      "professional_name": "Ahmad Karimi",
      "professional_rating": 4.8
    }
  ]
}
```

#### Response Fields

| Field                 | Type    | Description                            |
| --------------------- | ------- | -------------------------------------- |
| `id`                  | int     | Service ID                             |
| `title`               | string  | Service title                          |
| `description`         | string  | Service description                    |
| `price_per_unit`      | decimal | Price per unit                         |
| `pricing_type`        | string  | Pricing model (e.g. `FIXED`, `HOURLY`) |
| `category_name`       | string  | Service category name                  |
| `professional_name`   | string  | Full name or email of the professional |
| `professional_rating` | float   | Professional's average rating          |

#### Error Responses

| Status | Body                                                      | Condition                   |
| ------ | --------------------------------------------------------- | --------------------------- |
| `403`  | `{"error": "Only customers can access recommendations."}` | User is not a customer      |
| `404`  | `{"error": "Customer profile not found."}`                | No `CustomerProfile` linked |

---

### GET /recommendations/professionals/

Get recommended professionals for the authenticated customer.

**URL:** `/api/ml/recommendations/professionals/`  
**Method:** `GET`  
**Auth:** Token (Customer only)  
**URL Name:** `recommended-professionals`

#### Query Parameters

| Parameter     | Type | Default | Description                              |
| ------------- | ---- | ------- | ---------------------------------------- |
| `category_id` | int  | —       | Filter professionals by service category |
| `limit`       | int  | `10`    | Maximum number of results                |

#### Success Response — `200 OK`

```json
{
  "count": 2,
  "recommendations": [
    {
      "id": 5,
      "name": "Sara Mohammadi",
      "bio": "10 years of experience in home services.",
      "avg_rating": 4.9,
      "total_reviews": 42,
      "years_of_experience": 10,
      "city": "Kabul",
      "categories": ["Cleaning", "Plumbing"]
    }
  ]
}
```

#### Response Fields

| Field                 | Type         | Description                                    |
| --------------------- | ------------ | ---------------------------------------------- |
| `id`                  | int          | Professional ID                                |
| `name`                | string       | Full name or email                             |
| `bio`                 | string       | Professional's biography                       |
| `avg_rating`          | float        | Average review rating                          |
| `total_reviews`       | int          | Total number of reviews                        |
| `years_of_experience` | int          | Years of professional experience               |
| `city`                | string       | City of the professional                       |
| `categories`          | list[string] | Service category names the professional offers |

#### Error Responses

| Status | Body                                                      | Condition                   |
| ------ | --------------------------------------------------------- | --------------------------- |
| `403`  | `{"error": "Only customers can access recommendations."}` | User is not a customer      |
| `404`  | `{"error": "Customer profile not found."}`                | No `CustomerProfile` linked |

---

### GET /recommendations/categories/

Get recommended service categories for the customer.

**URL:** `/api/ml/recommendations/categories/`  
**Method:** `GET`  
**Auth:** Token (Customer only)  
**URL Name:** `recommended-categories`

#### Query Parameters

| Parameter | Type | Default | Description                                |
| --------- | ---- | ------- | ------------------------------------------ |
| `limit`   | int  | `5`     | Maximum number of category recommendations |

#### Success Response — `200 OK`

```json
{
  "count": 2,
  "recommendations": [
    {
      "id": 3,
      "name": "Electrical"
    },
    {
      "id": 7,
      "name": "Landscaping"
    }
  ]
}
```

#### Response Fields

| Field  | Type   | Description   |
| ------ | ------ | ------------- |
| `id`   | int    | Category ID   |
| `name` | string | Category name |

#### Error Responses

| Status | Body                                                      | Condition                   |
| ------ | --------------------------------------------------------- | --------------------------- |
| `403`  | `{"error": "Only customers can access recommendations."}` | User is not a customer      |
| `404`  | `{"error": "Customer profile not found."}`                | No `CustomerProfile` linked |

---

### GET /recommendations/services/:service_id/similar/

Get services similar to a given service ("You may also like").

**URL:** `/api/ml/recommendations/services/<int:service_id>/similar/`  
**Method:** `GET`  
**Auth:** Token (requires `CustomerProfile`)  
**URL Name:** `similar-services`

#### URL Parameters

| Parameter    | Type | Description                 |
| ------------ | ---- | --------------------------- |
| `service_id` | int  | ID of the reference service |

#### Query Parameters

| Parameter | Type | Default | Description                        |
| --------- | ---- | ------- | ---------------------------------- |
| `limit`   | int  | `5`     | Maximum number of similar services |

#### Success Response — `200 OK`

```json
{
  "count": 3,
  "similar_services": [
    {
      "id": 15,
      "title": "Standard House Cleaning",
      "description": "Basic cleaning service.",
      "price_per_unit": "100.00",
      "pricing_type": "FIXED",
      "category_name": "Cleaning",
      "professional_name": "Ali Rezaei",
      "professional_rating": 4.5
    }
  ]
}
```

#### Error Responses

| Status | Body                                       | Condition                   |
| ------ | ------------------------------------------ | --------------------------- |
| `404`  | `{"error": "Customer profile not found."}` | No `CustomerProfile` linked |

---

## Professional Recommendations

> These endpoints require the authenticated user to have `role == "professional"` and a linked `Professional` profile.

---

### GET /professional/suggested-categories/

Get suggested service categories the professional could add to expand their offerings.

**URL:** `/api/ml/professional/suggested-categories/`  
**Method:** `GET`  
**Auth:** Token (Professional only)  
**URL Name:** `suggested-categories`

#### Success Response — `200 OK`

```json
{
  "suggestions": [
    {
      "id": 4,
      "name": "Painting"
    },
    {
      "id": 9,
      "name": "Carpentry"
    }
  ]
}
```

#### Error Responses

| Status | Body                                               | Condition                        |
| ------ | -------------------------------------------------- | -------------------------------- |
| `403`  | `{"error": "Only professionals can access this."}` | User is not a professional       |
| `404`  | `{"error": "Professional profile not found."}`     | No `Professional` profile linked |

---

### GET /professional/pricing-suggestion/:service_id/

Get an optimal pricing suggestion for a specific service based on market data.

**URL:** `/api/ml/professional/pricing-suggestion/<int:service_id>/`  
**Method:** `GET`  
**Auth:** Token (Professional only)  
**URL Name:** `pricing-suggestion`

#### URL Parameters

| Parameter    | Type | Description                               |
| ------------ | ---- | ----------------------------------------- |
| `service_id` | int  | ID of the professional's service to price |

#### Success Response — `200 OK`

```json
{
  "current_price": 120.0,
  "market_average": 135.5,
  "suggested_price": 142.28,
  "min_market": 80.0,
  "max_market": 200.0
}
```

#### Response Fields

| Field             | Type  | Description                                            |
| ----------------- | ----- | ------------------------------------------------------ |
| `current_price`   | float | The service's current price                            |
| `market_average`  | float | Average price of similar services in the same category |
| `suggested_price` | float | Recommended price adjusted for rating and experience   |
| `min_market`      | float | Lowest price among comparable services                 |
| `max_market`      | float | Highest price among comparable services                |

#### Error Responses

| Status | Body                                                          | Condition                                                    |
| ------ | ------------------------------------------------------------- | ------------------------------------------------------------ |
| `400`  | `{"error": "Not enough market data for pricing suggestion."}` | No comparable services exist                                 |
| `403`  | `{"error": "Only professionals can access this."}`            | User is not a professional                                   |
| `404`  | `{"error": "Service not found."}`                             | Service doesn't exist or doesn't belong to this professional |

---

## Predictive Analytics

---

### GET /analytics/cancellation-risk/:booking_id/

Get a cancellation risk prediction for a specific booking.

**URL:** `/api/ml/analytics/cancellation-risk/<int:booking_id>/`  
**Method:** `GET`  
**Auth:** Token (Customer who owns the booking **or** assigned Professional)  
**URL Name:** `cancellation-risk`

#### URL Parameters

| Parameter    | Type | Description                 |
| ------------ | ---- | --------------------------- |
| `booking_id` | int  | ID of the booking to assess |

#### Success Response — `200 OK`

```json
{
  "risk_score": 0.325,
  "risk_level": "MODERATE",
  "factors": {
    "customer_history": 0.15,
    "professional_history": 0.1,
    "lead_time": 0.2,
    "price_deviation": 0.1,
    "first_time": 0.3,
    "category_rate": 0.12
  }
}
```

#### Response Fields

| Field        | Type   | Description                                                  |
| ------------ | ------ | ------------------------------------------------------------ |
| `risk_score` | float  | Composite risk score (0.0 – 1.0)                             |
| `risk_level` | string | Human-readable level: `LOW`, `MODERATE`, `HIGH`, `VERY_HIGH` |
| `factors`    | object | Breakdown of individual risk factor scores                   |

**Risk Level Mapping:**

| Score     | Level       |
| --------- | ----------- |
| < 0.2     | `LOW`       |
| 0.2 – 0.4 | `MODERATE`  |
| 0.4 – 0.6 | `HIGH`      |
| ≥ 0.6     | `VERY_HIGH` |

#### Error Responses

| Status | Body                              | Condition                                               |
| ------ | --------------------------------- | ------------------------------------------------------- |
| `403`  | `{"error": "Access denied."}`     | User is neither the booking's customer nor professional |
| `404`  | `{"error": "Booking not found."}` | Booking ID does not exist                               |

---

### GET /analytics/demand-forecast/

Forecast service demand for upcoming days.

**URL:** `/api/ml/analytics/demand-forecast/`  
**Method:** `GET`  
**Auth:** Token  
**URL Name:** `demand-forecast`

#### Query Parameters

| Parameter     | Type   | Default | Description                                              |
| ------------- | ------ | ------- | -------------------------------------------------------- |
| `category_id` | int    | —       | Filter forecast by service category                      |
| `city`        | string | —       | Filter forecast by city (case-insensitive partial match) |
| `days`        | int    | `7`     | Number of days to forecast                               |

#### Success Response — `200 OK`

```json
{
  "category_id": "1",
  "city": "Kabul",
  "forecasts": [
    {
      "date": "2026-02-15",
      "day_of_week": "Sunday",
      "predicted_bookings": 12.3,
      "confidence": "MEDIUM",
      "trend": "INCREASING"
    },
    {
      "date": "2026-02-16",
      "day_of_week": "Monday",
      "predicted_bookings": 8.7,
      "confidence": "HIGH",
      "trend": "STABLE"
    }
  ]
}
```

#### Response Fields

| Field                            | Type          | Description                             |
| -------------------------------- | ------------- | --------------------------------------- |
| `category_id`                    | string / null | Echoed filter                           |
| `city`                           | string / null | Echoed filter                           |
| `forecasts[].date`               | string        | ISO date (`YYYY-MM-DD`)                 |
| `forecasts[].day_of_week`        | string        | Day name (e.g. `Monday`)                |
| `forecasts[].predicted_bookings` | float         | Predicted number of bookings            |
| `forecasts[].confidence`         | string        | `LOW`, `MEDIUM`, or `HIGH`              |
| `forecasts[].trend`              | string        | `INCREASING`, `DECREASING`, or `STABLE` |

---

### GET /analytics/peak-hours/

Identify peak booking hours from the last 90 days.

**URL:** `/api/ml/analytics/peak-hours/`  
**Method:** `GET`  
**Auth:** Token  
**URL Name:** `peak-hours`

#### Query Parameters

| Parameter     | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `category_id` | int    | —       | Filter by service category                      |
| `city`        | string | —       | Filter by city (case-insensitive partial match) |

#### Success Response — `200 OK`

```json
{
  "category_id": null,
  "city": null,
  "peak_hours": [
    {
      "hour": 10,
      "time_range": "10:00 - 11:00",
      "bookings": 87,
      "intensity": 1.0
    },
    {
      "hour": 14,
      "time_range": "14:00 - 15:00",
      "bookings": 65,
      "intensity": 0.75
    },
    {
      "hour": 9,
      "time_range": "09:00 - 10:00",
      "bookings": 52,
      "intensity": 0.6
    }
  ]
}
```

#### Response Fields

| Field                     | Type          | Description                                     |
| ------------------------- | ------------- | ----------------------------------------------- |
| `category_id`             | string / null | Echoed filter                                   |
| `city`                    | string / null | Echoed filter                                   |
| `peak_hours[].hour`       | int           | Hour of day (0–23)                              |
| `peak_hours[].time_range` | string        | Human-readable time range                       |
| `peak_hours[].bookings`   | int           | Total bookings in that hour (last 90 days)      |
| `peak_hours[].intensity`  | float         | Normalized intensity (0.0 – 1.0, 1.0 = busiest) |

---

## URL Summary

| Method | URL                                              | View                                     | Description                          |
| ------ | ------------------------------------------------ | ---------------------------------------- | ------------------------------------ |
| GET    | `/api/ml/recommendations/services/`              | `RecommendedServicesView`                | Personalized service recommendations |
| GET    | `/api/ml/recommendations/professionals/`         | `RecommendedProfessionalsView`           | Professional recommendations         |
| GET    | `/api/ml/recommendations/categories/`            | `RecommendedCategoriesView`              | Category recommendations             |
| GET    | `/api/ml/recommendations/services/<id>/similar/` | `SimilarServicesView`                    | Similar services                     |
| GET    | `/api/ml/professional/suggested-categories/`     | `SuggestedCategoriesForProfessionalView` | Category suggestions for pros        |
| GET    | `/api/ml/professional/pricing-suggestion/<id>/`  | `PricingSuggestionView`                  | Optimal pricing suggestion           |
| GET    | `/api/ml/analytics/cancellation-risk/<id>/`      | `CancellationRiskView`                   | Cancellation risk prediction         |
| GET    | `/api/ml/analytics/demand-forecast/`             | `DemandForecastView`                     | Demand forecasting                   |
| GET    | `/api/ml/analytics/peak-hours/`                  | `PeakHoursView`                          | Peak booking hours                   |

---

## Common Error Responses

| Status Code        | Meaning                                 |
| ------------------ | --------------------------------------- |
| `400 Bad Request`  | Invalid parameters or insufficient data |
| `401 Unauthorized` | Missing or invalid token                |
| `403 Forbidden`    | Role-based access denied                |
| `404 Not Found`    | Resource not found                      |

All error responses follow the format:

```json
{
  "error": "Human-readable error message."
}
```
