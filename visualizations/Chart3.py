import pandas as pd
import altair as alt


df = pd.read_csv("Bank_Marketing_Dataset.csv")

# Quantile-based scoring: 3 levels per dimension (1–3)
df['IncS']  = pd.qcut(df['AnnualIncome'],             q=3, labels=[1, 2, 3]).astype(int)
df['NWS']   = pd.qcut(df['NetWorth'],                 q=3, labels=[1, 2, 3]).astype(int)
df['InvS']  = pd.qcut(df['InvestmentPortfolioValue'], q=3, labels=[1, 2, 3]).astype(int)

# Composite score (3–9) → 7  bins
df['Composite'] = df['IncS'] + df['NWS'] + df['InvS']

tier_map = {
    3: '3 – Lowest Wealth',
    4: '4 – Low',
    5: '5 – Low-Mid',
    6: '6 – Mid',
    7: '7 – Mid-High',
    8: '8 – High',
    9: '9 – Highest Wealth',
}
tier_order = list(tier_map.values())
df['WealthTier'] = df['Composite'].map(tier_map)

# Aggregate
grouped = (
    df.groupby('WealthTier')
    .agg(
        Total=('TermDepositSubscribed', 'count'),
        Subscribers=('TermDepositSubscribed', 'sum'),
        AvgIncome=('AnnualIncome', 'mean'),
        AvgNetWorth=('NetWorth', 'mean'),
        AvgInvestment=('InvestmentPortfolioValue', 'mean'),
    )
    .reset_index()
)
grouped['SubscriptionRate'] = (grouped['Subscribers'] / grouped['Total'] * 100).round(2)
grouped['AvgIncome']     = grouped['AvgIncome'].round(0).astype(int)
grouped['AvgNetWorth']   = grouped['AvgNetWorth'].round(0).astype(int)
grouped['AvgInvestment'] = grouped['AvgInvestment'].round(0).astype(int)

# Bar chart
bars = (
    alt.Chart(grouped)
    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, size=60)
    .encode(
        x=alt.X(
            'WealthTier:N',
            sort=tier_order,
            axis=alt.Axis(title='Wealth Tier (Composite Score)', labelAngle=0, labelLimit=200),
        ),
        y=alt.Y(
            'SubscriptionRate:Q',
            axis=alt.Axis(title='Subscription Rate (%)', format='.0f'),
            scale=alt.Scale(domain=[0, 55]),
        ),
        color=alt.Color(
            'WealthTier:N',
            sort=tier_order,
            scale=alt.Scale(
                domain=tier_order,
                range=['#dc2626', '#ea580c', '#d97706', '#ca8a04', '#65a30d', '#16a34a', '#059669'],
            ),
            legend=None,
        ),
        tooltip=[
            alt.Tooltip('WealthTier:N',        title='Tier'),
            alt.Tooltip('SubscriptionRate:Q',   title='Sub. Rate (%)', format='.1f'),
            alt.Tooltip('Subscribers:Q',        title='Subscribers', format=',d'),
            alt.Tooltip('Total:Q',              title='Total Customers', format=',d'),
            alt.Tooltip('AvgIncome:Q',          title='Avg Income ($)', format=',d'),
            alt.Tooltip('AvgNetWorth:Q',        title='Avg Net Worth ($)', format=',d'),
            alt.Tooltip('AvgInvestment:Q',      title='Avg Investment ($)', format=',d'),
        ],
    )
    .properties(width=700, height=400)
)

# Rate labels above bars
rate_text = (
    alt.Chart(grouped)
    .mark_text(dy=-10, fontSize=13, fontWeight='bold', color='#333')
    .encode(
        x=alt.X('WealthTier:N', sort=tier_order),
        y=alt.Y('SubscriptionRate:Q'),
        text=alt.Text('SubscriptionRate:Q', format='.1f'),
    )
)

# Sample size labels below bars
n_text = (
    alt.Chart(grouped)
    .mark_text(dy=15, fontSize=10, color='#999')
    .encode(
        x=alt.X('WealthTier:N', sort=tier_order),
        y=alt.value(400),
        text=alt.Text('Total:Q', format='n=,d'),
    )
)

#  Combine
chart = (
    (bars + rate_text + n_text)
    .properties(
        title=alt.Title(
            text='Wealth Segmentation: Which wealth profile subscribes most?',
            subtitle=['Composite score = Income + Net Worth + Investment'],
        ),
    )
    .configure_view(strokeWidth=0)
    .configure_axis(gridColor='#eee')
)


chart.show()