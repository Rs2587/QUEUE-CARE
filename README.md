# Crash-Free Patient Appointment Booking System

## Project Objective
To design a **crash-free patient appointment system** that ensures reliable booking during
high-traffic conditions by strictly controlling request flow and appointment allocation.

---

## Problem Statement
Traditional appointment systems often crash when multiple patients attempt to book
appointments simultaneously during peak hours. This leads to server overload, failed bookings,
and poor user experience.

---

## Solution Overview
This system allows patient appointment booking only within a **fixed time window** and
limits the number of daily appointments to prevent overload. It provides **SMS-style responses**
to users, ensuring clarity and reliability even when slots are unavailable.

---

## Key Objectives
- Allow **only 50 patients per day** to book appointments
- Accept requests **only between 8:00 – 8:05 AM**
- Automatically assign:
  - Token number
  - Appointment time slot
- Prevent server crashes by rejecting excess requests gracefully
- Send clear SMS-style responses for all cases

---

## System Responses
The system sends structured SMS-style messages:

### Successful Booking
```json
{
  "SMS": "Your token number is 1. Your appointment time is 09:00 - 09:10."
}
