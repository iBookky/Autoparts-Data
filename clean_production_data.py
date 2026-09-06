#!/usr/bin/env python3
"""
clean_production_data.py
Utility script to clean mock/test parts, cross-references, search logs, fake leads, and test transactions
to prepare the AutoParts platform for real production deployment.

Preserves:
- All system administrative and customer user accounts (owner, superadmin, admin, staff, customer)
- All metadata taxonomy (Car Brands, Car Models, Production Years, Categories, Aftermarket Brands, AI Models)
- All SaaS plan structures, feature matrices, and entitlements
- Platform settings, branding, and owner tax profile
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, clean_production_database, get_db_connection

def main():
    print("=" * 65)
    print("🚀 AutoParts Platform - Production Database Cleaner & Reset")
    print("=" * 65)
    
    # 1. Initialize schema and migrations if needed
    init_db()
    
    # 2. Execute cleaning
    print("\n🧹 Cleaning mock parts, temporary data, test logs, and demo leads...")
    res = clean_production_database()
    
    if res.get("success"):
        print("✅ SUCCESS: Database has been cleaned successfully!")
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM master_parts")
        p_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM temp_parts")
        t_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM cross_reference_relations")
        cr_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users")
        u_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM meta_categories")
        cat_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM meta_car_brands")
        brand_count = c.fetchone()[0]
        conn.close()
        
        print("\n📊 Current Database State:")
        print(f"  • Master Parts Catalog : {p_count} records (Clean / Ready for real data)")
        print(f"  • Temp Scraped Parts   : {t_count} records (Clean)")
        print(f"  • Cross References     : {cr_count} records (Clean)")
        print(f"  • Active Users Preserved: {u_count} accounts")
        print(f"  • Car Brands Taxonomy  : {brand_count} makes")
        print(f"  • Parts Categories     : {cat_count} categories")
        print("=" * 65)
        print("✨ Platform is 100% ready for real automotive inventory setup!\n")
    else:
        print(f"❌ Error during cleanup: {res.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
