# Customer API Documentation

This folder contains frontend-facing documentation for customer-related APIs, including customer profiles and shopping cart operations.

## Contents

- [Customer Profile APIs](profile.md)
- [Cart APIs](cart.md)

## Auth

All endpoints in this folder require authentication via DRF Token Authentication:

- Header: `Authorization: Token <token>`

## Base Path

All customer endpoints are served under the customer app routes. In this project, the base path is:

```
/api/
```

The customer endpoints documented here are:

- `/api/profile/`
- `/api/cart/` and its actions

If your API gateway uses a different prefix, update the base path accordingly.
