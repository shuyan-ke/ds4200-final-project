# ds4200-final-project
# 📊 Bank Term Deposit Analysis for Marketing Purpose

---

## 👥 Team

| Name | Responsibilities |
|------|-----------------|
| Shelley Yang | Introduction, data overview, writeup |
| Tam Vu | Reference research, HTML/CSS/JS development, content review |
| Shuyan Ke | GitHub setup, static images, visualization development |

---

## 📁 Repository Structure
```
├── index.html                        # Main project webpage
├── data/
│   └── Bank_Marketing_Dataset.csv
├── visualizations/
│   ├── DS4200_visualizations.ipynb   # Altair charts (Python)
│   ├── visualizations.html           # Exported Altair output
│   └── d3/                           # D3.js visualization files
├── assets/
│   └── images/
├── design_notes.docx                 # Visualization design explanations
└── README.md
```

---

## 📊 Dataset

- **Source:** Kaggle
- **Size:** 100,000 rows × 45 columns
- **Key features:** Age, gender, employment, annual income, education level, housing/loan status, `TermDepositSubscribed` (binary target)

---

## 📈 Visualizations

1. Subscription rate by education level *(Altair bar chart)*
2. Age distribution: subscribers vs. non-subscribers *(Altair area chart)*
3. Subscription rate by job type *(bar chart)*
4. Income distribution vs. subscription *(box plot)*
5. Interactive customer segment explorer *(D3)*

---

## 🔗 References

- [Why community banks are revamping their CD strategies](https://www.independentbanker.org/w/why-community-banks-are-revamping-their-cd-strategies)
- [CD marketing strategies — BankBound](https://www.bankbound.com/blog/cd-marketing/)

---

## 🚀 Running Locally
```bash
pip install pandas altair
jupyter notebook DS4200_visualizations.ipynb
```

To view the webpage, open `index.html` in a browser or visit the GitHub Pages link below.

---

🌐 **Live site:** *(add GitHub Pages URL once published)*  
📅 DS4200 · Northeastern University · Spring 2026
