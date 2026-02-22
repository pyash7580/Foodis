import os

filepath = r'd:\Foodis\core\views.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''            otp_code = None
            if phone:
                logger.debug(f"Calling send_otp for phone: {phone}")
                otp_code = send_otp(phone)
            elif email:
                logger.debug(f"Calling send_email_otp for email: {email}")
                otp_code = send_email_otp(email)
            
            return Response({
                'message': 'OTP sent successfully',
                'otp': otp_code  # Remove in production
            }, status=status.HTTP_200_OK)'''

replacement = '''            otp_code = None
            flow = "REGISTER"
            is_registered = False

            if phone:
                clean_phone_num = normalize_phone(phone)
                user = find_user_by_phone(clean_phone_num)
                if user:
                    flow = "LOGIN"
                    is_registered = True
                    
                logger.debug(f"Calling send_otp for phone: {phone}")
                otp_code = send_otp(phone)
            elif email:
                user = User.objects.filter(email=email).first()
                if user:
                    flow = "LOGIN"
                    is_registered = True
                    
                logger.debug(f"Calling send_email_otp for email: {email}")
                otp_code = send_email_otp(email)
            
            return Response({
                'message': 'OTP sent successfully',
                'otp': otp_code,  # Remove in production
                'flow': flow,
                'is_registered': is_registered,
                'is_new_user': not is_registered
            }, status=status.HTTP_200_OK)'''

if target in content:
    content = content.replace(target, replacement)
elif target.replace('\n', '\r\n') in content:
    content = content.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
else:
    print('Failed to find target in core/views.py')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('core/views.py replaced')
