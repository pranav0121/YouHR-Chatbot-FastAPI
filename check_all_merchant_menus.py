from app.database import SessionLocal
from app.models import ChatbotMenu, ChatbotSubmenu

db = SessionLocal()
merchant_menus = db.query(ChatbotMenu).filter_by(company_type='merchant').all()
print('Complete Merchant Menu Structure:')
for menu in merchant_menus:
    print(f'\nMenu: {menu.menu_title} ({menu.menu_key})')
    for submenu in menu.submenus:
        print(
            f'  -> Submenu: "{submenu.submenu_title}" (key: {submenu.submenu_key})')
db.close()
