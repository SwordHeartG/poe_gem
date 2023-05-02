import pandas as pd
import requests
import json

# 修改日期，读取宝石数据
date_str = '20230429'
df_price = pd.read_csv('POE/alt_gem/gem_price_{}.csv'.format(date_str))
df_comb = pd.read_csv('POE/alt_gem/quality_gem_combination.csv')
df_list = pd.read_csv('POE/alt_gem/quality_gem_list.csv')


# 从df_list中取出权重数据，添加到df_comb中
df_merged = pd.merge(df_comb, df_list, left_on=['gem_name', 'type_origin'], right_on=['gem_name', 'quality_type'], how='left').drop(
    columns=['vaal_gem_y', 'quality_type']).rename(columns={'vaal_gem_x': 'vaal_gem', 'weight': 'weight_origin'})
df_merged = pd.merge(df_merged, df_list, left_on=['gem_name', 'type_target'], right_on=['gem_name', 'quality_type'], how='left').drop(
    columns=['vaal_gem_y', 'quality_type']).rename(columns={'vaal_gem_x': 'vaal_gem', 'weight': 'weight_target'})


# 将df_list按gem_name分组，计算每种宝石的总权重
df_list_grouped = df_list[['gem_name','weight']].groupby('gem_name').sum().reset_index()

# 将df_merged和df_list_grouped合并
df_merged = pd.merge(df_merged, df_list_grouped, on='gem_name', how='left').rename(columns={'weight': 'weight_total'})
df_merged['success'] = df_merged['weight_target'] / (df_merged['weight_total'] - df_merged['weight_origin'])


# 在df_merged中先添加查询列
def join_columns(row):
    query_origin = '-'.join([row['type_origin'], row['gem_name']]).lower().replace('superior-', '').replace("'", '').replace(' ', '-') + '-1'
    query_target = '-'.join([row['type_target'], row['gem_name']]).lower().replace('superior-', '').replace("'", '').replace(' ', '-') + '-1'
    return query_origin, query_target

df_merged['query_origin'], df_merged['query_target'] = zip(*df_merged.apply(join_columns, axis=1))


# 将df_merged和df_price合并
df_price = df_price[['detailsId','price_history_low','price_history','listingCount','chaosValue']]

df_merged = pd.merge(df_merged, df_price, left_on='query_origin', right_on='detailsId', how='left').drop(columns=['detailsId']).rename(
    columns={'price_history_low': 'origin_history_low', 'price_history': 'origin_history', 'listingCount': 'origin_listingCount', 'chaosValue': 'origin_value'})

df_merged = pd.merge(df_merged, df_price, left_on='query_target', right_on='detailsId', how='left').drop(columns=['detailsId']).rename(
    columns={'price_history_low': 'target_history_low', 'price_history': 'target_history', 'listingCount': 'target_listingCount', 'chaosValue': 'target_value'})




# 从poe.ninja上请求Prime Regrading Lens 和 Secondary Regrading Lens 的价格
def get_ninja_price(item_name):
    url = 'https://poe.ninja/api/data/currencyoverview?league=Crucible&type=Currency&language=en'
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        for item in data['lines']:
            if item['currencyTypeName'] == item_name:
                return float(item['chaosEquivalent'])
    except:
        print('Error: Cannot get the price of {} from poe.ninja'.format(item_name))
        return None
    
prime_lens_price = get_ninja_price('Prime Regrading Lens')
secondary_lens_price = get_ninja_price('Secondary Regrading Lens')

# 在df_merged中添加镜片的价格
bulk_ratio = 1.25
df_merged.loc[df_merged['gem_type'] == 'skill','lens_price'] = prime_lens_price * bulk_ratio
df_merged.loc[df_merged['gem_type'] == 'support','lens_price'] = secondary_lens_price * bulk_ratio

# 计算df_merged中宝石的cost 和 profit，添加confidence列
df_merged['cost'] = ((df_merged['origin_value'] + df_merged['lens_price']) / df_merged['success']).round(2)
df_merged['profit'] = (df_merged['target_value'] - df_merged['cost']).round(2)
df_merged['confidence'] = pd.cut(df_merged['target_listingCount'], bins=[1, 5, 10, 100000], labels=['low', 'medium', 'high'], right=False)
df_merged = df_merged.sort_values(by='profit', ascending=False).reset_index(drop=True)

# 保存df_merged
df_merged.to_csv('POE/alt_gem/gem_analysis_lvl1_{}.csv'.format(date_str), index=False)

