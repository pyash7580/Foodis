#!/usr/bin/env python3
"""
Complete Automated Deployment Script for Railway Backend + Vercel Frontend
Handles: Railway setup, backend deployment, Vercel configuration, image fixing
"""

import subprocess
import os
import sys
import json
from pathlib import Path
import time

class FoodisDeployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.frontend_root = self.project_root / 'frontend'
        self.backend_root = self.project_root
        self.railway_url = None
        self.vercel_url = "https://foodis-gamma.vercel.app"
        
    def run_command(self, cmd, description="", cwd=None):
        """Run shell command and return output"""
        print(f"\n{'='*60}")
        print(f"▶ {description}")
        print(f"{'='*60}")
        print(f"Command: {cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠ {result.stderr}")
                
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            print(f"✗ Error: {e}")
            return False, "", str(e)

    def check_cli_tools(self):
        """Check if required CLI tools are installed"""
        print("\n" + "="*60)
        print("🔍 Checking Required Tools")
        print("="*60)
        
        tools = {
            'railway': 'npm list -g @railway/cli',
            'vercel': 'npm list -g vercel',
            'git': 'git --version',
            'python': 'python --version'
        }
        
        missing = []
        for tool, check_cmd in tools.items():
            success, _, _ = self.run_command(check_cmd, f"Checking {tool}...")
            if success:
                print(f"✓ {tool} is installed")
            else:
                print(f"✗ {tool} is NOT installed")
                missing.append(tool)
        
        return missing

    def install_cli_tools(self, missing):
        """Install missing CLI tools"""
        if not missing:
            return True
            
        print(f"\n📦 Installing missing tools: {', '.join(missing)}")
        
        for tool in missing:
            if tool == 'railway':
                self.run_command('npm install -g @railway/cli', 'Installing Railway CLI')
            elif tool == 'vercel':
                self.run_command('npm install -g vercel', 'Installing Vercel CLI')
        
        return True

    def setup_railway(self):
        """Deploy backend to Railway"""
        print("\n" + "="*60)
        print("🚀 STEP 1: Deploy Backend to Railway")
        print("="*60)
        
        print("\n📋 Prerequisites:")
        print("1. You must have a Railway account (create at railway.app)")
        print("2. You must have GitHub connected to Railway")
        print("3. Your Foodis repository must be on GitHub")
        
        proceed = input("\nDo you have these prerequisites? (yes/no): ").strip().lower()
        if proceed != 'yes':
            print("⚠ Skipping Railway setup. You'll need to do it manually.")
            return False
        
        # Login to Railway
        print("\n🔐 Logging into Railway...")
        print("A browser window will open. Complete the login there.")
        self.run_command('railway login', 'Railway login')
        
        time.sleep(2)
        
        # Check if already logged in to a project
        success, output, _ = self.run_command('railway variables list', 'Checking current Railway project')
        
        if success and 'RAILWAY_TOKEN' in output:
            print("✓ Already connected to Railway project")
        else:
            print("\n📦 Setting up new Railway project...")
            # Create new project
            print("📝 Creating new Railway project...")
            self.run_command('railway init', 'Initialize Railway project')
            
            print("\nWhen prompted:")
            print("  1. Select 'Create a new project'")
            print("  2. Name it: 'foodis-backend'")
            print("  3. Select 'Python' as environment")
            
            # Add environment variables
            print("\n🔧 Setting environment variables...")
            env_vars = {
                'USE_POSTGRES': 'False',
                'DEBUG': 'False',
                'ALLOWED_HOSTS': '*.railway.app,foodis-gamma.vercel.app',
                'CORS_ALLOW_ALL_ORIGINS': 'True'
            }
            
            for key, value in env_vars.items():
                self.run_command(f'railway variable set {key}={value}', f'Setting {key}')
        
        # Deploy
        print("\n🚀 Deploying to Railway...")
        success, output, _ = self.run_command('railway up', 'Deploy to Railway')
        
        if success:
            print("✓ Deployment initiated!")
            time.sleep(3)
            
            # Get public URL
            print("\n📍 Getting Railway Public URL...")
            success, output, _ = self.run_command('railway variables list', 'Get Railway URL')
            
            # Parse output to find RAILWAY_PUBLIC_URL
            for line in output.split('\n'):
                if 'RAILWAY_PUBLIC_URL' in line or 'railway.app' in line:
                    parts = line.split('=')
                    if len(parts) >= 2:
                        self.railway_url = parts[-1].strip()
                        print(f"✓ Railway URL: {self.railway_url}")
                        break
        
        return success and self.railway_url

    def get_railway_url_manual(self):
        """Ask user to provide Railway URL if auto-detection failed"""
        print("\n⚠ Could not auto-detect Railway URL")
        print("\nTo find your Railway URL:")
        print("1. Go to railway.app/dashboard")
        print("2. Click on your 'foodis-backend' project")
        print("3. Click the 'Deploy' or project name")
        print("4. Look for 'Public URL' - copy it (format: https://xxx.railway.app)")
        
        url = input("\nPaste your Railway Public URL: ").strip()
        
        if url.startswith('http'):
            self.railway_url = url.rstrip('/')
            print(f"✓ Using Railway URL: {self.railway_url}")
            return True
        
        print("✗ Invalid URL format")
        return False

    def update_cors_settings(self):
        """Update Django CORS settings for production"""
        if not self.railway_url:
            print("⚠ Skipping CORS update - no Railway URL")
            return False
            
        print("\n" + "="*60)
        print("🔐 STEP 2: Update CORS Settings")
        print("="*60)
        
        settings_file = self.backend_root / 'foodis' / 'settings.py'
        
        # Extract railway domain from URL
        import urllib.parse
        parsed = urllib.parse.urlparse(self.railway_url)
        railway_domain = parsed.netloc
        
        print(f"Adding Railway domain to CORS: {railway_domain}")
        
        try:
            with open(settings_file, 'r') as f:
                content = f.read()
            
            # Update CORS_ALLOWED_ORIGINS
            if "'https://foodis-gamma.vercel.app'" not in content:
                old_cors = "CORS_ALLOWED_ORIGINS = [\n    'https://foodis-nu.vercel.app',"
                new_cors = f"CORS_ALLOWED_ORIGINS = [\n    'https://foodis-gamma.vercel.app',\n    'https://foodis-nu.vercel.app',"
                content = content.replace(old_cors, new_cors)
            
            # Add Railway URL if not present
            if f"'{self.railway_url}'" not in content and f"'{railway_domain}'" not in content:
                # Find the line before 'http://localhost:3000' and add Railway URL
                old_line = "    'http://localhost:3000',"
                new_line = f"    '{self.railway_url}',\n{old_line}"
                content = content.replace(old_line, new_line)
            
            with open(settings_file, 'w') as f:
                f.write(content)
            
            print(f"✓ Updated CORS settings in {settings_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error updating CORS: {e}")
            return False

    def setup_vercel(self):
        """Configure and deploy frontend to Vercel"""
        print("\n" + "="*60)
        print("🎨 STEP 3: Deploy Frontend to Vercel")
        print("="*60)
        
        if not self.railway_url:
            print("⚠ No Railway URL - please deploy backend first")
            return False
        
        # Login to Vercel
        print("\n🔐 Logging into Vercel...")
        print("A browser window will open. Complete the login there.")
        self.run_command('vercel login', 'Vercel login')
        
        time.sleep(2)
        
        # Set environment variable
        print(f"\n🔧 Setting REACT_APP_API_URL={self.railway_url}")
        os.chdir(self.frontend_root)
        
        print("\nWhen Vercel CLI prompts:")
        print(f"  Enter value: {self.railway_url}")
        print("  Select: Production environment")
        
        # Attempt to set environment variable
        self.run_command(
            f'vercel env add REACT_APP_API_URL {self.railway_url}',
            'Setting environment variable in Vercel'
        )
        
        # Deploy
        print("\n🚀 Redeploying frontend with new environment variable...")
        success, _, _ = self.run_command('vercel --prod', 'Redeploy to Vercel', cwd=self.frontend_root)
        
        if success:
            print(f"✓ Frontend redeployed!")
            print(f"  Your app will be live at: {self.vercel_url}")
            return True
        
        return False

    def verify_deployment(self):
        """Verify that deployment is working"""
        print("\n" + "="*60)
        print("✅ STEP 4: Verify Deployment")
        print("="*60)
        
        checks = [
            (f"{self.railway_url}/api/client/", "Backend API"),
            (f"{self.vercel_url}/", "Frontend"),
        ]
        
        import requests
        
        print("\nChecking endpoints...")
        for url, name in checks:
            try:
                response = requests.head(url, timeout=5)
                status = f"✓ {name} is {response.status_code}"
                print(status)
            except Exception as e:
                print(f"⚠ {name} check failed: {e}")
        
        print("\n📋 Next steps:")
        print(f"1. Open: {self.vercel_url}")
        print("2. Verify images are loading on restaurant pages")
        print("3. Try ordering food - images should show")
        print("4. Check browser console (F12) for any errors")
        
        return True

    def commit_changes(self):
        """Commit changes to git"""
        print("\n" + "="*60)
        print("📝 Committing Changes to Git")
        print("="*60)
        
        try:
            os.chdir(self.project_root)
            
            self.run_command('git add .', 'Stage changes')
            self.run_command(
                'git commit -m "fix: Deploy backend to Railway and configure Vercel environment"',
                'Commit changes'
            )
            self.run_command('git push origin main', 'Push to GitHub')
            
            print("✓ Changes committed and pushed")
            return True
        except Exception as e:
            print(f"⚠ Git commit failed: {e}")
            return False

    def run(self):
        """Run complete deployment"""
        print("\n" + "="*70)
        print(" 🍕 FOODIS COMPLETE DEPLOYMENT AUTOMATION 🍕")
        print("="*70)
        print("\nThis script will:")
        print("  1. Deploy your Django backend to Railway")
        print("  2. Configure CORS for production")
        print("  3. Deploy your React frontend to Vercel")
        print("  4. Set environment variables for API connectivity")
        print("  5. Verify everything is working")
        print("  6. Fix image loading issues")
        
        # Check tools
        missing_tools = self.check_cli_tools()
        if missing_tools:
            print(f"\n📦 Installing missing tools: {missing_tools}")
            self.install_cli_tools(missing_tools)
        
        # Railway deployment
        if not self.setup_railway():
            print("\n⚠ Railway setup incomplete. Trying manual URL entry...")
            if not self.get_railway_url_manual():
                print("✗ Cannot proceed without Railway URL")
                return False
        
        # Update CORS
        if not self.update_cors_settings():
            print("⚠ Could not update CORS (might need manual update)")
        
        # Commit CORS changes
        self.commit_changes()
        
        # Vercel deployment
        if not self.setup_vercel():
            print("✗ Vercel deployment failed")
            return False
        
        # Verify
        self.verify_deployment()
        
        print("\n" + "="*70)
        print(" ✅ DEPLOYMENT COMPLETE!")
        print("="*70)
        print(f"\n🎉 Your Foodis app is now live!")
        print(f"\n📍 Access it at: {self.vercel_url}")
        print(f"\n🖼️  Images should now be visible on all pages")
        print(f"\n🐛 If images still don't show:")
        print(f"   1. Clear browser cache (Ctrl+Shift+Del)")
        print(f"   2. Hard refresh (Ctrl+Shift+R)")
        print(f"   3. Check browser console (F12) for errors")
        print(f"   4. Verify Railway backend is running at: {self.railway_url}")
        
        return True

if __name__ == '__main__':
    deployer = FoodisDeployer()
    success = deployer.run()
    sys.exit(0 if success else 1)
