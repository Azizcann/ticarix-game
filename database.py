import sqlite3
import hashlib
import json
import time

DB_FILE = "ticarix_users.db"

def init_db():
    """Veritabanını ve gerekli tabloları oluşturur."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Kullanıcılar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            game_data TEXT NOT NULL
        )
    ''')
    # Ortak Klanlar Tablosu (F5'te silinmemesi için global)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clans (
            clan_name TEXT PRIMARY KEY,
            clan_data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Şifreleri SHA-256 ile güvenli hale getirir."""
    return hashlib.sha256(password.encode()).hexdigest()

def get_default_game_data():
    """Yeni kayıt olan bir oyuncunun başlangıç oyun verilerini döndürür."""
    return {
        "money": 2500,
        "bank_balance": 0,
        "bank_debt": 0,
        "tcmb_policy_rate": 37.0,
        "last_bank_interest_time": time.time(),
        "last_shop_income_time": time.time(),
        "clan_name": "La Familia",
        "user_clan": None,
        "clan_members": 1,
        "accumulated_shop_money": 0,
        "active_job": None,
        "mine_level": 1,
        "mine_xp": 0,
        "mine_inventory": {"Kömür": 0, "Bakır": 0, "Demir": 0, "Gümüş": 0, "Altın": 0, "Elmas": 0},
        "mine_last_time": time.time(),
        "fish_level": 1,
        "fish_xp": 0,
        "fish_inventory": {"Sazan": 0, "Alabalık": 0, "Levrek": 0, "Somon": 0, "Kalkan": 0, "Kılıç Balığı": 0},
        "fish_last_time": time.time(),
        "shops": {
            "bakkal": {"name": "Mahalle Bakkalı", "count": 0, "cost": 500, "income": 15},
            "cafe": {"name": "Sahil Kafe", "count": 0, "cost": 4500, "income": 85},
            "holding": {"name": "Ticarix Plaza", "count": 0, "cost": 40000, "income": 550}
        }
    }

def register_user(username, email, password):
    """Yeni kullanıcı kaydı yapar."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        hashed_p = hash_password(password)
        initial_data = json.dumps(get_default_game_data(), ensure_ascii=False)
        
        cursor.execute("INSERT INTO users (username, email, password_hash, game_data) VALUES (?, ?, ?, ?)",
                       (username, email, hashed_p, initial_data))
        conn.commit()
        conn.close()
        return True, "Kayıt başarılı!"
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı veya e-posta zaten kullanımda!"

def login_user(identifier, password):
    """Kullanıcı girişi yapar."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    hashed_p = hash_password(password)
    
    cursor.execute("SELECT id, username, game_data FROM users WHERE (username = ? OR email = ?) AND password_hash = ?", 
                   (identifier, identifier, hashed_p))
    user = cursor.fetchone()
    conn.close()
    return user

def save_game_data(user_id, data):
    """Oyuncunun güncel oyun verilerini veritabanına kaydeder."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET game_data = ? WHERE id = ?", (json.dumps(data, ensure_ascii=False), user_id))
    conn.commit()
    conn.close()

# --- GLOBAL KLAN FONKSİYONLARI ---
def load_all_clans():
    """Veritabanındaki tüm klanları sözlük olarak yükler."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT clan_name, clan_data FROM clans")
    rows = cursor.fetchall()
    conn.close()
    
    clans_dict = {}
    for row in rows:
        clans_dict[row[0]] = json.loads(row[1])
    return clans_dict

def save_clan_to_db(clan_name, clan_data):
    """Tek bir klanın verisini veritabanına kaydeder/günceller."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO clans (clan_name, clan_data) VALUES (?, ?)",
                   (clan_name, json.dumps(clan_data, ensure_ascii=False)))
    conn.commit()
    conn.close()

def delete_clan_from_db(clan_name):
    """Klanı veritabanından tamamen siler."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clans WHERE clan_name = ?", (clan_name,))
    conn.commit()
    conn.close()