# Cart APIs

## Get Current Customer Cart

**GET** `/customer/cart/`

Creates a cart for the customer if none exists, then returns cart with items.

### Response 200

```json
{
  "id": "9a7f7d3a-5b5f-4d2b-9b43-2e6e1d7f1c2a",
  "customer": 12,
  "items": [
    {
      "id": 55,
      "service": 101,
      "quantity": 2,
      "estimated_price": "1000.00",
      "added_at": "2026-02-08T10:30:00Z",
      "updated_at": "2026-02-08T10:30:00Z"
    }
  ],
  "total_items": 1,
  "total_price": "1000.00",
  "is_empty": false
}
```

### Response 404

```json
{
  "error": "Customer profile not found"
}
```

---

## Add Item to Cart

**POST** `/customer/cart/add/`

Adds a service to the cart. If the service already exists in the cart, its quantity is increased.

### Request Body

```json
{
  "service": 101,
  "quantity": 2
}
```

### Response 201 (created)

```json
{
  "message": "Item added to cart successfully",
  "item": {
    "id": 55,
    "service": 101,
    "quantity": 2,
    "estimated_price": "1000.00",
    "added_at": "2026-02-08T10:30:00Z",
    "updated_at": "2026-02-08T10:30:00Z"
  }
}
```

### Response 200 (updated quantity)

```json
{
  "message": "Cart item quantity updated",
  "item": {
    "id": 55,
    "service": 101,
    "quantity": 4,
    "estimated_price": "2000.00",
    "added_at": "2026-02-08T10:30:00Z",
    "updated_at": "2026-02-08T10:31:00Z"
  }
}
```

### Response 400

```json
{
  "error": "Cart is full. Maximum 50 items allowed."
}
```

---

## Update Cart Item

**PATCH** `/customer/cart/{cart_id}/items/{item_id}/`

Updates quantity or other mutable fields for a cart item.

### Request Body

```json
{
  "quantity": 3
}
```

### Response 200

```json
{
  "message": "Cart item updated successfully",
  "item": {
    "id": 55,
    "service": 101,
    "quantity": 3,
    "estimated_price": "1500.00",
    "added_at": "2026-02-08T10:30:00Z",
    "updated_at": "2026-02-08T10:32:00Z"
  }
}
```

---

## Delete Cart Item

**DELETE** `/customer/cart/items/{item_id}/`

Removes a cart item from the current customer's cart.

### Response 200

```json
{
  "message": "Service Title deleted from cart!"
}
```

---

## Notes

- All cart endpoints require a customer profile.
- Cart has a maximum of 50 distinct services.
- `total_items` reflects the number of distinct items in the cart, not total quantity.
