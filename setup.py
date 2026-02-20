"""
Setup script for Foodis project
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    else:
        if result.stdout:
            print(result.stdout)
        return True

def main():
    """Main setup function"""
    print("="*60)
    print("Foodis Project Setup")
    print("="*60)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n⚠️  .env file not found. Creating from .env.example...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ .env file created. Please update it with your configuration.")
        else:
            print("❌ .env.example not found. Please create .env manually.")
            return
    
    # Create necessary directories
    directories = ['media', 'static', 'staticfiles']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Run migrations
    print("\n📦 Running database migrations...")
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        print("❌ Failed to create migrations")
        return
    
    if not run_command("python manage.py migrate", "Applying migrations"):
        print("❌ Failed to apply migrations")
        return
    
    # Collect static files
    print("\n📦 Collecting static files...")
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("\n" + "="*60)
    print("✅ Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update .env file with your configuration")
    print("2. Create a superuser: python manage.py createsuperuser")
    print("3. Start Redis: redis-server")
    print("4. Start Celery worker: celery -A foodis worker -l info")
    print("5. Start Celery beat: celery -A foodis beat -l info")
    print("6. Start Django server: python manage.py runserver")
    print("7. Start React frontend: cd frontend && npm install && npm start")
    print("="*60)

if __name__ == '__main__':
    main()

