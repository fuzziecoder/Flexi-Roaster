"""Test individual model imports"""
import sys
sys.path.insert(0, '.')

try:
    print("1. Importing database Base...")
    from backend.db.database import Base, engine
    print("   ✓ Success")
    
    print("2. Importing sqlalchemy components...")
    from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
    from sqlalchemy.orm import relationship
    print("   ✓ Success")
    
    print("3. Defining PipelineDB model...")
    class PipelineDB(Base):
        __tablename__ = "pipelines"
        id = Column(String, primary_key=True, index=True)
        name = Column(String, nullable=False)
    print("   ✓ Success")
    
    print("4. Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✓ Success")
    
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
