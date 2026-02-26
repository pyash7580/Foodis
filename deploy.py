#!/usr/bin/env python3
"""
FOODIS DEPLOYMENT HELPER SCRIPT
Complete automated deployment process
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}")
    print(f"{text}")
    print(f"{'='*50}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}[✓] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}[✗] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}[!] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.CYAN}[i] {text}{Colors.ENDC}")

def run_command(cmd, description=""):
    """Run a shell command and return success status"""
    try:
        if description:
            print_info(f"{description}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print_error(f"Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        print_error(f"Error running command: {str(e)}")
        return False, str(e)

def check_prerequisites():
    """Check if required tools are installed"""
    print_header("Checking Prerequisites")
    
    tools = {
        'git': 'git --version',
        'Node.js/npm': 'npm --version',
        'Python': 'python --version'
    }
    
    all_good = True
    for tool, cmd in tools.items():
        success, _ = run_command(cmd)
        if success:
            print_success(f"{tool} is installed")
        else:
            print_error(f"{tool} is NOT installed")
            all_good = False
    
    return all_good

def get_git_status():
    """Show current git status"""
    success, output = run_command('git status --short', 'Getting git status')
    if success:
        if output.strip():
            print("Current changes:")
            print(output)
        else:
            print("No uncommitted changes")
    return success

def choose_backend_provider():
    """Let user choose backend provider"""
    print_header("Step 1: Choose Backend Provider")
    
    print("Options:")
    print("  1) Railway (https://railway.app) - Recommended")
    print("  2) Render (https://render.com) - Stable free tier")
    print("  3) Heroku (https://heroku.com) - Traditional")
    print("  4) Use existing backend")
    print()
    
    choice = input(f"{Colors.CYAN}Enter your choice (1-4) [1]: {Colors.ENDC}").strip() or "1"
    
    instructions = {
        "1": """
RAILWAY DEPLOYMENT:
1. Install Railway CLI: npm install -g @railway/cli
2. Login: railway login
3. Deploy: railway up --detach
4. Get URL from: https://railway.app/dashboard
""",
        "2": """
RENDER DEPLOYMENT:
1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Use these settings:
   - Build: pip install -r requirements.txt && python manage.py migrate
   - Start: gunicorn foodis.wsgi:application --workers 2 --bind 0.0.0.0:$PORT
   - Env: DEBUG=False, DATABASE_URL=(your db), GOOGLE_MAPS_API_KEY=...
5. Get URL from Render dashboard
""",
        "3": """
HEROKU DEPLOYMENT:
1. Install: https://devcenter.heroku.com/articles/heroku-cli
2. Login: heroku login
3. Create: heroku create your-app-name
4. Deploy: git push heroku main
5. Config: heroku config:set DEBUG=False SECRET_KEY=your_key
""",
        "4": "Using existing backend configuration"
    }
    
    if choice in instructions:
        print(instructions[choice])
    
    return choice

def update_frontend_config(backend_url):
    """Update frontend configuration files"""
    print_header("Step 2: Update Frontend Configuration")
    
    if not backend_url:
        backend_url = input(f"{Colors.CYAN}Enter your backend URL (e.g., https://your-domain.railway.app): {Colors.ENDC}")
    
    if not backend_url:
        print_error("Backend URL is required")
        return False
    
    # Parse URL to extract domain without protocol
    parsed = urlparse(backend_url)
    domain = parsed.netloc or backend_url.replace('https://', '').replace('http://', '')
    
    print_info(f"Using backend URL: {backend_url}")
    print_info(f"Domain: {domain}")
    
    # Update .env.production
    env_prod_path = Path("frontend/.env.production")
    env_content = f"""CI=false
