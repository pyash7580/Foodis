"""
Standalone script to dump ALL data from local SQLite db.sqlite3
Run: python export_sqlite.py
Output: sqlite_export.json
"""
import os
import sys
import django

# Force SQLite — override any DB_HOST from .env
os.environ['DB_HOST'] = ''
os.environ['DB_NAME'] = ''
os.environ['DJANGO_SETTINGS_MODULE'] = 'foodis.settings'

# Bootstrap Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test.utils import setup_test_environment
from io import StringIO
from django.core.management import call_command

print("Dumping data from SQLite...")
buf = StringIO()
call_command(
    'dumpdata',
    '--exclude', 'auth.permission',
    '--exclude', 'contenttypes',
    '--natural-foreign',
    '--natural-primary',
    '--indent', '2',
    stdout=buf,
    verbosity=0,
)

output = buf.getvalue()
with open('sqlite_export.json', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"Done! Wrote {len(output):,} bytes to sqlite_export.json")
