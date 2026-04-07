import pandas as pd
import altair as alt


df = pd.read_csv("Bank_Marketing_Dataset.csv")

# Normalize each column to 0-1
df['income_norm'] = (df['AnnualIncome'] - df['AnnualIncome'].min()) / (df['AnnualIncome'].max() - df['AnnualIncome'].min())
df['networth_norm'] = (df['NetWorth'] - df['NetWorth'].min()) / (df['NetWorth'].max() - df['NetWorth'].min())
df['invest_norm'] = (df['InvestmentPortfolioValue'] - df['InvestmentPortfolioValue'].min()) / (df['InvestmentPortfolioValue'].max() - df['InvestmentPortfolioValue'].min())

# WealthScore = average of 3 normalized columns
df['WealthScore'] = (df['income_norm'] + df['networth_norm'] + df['invest_norm']) / 3

# Split into 4 equal groups
tier_order = ['Q1 – Low Wealth', 'Q2 – Mid-Low', 'Q3 – Mid-High', 'Q4 – High Wealth']
df['WealthTier'] = pd.qcut(df['WealthScore'], q=4, labels=tier_order)

# Aggregate
grouped = (
    df.groupby('WealthTier')
    .agg(
        Total=('TermDepositSubscribed', 'count'),
        Subscribers=('TermDepositSubscribed', 'sum'),
        AvgIncome=('AnnualIncome', 'mean'),
        AvgNetWorth=('NetWorth', 'mean'),
        AvgInvestment=('InvestmentPortfolioValue', 'mean')
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
                range=['#bfdbfe', '#60a5fa', '#2563eb', '#1e3a8a'],
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

#  Combine
chart = (
    (bars + rate_text)
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
chart.save("Chart3.html")