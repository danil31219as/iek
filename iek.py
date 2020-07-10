import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://www.iek.ru/products/catalog/pribory_ucheta_kontrolya_izmereniya_i_oborudovanie_elektropitaniya/pribory_ucheta/'
soup = BeautifulSoup(requests.get(url).text, 'html.parser')
a = soup.find('div', class_='catalog-section-tree').text.strip()
a = a.split('\n')
d_1 = {}
d_2 = {}
d_3 = {}
for elem in a:
    if elem:
        x = elem.strip().split(' ')
        if len(x[0].split('.')) == 2 and not x[0].split('.')[1]:
            d_1[x[0].split('.')[0]] = ' '.join(x[1:])
        elif len(x[0].split('.')) == 2:
            d_2[x[0]] = ' '.join(x[1:])
        elif len(x[0].split('.')) == 3:
            d_3[x[0]] = ' '.join(x[1:])
session = requests.Session()
start_time = time.time()
a = session.get('https://www.iek.ru/api/products?entity=all',
                auth=('163-20180420-142523-695', '_g2FQ8!mOh)9c^2V')).json()
print(start_time - time.time())
list_art = []
for elem in a:
    list_art.append(elem['art'])
contain = session.get(
    'https://www.iek.ru/api/residues/json/?sku=' + ','.join(list_art[:300]),
    auth=('163-20180420-142523-695', '_g2FQ8!mOh)9c^2V')).json()
start_time = time.time()
df = pd.DataFrame()
n = len(a)
for i in range(n):
    print(i)
    elem = a[i]
    art = elem['art']
    title = elem['name']
    groupId = elem['groupId'].split('.')
    level1 = d_1[groupId[0]]
    try:
        level2 = d_2['.'.join(groupId[:2])]
    except Exception as e:
        print(e)
        level2 = ''
    try:
        level3 = d_3['.'.join(groupId)]
    except Exception as e:
        print(e)
        level3 = ''
    try:
        price = elem['price']
    except Exception as e:
        print(e)
        price = ''
    try:
        description = elem['Description'][0]['desc_ru']
    except Exception as e:
        print(e)
        description = ''
    try:
        sklad = session.get('https://www.iek.ru/api/residues/json/?sku=' + art,
                            auth=('163-20180420-142523-695',
                                  '_g2FQ8!mOh)9c^2V')).json()['shopItems'][0][
            'residues']
        s_1 = sklad['47585e53-0113-11e0-8255-003048d2334c']
        s_2 = sklad['60f7e0ff-5151-11dc-bd86-00001a1a02c3']
        s_3 = sklad['aeef2063-c1e7-11d9-b0d7-00001a1a02c3']
        s_4 = sklad['baab86d3-db28-11e7-80fb-00155d04010a']
    except Exception as e:
        print(e)
        s_1, s_2, s_3, s_4 = '', '', '', ''
    try:
        img = elem['ImgPng'][0]['file_ref']['uri']
    except Exception as e:
        print(e)
        img = ''
    df = df.append([[art, title, level1, level2, level3, price, description,
                     s_1, s_2, s_3, s_4, img]], ignore_index=True)
print(time.time() - start_time)
df.columns = ['art', 'title', 'level1', 'level2', 'level3', 'price',
              'description', '47585e53-0113-11e0-8255-003048d2334c',
              '60f7e0ff-5151-11dc-bd86-00001a1a02c3',
              'aeef2063-c1e7-11d9-b0d7-00001a1a02c3',
              'baab86d3-db28-11e7-80fb-00155d04010a', 'img']
df.to_csv('all_iek.csv')
etim_set = set()
c = session.get('https://www.iek.ru/api/etim',
                auth=('163-20180420-142523-695', '_g2FQ8!mOh)9c^2V')).json()
for et in c:
    for att in et['Features']:
        etim_set.add(att['Attribute'])
etim_set = list(etim_set)
new_etim = []
for elem in etim_set:
    if 'code' not in elem.lower():
        new_etim.append(elem)
df = pd.DataFrame(columns=['art'] + new_etim)
D = {}
for abc in new_etim:
    D[abc] = ''
i = 0
for y in c:
    i += 1
    print(i)
    out = D
    out['art'] = y['Code']
    for att in y['Features']:
        if 'code' not in att['Attribute'].lower():
            out[att['Attribute']] = att['value']
    df = df.append(out, ignore_index=True)
df1 = df[list(df.columns)[:630]]
df2 = df[['art'] + list(df.columns)[630:1260]]
df3 = df[['art'] + list(df.columns)[1260:]]
df1.to_csv('chars_1.csv')
df2.to_csv('chars_2.csv')
df3.to_csv('chars_3.csv')