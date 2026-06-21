import os
import shutil
import sys
from datetime import datetime

# Adjust path to find app module config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings

def backup():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)
        
    backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"memora_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    shutil.copy2(db_path, backup_path)
    print(f"Success: Database backup written to {backup_path}")

def restore(backup_file: str):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found at {backup_file}")
        sys.exit(1)
        
    # Backup current first to prevent accidental loss
    if os.path.exists(db_path):
        temp_backup = db_path + ".bak"
        shutil.copy2(db_path, temp_backup)
        print(f"Note: Current active DB backed up to temporary file {temp_backup}")
        
    shutil.copy2(backup_file, db_path)
    print(f"Success: Database state restored from {backup_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 scripts/backup_db.py backup")
        print("  python3 scripts/backup_db.py restore <path_to_backup_file>")
        sys.exit(0)
        
    cmd = sys.argv[1].lower()
    if cmd == "backup":
        backup()
    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("Error: Missing backup filepath argument.")
            sys.exit(1)
        restore(sys.argv[2])
    else:
        print(f"Error: Unknown command '{cmd}'")
