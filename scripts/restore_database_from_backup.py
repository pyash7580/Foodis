#!/usr/bin/env python
"""
Restore database from a backup file (e.g. after migrations wiped the DB).

Use this to bring back your old restaurant, rider, and user data from a
backup of db.sqlite3 (or a copy you made before running migrations).

Images: if you use local media/, restore the media/ folder from your backup too.
If you use Cloudinary, image URLs in the DB will work once the DB is restored.

Usage:
  1. Copy your old database file to one of these names (in project root):
     - db.sqlite3.backup   (default)
     - or pass path as first argument
  2. Run: python scripts/restore_database_from_backup.py
  3. Confirm when prompted; script will replace current db.sqlite3 with the backup.
  4. Run migrations if needed: python manage.py migrate
  5. If you had local media files, copy your backup media/ folder over the current one.
"""

import os
import sys
import shutil
from pathlib import Path

# Project root (parent of scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_BACKUP = PROJECT_ROOT / "db.sqlite3.backup"
CURRENT_DB = PROJECT_ROOT / "db.sqlite3"


def main():
    backup_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BACKUP
    if not backup_path.is_absolute():
        backup_path = PROJECT_ROOT / backup_path

    if not backup_path.exists():
        print(f"Backup file not found: {backup_path}")
        print("\nTo restore your data:")
        print("  1. Locate your old database file (e.g. from a backup or another machine).")
        print("  2. Copy it to:", DEFAULT_BACKUP)
        print("  3. Run this script again.")
        print("\nIf you use PostgreSQL in production, restore from your provider's backup instead.")
        return 1

    if not CURRENT_DB.exists():
        print("Current database not found; will create it from backup.")
    else:
        size_mb = CURRENT_DB.stat().st_size / (1024 * 1024)
        print(f"Current database: {CURRENT_DB} ({size_mb:.2f} MB)")
    print(f"Backup file:      {backup_path} ({backup_path.stat().st_size / 1024:.1f} KB)")

    try:
        confirm = input("\nReplace current database with this backup? Type 'yes' to confirm: ").strip().lower()
    except EOFError:
        confirm = "no"
    if confirm != "yes":
        print("Aborted.")
        return 0

    # Optional: keep a copy of current DB before overwriting
    if CURRENT_DB.exists():
        safety = PROJECT_ROOT / "db.sqlite3.before_restore"
        shutil.copy2(CURRENT_DB, safety)
        print(f"Current DB saved as: {safety}")

    shutil.copy2(backup_path, CURRENT_DB)
    print("Restore complete. Database replaced with backup.")

    print("\nNext steps:")
    print("  1. Run migrations if needed:  python manage.py migrate")
    print("  2. If you use local media/, restore your backup media/ folder so images show again.")
    print("  3. If you use Cloudinary, image URLs in the DB will work as-is.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
