import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm

## style stuff for matplotlib
font_names = [f.name for f in fm.fontManager.ttflist]
mpl.rcParams['font.family'] = 'DejaVu Serif'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 2
params = {'mathtext.default': 'regular'}
plt.rcParams.update(params)


## Extract and parse
df = pd.read_csv('superstore.csv',parse_dates=['order_date','ship_date'])
df['order_date'] = pd.to_datetime(df['order_date'],format='mixed')
df['ship_date'] = pd.to_datetime(df['ship_date'],format='mixed')

## Regular Customers profitability
df['order_month'] = df['order_date'].dt.to_period('M')
start_month = df['order_month'].min()
end_month = df['order_month'].max()
total_months = (end_month.year - start_month.year)*12 + (end_month.month - start_month.month)+1

customer_order_stats = df.groupby(by='customer_name').agg(total_orders=('order_date','count'),unique_months=('order_month','nunique'),avg_profit=('profit','mean'))

customer_order_stats['regular_index'] = (customer_order_stats['total_orders'] * customer_order_stats['unique_months'])/total_months

customer_order_stats = customer_order_stats.sort_values('regular_index',ascending=False)

print('Top 5 regular customers:', customer_order_stats.nlargest(5,'regular_index')[['regular_index']])

print('Average profit of top 10 regulars: ', customer_order_stats.nlargest(10,'regular_index')['avg_profit'].mean())
print('Average profit of all customers: ', customer_order_stats['avg_profit'].mean())

## Subcategory negative profits
subcategory_stats = df.groupby(by='sub-category').agg(neg_sales=('profit', lambda x: x[x < 0].sum()))
print('Highest Losing Sub-categories: ',subcategory_stats.nsmallest(5,'neg_sales')[['neg_sales']])


## Product Category Temporal Trends
category_month = df.groupby(['order_month','category']).agg(sales=('sales','sum')).reset_index()
category_month['order_month'] = category_month['order_month'].dt.to_timestamp()

for category,group in category_month.groupby('category'):
    plt.plot(group['order_month'],group['sales']/1000,label=category)

plt.xlabel('Date')
plt.xticks(rotation=45,fontsize=12)
plt.ylabel('Monthly Sales (units $1k)')
plt.legend(frameon=False)
plt.title('Total Sales by Product Category')
plt.tight_layout()
plt.show()

## Sub-category Market Trends
subcategory_market_stats = df.groupby(['market','sub-category']).agg(total_sales=('sales','sum')).reset_index()
subcategory_market_stats['market_share'] = (subcategory_market_stats['total_sales']/subcategory_market_stats.groupby('market')['total_sales'].transform('sum'))

subcat_market_pivot = subcategory_market_stats.pivot(index='sub-category',columns='market',values='market_share')
top5 = df.groupby('sub-category')['sales'].sum().nlargest(5).index
subcat_market_pivot = subcat_market_pivot.loc[top5]

fig, ax = plt.subplots()
im = ax.imshow(subcat_market_pivot.values*100,aspect='auto')

ax.set_xticks(range(len(subcat_market_pivot.columns)))
ax.set_xticklabels(subcat_market_pivot.columns,rotation=45,ha='center')

ax.set_yticks(range(len(subcat_market_pivot.index)))
ax.set_yticklabels(subcat_market_pivot.index)

fig.colorbar(im,ax=ax,label='Market Share (%)')
plt.title('Sub-category Regional Market Trends')
plt.tight_layout()
plt.show()