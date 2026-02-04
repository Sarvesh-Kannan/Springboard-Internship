# Car Lease Contract Review and Negotiation AI Assistant

An intelligent, cross-platform mobile application that empowers consumers to understand and negotiate automotive lease and loan contracts using AI-powered analysis and conversational assistance.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flutter](https://img.shields.io/badge/flutter-3.x-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)

## Key Features

- **Automated Contract Analysis**: Extract 50+ parameters from lease contracts using Google Gemini LLM
- **Fairness Scoring**: Transparent 5-dimension scoring system (0-100 points) with color-coded visualization
- **Red Flag Detection**: Automatic identification of potentially unfavorable contract terms
- **VIN Verification**: Real-time vehicle lookup via NHTSA vPIC API
- **AI Chatbot Assistant**: Conversational AI for negotiation strategy and contract explanations
- **Secure Authentication**: JWT-based user authentication with bcrypt password hashing
- **Cross-Platform**: Flutter-based mobile app for iOS, Android, and Web

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)

## Architecture Overview

The system consists of two main components:

1. **Backend (Python/FastAPI)**: RESTful API handling contract analysis, user authentication, VIN lookup, and chatbot interactions
2. **Frontend (Flutter/Dart)**: Cross-platform mobile application with rich UI components and real-time updates

### System Layers

```
┌─────────────────────────────────────────────┐
│   Presentation Layer (Flutter Mobile App)   │
├─────────────────────────────────────────────┤
│            API Layer (FastAPI)              │
├─────────────────────────────────────────────┤
│   Authentication & User Management Layer    │
├─────────────────────────────────────────────┤
│         AI Chatbot Layer (Gemini)           │
├─────────────────────────────────────────────┤
│      Business Logic Layer (Analysis)        │
├─────────────────────────────────────────────┤
│    AI/LLM Layer (Google Gemini Flash)       │
├─────────────────────────────────────────────┤
│   Data Processing Layer (PDF/OCR/Text)      │
└─────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **AI/LLM**: Google Generative AI (Gemini Flash)
- **PDF Processing**: PDFPlumber, PDF2Image, Pytesseract
- **Authentication**: PyJWT, bcrypt
- **External APIs**: NHTSA vPIC API

### Frontend
- **Framework**: Flutter 3.x
- **Language**: Dart
- **UI**: Material Design 3
- **State Management**: Provider/Riverpod
- **HTTP Client**: http package
- **Secure Storage**: flutter_secure_storage

## Prerequisites

### Backend Requirements
- Python 3.11 or higher
- pip (Python package manager)
- Tesseract OCR (for scanned document processing)
- Google Gemini API key

### Frontend Requirements
- Flutter SDK 3.x or higher
- Dart SDK
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)
- Chrome or Edge (for web development)

### System Requirements
- Operating System: Windows 10+, macOS 10.14+, or Linux
- RAM: 8GB minimum, 16GB recommended
- Disk Space: 10GB free space

## Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd car_lease_ai
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   
   **On Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```
   
   **On macOS:**
   ```bash
   brew install tesseract
   ```
   
   **On Windows:**
   - Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Add Tesseract to your system PATH

5. **Set up environment variables**
   ```bash
   # Create .env file in project root
   touch .env
   ```
   
   Add the following to `.env`:
   ```env
   # Google Gemini API
   GOOGLE_API_KEY=your_gemini_api_key_here
   
   # JWT Configuration
   JWT_SECRET=your_secure_jwt_secret_here
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_MINUTES=1440
   
   # Application Settings
   ENVIRONMENT=development
   DEBUG=True
   
   # CORS Settings
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
   ```

6. **Create required directories**
   ```bash
   mkdir -p contracts extracted_text fineline_output uploads
   ```

### Frontend Setup

1. **Navigate to Flutter project**
   ```bash
   cd car_lease_intelligence_app
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure API endpoint**
   
   Create `lib/config/api_config.dart`:
   ```dart
   class ApiConfig {
     static const String baseUrl = 'http://localhost:8000';
     
     // API Endpoints
     static const String authSignup = '$baseUrl/auth/signup';
     static const String authLogin = '$baseUrl/auth/login';
     static const String leaseExtract = '$baseUrl/lease/extract';
     static const String vinLookup = '$baseUrl/vin';
     static const String chatbot = '$baseUrl/chatbot/chat';
   }
   ```

4. **Verify Flutter installation**
   ```bash
   flutter doctor
   ```

## ⚙️ Configuration

### Backend Configuration

**requirements.txt:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pdfplumber==0.10.3
pdf2image==1.16.3
pytesseract==0.3.10
Pillow==10.1.0
google-generativeai==0.3.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
requests==2.31.0
```

