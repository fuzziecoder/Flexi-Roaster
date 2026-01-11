"""
Database initialization script
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db.database import init_db, engine
from backend.db.models import Base

def main():
    """Initialize database tables"""
    print("Creating database tables...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✓ Database tables created successfully!")
    print(f"Database location: flexiroaster.db")
    
    # Print table names
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    main()
