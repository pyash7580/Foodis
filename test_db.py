import psycopg2
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    print("Testing port 6543 (Pooler)...")
    conn = psycopg2.connect(
        host='aws-1-ap-south-1.pooler.supabase.com',
        port=6543,
        dbname='postgres',
        user='postgres.bsuspfqdifzsokigqdzw',
        password='Patelyash@123',
        sslmode='require'
    )
    print('Success on 6543!')
    conn.close()
except Exception as e:
    print(f'Failed on 6543: {e}')

try:
    print("\nTesting port 5432 (Direct)...")
    conn = psycopg2.connect(
        host='aws-1-ap-south-1.pooler.supabase.com',
        port=5432,
        dbname='postgres',
        user='postgres.bsuspfqdifzsokigqdzw',
        password='Patelyash@123',
        sslmode='require'
    )
    print('Success on 5432!')
    conn.close()
except Exception as e:
    print(f'Failed on 5432: {e}')

try:
    print("\nTesting original db host just in case (db.bsuspfqdifzsokigqdzw.supabase.co)...")
    conn = psycopg2.connect(
        host='db.bsuspfqdifzsokigqdzw.supabase.co',
        port=5432,
        dbname='postgres',
        user='postgres',
        password='Patelyash@123',
        sslmode='require'
    )
    print('Success on direct host!')
    conn.close()
except Exception as e:
    print(f'Failed on direct host: {e}')
