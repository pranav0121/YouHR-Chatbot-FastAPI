from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ChatbotMenu, ChatbotSubmenu


def clear_chatbot_menus(db: Session):
    """Clear all data from chatbot menus and submenus."""
    db.query(ChatbotSubmenu).delete()
    db.query(ChatbotMenu).delete()
    db.commit()
    print("All chatbot menus and submenus have been cleared.")


if __name__ == "__main__":
    db = next(get_db())
    clear_chatbot_menus(db)