### Frontend Configuration

**pubspec.yaml (Key Dependencies):**
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  provider: ^6.1.1
  flutter_secure_storage: ^9.0.0
  file_picker: ^6.1.1
  percent_indicator: ^4.2.3
  intl: ^0.18.1
```

## Running the Application

### Start the Backend Server

**Development Mode** (with auto-reload):
```bash
cd car_lease_ai
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify Backend is Running:**
- API Root: http://localhost:8000/
- Swagger Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Start the Flutter App

**Web Platform:**
```bash
cd car_lease_intelligence_app
flutter run -d chrome
```

**iOS Simulator** (macOS only):
```bash
flutter run -d ios
```

**Android Emulator:**
```bash
flutter run -d android
```

**Build for Release:**
```bash
# Android APK
flutter build apk --release

# iOS (requires macOS and Xcode)
flutter build ios --release

# Web
flutter build web --release
```

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | User registration | No |
| POST | `/auth/login` | User authentication | No |
| POST | `/lease/extract` | Upload and analyze contract | Yes |
| GET | `/vin/{vin}` | VIN lookup | Yes |
| POST | `/chatbot/chat` | Chatbot conversation | Yes |
| GET | `/health` | Health check | No |

### Sample API Requests

**User Registration:**
```bash
curl -X POST "http://localhost:8000/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }'
```

**Contract Analysis:**
```bash
curl -X POST "http://localhost:8000/lease/extract" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -F "file=@contract.pdf"
```

## 📁 Project Structure

### Backend Structure
```
CAR_LEASE_AI/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── routers/
│   │   ├── auth.py                # Authentication endpoints
│   │   ├── chat_bot.py            # Chatbot endpoints
│   │   ├── lease.py               # Contract analysis endpoints
│   │   └── vin.py                 # VIN lookup endpoints
│   └── services/
│       ├── users.py               # User management service
│       └── vin_lookup.py          # NHTSA API integration
├── extract_text.py                # PDF text extraction module
├── fineline.py                    # LLM processing orchestration
├── fairness_score.py              # Contract fairness scoring
├── red_flags.py                   # Red flag detection logic
├── utils.py                       # Common utilities
├── test.py                        # Comprehensive test suite
├── requirements.txt               # Python dependencies
└── .env                           # Environment variables
```

### Frontend Structure
```
CAR_LEASE_INTELLIGENCE_APP/
├── lib/
│   ├── config/
│   │   └── api_config.dart        # API endpoint configuration
│   ├── models/
│   │   ├── user.dart              # User data model
│   │   └── lease_data.dart        # Lease contract model
│   ├── routing/
│   │   └── app_router.dart        # Navigation configuration
│   ├── screens/
│   │   ├── login_page.dart        # Login screen
│   │   ├── signup_page.dart       # Registration screen
│   │   ├── forgot_password_page.dart
│   │   └── home_page.dart         # Main dashboard
│   ├── services/
│   │   ├── auth_service.dart      # Authentication API client
│   │   └── lease_service.dart     # Contract analysis API client
│   ├── widgets/
│   │   └── chat_bot.dart          # Chatbot UI widget
│   └── main.dart                  # Flutter app entry point
├── pubspec.yaml                   # Flutter dependencies
└── README.md
```

## Testing

### Backend Testing

**Run the test suite:**
```bash
cd car_lease_ai
python test.py
```

**Test individual endpoints:**
```bash
# Test health check
curl http://localhost:8000/health

# Test contract extraction
curl -X POST http://localhost:8000/lease/extract \
  -H "Authorization: Bearer <token>" \
  -F "file=@contracts/sample_lease.pdf"
```

### Frontend Testing

**Run Flutter tests:**
```bash
cd car_lease_intelligence_app
flutter test
```

## Deployment

### Backend Deployment (Docker)

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t carlease-api .
docker run -p 8000:8000 --env-file .env carlease-api
```

### Frontend Deployment

**iOS (App Store):**
```bash
flutter build ios --release
# Upload to App Store Connect via Xcode
```

**Android (Google Play):**
```bash
flutter build appbundle --release
# Upload to Google Play Console
```

**Web (Static Hosting):**
```bash
flutter build web --release
# Deploy build/web/ folder to Firebase Hosting, Netlify, or Vercel
```

## License

- This project is licensed under the MIT License.
- This project is part of the Springboard Internship program.

## Author

Sarvesh Kannan

## Acknowledgments

- Google Gemini API for LLM capabilities
- NHTSA vPIC API for vehicle data
- Flutter team for the cross-platform framework
- FastAPI for the modern Python web framework

---

**Built using AI and modern technologies**
