from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Menu, Submenu


def add_hr_assistant_menus(db: Session):
    """Add HR Assistant menus and submenus to the database."""
    hr_menu = Menu(
        menu_key="hr_assistant",
        menu_title="HR Assistant",
        menu_icon="👩‍💼",
        company_type="hr"
    )

    hr_submenus = [
        Submenu(
            submenu_key="employees",
            submenu_title="Employees",
            api_endpoint="/api/chatbot/employees"
        ),
        Submenu(
            submenu_key="attendance",
            submenu_title="Attendance",
            api_endpoint="/api/chatbot/attendance"
        ),
        Submenu(
            submenu_key="payslips",
            submenu_title="Payslips",
            api_endpoint="/api/chatbot/payslips"
        )
    ]

    hr_menu.submenus.extend(hr_submenus)
    db.add(hr_menu)
    db.commit()
    print("HR Assistant menus and submenus added successfully.")


if __name__ == "__main__":
    db = next(get_db())
    add_hr_assistant_menus(db)
