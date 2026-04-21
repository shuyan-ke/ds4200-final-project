import pandas as pd
import altair as alt
from pathlib import Path

# Load data
SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH   = SCRIPT_DIR / "Bank_Marketing_Dataset.csv"

if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"Cannot find Bank_Marketing_Dataset.csv\n"
        f"  Looked in: {SCRIPT_DIR}\n"
        f"  Place the CSV in the same folder as this script."
    )

df = pd.read_csv(CSV_PATH)
alt.data_transformers.disable_max_rows()

# Features
df['Subscribed'] = df['TermDepositSubscribed'].map({1: 'Yes', 0: 'No'})

# Wealth composite → 4 quartile tiers (matches HTML: 25 000 per tier)
df['IncS']  = pd.qcut(df['AnnualIncome'],             q=3, labels=[1, 2, 3]).astype(int)
df['NWS']   = pd.qcut(df['NetWorth'],                 q=3, labels=[1, 2, 3]).astype(int)
df['InvS']  = pd.qcut(df['InvestmentPortfolioValue'], q=3, labels=[1, 2, 3]).astype(int)
df['Composite'] = df['IncS'] + df['NWS'] + df['InvS']
df['WealthTier'] = pd.qcut(
    df['Composite'], q=4,
    labels=['Low Wealth', 'Mid-Low', 'Mid-High', 'High Wealth'],
)
tier_order = ['Low Wealth', 'Mid-Low', 'Mid-High', 'High Wealth']

# Aggregated datasets
pie_data = df.groupby('Subscribed').size().reset_index(name='Count')
pie_data['Pct'] = (pie_data['Count'] / pie_data['Count'].sum() * 100).round(1)
pie_data['Label'] = (
    pie_data['Subscribed'] + '\n'
    + pie_data['Count'].apply(lambda x: f"{x:,}")
    + ' (' + pie_data['Pct'].astype(str) + '%)'
)

scatter_df = (
    df[['CallResponseScore', 'ResponsePropensity', 'Subscribed']]
    .sample(n=3_000, random_state=42)
    .copy()
)

wealth_df = df.groupby(['WealthTier', 'Subscribed']).size().reset_index(name='Count')
tier_totals = df.groupby('WealthTier').size().reset_index(name='TierTotal')
wealth_df = wealth_df.merge(tier_totals, on='WealthTier')
wealth_df['Rate'] = (wealth_df['Count'] / wealth_df['TierTotal'] * 100).round(1)

# Click Selection
click = alt.selection_point(fields=['Subscribed'])

# Chart 1
pie = (
    alt.Chart(pie_data)
    .mark_arc(outerRadius=130, innerRadius=55,
              stroke='white', strokeWidth=3, cursor='pointer')
    .encode(
        theta=alt.Theta('Count:Q', stack=True),
        color=alt.condition(
            click,
            alt.Color('Subscribed:N',
                       scale=alt.Scale(domain=['No', 'Yes'],
                                       range=['#9ca3af', '#1D9E75']),
                       legend=alt.Legend(title='Subscribed')),
            alt.value('#ddd'),
        ),
        opacity=alt.condition(click, alt.value(1.0), alt.value(0.35)),
        tooltip=[
            alt.Tooltip('Subscribed:N', title='Subscribed'),
            alt.Tooltip('Count:Q',      title='Count',      format=',d'),
            alt.Tooltip('Pct:Q',        title='Share (%)',   format='.1f'),
        ],
    )
    .add_params(click)
)

pie_labels = (
    alt.Chart(pie_data)
    .mark_text(radius=200, fontSize=13, fontWeight='bold',
               lineBreak='\n', align='center')
    .encode(
        theta=alt.Theta('Count:Q', stack=True),
        text='Label:N',
        color=alt.condition(click, alt.value('#333'), alt.value('#bbb')),
    )
)

chart1 = (
    (pie + pie_labels)
    .properties(width=520, height=420,
                title=alt.Title(
                    text='Chart 1 — Subscription Breakdown',
                    subtitle='Click a slice to filter Charts 2 & 3. '
                             'Double click background to reset.'))
)


_empty = alt.Chart(pd.DataFrame()).mark_point(opacity=0)
spacer_l = _empty.properties(width=400, height=10)
spacer_r = _empty.properties(width=140, height=10)

# Chart 2
sub_dropdown = alt.param(
    name='sub_filter', value='All',
    bind=alt.binding_select(options=['All', 'No', 'Yes'],
                            name='Subscribed: '),
)
reg_toggle = alt.param(
    name='show_regression', value=True,
    bind=alt.binding_checkbox(name=' Regression Lines'),
)

