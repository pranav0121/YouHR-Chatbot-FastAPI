from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Menu, Submenu


def add_merchant_menus(db: Session):
    """Add Merchant menus and submenus to the database."""
    merchant_menu = Menu(
        menu_key="merchant_management",
        menu_title="Merchant Management",
        menu_icon="💼",
        company_type="merchant"
    )

    merchant_submenus = [
        Submenu(
            submenu_key="today_sales",
            submenu_title="Today's Sales",
            api_endpoint="/api/merchant/sales/today"
        ),
        Submenu(
            submenu_key="weekly_sales",
            submenu_title="Weekly Sales",
            api_endpoint="/api/merchant/sales/weekly"
        )
    ]

    merchant_menu.submenus.extend(merchant_submenus)
    db.add(merchant_menu)
    db.commit()
    print("Merchant menus and submenus added successfully.")


if __name__ == "__main__":
    db = next(get_db())
    add_merchant_menus(db)
