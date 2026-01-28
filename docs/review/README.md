# Review Module Documentation

## Overview

The **Review Module** allows customers to rate and review professionals after a completed booking. It also enables professionals to respond to reviews, creating a transparent feedback loop.

Key Features:

- **Ratings & Comments**: Customers can leave 1-5 star ratings and comments.
- **Moderation**: Reviews can be flagged and moderated (default: approved).
- **Responses**: Professionals can reply to reviews once.
- **Statistics**: Aggregated review stats for professionals.

## Base URL

`/review/`

## Authentication

All endpoints require **Token Authentication**.
Headers: `Authorization: Token <your_token>`

## API Endpoints

### 1. Create Review

**POST** `/review/`

**Permissions**: Customer Only.

**Body Parameters**:
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `booking_id` | Integer | **Yes** | ID of the completed booking. |
| `rating` | Integer | **Yes** | 1 to 5. |
| `comment` | String | No | Review text. |

**Example Request**:

```json
{
  "booking_id": 12,
  "rating": 5,
  "comment": "Great service! arrived on time."
}
```

---

### 2. List Reviews

**GET** `/review/`

**Permissions**: Authenticated Users.

- **Customer**: List reviews given by them.
- **Professional**: List reviews received for their services.
- **Admin**: List all reviews.

---

### 3. Review Details

**GET** `/review/{id}/`

Get detailed information about a specific review, including the professional's response if available.

---

### 4. Respond to Review

**POST** `/review/{id}/respond/`

**Permissions**: Professional (must be the one reviewed).

**Body Parameters**:
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `response_text` | String | **Yes** | The professional's reply. |

**Example Request**:

```json
{
  "response_text": "Thank you for the kind words!"
}
```

---

### 5. Professional Stats

**GET** `/review/professional/{id}/stats/`

Get public statistics for a professional, including average rating and rating breakdown.

**Response Example**:

```json
{
  "average_rating": 4.8,
  "total_reviews": 42,
  "rating_breakdown": {
    "5_star": 35,
    "4_star": 5,
    "3_star": 2,
    "2_star": 0,
    "1_star": 0
  },
  "recent_reviews": [...]
}
```

---

## Data Models

### Review

| Field          | Type       | Description                           |
| :------------- | :--------- | :------------------------------------ |
| `booking`      | OneToOne   | The completed booking being reviewed. |
| `customer`     | ForeignKey | The user writing the review.          |
| `professional` | ForeignKey | The professional being reviewed.      |
| `rating`       | Integer    | 1-5 score.                            |
| `comment`      | TextField  | Optional text content.                |
| `is_approved`  | Boolean    | Moderation status.                    |
| `is_flagged`   | Boolean    | Flag for admin attention.             |

### ReviewResponse

| Field           | Type       | Description                    |
| :-------------- | :--------- | :----------------------------- |
| `review`        | OneToOne   | The review being responded to. |
| `professional`  | ForeignKey | The responder.                 |
| `response_text` | TextField  | Content of the response.       |

## Diagrams

### Review Model

See [Review Model UML](review_model.puml)

### Review Workflow

See [Review Workflow UML](review_workflow.puml)
