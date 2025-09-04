#!/usr/bin/env python3
"""
Test All Updated Systems - Frontend Integration Test
"""

import requests
import json


def test_all_systems():
    """Test all system endpoints to ensure frontend integration works"""

    base_url = 'http://localhost:8000'

    systems = [
        {'name': 'HR Assistant (Original)',
         'url': f'{base_url}/api/menu/pos_youhr?role=employee'},
        {'name': 'Merchant Management', 'url': f'{base_url}/api/menu/merchant'},
        {'name': 'Retention Executor',
            'url': f'{base_url}/api/menu/icp_hr?role=retention_executor'},
        {'name': 'ICP HR Assistant',
            'url': f'{base_url}/api/menu/icp_hr?role=hr_assistant'},
        {'name': 'Merchant Manager',
            'url': f'{base_url}/api/menu/icp_hr?role=merchant_manager'},
        {'name': 'General ICP HR', 'url': f'{base_url}/api/menu/icp_hr'}
    ]

    print('🔍 TESTING ALL SYSTEM INTEGRATIONS')
    print('=' * 60)

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
                print(f'   URL: {system["url"]}')

                results.append(
                    {'system': system['name'], 'status': 'SUCCESS', 'menus': menu_count, 'submenus': submenu_count})
            else:
                print(f'❌ {system["name"]}: HTTP {response.status_code}')
                results.append(
                    {'system': system['name'], 'status': 'FAILED', 'error': f'HTTP {response.status_code}'})

        except Exception as e:
            print(f'❌ {system["name"]}: {str(e)}')
            results.append(
                {'system': system['name'], 'status': 'ERROR', 'error': str(e)})

        print()

    print('=' * 60)
    print('📊 SUMMARY')
    print('=' * 60)

    success_count = len([r for r in results if r['status'] == 'SUCCESS'])
    total_count = len(results)

    print(f'Total Systems: {total_count}')
    print(f'Successful: {success_count}')
    print(f'Failed: {total_count - success_count}')
    print(f'Success Rate: {(success_count/total_count)*100:.1f}%')

    if success_count == total_count:
        print('\n🎉 All systems are working! Your Retention Executor is now accessible!')
        print('\n🌐 Open this in your browser to access all systems:')
        print(f'   {base_url}/static/chat.html')
    else:
        print('\n⚠️  Some systems failed. Check the API server.')


if __name__ == '__main__':
    test_all_systems()