REACT_APP_API_URL={backend_url}
REACT_APP_WS_URL=wss://{domain}/ws
GENERATE_SOURCEMAP=false"""
    
    try:
        env_prod_path.write_text(env_content)
        print_success(f"Updated {env_prod_path}")
    except Exception as e:
        print_error(f"Failed to update {env_prod_path}: {str(e)}")
        return False
    
    # Update vercel.json
    vercel_path = Path("frontend/vercel.json")
    vercel_config = {
        "version": 2,
        "buildCommand": "npm run build",
        "outputDirectory": "build",
        "rewrites": [
            {
                "source": "/(.*)",
                "destination": "/index.html"
            }
        ],
        "env": {
            "DISABLE_ESLINT_PLUGIN": "true",
            "SKIP_PREFLIGHT_CHECK": "true",
            "GENERATE_SOURCEMAP": "false",
            "CI": "false"
        }
    }
    
    try:
        vercel_path.write_text(json.dumps(vercel_config, indent=4))
        print_success(f"Updated {vercel_path}")
    except Exception as e:
        print_error(f"Failed to update {vercel_path}: {str(e)}")
        return False
    
    return True, backend_url

def build_and_test():
    """Build frontend and optionally test"""
    print_header("Step 3: Build Frontend")
    
    choice = input(f"{Colors.CYAN}Build and test locally? (y/n) [y]: {Colors.ENDC}").strip().lower() or "y"
    
    if choice == 'y':
        print_info("Building frontend...")
        success, output = run_command(
            "cd frontend && npm run build",
            "Building React app"
        )
        
        if success:
            print_success("Frontend build successful")
            return True
        else:
            print_error("Frontend build failed")
            print(output)
            return False
    
    return True

def commit_and_push():
    """Commit changes and push to remote"""
    print_header("Step 4: Commit and Push Changes")
    
    print("Current changes:")
    get_git_status()
    print()
    
    choice = input(f"{Colors.CYAN}Commit and push changes? (y/n) [y]: {Colors.ENDC}").strip().lower() or "y"
    
    if choice == 'y':
        msg = input(f"{Colors.CYAN}Enter commit message [fix: Update backend API URL for production]: {Colors.ENDC}").strip()
        if not msg:
            msg = "fix: Update backend API URL for production"
        
        # Stage files
        files_to_stage = [
            "frontend/.env.production",
            "frontend/vercel.json",
            "frontend/src/api/axiosInstance.js",
            "frontend/src/config.js"
        ]
        
        for file in files_to_stage:
            if Path(file).exists():
                run_command(f'git add "{file}"')
        
        # Commit
        success, _ = run_command(f'git commit -m "{msg}"', "Committing changes")
        if not success:
            print_warning("No changes to commit")
            return True
        
        print_success("Changes committed")
        
        # Push
        success, _ = run_command('git push origin main', "Pushing changes to remote")
        if success:
            print_success("Changes pushed successfully")
            return True
        else:
            print_error("Push failed - check your git configuration")
            return False
    
    return True

def show_next_steps(backend_url):
    """Show final instructions"""
    print_header("Deployment Complete!")
    
    print(f"""
{Colors.BOLD}Next Steps:{Colors.ENDC}

1. {Colors.CYAN}Wait for Vercel to rebuild{Colors.ENDC}
   - Rebuilding usually takes 3-5 minutes
   - Monitor at: https://vercel.com/dashboard

2. {Colors.CYAN}Test the deployed application{Colors.ENDC}
   - Visit: https://foodis-gamma.vercel.app/client
   - Open browser console: F12 → Console tab
   - Check for errors (should be clean)

3. {Colors.CYAN}Test functionality{Colors.ENDC}
   - Browse restaurants (should load)
   - Add items to cart
   - Try checkout
   - Place an order

4. {Colors.CYAN}Troubleshooting{Colors.ENDC}
   - If API calls fail, check:
     a) Backend is running: curl {backend_url}/health/
     b) CORS is enabled in Django settings
     c) Environment variables are set in Vercel
   - Check logs in Vercel dashboard

5. {Colors.CYAN}Monitor in production{Colors.ENDC}
   - Vercel: https://vercel.com/dashboard
   - Backend (Railway): https://railway.app/dashboard
   - Database: https://console.neon.tech

{Colors.BOLD}Important URLs:{Colors.ENDC}
- Frontend: https://foodis-gamma.vercel.app/client
- Backend: {backend_url}
- Django Admin: {backend_url}/admin
- API Root: {backend_url}/api/

{Colors.BOLD}Quick Commands:{Colors.ENDC}
- Test backend health: curl {backend_url}/health/
- Run automated tests: python e2e_workflow_test.py
- View Vercel logs: vercel logs foodis-gamma

""")

def main():
    """Main deployment flow"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════╗")
    print("║         FOODIS DEPLOYMENT HELPER              ║")
    print("║     Complete Setup & Deployment Guide         ║")
    print("╚════════════════════════════════════════════════╝")
    print(Colors.ENDC)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_error("Please install missing prerequisites and try again")
        return 1
    
    # Step 2: Show git status
    get_git_status()
    
    # Step 3: Choose backend
    provider = choose_backend_provider()
    
    # Step 4: Get backend URL
    backend_url = input(f"\n{Colors.CYAN}Enter your backend URL: {Colors.ENDC}").strip()
    if not backend_url:
        print_error("Backend URL is required")
        return 1
    
    # Step 5: Update configuration
    result = update_frontend_config(backend_url)
    if not result:
        print_error("Failed to update configuration")
        return 1
    
    # Step 6: Build
    if not build_and_test():
        print_warning("Build failed but continuing with deployment")
    
    # Step 7: Commit and push
    if not commit_and_push():
        print_warning("Failed to push changes - you can do this manually")
    
    # Step 8: Show next steps
    show_next_steps(backend_url)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
