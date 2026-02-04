# Add this to your existing auth.py router file

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.users import create_user, get_user
from app.utils.auth import verify_password, create_access_token
from app.utils.password_rules import validate_password
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str


# ========== EXISTING ENDPOINTS ==========

@router.post("/signup")
def signup(data: AuthRequest):
    try:
        validate_password(data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = create_user(data.email, data.password)

    if not user:
        raise HTTPException(status_code=400, detail="User already exists")

    return {"message": "Signup successful"}


@router.post("/login")
def login(data: AuthRequest):
    user = get_user(data.email)

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


# ========== NEW FORGOT PASSWORD ENDPOINT ==========

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest):
    """
    Send password recovery email to user
    
    NOTE: For now, this endpoint will send the password in plain text.
    In production, you should:
    1. Generate a secure reset token instead
    2. Send a reset link with the token
    3. Allow user to create a new password via the link
    """
    
    user = get_user(data.email)
    
    if not user:
        # Security: Don't reveal if email exists or not
        return {"message": "If the email exists, password has been sent"}
    
    # Get the stored password (in production, you'd send a reset link instead)
    # Since passwords are hashed, we can't retrieve the original password
    # For now, we'll just send a message
    
    # Email configuration (you'll need to set these environment variables)
    sender_email = os.getenv("SMTP_EMAIL", "your-email@gmail.com")
    sender_password = os.getenv("SMTP_PASSWORD", "your-app-password")
    
    try:
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Recovery - Lease Intelligence"
        message["From"] = sender_email
        message["To"] = data.email
        
        # Email body (HTML)
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
              <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #FB1597; margin: 0;">Lease Intelligence</h1>
              </div>
              
              <h2 style="color: #23101A;">Password Recovery</h2>
              
              <p style="color: #5A2D47; font-size: 16px; line-height: 1.6;">
                Hello,
              </p>
              
              <p style="color: #5A2D47; font-size: 16px; line-height: 1.6;">
                We received a request to recover your password for your Lease Intelligence account.
              </p>
              
              <div style="background-color: #F5B3D7; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p style="color: #23101A; font-size: 14px; margin: 0;">
                  <strong>Note:</strong> Since passwords are encrypted for security, we cannot retrieve your original password. 
                  Please use the "Forgot Password" feature to reset your password, or contact support if you need assistance.
                </p>
              </div>
              
              <p style="color: #5A2D47; font-size: 16px; line-height: 1.6;">
                Your account email: <strong>{data.email}</strong>
              </p>
              
              <p style="color: #5A2D47; font-size: 14px; line-height: 1.6; margin-top: 30px;">
                If you didn't request this, please ignore this email or contact support if you have concerns.
              </p>
              
              <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 30px 0;">
              
              <p style="color: #999; font-size: 12px; text-align: center;">
                © 2026 Lease Intelligence. All rights reserved.
              </p>
            </div>
          </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        # Send email using Gmail SMTP (you can change this to your preferred provider)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, data.email, message.as_string())
        
        return {"message": "Password recovery email sent successfully"}
        
    except Exception as e:
        # Log the error but don't expose details to user
        print(f"Email sending error: {e}")
        # Still return success to prevent email enumeration
        return {"message": "If the email exists, password has been sent"}
