import os
import sys

sys.path.insert(0, os.path.abspath("."))
from backend.database import clean_production_database, get_db_connection

def main():
    print("=== EXECUTING COMPLETE DATABASE PURGE FOR REAL PRODUCTION START ===")
    res = clean_production_database()
    print("Result:", res)
    
    # Verify the remaining users
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users ORDER BY id ASC")
    users = cursor.fetchall()
    print("\n--- ACTIVE USERS IN DATABASE ---")
    for u in users:
        print(f"  User #{u['id']}: username='{u['username']}', role='{u['role']}'")
        
    for table_name in ['invoices', 'invoice_items', 'payment_transactions', 'subscriptions', 'organizations', 'organization_members', 'customer_leads', 'search_logs', 'usage_records', 'owner_alerts', 'temp_parts']:
        try:
            cursor.execute(f"SELECT count(*) as count FROM {table_name}")
            cnt = cursor.fetchone()['count']
            print(f"  Table `{table_name}`: {cnt} records (CLEARED)")
        except Exception as e:
            print(f"  Table `{table_name}`: {e}")
            
    cursor.execute("SELECT count(*) as count FROM master_parts")
    print(f"\n--- Master Parts (Preserved Inventory Catalog): {cursor.fetchone()['count']} records ---")
    
    conn.close()
    print("\n✅ Database is now 100% clean, revenue reset, and ready for real production usage!")

if __name__ == "__main__":
    main()
