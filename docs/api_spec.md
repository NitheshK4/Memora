# OpenAPI Technical Specifications: Memora Graph API

The Memora backend is built using FastAPI and JWT bearer credentials.

## 🔑 Authentication Flows

### 1. User Registration
*   **Endpoint**: `POST /register`
*   **Content-Type**: `application/json`
*   **Request Body**:
    ```json
    {
      "username": "alice",
      "password": "super-secure-password"
    }
    ```
*   **Responses**:
    *   `200 OK`: `{"message": "User registered successfully"}`
    *   `400 Bad Request`: `{"detail": "Username already exists"}`

### 2. Token Generation
*   **Endpoint**: `POST /token`
*   **Content-Type**: `application/x-www-form-urlencoded`
*   **Request Body**:
    ```
    username=alice&password=super-secure-password
    ```
*   **Response**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer"
    }
    ```

---

## 🧠 Memory Graph Operations (Protected)

*All requests below require the Header: `Authorization: Bearer <JWT_TOKEN>`*

### 1. Send Dialog Message
*   **Endpoint**: `POST /chat`
*   **Request Body**:
    ```json
    {
      "user_id": "alice",
      "message": "I work at Google in San Francisco",
      "session_id": "sess_101"
    }
    ```
*   **Response**:
    ```json
    {
      "response": "Got it! Remembered that your employer is Google.",
      "extracted_facts": [
        {
          "property_name": "employer",
          "value_raw": "Google",
          "confidence": 0.9,
          "entity_type": "self"
        }
      ],
      "conflits_detected": [],
      "audit_logs": [
        {
          "id": 1,
          "user_id": "alice",
          "event_type": "created",
          "new_value": "Google",
          "reason": "Stored new graph fact.",
          "resolver_type": "rules",
          "created_at": "2026-06-21T15:27:00"
        }
      ],
      "active_memories": [
        {
          "id": 1,
          "user_id": "alice",
          "property_name": "employer",
          "value_canonical": "Google",
          "status": "active",
          "version": 1
        }
      ]
    }
    ```

### 2. Retrieve Graph Node Snapshots
*   **Endpoint**: `GET /graph/snapshot`
*   **Response**:
    ```json
    {
      "nodes": [
        {
          "id": 1,
          "label": "alice (self)",
          "type": "self",
          "name": "alice",
          "properties": {}
        },
        {
          "id": 2,
          "label": "Google (organization)",
          "type": "organization",
          "name": "Google",
          "properties": {}
        }
      ],
      "edges": [
        {
          "id": 1,
          "source": 1,
          "target": 2,
          "label": "works_at"
        }
      ]
    }
    ```

### 3. Trigger Reflection consolidation
*   **Endpoint**: `POST /reflection/trigger`
*   **Response**:
    ```json
    {
      "status": "success",
      "actions_performed": [
        "Merged duplicate entity 'Google Inc.' into 'Google'"
      ],
      "message": "Consolidation complete. 1 optimizations executed."
    }
    ```

### 4. Export Graph representation (Protected)
*   **Endpoint**: `GET /graph/export`
*   **Query Parameters**:
    *   `format` (string, optional): Export format. Options: `json` (default) or `rdf`.
*   **Response (JSON)**:
    ```json
    {
      "nodes": [
        {
          "id": 1,
          "label": "alice (self)",
          "type": "self",
          "name": "alice",
          "properties": {
            "employer": "Google"
          }
        }
      ],
      "edges": []
    }
    ```
*   **Response (RDF Turtle)**:
    ```turtle
    @prefix memora: <http://memora.ai/schema#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    memora:entity_1 a memora:Self ;
        rdfs:label "alice" ;
        memora:employer "Google" .
    ```

