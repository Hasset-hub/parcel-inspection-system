"""
Complete authentication fix script
Fixes password hash and verifies everything works
"""
import asyncio
import psycopg2
from app.core.security import get_password_hash, verify_password

def fix_database():
    """Fix the admin user in the database"""
    
    # Generate correct hash for Admin123!
    correct_hash = get_password_hash("Admin123!")
    print(f"✅ Generated password hash")
    print(f"   Hash: {correct_hash[:50]}...")
    
    # Connect to database
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="parcel_system",
            user="parcel_admin",
            password="Parcel123!"  # The password you set
        )
        print("✅ Connected to database")
        
        cur = conn.cursor()
        
        # Update admin user with correct values
        cur.execute("""
            UPDATE users
            SET 
                password_hash = %s,
                role = 'ADMIN',
                is_active = true
            WHERE username = 'admin'
        """, (correct_hash,))
        
        conn.commit()
        print("✅ Updated admin user")
        
        # Verify the update
        cur.execute("""
            SELECT username, role, is_active, 
                   substring(password_hash, 1, 30) as hash_preview
            FROM users 
            WHERE username = 'admin'
        """)
        
        result = cur.fetchone()
        if result:
            username, role, is_active, hash_preview = result
            print("\n✅ Admin user verified:")
            print(f"   Username: {username}")
            print(f"   Role: {role}")
            print(f"   Active: {is_active}")
            print(f"   Hash preview: {hash_preview}...")
            
            # Test password verification
            cur.execute("SELECT password_hash FROM users WHERE username = 'admin'")
            stored_hash = cur.fetchone()[0]
            
            if verify_password("Admin123!", stored_hash):
                print("\n✅ Password verification: PASSED")
                print("   Password 'Admin123!' matches the stored hash")
            else:
                print("\n❌ Password verification: FAILED")
                print("   Something is still wrong")
        else:
            print("❌ Admin user not found!")
        
        cur.close()
        conn.close()
        
        print("\n" + "="*50)
        print("✅ DATABASE FIX COMPLETE!")
        print("="*50)
        print("\nYou can now test login with:")
        print('  username: admin')
        print('  password: Admin123!')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    fix_database()
