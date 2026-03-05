import requests

url = 'https://cafef.vn/du-lieu/ajax/mobile/smart/ajaxchisothegioi.ashx'
headers = {'User-Agent': 'Mozilla/5.0'}

r = requests.get(url, headers=headers)
if r.status_code == 200:
    data = r.json()
    items = data.get('Data', [])
    for item in items[:20]:
        print(f"{item.get('index')}: {item.get('last')} ({item.get('changePercent')}%)")
