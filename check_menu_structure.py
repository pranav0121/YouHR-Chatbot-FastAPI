from app.database import SessionLocal
from app.models import ChatbotMenu

db = SessionLocal()
menu = db.query(ChatbotMenu).filter_by(company_type='merchant').first()
print('Menu fields:')
print(f'ID: {menu.id}')
print(f'Title: {menu.menu_title}')
print(f'Key: {menu.menu_key}')
print(f'Company Type: {menu.company_type}')
print(f'Role: {getattr(menu, "role", "NOT_SET")}')
print(f'Is Active: {getattr(menu, "is_active", "NOT_SET")}')
db.close()
