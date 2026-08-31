import os
import sqlite3
from datetime import datetime

DB_PATH = os.environ.get("DATABASE_URL", "parts_cross_ref.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Reads migration schema and initializes database tables."""
    migration_path = os.path.join(os.path.dirname(__file__), "migrations", "001_init_schema.sql")
    if not os.path.exists(migration_path):
        # Fallback if path resolved differently
        migration_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend", "migrations", "001_init_schema.sql"))
    
    with open(migration_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    conn = get_db_connection()
    try:
        conn.executescript(sql_script)
        conn.commit()
        print("Database initialized successfully with migrations.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise e
    finally:
        conn.close()

# Initialize on import
init_db()

# ================= USER ACCESS CONTROL =================

def get_user_by_username(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def create_db_user(username: str, password_hash: str, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"success": True, "user_id": user_id}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว"}
    finally:
        conn.close()

def get_all_db_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_db_user(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Prevent deleting the last admin
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        role_row = cursor.fetchone()
        if role_row and role_row['role'] == 'ADMIN':
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'ADMIN'")
            count_row = cursor.fetchone()
            if count_row['count'] <= 1:
                return {"success": False, "error": "ไม่สามารถลบผู้ดูแลระบบ (Admin) คนสุดท้ายได้"}
                
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        conn.close()

def update_db_user_role(user_id: int, role: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user role: {e}")
        return False
    finally:
        conn.close()

# ================= ADVANCED SEARCH & FILTERING =================

def advanced_search_parts(
    vin: str = None,
    car_brand: str = None,
    car_model: str = None,
    car_year: str = None,
    category: str = None,
    oem_code: str = None,
    oem_name: str = None,
    aftermarket_brand: str = None,
    aftermarket_part: str = None
):
    """
    Performs detailed query matches based on separated search input criteria.
    Matches are looked up in master_parts and temp_parts (if status is PENDING_URGENT and not older than 48h).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We will build two select statements (master and active temp) and union them
    where_clauses = []
    params = []
    
    # 1. VIN matching
    # In parts tables, if VIN is provided, we match via description/notes or match model/brand compatibility
    # If the user searches by VIN, we'll try matching part compatibility by analyzing VIN pattern or matches.
    # To keep it simple, we search if VIN is mentioned in notes or description, or if car_brand/model match the query.
    if vin:
        where_clauses.append("(description LIKE ? OR notes LIKE ?)")
        params.append(f"%{vin}%")
        params.append(f"%{vin}%")
        
    # 2. Car Info
    if car_brand:
        where_clauses.append("car_brand LIKE ?")
        params.append(f"%{car_brand}%")
    if car_model:
        where_clauses.append("car_model LIKE ?")
        params.append(f"%{car_model}%")
    if car_year:
        where_clauses.append("(? BETWEEN year_start AND year_end OR year_start LIKE ? OR year_end LIKE ?)")
        params.append(car_year)
        params.append(f"%{car_year}%")
        params.append(f"%{car_year}%")
        
    # 3. Category
    if category:
        where_clauses.append("category LIKE ?")
        params.append(f"%{category}%")
        
    # 4. OEM Code & Product Name
    if oem_code:
        where_clauses.append("oem_number LIKE ?")
        params.append(f"%{oem_code}%")
    if oem_name:
        where_clauses.append("(product_name_th LIKE ? OR product_name_en LIKE ?)")
        params.append(f"%{oem_name}%")
        params.append(f"%{oem_name}%")
        
    # 5. Aftermarket
    if aftermarket_brand:
        where_clauses.append("brand = ?")
        params.append(aftermarket_brand)
    if aftermarket_part:
        where_clauses.append("part_number LIKE ?")
        params.append(f"%{aftermarket_part}%")

    if not where_clauses:
        # Empty search returns empty list
        conn.close()
        return []
        
    where_str = " AND ".join(where_clauses)
    
    # Query Master
    sql_master = f"SELECT *, 'MASTER' as source, 'APPROVED' as status FROM master_parts WHERE {where_str}"
    cursor.execute(sql_master, params)
    master_rows = [dict(r) for r in cursor.fetchall()]
    
    # Query active PENDING_URGENT Temp (TTL < 48 hours)
    sql_temp = f"""
        SELECT *, 'TEMP' as source FROM temp_parts 
        WHERE ({where_str})
          AND status = 'PENDING_URGENT'
          AND datetime(created_at) >= datetime('now', '-48 hours')
    """
    cursor.execute(sql_temp, params)
    temp_rows = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return master_rows + temp_rows

def get_all_parts_system(filter_brand=None, filter_car=None, filter_source=None):
    """
    Returns all data inside the system (both master and temp parts) with optional filters.
    Used for System-wide data view in the Admin dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query Master
    master_clauses = []
    master_params = []
    if filter_brand:
        master_clauses.append("brand LIKE ?")
        master_params.append(f"%{filter_brand}%")
    if filter_car:
        master_clauses.append("(car_brand LIKE ? OR car_model LIKE ?)")
        master_params.append(f"%{filter_car}%")
        master_params.append(f"%{filter_car}%")
        
    master_where = ""
    if master_clauses:
        master_where = "WHERE " + " AND ".join(master_clauses)
        
    sql_master = f"SELECT *, 'MASTER' as source, 'APPROVED' as status FROM master_parts {master_where}"
    
    # Query Temp
    temp_clauses = []
    temp_params = []
    if filter_brand:
        temp_clauses.append("brand LIKE ?")
        temp_params.append(f"%{filter_brand}%")
    if filter_car:
        temp_clauses.append("(car_brand LIKE ? OR car_model LIKE ?)")
        temp_params.append(f"%{filter_car}%")
        temp_params.append(f"%{filter_car}%")
        
    temp_where = ""
    if temp_clauses:
        temp_where = "WHERE " + " AND ".join(temp_clauses)
        
    sql_temp = f"SELECT *, 'TEMP' as source FROM temp_parts {temp_where}"
    
    results = []
    
    if not filter_source or filter_source.upper() == 'MASTER':
        cursor.execute(sql_master, master_params)
        results += [dict(r) for r in cursor.fetchall()]
        
    if not filter_source or filter_source.upper() == 'TEMP':
        cursor.execute(sql_temp, temp_params)
        results += [dict(r) for r in cursor.fetchall()]
        
    conn.close()
    return results

# ================= MOCK/COMPATIBILITY OPERATIONS =================

def fuzzy_search_master(query_str: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    search_term = f"%{query_str}%"
    sql = """
        SELECT * FROM master_parts 
        WHERE brand LIKE ? 
           OR part_number LIKE ? 
           OR oem_number LIKE ? 
           OR car_brand LIKE ? 
           OR car_model LIKE ?
           OR product_name_th LIKE ?
           OR product_name_en LIKE ?
           OR category LIKE ?
    """
    cursor.execute(sql, (search_term, search_term, search_term, search_term, search_term, search_term, search_term, search_term))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insert_temp_part(part_data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        INSERT INTO temp_parts (
            brand, part_number, oem_number, product_name_th, product_name_en, category,
            car_brand, car_model, year_start, year_end, engine, fuel, 
            transmission, description, cost_unit, notes, source_type, status, staff_note
        ) VALUES (
            :brand, :part_number, :oem_number, :product_name_th, :product_name_en, :category,
            :car_brand, :car_model, :year_start, :year_end, :engine, :fuel, 
            :transmission, :description, :cost_unit, :notes, :source_type, :status, :staff_note
        )
    """
    # Ensure all bindings are present in part_data
    keys = [
        'brand', 'part_number', 'oem_number', 'product_name_th', 'product_name_en', 'category',
        'car_brand', 'car_model', 'year_start', 'year_end', 'engine', 'fuel',
        'transmission', 'description', 'cost_unit', 'notes', 'source_type', 'status', 'staff_note'
    ]
    for k in keys:
        if k not in part_data:
            part_data[k] = ""
            
    cursor.execute(sql, part_data)
    temp_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return temp_id

def check_exact_duplicate(brand: str, part_number: str, oem_number: str, car_brand: str, car_model: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    b = brand.strip().upper()
    pn = part_number.strip().upper()
    on = oem_number.strip().upper()
    cb = car_brand.strip().upper()
    cm = car_model.strip().upper()
    
    # Check master_parts
    cursor.execute("""
        SELECT 1 FROM master_parts 
        WHERE UPPER(brand) = ? 
          AND UPPER(part_number) = ? 
          AND UPPER(oem_number) = ? 
          AND UPPER(car_brand) = ? 
          AND UPPER(car_model) = ?
        LIMIT 1
    """, (b, pn, on, cb, cm))
    if cursor.fetchone():
        conn.close()
        return True
        
    # Check temp_parts
    cursor.execute("""
        SELECT 1 FROM temp_parts 
        WHERE UPPER(brand) = ? 
          AND UPPER(part_number) = ? 
          AND UPPER(oem_number) = ? 
          AND UPPER(car_brand) = ? 
          AND UPPER(car_model) = ?
        LIMIT 1
    """, (b, pn, on, cb, cm))
    res = cursor.fetchone() is not None
    conn.close()
    return res

def get_active_temp_parts_sales():
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        SELECT * FROM temp_parts 
        WHERE status = 'PENDING_URGENT' 
          AND datetime(created_at) >= datetime('now', '-48 hours')
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_temp_parts_admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        SELECT *, 
        CASE WHEN status = 'PENDING_URGENT' THEN 1 ELSE 2 END as priority_status,
        CASE WHEN staff_note IS NOT NULL AND staff_note != '' THEN 1 ELSE 2 END as priority_note
        FROM temp_parts
        WHERE status IN ('PENDING', 'PENDING_URGENT')
        ORDER BY priority_status ASC, priority_note ASC, created_at DESC
    """
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def check_is_new_pair(brand, part_number, oem_number, car_brand, car_model):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
        SELECT 1 FROM master_parts 
        WHERE brand = ? AND part_number = ? AND oem_number = ? AND car_brand = ? AND car_model = ?
        LIMIT 1
    """
    cursor.execute(sql, (brand, part_number, oem_number, car_brand, car_model))
    row = cursor.fetchone()
    conn.close()
    return row is None

def approve_temp_part(temp_id: int, updated_data: dict = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if not updated_data:
            cursor.execute("SELECT * FROM temp_parts WHERE id = ?", (temp_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Temporary part not found.")
            data = dict(row)
        else:
            data = updated_data
            data['id'] = temp_id

        master_keys = [
            'brand', 'part_number', 'oem_number', 'product_name_th', 'product_name_en', 'category',
            'car_brand', 'car_model', 'year_start', 'year_end', 'engine', 'fuel',
            'transmission', 'description', 'cost_unit', 'notes'
        ]
        master_data = {k: data.get(k) for k in master_keys}

        upsert_sql = """
            INSERT OR REPLACE INTO master_parts (
                brand, part_number, oem_number, product_name_th, product_name_en, category,
                car_brand, car_model, year_start, year_end, engine, fuel,
                transmission, description, cost_unit, notes, updated_at
            ) VALUES (
                :brand, :part_number, :oem_number, :product_name_th, :product_name_en, :category,
                :car_brand, :car_model, :year_start, :year_end, :engine, :fuel,
                :transmission, :description, :cost_unit, :notes, CURRENT_TIMESTAMP
            )
        """
        cursor.execute(upsert_sql, master_data)
        cursor.execute("DELETE FROM temp_parts WHERE id = ?", (temp_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def edit_temp_part(temp_id: int, updated_fields: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clauses = []
    values = []
    for key, value in updated_fields.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)
    values.append(temp_id)
    sql = f"UPDATE temp_parts SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    try:
        cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def reject_temp_part(temp_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM temp_parts WHERE id = ?", (temp_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def edit_master_part(master_id: int, updated_fields: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    set_clauses = []
    values = []
    for key, value in updated_fields.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)
    values.append(master_id)
    sql = f"UPDATE master_parts SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    try:
        cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_master_part(master_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM master_parts WHERE id = ?", (master_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# ================= METADATA CONTROL METHODS =================

# 1. Get List Operations
def get_meta_aftermarket_brands():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meta_aftermarket_brands ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_meta_car_brands():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meta_car_brands ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_meta_car_models(car_brand: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if car_brand:
        cursor.execute("SELECT * FROM meta_car_models WHERE car_brand = ? ORDER BY name ASC", (car_brand,))
    else:
        cursor.execute("SELECT * FROM meta_car_models ORDER BY car_brand ASC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_meta_car_years():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meta_car_years ORDER BY year DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# 2. Insertion Operations
def add_meta_aftermarket_brand(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO meta_aftermarket_brands (name) VALUES (?)", (name.strip().upper(),))
        conn.commit()
        return {"success": True, "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "แบรนด์นี้มีอยู่แล้ว"}
    finally:
        conn.close()

def add_meta_car_brand(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO meta_car_brands (name) VALUES (?)", (name.strip().upper(),))
        conn.commit()
        return {"success": True, "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "ยี่ห้อนี้มีอยู่แล้ว"}
    finally:
        conn.close()

def add_meta_car_model(car_brand: str, name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO meta_car_models (car_brand, name) VALUES (?, ?)", (car_brand.strip().upper(), name.strip()))
        conn.commit()
        return {"success": True, "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "รุ่นรถนี้มีอยู่แล้ว"}
    finally:
        conn.close()

def add_meta_car_year(year: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO meta_car_years (year) VALUES (?)", (year.strip(),))
        conn.commit()
        return {"success": True, "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "ปีรุ่นนี้มีอยู่แล้ว"}
    finally:
        conn.close()

# 3. Deletion Operations
def delete_meta_aftermarket_brand(brand_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM meta_aftermarket_brands WHERE id = ?", (brand_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_meta_car_brand(brand_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM meta_car_brands WHERE id = ?", (brand_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_meta_car_model(model_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM meta_car_models WHERE id = ?", (model_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def delete_meta_car_year(year_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM meta_car_years WHERE id = ?", (year_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# 4. Update Operations
def update_meta_aftermarket_brand(brand_id: int, new_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE meta_aftermarket_brands SET name = ? WHERE id = ?", (new_name.strip().upper(), brand_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_meta_car_brand(brand_id: int, new_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE meta_car_brands SET name = ? WHERE id = ?", (new_name.strip().upper(), brand_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_meta_car_model(model_id: int, new_brand: str, new_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE meta_car_models SET car_brand = ?, name = ? WHERE id = ?", (new_brand.strip().upper(), new_name.strip(), model_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_meta_car_year(year_id: int, new_year: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE meta_car_years SET year = ? WHERE id = ?", (new_year.strip(), year_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

# ================= AI MODEL KEYS & USAGE TRACKING =================

def get_ai_keys_config():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ai_keys_config ORDER BY model_name ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_ai_key_config(model_name: str, api_key: str = None, is_active: int = 1):
    conn = get_db_connection()
    cursor = conn.cursor()
    key_val = api_key.strip() if api_key else ""
    try:
        # If setting this model as active, deactivate all others first
        if is_active == 1:
            cursor.execute("UPDATE ai_keys_config SET is_active = 0")
            
        cursor.execute("""
            INSERT INTO ai_keys_config (model_name, api_key, is_active, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(model_name) DO UPDATE SET
                api_key = excluded.api_key,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
        """, (model_name.strip(), key_val, is_active))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error setting AI key: {e}")
        return False
    finally:
        conn.close()

def activate_ai_key_config(config_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE ai_keys_config SET is_active = 0")
        cursor.execute("UPDATE ai_keys_config SET is_active = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (config_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error activating AI key config: {e}")
        return False
    finally:
        conn.close()

def delete_ai_key_config(config_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ai_keys_config WHERE id = ?", (config_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting AI key: {e}")
        return False
    finally:
        conn.close()

def log_ai_usage(model_name: str, tokens: int = 0):
    import datetime
    conn = get_db_connection()
    cursor = conn.cursor()
    today_str = datetime.date.today().isoformat() # 'YYYY-MM-DD'
    try:
        cursor.execute("""
            INSERT INTO ai_usage_stats (model_name, usage_date, call_count, tokens_used)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(model_name, usage_date) DO UPDATE SET
                call_count = call_count + 1,
                tokens_used = tokens_used + ?
        """, (model_name.strip(), today_str, tokens, tokens))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging AI usage: {e}")
        return False
    finally:
        conn.close()

def get_ai_usage_stats(start_date: str = None, end_date: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM ai_usage_stats"
    params = []
    
    if start_date and end_date:
        query += " WHERE usage_date >= ? AND usage_date <= ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE usage_date >= ?"
        params.append(start_date)
    elif end_date:
        query += " WHERE usage_date <= ?"
        params.append(end_date)
        
    query += " ORDER BY usage_date DESC, model_name ASC"
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
