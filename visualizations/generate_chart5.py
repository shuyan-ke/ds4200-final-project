import pandas as pd
import json

# ── 1. Load data ──────────────────────────────────────────────────────────────
df = pd.read_csv("Bank_Marketing_Dataset.csv")

# ── 2. Select relevant columns ────────────────────────────────────────────────
cols = ['MarketingScore', 'ResponsePropensity', 'AnnualIncome', 'NetWorth',
        'InvestmentPortfolioValue', 'TermDepositSubscribed', 'CustomerSegment',
        'JobTitle', 'RiskRating', 'SalaryCategory', 'Age']
out = df[cols].copy()

# ── 3. Engineer WealthScore ───────────────────────────────────────────────────
out['income_norm'] = (out['AnnualIncome'] - out['AnnualIncome'].min()) / (out['AnnualIncome'].max() - out['AnnualIncome'].min())
out['networth_norm']= (out['NetWorth'] - out['NetWorth'].min()) / (out['NetWorth'].max() - out['NetWorth'].min())
out['invest_norm'] = (out['InvestmentPortfolioValue'] - out['InvestmentPortfolioValue'].min()) / (out['InvestmentPortfolioValue'].max() - out['InvestmentPortfolioValue'].min())
out['WealthScore'] = (out['income_norm'] + out['networth_norm'] + out['invest_norm']) / 3

# ── 4. Clean up ───────────────────────────────────────────────────────────────
out = out.drop(columns=['AnnualIncome', 'NetWorth', 'InvestmentPortfolioValue',  
                        'income_norm', 'networth_norm', 'invest_norm'])

# ── 5. Sample ────────────────────────────────────────────────────────────────
# Preserves real 30/70 ratio from full dataset
yes = out[out['TermDepositSubscribed'] == 1].sample(900,  random_state=42)
no  = out[out['TermDepositSubscribed'] == 0].sample(2100, random_state=42)
sampled = pd.concat([yes, no]).sample(frac=1, random_state=42).reset_index(drop=True)
sampled['TermDepositSubscribed'] = sampled['TermDepositSubscribed'].map({1: 'Yes', 0: 'No'})

# ── 6. Round floats ──────────────────────────────────────────────────────────
sampled['MarketingScore'] = sampled['MarketingScore'].round(4)
sampled['ResponsePropensity'] = sampled['ResponsePropensity'].round(4)
sampled['WealthScore'] = sampled['WealthScore'].round(4)

# ── 7. Export to JSON ────────────────────────────────────────────────────────
inline_json = json.dumps(sampled.to_dict(orient='records'))

# ── 8. Inject into template and write final HTML ─────────────────────────────
with open("Chart5_TEMPLATE.html", "r") as f:
    template = f.read()

html = template.replace("__DATA_PLACEHOLDER__", inline_json)

with open("Chart5.html", "w") as f:
    f.write(html)
