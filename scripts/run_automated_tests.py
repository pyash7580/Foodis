import os
import subprocess
import sys
from pathlib import Path

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent

def run_command(command, cwd, label):
    print(f"\n>>> Running {label} tests...")
    print("-" * 40)
    try:
        # Use shell=True for Windows compatibility with scripts like npm
        process = subprocess.run(command, cwd=cwd, shell=True, check=False, capture_output=False)
        if process.returncode == 0:
            print(f"\n[PASS] {label} tests passed!")
            return True
        else:
            print(f"\n[FAIL] {label} tests failed with exit code {process.returncode}")
            return False
    except Exception as e:
        print(f"\n[ERROR] Failed to execute {label} tests: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("      FOODIS UNIFIED TEST RUNNER")
    print("=" * 60)

    # 1. Backend Tests
    backend_success = run_command("python manage.py test", BASE_DIR, "Django Backend")

    # 2. Frontend Tests
    # Note: CI=true prevents interactive mode in react-scripts test
    os.environ["CI"] = "true"
    frontend_success = run_command("npm test -- --watchAll=false --passWithNoTests", BASE_DIR / "frontend", "React Frontend")

    print("\n" + "=" * 60)
    print("      TEST SUMMARY")
    print("-" * 60)
    print(f"Backend Tests : {'PASS' if backend_success else 'FAIL'}")
    print(f"Frontend Tests: {'PASS' if frontend_success else 'FAIL'}")
    print("=" * 60)

    if not backend_success or not frontend_success:
        print("\nTIP: Check the logs above for specific failures.")
        print("To debug, you can run specific tests or ask Antigravity for help.")
        sys.exit(1)
    else:
        print("\nAll systems operational. Great job!")
        sys.exit(0)

if __name__ == "__main__":
    main()
