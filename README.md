CRM System with Real-Time Chat

A full-stack CRM application built with Django, Django REST Framework, React, and WebSockets.
The system allows agents to manage leads, assign customers, track conversations, and communicate with customers in real time.

*Features*
JWT Authentication
Role-based access (Agent / Customer)
Lead Management System
Customer Assignment
Internal Notes for Leads
Real-Time Chat using WebSockets
Typing Indicators
Read / Unread Message Tracking
Protected APIs
Persistent Chat History
Search and Filter Leads

*Tech Stack*
*Backend*
Django
Django REST Framework
Django Channels
Simple JWT
MySQL
Redis

*Frontend*
React
Context API
Axios
React Router
Real-Time Communication
WebSockets
Django Channels
Redis Channel Layer
Project Architecture

*The project follows a layered architecture:*

Frontend (React)
        ↓
REST APIs / WebSockets
        ↓
Django Views & Consumers
        ↓
Serializers
        ↓
Models
        ↓
MySQL Database

*Folder Structure*
crm-project/
│
├── backend/
│   ├── users/
│   ├── leads/
│   ├── chat/
│   └── crm_backend/
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── context/
│   │   └── api/
│
└── README.md

*Project Flow*
1. User Registration

The registration system starts with the custom User model.

The user model stores:

Email
Password
Role
First Name
Last Name
Timestamps
Backend Flow
Request → Serializer → View → Model → Database
Important Files
backend/users/models.py
backend/users/serializers.py
backend/users/views.py

The serializer validates incoming registration data before the view saves it to the database.

2. Authentication (Login)

Users log in using email and password.

After successful authentication:

Access Token is generated
Refresh Token is generated

JWT settings are configured inside:

backend/crm_backend/settings.py

Frontend stores and manages tokens using:

frontend/src/context/AuthContext.jsx
frontend/src/api/axiosInstance.js

This allows authenticated users to access protected routes and APIs.

3. Lead Creation

Agents can create and manage leads after login.

The Lead model stores:

Owner
Customer
Name
Email
Phone
Company
Status
Source
Value
Follow-up Date
Description
Lead Creation Flow
Frontend Form → Serializer → View → Lead Model → Database
Important Files
backend/leads/models.py
backend/leads/serializers.py
backend/leads/views.py

frontend/src/components/LeadForm.jsx
4. Lead Management

Leads can be:

Listed
Updated
Deleted
Filtered
Searched
Frontend Pages
frontend/src/pages/Lead.jsx
frontend/src/pages/LeadDetail.jsx
frontend/src/components/LeadCard.jsx
5. Notes System

Agents can add internal notes to leads.

Each note is linked to:

One Lead
One Author
Important Files
backend/leads/models.py
backend/leads/serializers.py
backend/leads/views.py

frontend/src/components/NoteList.jsx

This helps maintain lead history separately from the main lead description.

6. Customer Account Creation

Customers use the same authentication system as agents.

The registration flow remains:

Request → Serializer → View → User Model → Database

The difference is:

Role is set to customer
7. Customer Assignment to Lead

A customer can be assigned to a lead.

This relationship exists through:

customer = models.ForeignKey(...)

Agents select customers from a dropdown while editing leads.

Important Files
backend/users/views.py
backend/users/urls.py

frontend/src/components/LeadForm.jsx

This step is important because it defines which customer can access the conversation related to that lead.

8. Conversation System

Each lead has exactly one conversation.

The relationship is defined using:

OneToOneField
Conversation Flow

When an agent opens chat:

Backend receives the lead ID
Backend checks for an existing conversation
If not found, get_or_create() creates one
Important Files
backend/chat/models.py
backend/chat/views.py

frontend/src/pages/LeadDetail.jsx
9. Message Storage

Messages are permanently stored in the database.

Each message contains:

Conversation
Sender
Sender Type
Sender Name
Content
Read Status
Timestamp
Important Files
backend/chat/models.py
backend/chat/serializers.py
backend/chat/views.py
Frontend
frontend/src/components/ChatWindow.jsx

This ensures chat history remains persistent.

10. Real-Time Chat with WebSockets

After conversation setup:

Frontend opens a WebSocket connection
JWT token is sent for authentication
Conversation ID is attached
Backend Socket Handling

The consumer:

Validates JWT
Loads the authenticated user
Checks permissions
Joins conversation group
Accepts WebSocket connection
Important Files
backend/crm_backend/asgi.py
backend/crm_backend/routing.py
backend/chat/consumers.py
11. Message Sending Flow
Real-Time Message Flow
Frontend Message
        ↓
WebSocket Consumer
        ↓
Save Message to Database
        ↓
Broadcast to Conversation Group
        ↓
All Connected Users Receive Message

Messages are stored before broadcasting, ensuring the database remains the source of truth.

12. Customer Dashboard & Chat Access

Customers log in using the same authentication system.

Customers can:

View only assigned conversations
Open chat rooms
Communicate with assigned agents
Important Files
frontend/src/pages/CustomerDashboard.jsx
frontend/src/pages/CustomerChatRoom.jsx

The same ChatWindow.jsx component is reused for both agents and customers.

