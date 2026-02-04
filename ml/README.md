# ServiceBridge ML App

A Django application that provides machine learning capabilities for the ServiceBridge platform, including recommendation systems, intelligent matching, and predictive analytics.

## Overview

The ML app enhances the ServiceBridge platform with AI-powered features to improve user experience and platform efficiency:

- **Recommendation System**: Suggest relevant services and professionals to customers
- **Intelligent Matching**: Smart professional-customer pairing based on multiple factors
- **Predictive Analytics**: Booking cancellation risk prediction and demand forecasting
- **Quality Scoring**: ML-based professional quality assessment

## Features

### Implemented ✅

- **Data Models**: Complete database schema for ML features
- **User Interaction Tracking**: Generic system to track user behavior
- **Professional Scoring**: Multi-factor quality scoring system
- **Customer Preferences**: Learned preference storage
- **Recommendation Logging**: A/B testing and analytics tracking

### Planned 🚧

- **Service Recommendations**: Collaborative filtering for service suggestions
- **Professional Matching**: Intelligent professional-customer pairing
- **Cancellation Prediction**: ML model to predict booking cancellations
- **Demand Forecasting**: Predict service demand patterns
- **Real-time Scoring**: Dynamic professional quality updates

## Installation

### Dependencies

Add the following to your `requirements.txt`:

```txt
scikit-learn>=1.4.0
pandas>=2.2.0
numpy>=1.26.0
joblib>=1.3.0
scipy>=1.11.0
```

### Setup

1. **Add to INSTALLED_APPS** in `settings.py`:

   ```python
   INSTALLED_APPS = [
       # ... other apps
       'ml',
   ]
   ```

2. **Run migrations**:

   ```bash
   python manage.py makemigrations ml
   python manage.py migrate
   ```

3. **Include URLs** (when views are implemented):
   ```python
   # In main urls.py
   path('api/ml/', include('ml.urls')),
   ```

## Models

### UserInteraction

Tracks all user interactions for collaborative filtering and behavior analysis.

**Fields:**

- `user`: ForeignKey to User
- `interaction_type`: VIEW, SEARCH, BOOKMARK, BOOK, COMPLETE, REVIEW, CANCEL
- `content_type/object_id`: Generic relation to any model (Service, Professional, etc.)
- `session_id`: Session tracking
- `metadata`: Additional context data
- `created_at`: Timestamp

### ServiceSimilarity

Pre-computed similarity scores between services for recommendation.

**Fields:**

- `service_a/service_b`: ForeignKeys to Service
- `similarity_score`: Float (0.0-1.0)
- `updated_at`: Last computation timestamp

### ProfessionalScore

ML-computed quality scores for professionals.

**Fields:**

- `professional`: OneToOneField to Professional
- Component scores: `rating_score`, `completion_rate_score`, `response_time_score`, `experience_score`, `consistency_score`
- `overall_score`: Composite score (0.0-1.0)
- `bookings_analyzed`: Number of bookings used for scoring
- `last_computed_at`: Timestamp

### CustomerPreference

Learned customer preferences and behavior patterns.

**Fields:**

- `customer`: OneToOneField to CustomerProfile
- `preferred_categories`: JSON list of preferred service categories with weights
- `preferred_price_range`: JSON with min/max price preferences
- `preferred_times/days`: JSON arrays of preferred scheduling
- `avg_booking_value`: Computed average spending
- `booking_frequency_days`: Computed booking frequency

### RecommendationLog

Tracks recommendations for analytics and A/B testing.

**Fields:**

- `user`: ForeignKey to User
- `recommendation_type`: Type of recommendation
- `recommended_items`: JSON list of recommended item IDs
- `selected_item_id`: Which item was selected (if any)
- `algorithm_version`: Version of algorithm used
- `context`: Additional context data
- `created_at/clicked_at`: Timestamps

## API Endpoints (Planned)

### Recommendations

```
GET /api/ml/recommendations/services/ - Get service recommendations
GET /api/ml/recommendations/professionals/ - Get professional recommendations
GET /api/ml/recommendations/similar/<service_id>/ - Get similar services
```

### Professional Scores

```
GET /api/ml/professionals/<id>/score/ - Get professional quality score
GET /api/ml/professionals/scores/ - Get top-rated professionals
```

### Analytics

```
GET /api/ml/analytics/customer/<id>/ - Customer behavior analytics
GET /api/ml/analytics/professional/<id>/ - Professional performance analytics
POST /api/ml/interactions/ - Log user interaction
```

## Usage Examples

### Tracking User Interactions

```python
from ml.models import UserInteraction
from django.contrib.contenttypes.models import ContentType

# Track service view
service_ct = ContentType.objects.get_for_model(Service)
UserInteraction.objects.create(
    user=request.user,
    interaction_type='VIEW',
    content_type=service_ct,
    object_id=service.id,
    session_id=request.session.session_key,
    metadata={'source': 'search', 'position': 1}
)
```

### Getting Professional Scores

```python
from ml.models import ProfessionalScore

# Get professional's ML score
score = ProfessionalScore.objects.get(professional=professional)
print(f"Overall score: {score.overall_score}")
print(f"Rating component: {score.rating_score}")
```

### Customer Preferences

```python
from ml.models import CustomerPreference

# Get customer's learned preferences
prefs = CustomerPreference.objects.get(customer=customer_profile)
print(f"Preferred categories: {prefs.preferred_categories}")
print(f"Average booking value: {prefs.avg_booking_value}")
```

## Development Roadmap

### Phase 1: Foundation (Current)

- ✅ Database models
- ✅ Basic data collection
- ⏳ Admin interface

### Phase 2: Core ML Features

- ⏳ Collaborative filtering for recommendations
- ⏳ Professional scoring algorithm
- ⏳ Customer preference learning
- ⏳ Basic API endpoints

### Phase 3: Advanced Features

- ⏳ Real-time recommendations
- ⏳ Cancellation prediction model
- ⏳ Demand forecasting
- ⏳ A/B testing framework

### Phase 4: Optimization

- ⏳ Model performance monitoring
- ⏳ Automated model retraining
- ⏳ Scalability improvements

## Contributing

1. **Data Collection**: Ensure user interactions are properly logged
2. **Model Training**: Use the collected data to train ML models
3. **API Development**: Implement REST endpoints for ML features
4. **Testing**: Add comprehensive tests for ML algorithms
5. **Monitoring**: Track model performance and accuracy

## Dependencies

- **scikit-learn**: Machine learning algorithms
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **joblib**: Model serialization
- **scipy**: Scientific computing

## Configuration

Add to `settings.py`:

```python
# ML App Settings
ML_SETTINGS = {
    'MIN_INTERACTIONS_FOR_RECOMMENDATION': 5,
    'SIMILARITY_THRESHOLD': 0.3,
    'PROFESSIONAL_SCORE_WEIGHTS': {
        'rating': 0.4,
        'completion_rate': 0.3,
        'response_time': 0.2,
        'experience': 0.05,
        'consistency': 0.05,
    },
    'RECOMMENDATION_CACHE_TIMEOUT': 3600,  # 1 hour
}
```

## License

This project is part of the ServiceBridge platform. See main project license for details.</content>
<parameter name="filePath">/home/karimi/Desktop/django/serviceBridge/README_ML.md
