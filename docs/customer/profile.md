# Customer Profile APIs

## Get Current Customer Profile

**GET** `/api/profile/`

Returns the authenticated customer's profile.

### Response 200

```json
{
  "id": 12,
  "user": 5,
  "profile_image": null,
  "city": "Kabul",
  "district": "13th",
  "detailed_address": "123 Test St",
  "latitude": null,
  "longitude": null,
  "preferred_language": "fa",
  "total_bookings": 0,
  "avg_rating_given": 0.0,
  "created_at": "2026-02-08T10:30:00Z",
  "updated_at": "2026-02-08T10:30:00Z"
}
```

### Response 404

```json
{
  "detail": "Not found."
}
```

---

## Update Current Customer Profile

**PATCH** `/api/profile/`

Updates any subset of profile fields. Only the profile owner may update.

### Request Body (any subset)

```json
{
  "city": "Kabul",
  "district": "13th",
  "detailed_address": "New Address",
  "preferred_language": "en",
  "latitude": 34.5553,
  "longitude": 69.2075
}
```

### Response 200

```json
{
  "message": "Profile successfully updated!",
  "data": {
    "id": 12,
    "user": 5,
    "profile_image": null,
    "city": "Kabul",
    "district": "13th",
    "detailed_address": "New Address",
    "latitude": "34.555300",
    "longitude": "69.207500",
    "preferred_language": "en",
    "total_bookings": 0,
    "avg_rating_given": 0.0,
    "created_at": "2026-02-08T10:30:00Z",
    "updated_at": "2026-02-08T10:31:00Z"
  }
}
```

### Response 400

```json
{
  "city": ["This field may not be blank."]
}
```

---

## Delete Current Customer Profile

**DELETE** `/api/profile/`

Deletes the authenticated customer's profile. Only the profile owner may delete.

### Response 204

```json
{
  "message": "Profile deleted successfully"
}
```
