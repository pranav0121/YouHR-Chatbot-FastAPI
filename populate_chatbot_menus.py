from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatbotMenu, ChatbotSubmenu


def populate_chatbot_menus(db: Session):
    """Populate chatbot menus and submenus with initial data."""
    # Clear existing data
    db.query(ChatbotSubmenu).delete()
    db.query(ChatbotMenu).delete()
    db.commit()

    menus = [
        ChatbotMenu(
            menu_key="hr_assistant",
            menu_title="HR Assistant",
            menu_icon="👩‍💼",
            company_type="icp_hr",
            role="employee",
            submenus=[
                ChatbotSubmenu(
                    submenu_key="employees",
                    submenu_title="Employees",
                    api_endpoint="/api/chatbot/employees"
                ),
                ChatbotSubmenu(
                    submenu_key="attendance",
                    submenu_title="Attendance",
                    api_endpoint="/api/chatbot/attendance"
                )
            ]
        ),
        ChatbotMenu(
            menu_key="merchant_manager",
            menu_title="Merchant Manager",
            menu_icon="💼",
            company_type="merchant",
            role="manager",
            submenus=[
                ChatbotSubmenu(
                    submenu_key="today_sales",
                    submenu_title="Today's Sales",
                    api_endpoint="/api/merchant/sales/today"
                ),
                ChatbotSubmenu(
                    submenu_key="weekly_sales",
                    submenu_title="Weekly Sales",
                    api_endpoint="/api/merchant/sales/weekly"
                )
            ]
        ),
        ChatbotMenu(
            menu_key="retention_manager",
            menu_title="Retention Manager",
            menu_icon="🔄",
            company_type="icp_hr",
            role="manager",
            submenus=[
                ChatbotSubmenu(
                    submenu_key="retention_stats",
                    submenu_title="Retention Stats",
                    api_endpoint="/api/retention/stats"
                ),
                ChatbotSubmenu(
                    submenu_key="retention_plans",
                    submenu_title="Retention Plans",
                    api_endpoint="/api/retention/plans"
                )
            ]
        )
    ]

    db.add_all(menus)
    db.commit()
    print("Chatbot menus and submenus populated successfully.")


if __name__ == "__main__":
    db = next(get_db())
    populate_chatbot_menus(db)
