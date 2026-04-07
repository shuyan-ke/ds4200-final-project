import pandas as pd
import altair as alt

df = pd.read_csv("Bank_Marketing_Dataset.csv")

alt.data_transformers.disable_max_rows()

# Normalize each column to 0-1
df['income_norm'] = (df['AnnualIncome'] - df['AnnualIncome'].min()) / (df['AnnualIncome'].max() - df['AnnualIncome'].min())
df['networth_norm'] = (df['NetWorth'] - df['NetWorth'].min()) / (df['NetWorth'].max() - df['NetWorth'].min())
df['invest_norm'] = (df['InvestmentPortfolioValue'] - df['InvestmentPortfolioValue'].min()) / (df['InvestmentPortfolioValue'].max() - df['InvestmentPortfolioValue'].min())

# WealthScore = average of 3 normalized columns
df['WealthScore'] = (df['income_norm'] + df['networth_norm'] + df['invest_norm']) / 3

# Split into 4 equal groups
tier_order = ['Low Wealth', 'Mid-Low', 'Mid-High', 'High Wealth']
df['WealthTier'] = pd.qcut(df['WealthScore'], q=4, labels=tier_order)

df['Subscribed'] = df['TermDepositSubscribed'].map({1: 'Yes', 0: 'No'})

# Sample for Chart 2 scatter
scatter_df = (
    df[['CallResponseScore', 'ResponsePropensity', 'Subscribed']]
    .sample(n=3_000, random_state=42)
    .copy()
)

# Pie data
pie_data = df.groupby('Subscribed').size().reset_index(name='Count')
pie_data['Pct'] = (pie_data['Count'] / pie_data['Count'].sum() * 100).round(1)
pie_data['Label'] = pie_data['Subscribed'] + '\n' + pie_data['Count'].apply(lambda x: f"{x:,}") + ' (' + pie_data['Pct'].astype(str) + '%)'

#  Wealth tier data
wealth_df = df.groupby(['WealthTier', 'Subscribed']).size().reset_index(name='Count')
tier_totals = df.groupby('WealthTier').size().reset_index(name='TierTotal')
wealth_df = wealth_df.merge(tier_totals, on='WealthTier')
wealth_df['Rate'] = (wealth_df['Count'] / wealth_df['TierTotal'] * 100).round(1)


click = alt.selection_point(fields=['Subscribed'])


# Chart 1
pie = (
    alt.Chart(pie_data)
    .mark_arc(outerRadius=130, innerRadius=55, stroke='white', strokeWidth=3, cursor='pointer')
    .encode(
        theta=alt.Theta('Count:Q', stack=True),
        color=alt.condition(
            click,
            alt.Color(
                'Subscribed:N',
                scale=alt.Scale(domain=['No', 'Yes'], range=['#9ca3af', '#1D9E75']),
                legend=alt.Legend(title='Subscribed'),
            ),
            alt.value('#ddd'),
        ),
        opacity=alt.condition(click, alt.value(1.0), alt.value(0.35)),
        tooltip=[
            alt.Tooltip('Subscribed:N', title='Subscribed'),
            alt.Tooltip('Count:Q', title='Count', format=',d'),
            alt.Tooltip('Pct:Q', title='Share (%)', format='.1f'),
        ],
    )
    .add_params(click)
)

pie_labels = (
    alt.Chart(pie_data)
    .mark_text(radius=200, fontSize=13, fontWeight='bold', lineBreak='\n', align='center')
    .encode(
        theta=alt.Theta('Count:Q', stack=True),
        text='Label:N',
        color=alt.condition(
            click,
            alt.value('#333'),
            alt.value('#bbb'),
        ),
    )
)

chart1 = (
    (pie + pie_labels)
    .properties(
        width=520, height=420,
        title=alt.Title(
            text='Chart 1 — Subscription Breakdown',
            subtitle='Click a slice to filter Charts 2 & 3. Double click background to reset.',
        ),
    )
)

# Chart 2
chart2 = (
    alt.Chart(scatter_df)
    .mark_circle(size=50, strokeWidth=0.5, stroke='white')
    .encode(
        x=alt.X('CallResponseScore:Q', title='Call Response Score',
                 scale=alt.Scale(zero=False)),
        y=alt.Y('ResponsePropensity:Q', title='Response Propensity',
                 scale=alt.Scale(domain=[0, 0.62])),
        color=alt.condition(
            click,
            alt.Color('Subscribed:N',
                       scale=alt.Scale(domain=['No', 'Yes'], range=['#94A3B8', '#F59E0B']),
                       legend=None),
            alt.value('#e2e2e2'),
        ),
        opacity=alt.condition(click, alt.value(0.6), alt.value(0.04)),
        tooltip=[
            alt.Tooltip('CallResponseScore:Q', title='Call Score', format='.1f'),
            alt.Tooltip('ResponsePropensity:Q', title='Propensity', format='.2f'),
            alt.Tooltip('Subscribed:N', title='Subscribed'),
        ],
        order=alt.Order('Subscribed:N', sort='descending'),
    )
    .properties(
        width=620, height=420,
        title=alt.Title(
            text='Chart 2 — Call Response vs. Propensity',
            subtitle='n = 3,000 sampled',
        ),
    )
)

# Chart 3
chart3 = (
    alt.Chart(wealth_df)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X('WealthTier:N', sort=tier_order,
                 axis=alt.Axis(title='Wealth Tier', labelAngle=0, labelLimit=200)),
        y=alt.Y('Count:Q', axis=alt.Axis(title='Customer Count', format=',d')),
        color=alt.condition(
            click,
            alt.Color('Subscribed:N',
                       scale=alt.Scale(domain=['No', 'Yes'], range=['#94A3B8', '#F59E0B']),
                       legend=None),
            alt.value('#e2e2e2'),
        ),
        opacity=alt.condition(click, alt.value(1.0), alt.value(0.15)),
        xOffset='Subscribed:N',
        tooltip=[
            alt.Tooltip('WealthTier:N', title='Tier'),
            alt.Tooltip('Subscribed:N', title='Subscribed'),
            alt.Tooltip('Count:Q', title='Count', format=',d'),
            alt.Tooltip('Rate:Q', title='% of Tier', format='.1f'),
        ],
    )
    .properties(
        width=620, height=420,
        title=alt.Title(
            text='Chart 3 — Wealth Segmentation',
            subtitle='Composite score (Income + Net Worth + Investment)',
        ),
    )
)

# Dashboard
dashboard = (
    alt.vconcat(
        alt.hconcat(
            alt.Chart(pd.DataFrame({'x': []})).mark_point(opacity=0).properties(width=400, height=10),
            chart1,
            alt.Chart(pd.DataFrame({'x': []})).mark_point(opacity=0).properties(width=140, height=10),
        ),
        alt.hconcat(chart2, chart3),
    )
    .resolve_scale(color='shared')
    .configure_view(strokeWidth=0)
    .configure_axis(gridColor='#eee')
    .configure_concat(spacing=35)
)

dashboard.show()
