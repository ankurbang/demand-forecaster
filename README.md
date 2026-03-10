# 📊 SKU Demand Forecasting Tool

A Streamlit-based web application that automatically identifies the best forecasting model per SKU using a **Champion-Challenger** tournament approach across 7 forecasting algorithms.

---

## 🧠 About the Project

This tool was built to simplify demand planning by automating model selection. Instead of manually tuning forecasting models, it:

- Ingests historical demand data from an Excel file (`Forecasting data.xlsx`)
- Runs **7 forecasting models** on each SKU's history
- Evaluates each model using **MAPE** (Mean Absolute Percentage Error) on the last 6 months of actuals
- Automatically selects the **champion model** with the lowest error
- Allows users to **manually override** the model selection
- Displays an **interactive Plotly chart** of historical demand vs. forecast
- Exports the 12-month forecast as a **downloadable CSV**

### 🔬 Models Evaluated

| # | Model | Description |
|---|-------|-------------|
| 1 | **Naive** | Repeats the last known value |
| 2 | **Moving Average** | Average of the last 3 periods |
| 3 | **Linear Trend** | OLS regression over time |
| 4 | **SES** | Simple Exponential Smoothing |
| 5 | **Holt-Winters** | Triple exponential smoothing with trend & seasonality |
| 6 | **ARIMA** | Auto-Regressive Integrated Moving Average (1,1,1) |
| 7 | **Prophet** | Facebook's time-series model with yearly seasonality |

---

## 📁 Project Structure

```
Demand_Forecaster/
├── app.py                  # Main Streamlit application
├── Forecasting data.xlsx   # Input data file (Demand History sheet)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## ⚙️ Setup Instructions

### Prerequisites

- Python 3.9 or higher
- pip

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/ankurbang/demand-forecaster.git
cd demand-forecaster
```

---

### Step 2 — Create a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ You should see `(venv)` at the start of your terminal prompt once activated.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ This may take a few minutes as it installs Prophet, statsmodels, and other packages.

---

### Step 4 — Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📊 Input File Format

The app expects an Excel file named `Forecasting data.xlsx` with a sheet called **`Demand History`**.

- The **first column** should be the SKU identifier (column name: `SKU`)
- Remaining columns should be **monthly demand figures** with date-parseable headers (e.g., `Jan-2023`, `2023-01-01`)
- Optional metadata columns (`H1`, `H2`, `H3`, `H4`, `UOM`, `DESCRIPTION`, `CATEGORY`) are automatically excluded from the time series

---

## 📦 Requirements

Create a `requirements.txt` with the following content if not present:

```
streamlit
pandas
numpy
statsmodels
prophet
scikit-learn
plotly
openpyxl
```

---

## 🚀 Usage

1. Launch the app with `streamlit run app.py`
2. Upload `Forecasting data.xlsx` using the **sidebar uploader**
3. Select a **SKU** from the dropdown
4. Click **"Generate Forecasts"**
5. Review the auto-selected champion model and the forecast chart
6. Optionally override the model using the **Manual Model Override** dropdown
7. Download the 12-month forecast as a CSV

---

## ⚠️ Notes

- SKUs with fewer than 10 historical data points will default to the **Naive** model
- Holt-Winters seasonality requires at least **24 months** of data; otherwise it falls back to trend-only
- Prophet requires dates to be parseable — ensure column headers follow a consistent date format
