from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatbotMenu


def query_chatbot_menus(db: Session):
    """Query and print all data from the chatbot_menus table."""
    menus = db.query(ChatbotMenu).all()
    if not menus:
        print("No data found in chatbot_menus table.")
    else:
        for menu in menus:
            print(
                f"Menu ID: {menu.id}, Key: {menu.menu_key}, Title: {menu.menu_title}, Company Type: {menu.company_type}, Role: {menu.role}")


if __name__ == "__main__":
    db = next(get_db())
    query_chatbot_menus(db)
