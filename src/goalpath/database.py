"""
Database configuration and setup for GoalPath
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path
from typing import Generator

from .models import Base
# Import specific models to avoid circular imports  
from .models import Project, Task, Goal
from .models.extended import (
    Reminder, Issue, TaskComment, TaskAttachment, 
    ProjectContext, ScheduleEvent
)

class DatabaseManager:
    """Database manager for GoalPath application"""
    
    def __init__(self, database_url: str = None):
        if database_url is None:
            # Default to SQLite in project root
            db_path = Path(__file__).parent.parent.parent.parent / "goalpath.db"
            database_url = f"sqlite:///{db_path}"
        
        self.database_url = database_url
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _create_engine(self):
        """Create SQLAlchemy engine with appropriate configuration"""
        if self.database_url.startswith("sqlite"):
            # SQLite specific configuration
            engine = create_engine(
                self.database_url,
                connect_args={
                    "check_same_thread": False,  # Allow multiple threads
                    "timeout": 20  # 20 second timeout
                },
                poolclass=StaticPool,
                echo=False  # Set to True for SQL debugging
            )
            
            # Enable foreign key constraints for SQLite
            @event.listens_for(engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()
        else:
            # PostgreSQL or other database configuration
            engine = create_engine(
                self.database_url,
                echo=False  # Set to True for SQL debugging
            )
        
        return engine
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_sync_session(self) -> Session:
        """Get synchronous database session (manual cleanup required)"""
        return self.SessionLocal()

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions"""
    yield from db_manager.get_session()

# Initialize database
def init_database(drop_existing: bool = False):
    """Initialize database with tables"""
    if drop_existing:
        print("Dropping existing tables...")
        db_manager.drop_tables()
    
    print("Creating database tables...")
    db_manager.create_tables()
    print("Database tables created successfully!")

if __name__ == "__main__":
    # Test database setup
    print(f"Database URL: {db_manager.database_url}")
    init_database(drop_existing=True)
    
    # Test basic operations
    with db_manager.get_sync_session() as session:
        # Test creating a project
        from .models import Project
        
        project = Project(
            name="Test Project",
            description="A test project for database validation",
            status="active",
            priority="medium"
        )
        
        session.add(project)
        session.commit()
        session.refresh(project)
        
        print(f"Created project: {project.name} (ID: {project.id})")
        
        # Query the project back
        retrieved_project = session.query(Project).filter(Project.name == "Test Project").first()
        print(f"Retrieved project: {retrieved_project.name}")
        
        print("Database test completed successfully!")