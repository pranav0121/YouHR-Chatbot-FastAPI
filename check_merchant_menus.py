from app.database import SessionLocal
from app.models import ChatbotMenu

db = SessionLocal()
merchant_menus = db.query(ChatbotMenu).filter_by(company_type='merchant').all()
print('Merchant Menus in Database:')
for menu in merchant_menus:
    print(f'- {menu.menu_title} ({menu.menu_key})')
print(f'Total: {len(merchant_menus)} menus')
db.close()
