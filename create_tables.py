from app.database import engine, Base
from app.models import ChatbotMenu, ChatbotSubmenu, AttendanceRecord

print("Creating database tables...")

# Create all tables
Base.metadata.create_all(bind=engine)

print("✅ Database tables created successfully!")
