#!/usr/bin/env python3
"""
Populate Missing Merchant Management Submenus
This script adds all 16 missing merchant management submenus to the database
"""

import sys
from app.database import get_db
from app import models


def populate_merchant_submenus():
    db = next(get_db())

    try:
        # Get existing merchant menus
        menus = db.query(models.ChatbotMenu).filter(
            models.ChatbotMenu.company_type == 'pos_youhr',
            models.ChatbotMenu.role == 'merchant'
        ).all()

        print("🔧 POPULATING MERCHANT MANAGEMENT SUBMENUS")
        print("=" * 60)

        # Define the submenu structure based on our API endpoints
        submenu_structure = {
            "Marketing & Growth": [
                {
                    "submenu_title": "Check campaign results (sent, delivered, read)",
                    "submenu_description": "View marketing campaign performance and statistics"
                },
                {
                    "submenu_title": "Check loan status (see if approved, pending, declined)",
                    "submenu_description": "Monitor loan application status and updates"
                },
                {
                    "submenu_title": "Continue loan application (upload missing documents or complete KYC)",
                    "submenu_description": "Complete pending loan application requirements"
                }
            ],
            "Operations": [
                {
                    "submenu_title": "Approve pending leave requests",
                    "submenu_description": "Review and approve employee leave applications"
                },
                {
                    "submenu_title": "Approve shift change requests",
                    "submenu_description": "Review and approve employee shift modifications"
                }
            ],
            "Notifications": [
                {
                    "submenu_title": "See latest payment settlement update",
                    "submenu_description": "View recent payment processing updates"
                },
                {
                    "submenu_title": "Renew subscription (if expiring soon)",
                    "submenu_description": "Manage and renew service subscriptions"
                },
                {
                    "submenu_title": "Read messages from Head Office",
                    "submenu_description": "View important communications from management"
                }
            ],
            "Help & Support": [
                {
                    "submenu_title": "Report POS app problem",
                    "submenu_description": "Report issues with the POS application"
                },
                {
                    "submenu_title": "Report hardware issue (printer, scanner, POS machine)",
                    "submenu_description": "Report problems with hardware equipment"
                },
                {
                    "submenu_title": "Report AI camera problem (YouLens)",
                    "submenu_description": "Report issues with AI camera systems"
                },
                {
                    "submenu_title": "Request camera installation or training",
                    "submenu_description": "Request new camera setup or training sessions"
                },
                {
                    "submenu_title": "Ask for general support",
                    "submenu_description": "Get help with general questions or issues"
                }
            ],
            "Feedback & Ideas": [
                {
                    "submenu_title": "Rate your experience with this bot (👍 Good / 👎 Bad)",
                    "submenu_description": "Provide feedback on chatbot performance"
                },
                {
                    "submenu_title": "Share feedback on POS / Loan / Camera / Staff",
                    "submenu_description": "Share detailed feedback on various services"
                },
                {
                    "submenu_title": "Suggest a new feature for YouShop",
                    "submenu_description": "Propose new features or improvements"
                }
            ]
        }

        submenus_added = 0

        # Process each menu and add submenus
        for menu in menus:
            menu_title = menu.menu_title
            print(f"\n📂 Processing menu: {menu_title}")

            if menu_title in submenu_structure:
                submenus_data = submenu_structure[menu_title]

                for submenu_data in submenus_data:
                    # Check if submenu already exists
                    existing_submenu = db.query(models.ChatbotSubmenu).filter(
                        models.ChatbotSubmenu.menu_id == menu.id,
                        models.ChatbotSubmenu.submenu_title == submenu_data["submenu_title"]
                    ).first()

                    if not existing_submenu:
                        # Create new submenu
                        new_submenu = models.ChatbotSubmenu(
                            menu_id=menu.id,
                            submenu_title=submenu_data["submenu_title"],
                            submenu_description=submenu_data["submenu_description"]
                        )

                        db.add(new_submenu)
                        submenus_added += 1
                        print(f"   ✅ Added: {submenu_data['submenu_title']}")
                    else:
                        print(
                            f"   ⚠️  Already exists: {submenu_data['submenu_title']}")
            else:
                print(f"   ❌ No submenu structure defined for: {menu_title}")

        # Commit changes
        db.commit()

        print(f"\n🎉 COMPLETED!")
        print(f"📊 Total submenus added: {submenus_added}")
        print("=" * 60)

        # Verify the addition
        print("\n🔍 VERIFICATION - Current submenu count:")
        total_submenus = db.query(models.ChatbotSubmenu).join(
            models.ChatbotMenu
        ).filter(
            models.ChatbotMenu.company_type == 'pos_youhr',
            models.ChatbotMenu.role == 'merchant'
        ).count()

        print(f"Total merchant submenus in database: {total_submenus}")

    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

    return True


if __name__ == "__main__":
    success = populate_merchant_submenus()
    if success:
        print("\n✅ Merchant submenu population completed successfully!")
    else:
        print("\n❌ Failed to populate merchant submenus.")
        sys.exit(1)
