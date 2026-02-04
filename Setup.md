# Car Lease AI - Complete Setup Guide

This guide provides detailed, step-by-step instructions for setting up the Car Lease Contract Review and Negotiation AI Assistant on your local machine.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup (Optional)](#database-setup-optional)
6. [Running the Application](#running-the-application)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)
- **CPU**: Dual-core processor, 2.0 GHz or faster
- **RAM**: 8 GB
- **Storage**: 10 GB free space
- **Internet**: Stable connection for API calls

### Recommended Requirements
- **CPU**: Quad-core processor, 2.5 GHz or faster
- **RAM**: 16 GB
- **Storage**: 20 GB free space (SSD preferred)

---

## Backend Setup

### Step 1: Install Python

**Windows:**
1. Download Python 3.11+ from https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version
pip3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verify installation
python3.11 --version
pip3 --version
```

### Step 2: Install Tesseract OCR

Tesseract is required for processing scanned PDF documents.

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default installation path: `C:\Program Files\Tesseract-OCR`)
3. Add to PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click "OK" to save

4. Verify installation:
   ```cmd
   tesseract --version
   ```

**macOS:**
```bash
brew install tesseract

# Verify installation
tesseract --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr

# Verify installation
tesseract --version
```

### Step 3: Install Poppler (for PDF to Image conversion)

**Windows:**
1. Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\Library\bin` to PATH (same process as Tesseract)

**macOS:**
```bash
brew install poppler
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install poppler-utils
```

### Step 4: Clone the Repository

```bash
# Create a project directory
mkdir ~/projects
cd ~/projects

# Clone the repository
git clone <your-repository-url> car_lease_ai
cd car_lease_ai
```

### Step 5: Create Virtual Environment

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt.

### Step 6: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected dependencies:**
- fastapi
- uvicorn
- pdfplumber
- pdf2image
- pytesseract
- Pillow
- google-generativeai
- python-jose
- passlib
- python-dotenv
- requests

### Step 7: Create Directory Structure

```bash
mkdir -p contracts extracted_text fineline_output uploads
```

**Directory purposes:**
- `contracts/`: Sample lease contract PDFs
- `extracted_text/`: Cached extracted text from PDFs
- `fineline_output/`: LLM processing results
- `uploads/`: Temporary storage for user-uploaded files

### Step 8: Obtain Google Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the generated API key (you'll need this for the `.env` file)

### Step 9: Create Environment Configuration File

Create a `.env` file in the project root:

```bash
# On Windows
type nul > .env

# On macOS/Linux
touch .env
```

Open `.env` in a text editor and add:

```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_actual_gemini_api_key_here

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_min_32_characters_long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# Application Settings
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# CORS Settings (add your Flutter app URLs)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:52000

# File Upload Settings
MAX_UPLOAD_SIZE=10485760
ALLOWED_FILE_TYPES=application/pdf

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
```

**Security Note:** 
- Replace `your_actual_gemini_api_key_here` with your actual API key
- Generate a strong JWT secret (at least 32 characters)
- Never commit `.env` file to version control (add to `.gitignore`)

### Step 10: Verify Backend Installation

```bash
# Run health check test
python test.py

# If successful, you should see:
# Test 1: Root Endpoint - PASSED
# Test 2: Health Check - PASSED
# etc.
```

---

## Frontend Setup

### Step 1: Install Flutter SDK

**Windows:**
1. Download Flutter SDK from: https://docs.flutter.dev/get-started/install/windows
2. Extract to `C:\src\flutter`
3. Add `C:\src\flutter\bin` to PATH
4. Open a new terminal and run:
   ```cmd
   flutter doctor
   ```

**macOS:**
```bash
# Download Flutter
cd ~/development
curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/flutter_macos_arm64_3.x.x-stable.zip
unzip flutter_macos_arm64_3.x.x-stable.zip

# Add to PATH
echo 'export PATH="$PATH:`pwd`/flutter/bin"' >> ~/.zshrc
source ~/.zshrc

# Verify installation
flutter doctor
```

**Linux:**
```bash
# Download Flutter
cd ~/development
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.x.x-stable.tar.xz
tar xf flutter_linux_3.x.x-stable.tar.xz

# Add to PATH
echo 'export PATH="$PATH:~/development/flutter/bin"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
flutter doctor
```

### Step 2: Install Platform-Specific Tools

**For iOS Development (macOS only):**
1. Install Xcode from App Store
2. Open Xcode and accept license agreements
3. Install iOS Simulator:
   ```bash
   xcode-select --install
   sudo xcodebuild -license
   ```

**For Android Development:**
1. Download Android Studio from: https://developer.android.com/studio
2. Install Android Studio
3. Open Android Studio → More Actions → SDK Manager
4. Install:
   - Android SDK Platform-Tools
   - Android SDK Build-Tools
   - Android Emulator
5. Create an Android Virtual Device (AVD):
   - Tools → Device Manager → Create Device

**For Web Development:**
- Chrome or Edge browser (usually pre-installed)

### Step 3: Verify Flutter Installation

```bash
flutter doctor
```

**Expected output:**
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.x.x)
[✓] Android toolchain - develop for Android devices
[✓] Xcode - develop for iOS and macOS (macOS only)
[✓] Chrome - develop for the web
[✓] Android Studio
[✓] VS Code
[✓] Connected device
```

**Fix any issues marked with `[✗]` before proceeding.**

### Step 4: Navigate to Flutter Project

```bash
cd car_lease_intelligence_app
```

### Step 5: Install Flutter Dependencies

```bash
flutter pub get
```

This downloads all required packages defined in `pubspec.yaml`.

### Step 6: Configure API Endpoints

Create `lib/config/api_config.dart`:

```dart
class ApiConfig {
  // Development configuration
  static const String baseUrl = 'http://localhost:8000';
  
  // For Android Emulator, use: 'http://10.0.2.2:8000'
  // For iOS Simulator, use: 'http://localhost:8000'
  // For physical device, use your computer's IP: 'http://192.168.1.X:8000'
  
  // API Endpoints
  static const String authSignup = '$baseUrl/auth/signup';
  static const String authLogin = '$baseUrl/auth/login';
  static const String leaseExtract = '$baseUrl/lease/extract';
  static const String vinLookup = '$baseUrl/vin';
  static const String chatbot = '$baseUrl/chatbot/chat';
  static const String health = '$baseUrl/health';
  
  // Request timeout
  static const Duration timeout = Duration(seconds: 30);
  
  // File upload limits
  static const int maxFileSize = 10 * 1024 * 1024; // 10MB
}
```

**📱 Important Notes for Different Platforms:**

- **Android Emulator**: Use `10.0.2.2` instead of `localhost`
- **iOS Simulator**: Use `localhost` or `127.0.0.1`
- **Physical Device**: Use your computer's local IP address
  ```bash
  # Find your IP address:
  # Windows: ipconfig
  # macOS: ifconfig | grep "inet "
  # Linux: hostname -I
  ```

### Step 7: Update CORS Settings

Update the backend `.env` file with your Flutter app URLs:

```env
# Add your device-specific URLs
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://10.0.2.2:8000,http://192.168.1.X:8000
```

---

## Environment Configuration

### Backend Environment Variables

Create/update `.env` file in the backend root directory:

```env
# ======================
# Google Gemini API
# ======================
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# ======================
# JWT Configuration
# ======================
JWT_SECRET=your_super_secret_jwt_key_at_least_32_characters_long_random_string
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# ======================
# Application Settings
# ======================
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# ======================
# CORS Settings
# ======================
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://10.0.2.2:8000

# ======================
# File Upload Settings
# ======================
MAX_UPLOAD_SIZE=10485760
ALLOWED_FILE_TYPES=application/pdf

# ======================
# Rate Limiting
# ======================
RATE_LIMIT_PER_MINUTE=10

# ======================
# Database (Optional)
# ======================
# DATABASE_URL=postgresql://user:password@localhost:5432/carlease_db

# ======================
# Redis (Optional)
# ======================
# REDIS_URL=redis://localhost:6379/0
```

### Generating Secure JWT Secret

**Using Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Using OpenSSL:**
```bash
openssl rand -base64 32
```

---

## Database Setup (Optional)

For production use, set up PostgreSQL for persistent data storage.

### Install PostgreSQL

**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer and remember the password you set

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Create Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE carlease_db;
CREATE USER carlease_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE carlease_db TO carlease_user;

# Exit psql
\q
```

### Update .env with Database URL

```env
DATABASE_URL=postgresql://carlease_user:your_secure_password@localhost:5432/carlease_db
```

---

## Running the Application

### Start Backend Server

**Terminal 1 - Backend:**
```bash
cd car_lease_ai

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend is running:**
- Open browser: http://localhost:8000/docs
- You should see the Swagger API documentation

### Start Flutter App

**Terminal 2 - Frontend:**

**For Web:**
```bash
cd car_lease_intelligence_app
flutter run -d chrome
```

**For iOS Simulator:**
```bash
flutter run -d ios
```

**For Android Emulator:**
```bash
# Start Android emulator first (or use Android Studio)
flutter emulators --launch <emulator_id>

# Run app
flutter run -d android
```

**For Physical Device:**
1. Enable USB debugging on your device
2. Connect via USB
3. Run:
   ```bash
   flutter devices  # Find your device ID
   flutter run -d <device_id>
   ```

---

## Troubleshooting

### Backend Issues

**Problem: "ModuleNotFoundError: No module named 'fastapi'"**
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem: "tesseract is not installed or it's not in your PATH"**
```bash
# Verify Tesseract installation
tesseract --version

# If not found, reinstall and add to PATH (see Step 2)
```

**Problem: "google.generativeai.types.generation_types.BlockedPromptException"**
- Your API key might be invalid or expired
- Check quota limits on Google AI Studio
- Verify API key in `.env` file

**Problem: Port 8000 already in use**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Problem: "flutter: command not found"**
```bash
# Verify Flutter is in PATH
echo $PATH  # macOS/Linux
echo %PATH%  # Windows

# Add Flutter to PATH (see Frontend Setup Step 1)
```

**Problem: "Gradle build failed" (Android)**
```bash
# Clean and rebuild
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter run
```

**Problem: "Error connecting to API"**
- Ensure backend server is running
- Check `api_config.dart` has correct URL
- For Android emulator, use `http://10.0.2.2:8000`
- For physical device, use computer's local IP
- Verify CORS settings in backend `.env`

**Problem: "CocoaPods not installed" (iOS)**
```bash
sudo gem install cocoapods
cd ios
pod install
cd ..
flutter run
```

### Network Issues

**Problem: Cannot connect from mobile device to backend**

1. Find your computer's IP:
   ```bash
   # Windows
   ipconfig
   
   # macOS
   ifconfig | grep "inet "
   
   # Linux
   hostname -I
   ```

2. Update `api_config.dart`:
   ```dart
   static const String baseUrl = 'http://192.168.1.X:8000';
   ```

3. Ensure firewall allows incoming connections on port 8000

4. Update backend CORS:
   ```env
   ALLOWED_ORIGINS=http://192.168.1.X:8000
   ```

---

## Production Deployment

### Backend Deployment Checklist

- [ ] Set `ENVIRONMENT=production` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Use strong JWT secret (32+ characters)
- [ ] Configure PostgreSQL database
- [ ] Set up Redis for caching
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS origins
- [ ] Set up logging and monitoring
- [ ] Implement rate limiting
- [ ] Set up automated backups
- [ ] Use environment-specific secrets management

### Frontend Deployment Checklist

- [ ] Update `baseUrl` to production API URL
- [ ] Enable HTTPS for API calls
- [ ] Build release versions:
  ```bash
  flutter build apk --release      # Android
  flutter build ios --release      # iOS
  flutter build web --release      # Web
  ```
- [ ] Set up app signing (Android/iOS)
- [ ] Configure app icons and splash screens
- [ ] Submit to app stores (if applicable)
- [ ] Set up analytics and crash reporting

### Recommended Production Stack

**Backend Hosting:**
- AWS Elastic Beanstalk
- Google Cloud Run
- DigitalOcean App Platform
- Heroku

**Database:**
- AWS RDS (PostgreSQL)
- Google Cloud SQL
- DigitalOcean Managed Database

**Frontend Hosting:**
- Firebase Hosting (Web)
- Netlify (Web)
- Vercel (Web)
- App Store / Google Play (Mobile)

---

## Next Steps

1. Complete the setup following this guide
2. Read the [README.md](README.md) for project overview
3. Run the test suite: `python test.py`
4. Explore API documentation: http://localhost:8000/docs
5. Start developing your features!

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review error logs in the terminal
3. Search for similar issues in the project repository
4. Contact the development team

---

**Setup complete! You're ready to start developing with Car Lease AI.**
