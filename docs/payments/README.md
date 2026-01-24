# Payment Module Documentation

## Overview

The **ServiceBridge Payment Module** handles the escrow-based payment process between Customers and Professionals.

Key Features:

- **Escrow System**: Funds are held (status: `HELD`) until the service is successfully completed.
- **Multiple Methods**: Supports `CASH` (Cash on Delivery), `MOBILE_MONEY`, and `BANK_TRANSFER`.
- **Role-Based Workflow**: Strict permissions for initiating, confirming, and releasing payments to ensure security.
- **Audit Trail**: Every status change is recorded in `PaymentHistory`.

## Base URL

`/payment/`

## Authentication

All endpoints require **Token Authentication**.
Headers: `Authorization: Token <your_token>`

## Payment Workflow

1.  **Initiate (Customer)**: Customer creates a payment for an `ACCEPTED` or `IN_PROGRESS` booking. Status -> `PENDING`.
2.  **Confirm (Admin/Pro)**:
    - **CASH**: The assigned Professional confirms receipt.
    - **Digital**: Admin verifies and confirms receipt.
    - Status -> `HELD`.
3.  **Release (Admin/Customer)**:
    - After Booking is `COMPLETED`, the payment can be released to the Professional.
    - Status -> `RELEASED`.

## API Endpoints

### 1. Initiate Payment

**POST** `/payment/`

**Permissions**: Customer Only.

**Body Parameters**:
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `booking_id` | Integer | **Yes** | ID of the booking (Must be yours and accepted). |
| `payment_method` | String | No | `CASH` (default), `MOBILE_MONEY`, `BANK_TRANSFER`. |

**Example Request**:

```json
{
  "booking_id": 12,
  "payment_method": "CASH"
}
```

**Response (201 Created)**:

```json
{
  "id": "uuid-string",
  "transaction_id": "TXN-1234ABCD",
  "amount": "500.00",
  "status": "PENDING",
  ...
}
```

---

### 2. List Payments

**GET** `/payment/`

**Permissions**: Authenticated Users.

- **Customer**: Sees payments for their bookings.
- **Professional**: Sees payments for their assigned jobs.
- **Admin**: Sees all payments.

---

### 3. Retrieve Payment Details

**GET** `/payment/{id}/`

**Response Example**:

```json
{
  "id": 5,
  "transaction_id": "TXN-9F8E7D6C",
  "booking_id": 12,
  "service_title": "Plumbing Repair",
  "customer_name": "John Doe",
  "professional_name": "Pro Plumber",
  "amount": "500.00",
  "payment_method": "CASH",
  "status": "HELD",
  "external_transaction_id": "",
  "history": [...]
}
```

---

### 4. Confirm Payment

**POST** `/payment/{id}/confirm/`

Moves status from `PENDING` -> `HELD`.

**Permissions**:

- **CASH**: Assigned Professional or Admin.
- **Others**: Admin Only.

**Body Parameters**:
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `external_transaction_id` | String | No | Ref ID from M-Paisa/Bank. |
| `notes` | String | No | Any additional comments. |

**Example Request**:

```json
{
  "notes": "Cash received on site."
}
```

---

### 5. Release Payment

**POST** `/payment/{id}/release/`

Moves status from `HELD` -> `RELEASED`.

**Prerequisites**:

- Booking status must be `COMPLETED`.
- Payment status must be `HELD`.

**Permissions**: Customer or Admin.

**Response**:

```json
{
  "message": "Payment released to professional.",
  "data": { ... }
}
```

---

### 6. Cancel Payment

**POST** `/payment/{id}/cancel/`

**Permissions**: Customer Only.
**Prerequisite**: Payment status must be `PENDING`.

---

## Data Models

### Payment Statuses

| Status      | Description                                       |
| :---------- | :------------------------------------------------ |
| `PENDING`   | Created, waiting for funds transfer/confirmation. |
| `HELD`      | Funds received/confirmed. Held in Escrow.         |
| `RELEASED`  | Service done, funds released to the Professional. |
| `REFUNDED`  | Funds returned to the Customer.                   |
| `FAILED`    | Transaction failed.                               |
| `CANCELLED` | Payment cancelled by the user.                    |

### Payment Methods

- `CASH`
- `MOBILE_MONEY`
- `BANK_TRANSFER`

## Diagrams

### Payment State Machine

See [Payment Workflow UML](payment_workflow.puml)

### Data Model

See [Payment Model UML](payment_model.puml)
