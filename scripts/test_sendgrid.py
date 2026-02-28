import smtplib
from email.mime.text import MIMEText

def test_send_email():
    smtp_server = "smtp.sendgrid.net"
    smtp_port = 587
    username = "apikey"
    import os
    password = os.environ.get("SENDGRID_API_KEY", "YOUR_API_KEY_HERE")
    
    sender = "noreply@foodis.com"
    recipient = "pyash7580@gmail.com"
    
    msg = MIMEText("This is a test email from smtplib.")
    msg['Subject'] = "Foodis - smtplib Test"
    msg['From'] = sender
    msg['To'] = recipient
    
    print(f"Connecting to {smtp_server}:{smtp_port}...")
    try:
        # Create a custom SSL context that doesn't verify certificates
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(sender, [recipient], msg.as_string())
        server.quit()
        print("Email sent successfully via smtplib!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    test_send_email()

if __name__ == '__main__':
    test_send_email()
