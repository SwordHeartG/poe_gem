import requests
import json
import pandas as pd
import datetime


# 从ninja获取宝石数据，并转换为字典
url = 'https://poe.ninja/api/data/itemoverview?league=Crucible&type=SkillGem&language=en'
response = requests.get(url)
data = json.loads(response.text)


# 遍历字典，获取宝石数据，并合并为dataframe
df = pd.DataFrame()
for line in data['lines']:
    dict1 = {key:line[key] for key in ['name', 'corrupted', 'gemLevel', 'gemQuality', 'chaosValue', 'detailsId', 'listingCount'] if key in line}
    price_history = ','.join([str(item) if item is not None else 'N/A' for item in line['sparkline']['data']])
    price_history_low = ','.join([str(item) if item is not None else 'N/A' for item in line['lowConfidenceSparkline']['data']])
    dict2 = {'price_history': price_history, 'price_history_low': price_history_low}
    dict1.update(dict2)
    df = pd.concat([df, pd.DataFrame(dict1, index=[0])], ignore_index=True)

# 保存到csv文件,并以当前日期命名
df.to_csv('POE/alt_gem/gem_price_{}.csv'.format(datetime.datetime.now().strftime('%Y%m%d')), index=False)
