# ML App — Documentation

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Data Models](#data-models)
- [Recommendation Engine](#recommendation-engine)
- [Predictive Analytics](#predictive-analytics)
- [UML Diagrams](#uml-diagrams)
- [API Reference](./API.md)

---

## Overview

The **ml** (Machine Learning) app provides intelligent recommendation and predictive analytics capabilities for the ServiceBridge platform. It enhances the user experience by delivering:

- **Personalized service recommendations** for customers using a hybrid multi-strategy approach
- **Professional recommendations** ranked by composite quality scores
- **Similar services** discovery ("You may also like")
- **Category suggestions** for both customers and professionals
- **Optimal pricing suggestions** for professionals based on market data
- **Cancellation risk prediction** for bookings
- **Demand forecasting** and **peak-hour analysis** for operational intelligence

All endpoints require **Token Authentication** and are served under the `/api/ml/` prefix.

---

## Architecture

The app is split into four main layers:

| Layer         | Module                                  | Responsibility                                                                               |
| ------------- | --------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Models**    | `models.py`                             | Persistent storage for interactions, similarity scores, preferences, and recommendation logs |
| **Engines**   | `recommendation_engine.py`              | Business logic for generating recommendations (customer + professional)                      |
| **Analytics** | `predictive_analytics.py`               | Cancellation risk prediction and demand forecasting                                          |
| **API**       | `views.py`, `serializers.py`, `urls.py` | REST endpoints exposed to clients                                                            |

### High-Level Flow

```
Client (HTTP)
    │
    ▼
views.py  ──►  serializers.py (response shaping)
    │
    ▼
recommendation_engine.py   OR   predictive_analytics.py
    │                                    │
    ▼                                    ▼
models.py  ◄──────────────────────  Booking / Service / Professional (cross-app models)
```

---

## Data Models

### `UserInteraction`

Tracks user interactions for collaborative filtering.

| Field              | Type                   | Description                                                                  |
| ------------------ | ---------------------- | ---------------------------------------------------------------------------- |
| `user`             | FK → `User`            | The user who performed the interaction                                       |
| `interaction_type` | `CharField`            | One of: `VIEW`, `SEARCH`, `BOOKMARK`, `BOOK`, `COMPLETE`, `REVIEW`, `CANCEL` |
| `content_type`     | FK → `ContentType`     | Django content type (generic relation)                                       |
| `object_id`        | `PositiveIntegerField` | ID of the related object                                                     |
| `content_object`   | `GenericForeignKey`    | Resolved target object (Service, Professional, etc.)                         |
| `session_id`       | `CharField`            | Browser/app session identifier                                               |
| `metadata`         | `JSONField`            | Arbitrary context data                                                       |
| `created_at`       | `DateTimeField`        | Auto-set on creation                                                         |

**Indexes:** `(user, interaction_type)`, `(content_type, object_id)`, `(created_at)`

---

### `ServiceSimilarity`

Pre-computed pairwise similarity scores between services (0.0 – 1.0).

| Field              | Type            | Description                   |
| ------------------ | --------------- | ----------------------------- |
| `service_a`        | FK → `Service`  | First service                 |
| `service_b`        | FK → `Service`  | Second service                |
| `similarity_score` | `FloatField`    | Similarity value (0.0 to 1.0) |
| `updated_at`       | `DateTimeField` | Last recomputation time       |

**Constraints:** `unique_together = ['service_a', 'service_b']`

---

### `ProfessionalScore`

ML-computed composite quality scores for professionals.

| Field                   | Type                      | Default | Description                            |
| ----------------------- | ------------------------- | ------- | -------------------------------------- |
| `professional`          | OneToOne → `Professional` | —       | Target professional                    |
| `rating_score`          | `FloatField`              | 0.5     | Normalized rating component            |
| `completion_rate_score` | `FloatField`              | 0.5     | Booking completion rate component      |
| `response_time_score`   | `FloatField`              | 0.5     | Response speed component               |
| `experience_score`      | `FloatField`              | 0.5     | Years of experience component          |
| `consistency_score`     | `FloatField`              | 0.5     | Service consistency component          |
| `overall_score`         | `FloatField`              | 0.5     | Final weighted composite               |
| `bookings_analyzed`     | `IntegerField`            | 0       | Number of bookings used in computation |
| `last_computed_at`      | `DateTimeField`           | auto    | Timestamp of last score update         |

---

### `CustomerPreference`

Learned customer preferences derived from booking history.

| Field                    | Type                         | Description                            |
| ------------------------ | ---------------------------- | -------------------------------------- |
| `customer`               | OneToOne → `CustomerProfile` | Target customer                        |
| `preferred_categories`   | `JSONField`                  | List of `{"id": int, "weight": float}` |
| `preferred_price_range`  | `JSONField`                  | `{"min": float, "max": float}`         |
| `preferred_times`        | `JSONField`                  | e.g. `["morning", "afternoon"]`        |
| `preferred_days`         | `JSONField`                  | e.g. `["saturday", "sunday"]`          |
| `avg_booking_value`      | `DecimalField`               | Mean booking price                     |
| `booking_frequency_days` | `FloatField`                 | Average days between bookings          |
| `last_computed_at`       | `DateTimeField`              | auto                                   |

---

### `RecommendationLog`

Audit trail for recommendations — used for A/B testing and model improvement.

| Field                 | Type                       | Description                              |
| --------------------- | -------------------------- | ---------------------------------------- |
| `user`                | FK → `User`                | User who received the recommendations    |
| `recommendation_type` | `CharField`                | Algorithm/strategy identifier            |
| `recommended_items`   | `JSONField`                | List of recommended item IDs             |
| `selected_item_id`    | `IntegerField` (nullable)  | ID the user actually clicked             |
| `algorithm_version`   | `CharField`                | Version string for tracking changes      |
| `context`             | `JSONField`                | Extra metadata (location, filters, etc.) |
| `created_at`          | `DateTimeField`            | When recommendations were served         |
| `clicked_at`          | `DateTimeField` (nullable) | When user clicked a recommendation       |

---

## Recommendation Engine

### `RecommendationEngine` (Customer-facing)

Initialized with a `CustomerProfile` instance.

#### `get_recommended_services(limit=10)`

Returns a **hybrid-ranked** list of `Service` objects. Combines four strategies:

| Strategy                | Weight | Method                                | Description                                                                                                                          |
| ----------------------- | ------ | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Collaborative Filtering | 40%    | `_collaborative_filtering_services()` | "Customers who booked X also booked Y" — finds users with overlapping completed-booking categories and surfaces their other bookings |
| Content-Based           | 30%    | `_content_based_services()`           | Matches services by category overlap, price similarity (±50% of customer average), and professional rating                           |
| Location-Based          | 20%    | `_location_based_services()`          | Scores services inversely proportional to distance (≤ 50 km) using the Haversine formula                                             |
| Popularity              | 10%    | `_popularity_based_services()`        | Trending services from the last 30 days weighted by booking count (70%) and rating (30%)                                             |

Already-booked services are excluded from results.

#### `get_recommended_professionals(category_id=None, limit=10)`

Returns professionals ranked by a composite score:

| Component                       | Weight |
| ------------------------------- | ------ |
| Rating (avg_rating / 5)         | 30%    |
| Experience (capped at 10 years) | 15%    |
| Review count (capped at 50)     | 15%    |
| Completion rate                 | 25%    |
| Location proximity (≤ 50 km)    | 15%    |

#### `get_similar_services(service_id, limit=5)`

Finds services in the **same category**, scored by:

- Base category match: **0.5**
- Price similarity: up to **+0.3**
- Professional rating: up to **+0.2**

#### `get_recommended_categories(limit=5)`

Discovers categories the customer hasn't booked yet, ranked by co-occurrence frequency with the customer's booked categories.

---

### `ProfessionalRecommendationEngine`

Initialized with a `Professional` instance.

#### `get_suggested_categories(limit=3)`

Finds categories offered by similar professionals (those sharing at least one category) that this professional does **not** yet offer. Ranked by frequency.

#### `get_optimal_pricing(service_id)`

Market-based pricing suggestion. Steps:

1. Collects prices of all active services in the same category
2. Computes market average
3. Applies a **rating adjustment** (+/− 10% based on professional rating)
4. Applies an **experience adjustment** (+2% per year of experience)
5. Returns current price, market average, suggested price, and min/max market prices

---

## Predictive Analytics

### `CancellationRiskPredictor`

#### `predict_risk(booking) → dict`

Calculates a weighted cancellation risk score (0.0–1.0) from six factors:

| Factor               | Weight | Description                                                                  |
| -------------------- | ------ | ---------------------------------------------------------------------------- |
| Customer history     | 25%    | Customer's historical cancellation rate (fallback 0.2 if < 3 bookings)       |
| Professional history | 20%    | Professional's rejection + cancellation rate (fallback 0.15 if < 5 bookings) |
| Lead time            | 15%    | Same-day → 0.4, < 3 days → 0.2, > 30 days → 0.3, else 0.1                    |
| Price deviation      | 15%    | Deviation from customer's average completed-booking price                    |
| First-time pairing   | 10%    | 0.3 if customer and professional have never worked together                  |
| Category rate        | 15%    | Overall cancellation rate for the service category                           |

**Risk Levels:**

| Score Range | Level       |
| ----------- | ----------- |
| < 0.2       | `LOW`       |
| 0.2 – 0.4   | `MODERATE`  |
| 0.4 – 0.6   | `HIGH`      |
| ≥ 0.6       | `VERY_HIGH` |

---

### `DemandForecaster`

#### `get_demand_forecast(category_id=None, city=None, days_ahead=7)`

Forecasts daily booking volume by analyzing 12 weeks of historical data for the same day-of-week. Returns predicted bookings, confidence level (`LOW` / `MEDIUM` / `HIGH`), and trend (`INCREASING` / `DECREASING` / `STABLE`).

#### `get_peak_hours(category_id=None, city=None)`

Identifies the top 5 busiest booking hours from the last 90 days. Each hour entry includes:

- `hour` — 0–23
- `time_range` — human-readable range (`"09:00 - 10:00"`)
- `bookings` — absolute count
- `intensity` — normalized 0.0–1.0 (1.0 = busiest hour)

---

## UML Diagrams

### Class Diagram

```mermaid
classDiagram
    direction TB

    class UserInteraction {
        +int id
        +ForeignKey user
        +str interaction_type
        +ForeignKey content_type
        +int object_id
        +GenericForeignKey content_object
        +str session_id
        +dict metadata
        +datetime created_at
        +__str__() str
    }

    class ServiceSimilarity {
        +int id
        +ForeignKey service_a
        +ForeignKey service_b
        +float similarity_score
        +datetime updated_at
        +__str__() str
    }

    class ProfessionalScore {
        +int id
        +OneToOneField professional
        +float rating_score
        +float completion_rate_score
        +float response_time_score
        +float experience_score
        +float consistency_score
        +float overall_score
        +int bookings_analyzed
        +datetime last_computed_at
        +__str__() str
    }

    class CustomerPreference {
        +int id
        +OneToOneField customer
        +list preferred_categories
        +dict preferred_price_range
        +list preferred_times
        +list preferred_days
        +Decimal avg_booking_value
        +float booking_frequency_days
        +datetime last_computed_at
        +__str__() str
    }

    class RecommendationLog {
        +int id
        +ForeignKey user
        +str recommendation_type
        +list recommended_items
        +int selected_item_id
        +str algorithm_version
        +dict context
        +datetime created_at
        +datetime clicked_at
        +__str__() str
    }

    class RecommendationEngine {
        -CustomerProfile customer
        -User user
        +__init__(customer_profile)
        +get_recommended_services(limit) list~Service~
        +get_recommended_professionals(category_id, limit) list~Professional~
        +get_similar_services(service_id, limit) list~Service~
        +get_recommended_categories(limit) list~ServiceCategory~
        -_collaborative_filtering_services() dict
        -_content_based_services() dict
        -_location_based_services() dict
        -_popularity_based_services() dict
        -_calculate_professional_score(professional) float
        -_haversine_distance(lat1, lon1, lat2, lon2) float
    }

    class ProfessionalRecommendationEngine {
        -Professional professional
        +__init__(professional)
        +get_suggested_categories(limit) list~ServiceCategory~
        +get_optimal_pricing(service_id) dict
    }

    class CancellationRiskPredictor {
        +predict_risk(booking) dict
        -_get_customer_cancellation_rate(customer) float
        -_get_professional_issue_rate(professional) float
        -_calculate_lead_time_risk(booking) float
        -_calculate_price_risk(booking) float
        -_is_first_time_pairing(booking) bool
        -_get_category_cancellation_rate(category_id) float
        -_get_risk_level(score) str
    }

    class DemandForecaster {
        +get_demand_forecast(category_id, city, days_ahead) list~dict~
        +get_peak_hours(category_id, city) list~dict~
        -_get_historical_demand(day_of_week, category_id, city) dict
    }

    %% Relationships
    UserInteraction --> User : user
    UserInteraction --> ContentType : content_type
    ServiceSimilarity --> Service : service_a
    ServiceSimilarity --> Service : service_b
    ProfessionalScore --> Professional : professional
    CustomerPreference --> CustomerProfile : customer
    RecommendationLog --> User : user

    RecommendationEngine ..> UserInteraction : reads
    RecommendationEngine ..> ServiceSimilarity : reads
    RecommendationEngine ..> CustomerPreference : reads
    RecommendationEngine ..> Booking : queries
    RecommendationEngine ..> Service : queries
    RecommendationEngine ..> Professional : queries

    ProfessionalRecommendationEngine ..> Service : queries
    ProfessionalRecommendationEngine ..> Professional : queries
    ProfessionalRecommendationEngine ..> ServiceCategory : queries

    CancellationRiskPredictor ..> Booking : queries
    DemandForecaster ..> Booking : queries
```

### Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ USER_INTERACTION : has
    USER ||--o{ RECOMMENDATION_LOG : receives

    CONTENT_TYPE ||--o{ USER_INTERACTION : referenced_by

    SERVICE ||--o{ SERVICE_SIMILARITY : "service_a"
    SERVICE ||--o{ SERVICE_SIMILARITY : "service_b"

    PROFESSIONAL ||--|| PROFESSIONAL_SCORE : has
    CUSTOMER_PROFILE ||--|| CUSTOMER_PREFERENCE : has

    USER_INTERACTION {
        int id PK
        int user_id FK
        string interaction_type
        int content_type_id FK
        int object_id
        string session_id
        json metadata
        datetime created_at
    }

    SERVICE_SIMILARITY {
        int id PK
        int service_a_id FK
        int service_b_id FK
        float similarity_score
        datetime updated_at
    }

    PROFESSIONAL_SCORE {
        int id PK
        int professional_id FK
        float rating_score
        float completion_rate_score
        float response_time_score
        float experience_score
        float consistency_score
        float overall_score
        int bookings_analyzed
        datetime last_computed_at
    }

    CUSTOMER_PREFERENCE {
        int id PK
        int customer_id FK
        json preferred_categories
        json preferred_price_range
        json preferred_times
        json preferred_days
        decimal avg_booking_value
        float booking_frequency_days
        datetime last_computed_at
    }

    RECOMMENDATION_LOG {
        int id PK
        int user_id FK
        string recommendation_type
        json recommended_items
        int selected_item_id
        string algorithm_version
        json context
        datetime created_at
        datetime clicked_at
    }
```

### Component Diagram

```mermaid
graph TB
    subgraph Client
        A[Mobile / Web App]
    end

    subgraph "API Layer (views.py)"
        B1[RecommendedServicesView]
        B2[RecommendedProfessionalsView]
        B3[RecommendedCategoriesView]
        B4[SimilarServicesView]
        B5[SuggestedCategoriesForProfessionalView]
        B6[PricingSuggestionView]
        B7[CancellationRiskView]
        B8[DemandForecastView]
        B9[PeakHoursView]
    end

    subgraph "Serializers (serializers.py)"
        S1[ServiceRecommendationSerializer]
        S2[ProfessionalRecommendationSerializer]
        S3[CategoryRecommendationSerializer]
        S4[CancellationRiskSerializer]
        S5[DemandForecastSerializer]
        S6[PeakHoursSerializer]
        S7[PricingSuggestionSerializer]
    end

    subgraph "Business Logic"
        E1[RecommendationEngine]
        E2[ProfessionalRecommendationEngine]
        E3[CancellationRiskPredictor]
        E4[DemandForecaster]
    end

    subgraph "Data Layer (models.py)"
        M1[UserInteraction]
        M2[ServiceSimilarity]
        M3[ProfessionalScore]
        M4[CustomerPreference]
        M5[RecommendationLog]
    end

    subgraph "External Models"
        X1[Booking]
        X2[Service]
        X3[Professional]
        X4[CustomerProfile]
        X5[ServiceCategory]
    end

    A --> B1 & B2 & B3 & B4 & B5 & B6 & B7 & B8 & B9

    B1 --> S1
    B2 --> S2
    B3 --> S3
    B7 --> S4
    B8 --> S5
    B9 --> S6
    B6 --> S7

    B1 & B2 & B3 & B4 --> E1
    B5 & B6 --> E2
    B7 --> E3
    B8 & B9 --> E4

    E1 --> M1 & M2 & M4
    E1 --> X1 & X2 & X3 & X4 & X5
    E2 --> X2 & X3 & X5
    E3 --> X1
    E4 --> X1
```

### Sequence Diagram — Service Recommendation Flow

```mermaid
sequenceDiagram
    actor C as Customer
    participant V as RecommendedServicesView
    participant E as RecommendationEngine
    participant DB as Database

    C->>V: GET /api/ml/recommendations/services/?limit=10
    V->>V: Validate token & role == customer
    V->>E: RecommendationEngine(customer_profile)
    V->>E: get_recommended_services(limit=10)

    par Strategy Execution
        E->>DB: Collaborative filtering query
        DB-->>E: collab scores (weight 0.4)
    and
        E->>DB: Content-based query
        DB-->>E: content scores (weight 0.3)
    and
        E->>DB: Location-based query
        DB-->>E: location scores (weight 0.2)
    and
        E->>DB: Popularity query (last 30 days)
        DB-->>E: popularity scores (weight 0.1)
    end

    E->>E: Merge & weight scores
    E->>DB: Exclude already-booked services
    E->>DB: Fetch top-N Service objects
    E-->>V: list[Service]
    V->>V: Serialize via ServiceRecommendationSerializer
    V-->>C: 200 OK {count, recommendations}
```

### Sequence Diagram — Cancellation Risk Prediction

```mermaid
sequenceDiagram
    actor U as User
    participant V as CancellationRiskView
    participant P as CancellationRiskPredictor
    participant DB as Database

    U->>V: GET /api/ml/analytics/cancellation-risk/{booking_id}/
    V->>DB: Booking.objects.get(id=booking_id)
    V->>V: Verify access (customer owns booking OR professional assigned)

    V->>P: CancellationRiskPredictor()
    V->>P: predict_risk(booking)

    P->>DB: Customer cancellation rate
    P->>DB: Professional issue rate
    P->>P: Calculate lead time risk
    P->>DB: Customer avg booking price (price deviation)
    P->>DB: Check first-time pairing
    P->>DB: Category cancellation rate

    P->>P: Weighted sum → risk_score
    P->>P: Map score → risk_level
    P-->>V: {risk_score, risk_level, factors}

    V->>V: Serialize via CancellationRiskSerializer
    V-->>U: 200 OK {risk_score, risk_level, factors}
```
