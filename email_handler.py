import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailHandler:
    def __init__(self):
        # Initialize without requiring .env file
        self.sender_email = None
        self.app_password = None
    
    def configure(self, email, password):
        """Configure email credentials"""
        self.sender_email = email
        self.app_password = password
        
    def send_otp(self, receiver_email):
        # Skip email sending if credentials aren't configured
        if not self.sender_email or not self.app_password:
            print("Email credentials not configured - skipping email send")
            return "123456"  # Return default OTP for testing
            
        try:
            otp = str(random.randint(100000, 999999))
            
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = "Secure File System - Your OTP Verification"
            
            body = f"""
            <html>
              <body style='font-family: Arial, sans-serif;'>
                <h2 style='color: #2C3E50;'>Email Verification</h2>
                <p>Your OTP for verification is:</p>
                <h1 style='color: #3498DB; font-size: 32px;'>{otp}</h1>
                <p>This OTP will expire in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
              </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.app_password)
                server.send_message(msg)
                print(f"OTP sent successfully to {receiver_email}")
                
            return otp
        except Exception as e:
            print(f"Error sending email: {e}")
            return "123456"  # Return default OTP for testing if email fails 