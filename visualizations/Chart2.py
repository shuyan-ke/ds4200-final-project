import altair as alt
import pandas as pd

# Load data
df = pd.read_csv("Bank_Marketing_Dataset.csv")

sample = (
    df[["CallResponseScore", "ResponsePropensity", "TermDepositSubscribed"]]
    .sample(n=4_000, random_state=42)
    .copy()
)
sample["TermDepositSubscribed"] = sample["TermDepositSubscribed"].map({1: "Yes", 0: "No"})

alt.data_transformers.disable_max_rows()

# Build chart
chart = (
    alt.Chart(sample)
    .mark_circle(size=50, opacity=0.55, strokeWidth=0.5, stroke="white")
    .encode(
        x=alt.X("CallResponseScore:Q", title="Call Response Score",
                 scale=alt.Scale(zero=False)),
        y=alt.Y("ResponsePropensity:Q", title="Response Propensity",
                 scale=alt.Scale(zero=False)),
        color=alt.Color(
            "TermDepositSubscribed:N",
            title="Subscribed",
            scale=alt.Scale(domain=["No", "Yes"], range=["#94A3B8", "#F59E0B"]),
        ),
        tooltip=[
            alt.Tooltip("CallResponseScore:Q", title="Call Response Score", format=".1f"),
            alt.Tooltip("ResponsePropensity:Q", title="Response Propensity", format=".2f"),
            alt.Tooltip("TermDepositSubscribed:N", title="Subscribed"),
        ],
        order=alt.Order("TermDepositSubscribed:N", sort="descending"),
    )
    .properties(
        width=720,
        height=460,
        title=alt.Title(
            text="Campaign Behavior — Call Response vs. Subscription Propensity",
            subtitle="Does a better call response lead to higher subscription?  (n = 4,000 sampled)",
        ),
    )
)

chart.show()