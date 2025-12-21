#!/usr/bin/env python3
"""
Maintenance script to clean up old failed mappings
Run this periodically (e.g., via cron) to keep database clean
"""
from app.database import db, FailedMapping
from datetime import datetime, timedelta
from config import Config

def cleanup_old_failed_mappings(days: int = 30):
    """Remove failed mappings older than specified days"""
    session = db.Session()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = session.query(FailedMapping).filter(
            FailedMapping.checked_at < cutoff_date
        ).delete()
        session.commit()
        print(f"✓ Cleaned up {deleted} failed mappings older than {days} days")
        return deleted
    except Exception as e:
        print(f"✗ Error during cleanup: {e}")
        session.rollback()
        return 0
    finally:
        session.close()

def show_stats():
    """Show database statistics"""
    session = db.Session()
    try:
        from app.database import Mapping
        
        total_mappings = session.query(Mapping).count()
        total_failed = session.query(FailedMapping).count()
        
        print("\n=== Database Statistics ===")
        print(f"Total successful mappings: {total_mappings}")
        print(f"Total failed mappings: {total_failed}")
        
        if total_failed > 0:
            oldest = session.query(FailedMapping).order_by(
                FailedMapping.checked_at
            ).first()
            newest = session.query(FailedMapping).order_by(
                FailedMapping.checked_at.desc()
            ).first()
            
            print(f"Oldest failed mapping: {oldest.checked_at}")
            print(f"Newest failed mapping: {newest.checked_at}")
        
        print("===========================\n")
    finally:
        session.close()

if __name__ == '__main__':
    import sys
    
    print("Database Maintenance Script")
    print(f"Database type: {Config.DB_TYPE}\n")
    
    show_stats()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--clean':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        cleanup_old_failed_mappings(days)
        show_stats()
    else:
        print("Usage:")
        print("  python maintenance.py              # Show statistics only")
        print("  python maintenance.py --clean      # Clean mappings older than 30 days")
        print("  python maintenance.py --clean 60   # Clean mappings older than 60 days")
