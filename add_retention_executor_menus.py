from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Menu, Submenu


def add_retention_executor_menus(db: Session):
    """Add Retention Executor menus and submenus to the database."""
    retention_menu = Menu(
        menu_key="retention_executor",
        menu_title="Retention Executor",
        menu_icon="🔄",
        company_type="retention"
    )

    retention_submenus = [
        Submenu(
            submenu_key="assigned_merchants",
            submenu_title="Assigned Merchants",
            api_endpoint="/api/icp/executor/assigned-merchants"
        ),
        Submenu(
            submenu_key="merchant_profile",
            submenu_title="Merchant Profile",
            api_endpoint="/api/icp/executor/merchant-profile/{merchant_id}"
        )
    ]

    retention_menu.submenus.extend(retention_submenus)
    db.add(retention_menu)
    db.commit()
    print("Retention Executor menus and submenus added successfully.")


if __name__ == "__main__":
    db = next(get_db())
    add_retention_executor_menus(db)
