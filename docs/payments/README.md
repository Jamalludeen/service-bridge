# Payment Module Documentation

## Overview

This document describes the Payment module, its models, endpoints, and workflows in the serviceBridge project.

## UML Diagrams

### 1. Payment Model UML

```plantuml
@startuml
class Payment {
  +id: UUID
  +booking: Booking
  +amount: Decimal
  +transaction_id: str
  +status: str
  +created_at: datetime
  +updated_at: datetime
}

Payment --> Booking : relates to
@enduml
```

### 2. Payment Workflow UML

```plantuml
@startuml
start
:Customer books a service;
:Booking created;
:Payment initiated;
if (Payment successful?) then (yes)
  :Update payment status to PAID;
  :Notify customer and professional;
else (no)
  :Update payment status to FAILED;
  :Notify customer;
endif
stop
@enduml
```

## Endpoints

- `POST /payments/` - Create a new payment
- `GET /payments/{id}/` - Retrieve payment details
- `GET /payments/` - List all payments

## Fields

- `booking`: Related booking
- `amount`: Payment amount
- `transaction_id`: Unique transaction reference
- `status`: Payment status (e.g., PENDING, PAID, FAILED)
- `created_at`, `updated_at`: Timestamps

---

For more details, see the Payment model and API code.
