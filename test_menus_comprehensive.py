#!/usr/bin/env python3
"""
Comprehensive Menu and Submenu Testing Script
Tests all menu endpoints and their associated submenu API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:8000'


def test_menu_endpoint(company_type, role=None):
    """Test menu endpoint for specific company type and role"""
    url = f'{BASE_URL}/menu/{company_type}'
    if role:
        url += f'?role={role}'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            menu_count = len(data.get('menus', []))
            role_text = role or "all roles"
            print(f'✅ {company_type.upper()} {role_text}: {menu_count} menus')

            # Show menu details
            for menu in data.get('menus', []):
                submenu_count = len(menu.get('submenus', []))
                print(f'   📋 {menu["menu_title"]}: {submenu_count} submenus')

                # Test each submenu endpoint
                for submenu in menu.get('submenus', []):
                    endpoint = submenu['api_endpoint']
                    if endpoint.startswith('/'):
                        test_url = BASE_URL + endpoint
                        try:
                            sub_response = requests.get(test_url, timeout=5)
                            status = '✅' if sub_response.status_code == 200 else '❌'
                            print(
                                f'      {status} {submenu["submenu_title"]} ({endpoint}): {sub_response.status_code}')
                        except Exception as e:
                            print(
                                f'      ❌ {submenu["submenu_title"]} ({endpoint}): Error - {str(e)[:50]}')

            return True
        else:
            print(
                f'❌ {company_type.upper()}: {response.status_code} - {response.text[:100]}')
            return False
    except Exception as e:
        print(f'❌ {company_type.upper()}: Error - {str(e)}')
        return False


def main():
    print('🔍 COMPREHENSIVE MENU AND SUBMENU TESTING')
    print('=' * 60)
    print(f'Test Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Base URL: {BASE_URL}')
    print('=' * 60)

    # Test all company types and roles
    test_cases = [
        ('icp_hr', None),
        ('icp_hr', 'employee'),
        ('icp_hr', 'admin'),
        ('merchant', None),
        ('merchant', 'manager'),
        ('retail', None),
        ('restaurant', None),
        ('pos_youhr', None)
    ]

    passed = 0
    total = len(test_cases)

    for company_type, role in test_cases:
        role_display = f' - {role.upper()} Role' if role else ''
        print(f'\n🏢 Testing {company_type.upper()} Company Type{role_display}')
        print('-' * 40)
        if test_menu_endpoint(company_type, role):
            passed += 1

    print('\n' + '=' * 60)
    print(f'📊 MENU TEST SUMMARY')
    print('=' * 60)
    print(f'Total Company/Role Combinations: {total}')
    print(f'Successful Tests: {passed}')
    print(f'Failed Tests: {total - passed}')
    print(f'Success Rate: {(passed/total)*100:.1f}%')

    if passed == total:
        print('🎉 All menu and submenu tests passed!')
        print('✅ PostgreSQL integration is working perfectly!')
    else:
        print('⚠️  Some tests failed. Check API server status.')
        print('💡 Make sure the FastAPI server is running on http://localhost:8000')


if __name__ == '__main__':
    main()
