#!/usr/bin/env python3
"""
Test Retention Executor Menu Access
"""

import requests
import json


def test_retention_executor():
    """Test the retention executor menu endpoint"""
    url = 'http://localhost:8000/api/menu/icp_hr?role=retention_executor'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print('✅ Retention Executor menus found!')
            print(f'URL to access: {url}')
            print()

            # Check if we have data or menus
            menus = data.get('menus', data.get('data', []))

            if menus:
                for menu in menus:
                    print(f'📋 {menu["menu_title"]}')
                    for submenu in menu.get('submenus', []):
                        print(
                            f'   • {submenu["submenu_title"]} - {submenu["api_endpoint"]}')
                    print()
            else:
                print('❌ No menus found in response')

            return True
        else:
            print(f'❌ Error: {response.status_code} - {response.text}')
            return False
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False


def test_direct_browser_access():
    """Show direct browser URLs for accessing retention executor"""
    print('🌐 Direct Browser Access URLs:')
    print('=' * 50)
    print('1. Retention Executor Menu:')
    print('   http://localhost:8000/api/menu/icp_hr?role=retention_executor')
    print()
    print('2. General ICP HR Menu (includes all roles):')
    print('   http://localhost:8000/api/menu/icp_hr')
    print()
    print('3. HR Assistant Menu:')
    print('   http://localhost:8000/api/menu/icp_hr?role=hr_assistant')
    print()
    print('4. Merchant Manager Menu:')
    print('   http://localhost:8000/api/menu/icp_hr?role=merchant_manager')
    print()
    print('5. Merchant Shortcut (maps to merchant_manager):')
    print('   http://localhost:8000/api/menu/merchant')


if __name__ == '__main__':
    print('🔍 RETENTION EXECUTOR MENU TEST')
    print('=' * 40)

    if test_retention_executor():
        print('✅ Success! Your Retention Executor is accessible.')
    else:
        print('❌ Failed to access Retention Executor menus.')

    print()
    test_direct_browser_access()
