# Authentication API Documentation - Service Bridge Platform

**Version:** 2.0
**Last Updated:** January 2026
**Base URL:** `http://your-domain/auth/`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Flow](#authentication-flow)
3. [API Endpoints](#api-endpoints)
4. [Flutter Integration Guide](#flutter-integration-guide)
5. [Error Handling](#error-handling)
6. [Security Features](#security-features)
7. [Testing Guide](#testing-guide)

---

## Overview

The Service Bridge platform uses a unified email-first authentication flow with OTP-based 2-factor authentication. Every login requires OTP verification for maximum security.

### Key Features

- ✅ **Email-first authentication** - Start with email, system detects if user exists
- ✅ **OTP 2FA on every login** - Enhanced security with one-time passwords
- ✅ **Role-based registration** - Separate endpoints for Customer, Professional, and Admin
- ✅ **Session-based flow** - Secure state management with 15-minute session expiry
- ✅ **Account protection** - Automatic lockout after 5 failed password attempts
- ✅ **Afghan phone validation** - Supports +93 and 07 format phone numbers

### User Roles

- **Customer** - Service consumers
- **Professional** - Service providers
- **Admin** - Platform administrators

---

## Authentication Flow

### Flow 1: New User Registration

```
1. Enter Email → OTP Sent
2. Verify OTP → Success
3. Fill Registration Form (username, password, phone, names)
4. Re-enter Password → Token Generated ✅
```

**Total Steps:** 4
**Estimated Time:** 2-3 minutes

---

### Flow 2: Existing User Login (2FA)

```
1. Enter Email → OTP Sent
2. Verify OTP → Success
3. Enter Password → Token Generated ✅
```

**Total Steps:** 3
**Estimated Time:** 1-2 minutes

---

## API Endpoints

### 1. Initiate Authentication

**Description:** Start the authentication process by providing an email address. The system will check if the user exists and send an OTP.

**Endpoint:** `POST /auth/{role}/initiate/`

**Role Options:**
- `/auth/customer/initiate/`
- `/auth/professional/initiate/`
- `/auth/admin/initiate/`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@gmail.com"
}
```

**Validation Rules:**
- Email must end with `@gmail.com`
- Email is case-insensitive (automatically converted to lowercase)

**Success Response (200 OK):**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "user_exists": false,
  "message": "OTP sent to your email",
  "next_step": "verify_otp"
}
```

**Error Response (400 Bad Request):**
```json
{
  "email": [
    "Please enter a valid Gmail address."
  ]
}
```

**Important Notes:**
- Save the `session_id` - you'll need it for all subsequent requests
- Check `user_exists` to determine which flow to follow
- OTP will be sent to the provided email address
- OTP is valid for 5 minutes

---

### 2. Verify OTP

**Description:** Verify the OTP code received via email.

**Endpoint:** `POST /auth/verify-otp/`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "otp": "123456"
}
```

**Validation Rules:**
- OTP must be exactly 6 digits
- OTP must be numeric only
- Session must be valid and not expired

**Success Response - New User (200 OK):**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "user_exists": false,
  "message": "OTP verified successfully",
  "next_step": "complete_registration"
}
```

**Success Response - Existing User (200 OK):**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "user_exists": true,
  "message": "OTP verified successfully",
  "next_step": "enter_password"
}
```

**Error Responses:**

Invalid OTP (400 Bad Request):
```json
{
  "message": "Invalid OTP"
}
```

Expired OTP (400 Bad Request):
```json
{
  "message": "OTP has expired. Please request a new one."
}
```

Invalid Session (400 Bad Request):
```json
{
  "message": "Invalid or expired session"
}
```

**Rate Limiting:**
- Maximum 1 request per minute per IP

---

### 3. Complete Registration (New Users Only)

**Description:** Provide registration details including username, password, and phone number. This step is only for new users.

**Endpoint:** `POST /auth/complete-registration/`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "username": "john_doe",
  "password": "SecurePass123!",
  "phone": "0781234567",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Field Requirements:**

| Field | Required | Description | Format |
|-------|----------|-------------|--------|
| session_id | Yes | Session ID from previous step | String |
| username | Yes | Unique username | 1-150 characters |
| password | Yes | Strong password | Min 8 chars, must pass Django validators |
| phone | Yes | Afghan mobile number | 07XXXXXXXX or +937XXXXXXXX |
| first_name | No | User's first name | 1-150 characters |
| last_name | No | User's last name | 1-150 characters |

**Phone Number Formats:**
- `0781234567` (automatically converted to +93781234567)
- `+93781234567`
- Valid prefixes: 70, 71, 72, 73, 74, 75, 76, 77, 78, 79

**Password Requirements:**
- Minimum 8 characters
- Cannot be too similar to username or email
- Cannot be entirely numeric
- Cannot be a commonly used password

**Success Response (200 OK):**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "message": "Registration data saved. Please confirm your password.",
  "next_step": "confirm_password"
}
```

**Error Responses:**

Username already taken (400 Bad Request):
```json
{
  "username": [
    "Username already taken."
  ]
}
```

Phone already registered (400 Bad Request):
```json
{
  "phone": [
    "Phone number already registered."
  ]
}
```

Invalid phone format (400 Bad Request):
```json
{
  "phone": [
    "Phone must be valid Afghan number."
  ]
}
```

Weak password (400 Bad Request):
```json
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common."
  ]
}
```

---

### 4. Authenticate with Password

**Description:** Final step - authenticate with password to receive access token. Works for both new and existing users.

**Endpoint:** `POST /auth/authenticate/`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s",
  "password": "SecurePass123!"
}
```

**Success Response (200 OK):**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 42,
    "username": "john_doe",
    "email": "user@gmail.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+93781234567",
    "role": "customer",
    "is_verified": true
  },
  "message": "Authentication successful"
}
```

**Token Usage:**
After receiving the token, include it in all authenticated API requests:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Error Responses:**

Invalid password (400 Bad Request):
```json
{
  "message": "Invalid password"
}
```

Account locked (403 Forbidden):
```json
{
  "message": "Account locked. Try again in 287 seconds."
}
```

Too many failed attempts (403 Forbidden):
```json
{
  "message": "Too many failed attempts. Account locked for 5 minutes."
}
```

Password mismatch for new user (400 Bad Request):
```json
{
  "message": "Password does not match"
}
```

**Security Features:**
- Account automatically locks after 5 failed password attempts
- Lockout duration: 5 minutes
- Failed attempt counter resets on successful login

---

### 5. Resend OTP (Utility)

**Description:** Request a new OTP if the previous one expired or wasn't received.

**Endpoint:** `POST /auth/resend-otp/`

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "K7mN9pQ2rT5vX8zA3bC6dE1fG4hJ7kL0mN3oP5qR7s"
}
```

**Success Response (200 OK):**
```json
{
  "message": "New OTP sent to your email"
}
```

**Error Response (400 Bad Request):**
```json
{
  "message": "Invalid or expired session"
}
```

**Usage Notes:**
- Can be called at any point before password authentication
- Generates and sends a new 6-digit OTP
- New OTP replaces the old one
- Recommended to implement a cooldown timer (30 seconds) on the frontend

---

## Flutter Integration Guide

### Step 1: Setup HTTP Client

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class AuthService {
  static const String baseUrl = 'http://your-domain/auth';

  // Store session data
  String? sessionId;
  bool? userExists;
}
```

### Step 2: Initiate Authentication

```dart
Future<Map<String, dynamic>> initiateAuth(String email, String role) async {
  final url = Uri.parse('$baseUrl/$role/initiate/');

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      // Store session data
      sessionId = data['session_id'];
      userExists = data['user_exists'];

      return {
        'success': true,
        'data': data,
      };
    } else {
      final error = jsonDecode(response.body);
      return {
        'success': false,
        'error': error,
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': 'Network error: $e',
    };
  }
}
```

### Step 3: Verify OTP

```dart
Future<Map<String, dynamic>> verifyOTP(String otp) async {
  final url = Uri.parse('$baseUrl/verify-otp/');

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': sessionId,
        'otp': otp,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'success': true,
        'data': data,
      };
    } else {
      final error = jsonDecode(response.body);
      return {
        'success': false,
        'error': error,
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': 'Network error: $e',
    };
  }
}
```

### Step 4: Complete Registration (New Users)

```dart
Future<Map<String, dynamic>> completeRegistration({
  required String username,
  required String password,
  required String phone,
  String? firstName,
  String? lastName,
}) async {
  final url = Uri.parse('$baseUrl/complete-registration/');

  try {
    final body = {
      'session_id': sessionId,
      'username': username,
      'password': password,
      'phone': phone,
    };

    if (firstName != null && firstName.isNotEmpty) {
      body['first_name'] = firstName;
    }
    if (lastName != null && lastName.isNotEmpty) {
      body['last_name'] = lastName;
    }

    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'success': true,
        'data': data,
      };
    } else {
      final error = jsonDecode(response.body);
      return {
        'success': false,
        'error': error,
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': 'Network error: $e',
    };
  }
}
```

### Step 5: Authenticate with Password

```dart
Future<Map<String, dynamic>> authenticatePassword(String password) async {
  final url = Uri.parse('$baseUrl/authenticate/');

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'session_id': sessionId,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      // Store token securely (use flutter_secure_storage)
      final token = data['token'];
      final user = data['user'];

      await secureStorage.write(key: 'auth_token', value: token);
      await secureStorage.write(key: 'user_data', value: jsonEncode(user));

      return {
        'success': true,
        'data': data,
      };
    } else {
      final error = jsonDecode(response.body);
      return {
        'success': false,
        'error': error,
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': 'Network error: $e',
    };
  }
}
```

### Step 6: Resend OTP

```dart
Future<Map<String, dynamic>> resendOTP() async {
  final url = Uri.parse('$baseUrl/resend-otp/');

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'session_id': sessionId}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return {
        'success': true,
        'message': data['message'],
      };
    } else {
      final error = jsonDecode(response.body);
      return {
        'success': false,
        'error': error,
      };
    }
  } catch (e) {
    return {
      'success': false,
      'error': 'Network error: $e',
    };
  }
}
```

### Complete Usage Example

```dart
// Example: New User Registration Flow
void newUserFlow() async {
  // Step 1: Initiate
  var result = await authService.initiateAuth('newuser@gmail.com', 'customer');
  if (!result['success']) {
    showError(result['error']);
    return;
  }

  // Navigate to OTP screen
  navigateToOTPScreen();

  // Step 2: Verify OTP
  result = await authService.verifyOTP('123456');
  if (!result['success']) {
    showError(result['error']);
    return;
  }

  // Check if new user
  if (!result['data']['user_exists']) {
    // Navigate to registration form
    navigateToRegistrationForm();

    // Step 3: Complete registration
    result = await authService.completeRegistration(
      username: 'john_doe',
      password: 'SecurePass123!',
      phone: '0781234567',
      firstName: 'John',
      lastName: 'Doe',
    );

    if (!result['success']) {
      showError(result['error']);
      return;
    }
  }

  // Step 4: Authenticate
  result = await authService.authenticatePassword('SecurePass123!');
  if (result['success']) {
    // Navigate to home screen
    navigateToHome(result['data']['user']);
  } else {
    showError(result['error']);
  }
}

// Example: Existing User Login Flow
void existingUserFlow() async {
  // Step 1: Initiate
  var result = await authService.initiateAuth('existing@gmail.com', 'customer');
  if (!result['success']) return;

  // Step 2: Verify OTP
  result = await authService.verifyOTP('654321');
  if (!result['success']) return;

  // Step 3: Authenticate (skip registration)
  result = await authService.authenticatePassword('ExistingPass456!');
  if (result['success']) {
    navigateToHome(result['data']['user']);
  }
}
```

### Secure Token Storage

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final secureStorage = FlutterSecureStorage();

// Store token
await secureStorage.write(key: 'auth_token', value: token);

// Retrieve token
String? token = await secureStorage.read(key: 'auth_token');

// Delete token (logout)
await secureStorage.delete(key: 'auth_token');

// Use token in authenticated requests
Future<http.Response> getProfile() async {
  final token = await secureStorage.read(key: 'auth_token');

  return await http.get(
    Uri.parse('http://your-domain/api/profile/'),
    headers: {
      'Authorization': 'Token $token',
    },
  );
}
```

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Continue to next step |
| 400 | Bad Request | Show validation errors to user |
| 403 | Forbidden | Account locked or rate limited |
| 500 | Server Error | Show generic error, retry later |

### Common Error Scenarios

#### 1. Invalid Email Format
```json
{
  "email": ["Please enter a valid Gmail address."]
}
```
**Solution:** Show error message, ask user to correct email

#### 2. Invalid OTP
```json
{
  "message": "Invalid OTP"
}
```
**Solution:** Show error, allow retry (max 5 attempts), offer resend option

#### 3. Expired OTP
```json
{
  "message": "OTP has expired. Please request a new one."
}
```
**Solution:** Automatically trigger resend OTP or show resend button

#### 4. Expired Session
```json
{
  "message": "Invalid or expired session"
}
```
**Solution:** Restart flow from Step 1 (initiate authentication)

#### 5. Username Taken
```json
{
  "username": ["Username already taken."]
}
```
**Solution:** Show error, suggest alternatives (username + random numbers)

#### 6. Account Locked
```json
{
  "message": "Account locked. Try again in 287 seconds."
}
```
**Solution:** Show countdown timer, disable login button until timer expires

#### 7. Network Error
**Solution:** Show "Check your internet connection" message, add retry button

### Flutter Error Handling Example

```dart
void handleError(dynamic error) {
  if (error is Map) {
    // API validation error
    if (error.containsKey('message')) {
      showSnackbar(error['message']);
    } else if (error.containsKey('email')) {
      showSnackbar(error['email'][0]);
    } else if (error.containsKey('username')) {
      showSnackbar(error['username'][0]);
    } else if (error.containsKey('password')) {
      showSnackbar(error['password'].join('\n'));
    }
  } else if (error is String) {
    // Network or generic error
    showSnackbar(error);
  }
}

// Usage
final result = await authService.initiateAuth(email, role);
if (!result['success']) {
  handleError(result['error']);
}
```

---

## Security Features

### 1. OTP Security
- **Expiry:** 5 minutes
- **Length:** 6 digits
- **Delivery:** Email only
- **One-time use:** Cleared after verification
- **Rate limiting:** 1 OTP verification per minute

### 2. Password Security
- **Minimum length:** 8 characters
- **Validation:** Django password validators (strength check)
- **Storage:** Hashed using PBKDF2 algorithm
- **Failed attempts:** Max 5 before account lockout

### 3. Account Lockout
- **Trigger:** 5 consecutive failed password attempts
- **Duration:** 5 minutes
- **Reset:** Automatic after timeout or successful login
- **Counter reset:** On successful authentication

### 4. Session Security
- **Expiry:** 15 minutes
- **Storage:** Server-side cache (Redis recommended for production)
- **ID generation:** Cryptographically secure random tokens
- **Single use:** Cleared after token generation

### 5. Token Security
- **Format:** DRF Token (40-character hexadecimal)
- **Storage:** Database with user association
- **Refresh:** New token generated on each login
- **Revocation:** Token deleted on logout

### 6. Rate Limiting
- **OTP verification:** 1 request per minute
- **Password authentication:** 10 requests per minute
- **Initiate auth:** 10 requests per hour

---

## Testing Guide

### Manual Testing Checklist

#### New User Registration Flow
- [ ] Enter valid Gmail address
- [ ] Receive OTP via email
- [ ] Enter correct OTP code
- [ ] Fill registration form with valid data
- [ ] Re-enter password correctly
- [ ] Receive authentication token

#### Existing User Login Flow
- [ ] Enter registered email
- [ ] Receive OTP via email
- [ ] Enter correct OTP code
- [ ] Enter correct password
- [ ] Receive authentication token

#### Error Cases
- [ ] Enter invalid email format → See validation error
- [ ] Enter wrong OTP → See error message
- [ ] Wait 6 minutes → OTP expires
- [ ] Enter duplicate username → See error
- [ ] Enter weak password → See validation errors
- [ ] Enter wrong password 5 times → Account locked
- [ ] Wait 16 minutes → Session expires

### Test Data

#### Valid Test Accounts (for testing)
```
Email: testuser1@gmail.com
Password: TestPass123!
Role: customer

Email: testpro1@gmail.com
Password: TestPass123!
Role: professional
```

#### Valid Phone Numbers
```
0781234567
0791234567
+93781234567
+93791234567
```

#### Invalid Phone Numbers
```
1234567890 (not Afghan format)
0781234 (too short)
0691234567 (invalid prefix)
```

### Postman Collection

Import this JSON to test the API in Postman:

```json
{
  "info": {
    "name": "Service Bridge Auth API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "1. Initiate Auth (Customer)",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"email\": \"test@gmail.com\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/customer/initiate/",
          "host": ["{{base_url}}"],
          "path": ["auth", "customer", "initiate", ""]
        }
      }
    },
    {
      "name": "2. Verify OTP",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"{{session_id}}\",\n  \"otp\": \"123456\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/verify-otp/",
          "host": ["{{base_url}}"],
          "path": ["auth", "verify-otp", ""]
        }
      }
    },
    {
      "name": "3. Complete Registration",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"{{session_id}}\",\n  \"username\": \"testuser\",\n  \"password\": \"TestPass123!\",\n  \"phone\": \"0781234567\",\n  \"first_name\": \"Test\",\n  \"last_name\": \"User\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/complete-registration/",
          "host": ["{{base_url}}"],
          "path": ["auth", "complete-registration", ""]
        }
      }
    },
    {
      "name": "4. Authenticate",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"{{session_id}}\",\n  \"password\": \"TestPass123!\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/authenticate/",
          "host": ["{{base_url}}"],
          "path": ["auth", "authenticate", ""]
        }
      }
    },
    {
      "name": "5. Resend OTP",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"session_id\": \"{{session_id}}\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/auth/resend-otp/",
          "host": ["{{base_url}}"],
          "path": ["auth", "resend-otp", ""]
        }
      }
    }
  ]
}
```

---

## Frequently Asked Questions (FAQ)

### Q1: What happens if the user closes the app mid-flow?
**A:** The session remains active for 15 minutes. If the user reopens the app within that time and has the session_id stored, they can continue from where they left off. Otherwise, they'll need to restart from Step 1.

### Q2: Can I use a custom email domain?
**A:** Currently, only Gmail addresses (@gmail.com) are supported. This is a validation rule on the backend.

### Q3: How long is the authentication token valid?
**A:** Tokens don't expire automatically but are replaced on each new login. Implement token refresh logic on the frontend if needed.

### Q4: What if the user doesn't receive the OTP email?
**A:** Use the Resend OTP endpoint. Also advise users to check their spam/junk folder.

### Q5: Can I customize the OTP email template?
**A:** Yes, the email template is located in `core/email_templates.py` on the backend.

### Q6: How do I handle multiple device logins?
**A:** Each login generates a new token and deletes the old one. Users will be logged out from other devices.

### Q7: Is there a sandbox/test environment?
**A:** Contact your backend team for test environment credentials and base URL.

### Q8: How do I logout a user?
**A:** Call the `/auth/logout/` endpoint with the authentication token in the header. This will delete the token from the server.

```dart
Future<void> logout() async {
  final token = await secureStorage.read(key: 'auth_token');

  await http.post(
    Uri.parse('http://your-domain/auth/logout/'),
    headers: {'Authorization': 'Token $token'},
  );

  await secureStorage.delete(key: 'auth_token');
  await secureStorage.delete(key: 'user_data');
}
```

---

## Support

For technical support or questions:
- **Backend Team:** Contact your Django developer
- **API Issues:** Check the server logs at `D:\sideProjects\service-bridge\general.log`
- **Documentation Updates:** Keep this document synced with API changes

---

## Changelog

### Version 2.0 (January 2026)
- ✅ Introduced unified authentication flow
- ✅ Added OTP 2FA on every login
- ✅ Implemented session-based state management
- ✅ Added account lockout after failed attempts
- ✅ Made first_name and last_name optional
- ✅ Added resend OTP functionality

### Version 1.0 (Previous)
- Basic registration and login endpoints
- Single-step OTP verification for registration only

---

**Document End** - Last Updated: January 2026
