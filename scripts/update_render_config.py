import requests
import os
import json
from decouple import config

def update_render_service():
    api_key = config('RENDER_API_KEY')
    service_id = 'srv-d6ckpi7pm1nc73994lf0'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    # Correct build and start commands
    build_cmd = 'pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate'
    start_cmd = 'daphne -b 0.0.0.0 -p $PORT foodis.asgi:application'
    
    data = {
        'serviceDetails': {
            'envSpecificDetails': {
                'buildCommand': build_cmd,
                'startCommand': start_cmd
            }
        }
    }
    
    print(f"Updating service {service_id}...")
    r = requests.patch(f'https://api.render.com/v1/services/{service_id}', headers=headers, json=data)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("Success!")
        print(json.dumps(r.json()['serviceDetails']['envSpecificDetails'], indent=2))
        
        # Now trigger deploy
        print("Triggering deploy...")
        requests.post(f'https://api.render.com/v1/services/{service_id}/deploys', headers=headers, json={'clearCache': 'clear'})
        print("Deploy triggered.")
    else:
        print(f"Error: {r.text}")

if __name__ == '__main__':
    update_render_service()
