#!/usr/bin/env python3
"""
Test Only Essential 3 Systems
"""

import requests


def test_essential_systems():
    """Test only the 3 essential systems"""

    base_url = 'http://localhost:8000'

    systems = [
        {'name': 'HR Assistant', 'url': f'{base_url}/api/menu/pos_youhr?role=employee'},
        {'name': 'Merchant Management', 'url': f'{base_url}/api/menu/merchant'},
        {'name': 'Retention Executor',
            'url': f'{base_url}/api/menu/icp_hr?role=retention_executor'}
    ]

    print('🔍 TESTING 3 ESSENTIAL SYSTEMS')
    print('=' * 50)

    results = []

    for system in systems:
        try:
            response = requests.get(system['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Handle different response formats
                menus = []
                if isinstance(data, list):
                    menus = data
                elif 'data' in data:
                    menus = data['data']
                elif 'menus' in data:
                    menus = data['menus']

                menu_count = len(menus)
                submenu_count = sum(len(menu.get('submenus', []))
                                    for menu in menus)

                print(f'✅ {system["name"]}')
                print(f'   Menus: {menu_count}, Submenus: {submenu_count}')

                results.append({'system': system['name'], 'status': 'SUCCESS'})
            else:
                print(f'❌ {system["name"]}: HTTP {response.status_code}')
                results.append({'system': system['name'], 'status': 'FAILED'})

        except Exception as e:
            print(f'❌ {system["name"]}: {str(e)}')
            results.append({'system': system['name'], 'status': 'ERROR'})

        print()

    success_count = len([r for r in results if r['status'] == 'SUCCESS'])

    print('=' * 50)
    print(f'📊 Results: {success_count}/3 systems working')

    if success_count == 3:
        print('🎉 Perfect! All 3 essential systems are ready!')
        print()
        print('🌐 Access your interface at:')
        print(f'   {base_url}/static/chat.html')
        print()
        print('Available systems:')
        print('• 👥 HR Assistant - Employee management')
        print('• 🏪 Merchant Management - Sales & staff')
        print('• 🎯 Retention Executor - Merchant follow-up')
    else:
        print('⚠️  Some systems failed.')


if __name__ == '__main__':
    test_essential_systems()