# Scatter points
scatter_points = (
    alt.Chart(scatter_df)
    .transform_filter("sub_filter == 'All' || datum.Subscribed == sub_filter")
    .mark_circle(size=50, stroke='white', strokeWidth=0.5)
    .encode(
        x=alt.X('CallResponseScore:Q', title='Call Response Score',
                 scale=alt.Scale(zero=False)),
        y=alt.Y('ResponsePropensity:Q', title='Response Propensity',
                 scale=alt.Scale(domain=[0, 0.62])),
        color=alt.condition(
            click,
            alt.Color('Subscribed:N',
                       scale=alt.Scale(domain=['No', 'Yes'],
                                       range=['#94A3B8', '#F59E0B']),
                       legend=None),
            alt.value('#e2e2e2'),
        ),
        opacity=alt.condition(click, alt.value(0.6), alt.value(0.04)),
        tooltip=[
            alt.Tooltip('CallResponseScore:Q',  title='Call Score',  format='.1f'),
            alt.Tooltip('ResponsePropensity:Q',  title='Propensity', format='.2f'),
            alt.Tooltip('Subscribed:N',          title='Subscribed'),
        ],
        order=alt.Order('Subscribed:N', sort='descending'),
    )
)

# Regression "No" group
reg_no = (
    alt.Chart(scatter_df)
    .transform_filter("sub_filter == 'All' || sub_filter == 'No'")
    .transform_filter("datum.Subscribed === 'No'")
    .transform_regression('ResponsePropensity', 'CallResponseScore',
                          method='linear')
    .mark_line(strokeWidth=2.5, strokeDash=[6, 3])
    .encode(x='CallResponseScore:Q', y='ResponsePropensity:Q',
            color=alt.value('#94A3B8'))
)
reg_no.encoding['opacity'] = {
    'condition': {'test': 'show_regression', 'value': 1}, 'value': 0,
}

# Regression "Yes" group
reg_yes = (
    alt.Chart(scatter_df)
    .transform_filter("sub_filter == 'All' || sub_filter == 'Yes'")
    .transform_filter("datum.Subscribed === 'Yes'")
    .transform_regression('ResponsePropensity', 'CallResponseScore',
                          method='linear')
    .mark_line(strokeWidth=2.5, strokeDash=[6, 3])
    .encode(x='CallResponseScore:Q', y='ResponsePropensity:Q',
            color=alt.value('#F59E0B'))
)
reg_yes.encoding['opacity'] = {
    'condition': {'test': 'show_regression', 'value': 1}, 'value': 0,
}

chart2 = (
    (scatter_points + reg_no + reg_yes)
    .add_params(sub_dropdown, reg_toggle)
    .properties(width=620, height=420,
                title=alt.Title(
                    text='Chart 2 — Call Response vs. Propensity',
                    subtitle='n = 3,000 sampled  |  '
                             'Dashed lines = linear regression by group'))
)

# Chart 3
chart3 = (
    alt.Chart(wealth_df)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X('WealthTier:N', sort=tier_order,
                 axis=alt.Axis(title='Wealth Tier',
                               labelAngle=0, labelLimit=200)),
        y=alt.Y('Count:Q',
                 axis=alt.Axis(title='Customer Count', format=',d')),
        color=alt.condition(
            click,
            alt.Color('Subscribed:N',
                       scale=alt.Scale(domain=['No', 'Yes'],
                                       range=['#94A3B8', '#F59E0B']),
                       legend=None),
            alt.value('#e2e2e2'),
        ),
        opacity=alt.condition(click, alt.value(1.0), alt.value(0.15)),
        xOffset='Subscribed:N',
        tooltip=[
            alt.Tooltip('WealthTier:N',  title='Tier'),
            alt.Tooltip('Subscribed:N',  title='Subscribed'),
            alt.Tooltip('Count:Q',       title='Count',     format=',d'),
            alt.Tooltip('Rate:Q',        title='% of Tier', format='.1f'),
        ],
    )
    .properties(width=620, height=420,
                title=alt.Title(
                    text='Chart 3 — Wealth Segmentation',
                    subtitle='Composite score (Income + Net Worth + Investment)'))
)

# Dashboard 
dashboard = (
    alt.vconcat(
        alt.hconcat(spacer_l, chart1, spacer_r),
        alt.hconcat(chart2, chart3),
    )
    .resolve_scale(color='shared')
    .configure_view(strokeWidth=0)
    .configure_axis(gridColor='#eee')
    .configure_concat(spacing=35)
)

OUT = SCRIPT_DIR / 'my_chart.html'
dashboard.save(str(OUT))
print(f"Saved → {OUT}")
dashboard.show()
