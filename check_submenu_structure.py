#!/usr/bin/env python3
"""
Check Menu Structure for JavaScript Functions
"""

import sys
from app.database import get_db
from app import models


def check_menu_structure():
    db = next(get_db())

    # Get merchant menus
    menus = db.query(models.ChatbotMenu).filter(
        models.ChatbotMenu.company_type == 'pos_youhr',
        models.ChatbotMenu.role == 'merchant'
    ).all()

    all_submenus = []

    print("🔍 MERCHANT MANAGEMENT SUBMENU STRUCTURE")
    print("=" * 60)

    for menu in menus:
        print(f"\n📂 {menu.menu_title}")
        print("-" * 40)

        submenus = db.query(models.ChatbotSubmenu).filter(
            models.ChatbotSubmenu.menu_id == menu.id
        ).all()

        for submenu in submenus:
            print(f"   • {submenu.submenu_title}")
            all_submenus.append(submenu.submenu_title)

    print(f"\n📊 TOTAL SUBMENUS: {len(all_submenus)}")
    print("=" * 60)

    # Check which ones might need JavaScript functions
    print("\n🔧 SUBMENUS NEEDING JAVASCRIPT FUNCTIONS:")
    print("-" * 50)

    needs_js_functions = [
        "Check campaign results (sent, delivered, read)",
        "Check loan status (see if approved, pending, declined)",
        "Continue loan application (upload missing documents or complete KYC)",
        "Approve pending leave requests",
        "Approve shift change requests",
        "See latest payment settlement update",
        "Renew subscription (if expiring soon)",
        "Read messages from Head Office",
        "Report POS app problem",
        "Report hardware issue (printer, scanner, POS machine)",
        "Report AI camera problem (YouLens)",
        "Request camera installation or training",
        "Ask for general support",
        "Rate your experience with this bot (👍 Good / 👎 Bad)",
        "Share feedback on POS / Loan / Camera / Staff",
        "Suggest a new feature for YouShop"
    ]

    for submenu in needs_js_functions:
        if submenu in all_submenus:
            print(f"   ✅ {submenu}")
        else:
            print(f"   ❌ {submenu} (MISSING FROM DB)")

    db.close()


if __name__ == "__main__":
    check_menu_structure()
