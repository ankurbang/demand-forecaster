import streamlit as st
import pandas as pd
import numpy as np
import warnings
import io
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_percentage_error
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

# --- UI CONFIG ---
st.set_page_config(page_title="Champion-Challenger Demand Forecast", layout="wide")
st.title("SKU Demand Forecasting Tool")
st.markdown("Upload your 'Forecasting data.xlsx' to find the best model per SKU.")

# --- FORECASTING ENGINE ---

def run_models(series, periods=12):
    """Runs 7 models and returns forecasts."""
    results = {}
    # 1. Naive
    results['Naive'] = np.full(periods, series.iloc[-1])
    
    # 2. Moving Average
    results['Moving Average'] = np.full(periods, series.tail(3).mean())

    # 3. Linear Trend
    try:
        x = np.arange(len(series)).reshape(-1, 1)
        model = LinearRegression().fit(x, series.values)
        future_x = np.arange(len(series), len(series) + periods).reshape(-1, 1)
        results['Linear Trend'] = model.predict(future_x)
    except: results['Linear Trend'] = results['Naive']

    # 4. SES
    try:
        results['SES'] = SimpleExpSmoothing(series, initialization_method="estimated").fit().forecast(periods)
    except: results['SES'] = results['Naive']

    # 5. Holt-Winters
    try:
        # Fallback to non-seasonal if data is short
        seasonal = 'add' if len(series) >= 24 else None 
        results['Holt-Winters'] = ExponentialSmoothing(series, trend='add', seasonal=seasonal, seasonal_periods=12).fit().forecast(periods)
    except: results['Holt-Winters'] = results['Naive']

    # 6. ARIMA
    try:
        results['ARIMA'] = ARIMA(series, order=(1,1,1)).fit().forecast(periods)
    except: results['ARIMA'] = results['Naive']

    # 7. Prophet
    try:
        df_p = series.reset_index()
        df_p.columns = ['ds', 'y']
        df_p['ds'] = pd.to_datetime(df_p['ds'])
        m = Prophet(yearly_seasonality=True, interval_width=0.95).fit(df_p)
        future = m.make_future_dataframe(periods=periods, freq='MS')
        results['Prophet'] = m.predict(future)['yhat'].tail(periods).values
    except: results['Prophet'] = results['Naive']

    return results

def get_best_model(series):
    """Requirement: Identify best model based on historic MAPE (Last 6 months)."""
    if len(series) < 10: return "Naive", 0.0
    
    train = series.iloc[:-6]
    actuals = series.iloc[-6:]
    preds = run_models(train, periods=6)
    
    mapes = {}
    for name, forecast in preds.items():
        try:
            mapes[name] = mean_absolute_percentage_error(actuals, forecast)
        except: mapes[name] = 1.0 # Max penalty
        
    best_model = min(mapes, key=mapes.get)
    return best_model, mapes[best_model]

# --- MAIN APP LOGIC ---

uploaded_file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file:
    # 1. Load Data
    xl = pd.ExcelFile(uploaded_file)
    sheet = "Demand History" if "Demand History" in xl.sheet_names else xl.sheet_names[0]
    df = pd.read_excel(uploaded_file, sheet_name=sheet)

    # Clean Columns
    df.columns = [str(c).strip() for c in df.columns]
    sku_col = 'SKU' if 'SKU' in df.columns else df.columns[0]
    
    skus = df[sku_col].unique()
    selected_sku = st.selectbox("Select SKU to Analyze", skus)
    
    # 2. Extract and Clean Time Series
    sku_row = df[df[sku_col] == selected_sku].iloc[0]
    # Filter only columns that look like dates or are known demand periods
    meta_to_drop = [sku_col, 'H1', 'H2', 'H3', 'H4', 'UOM', 'DESCRIPTION', 'CATEGORY']
    history = sku_row.drop(labels=meta_to_drop, errors='ignore')
    
    # Convert index to datetime and values to numeric
    history.index = pd.to_datetime(history.index, errors='coerce')
    history = pd.to_numeric(history, errors='coerce').fillna(0)
    history = history.dropna().sort_index()

    if st.button("Generate Forecasts"):
        with st.spinner(f"Evaluating 7 models for {selected_sku}..."):
            # Tournament
            champion, error = get_best_model(history)
            all_forecasts = run_models(history, periods=12)
            
            # Store in session state for interactivity
            st.session_state['fc_results'] = all_forecasts
            st.session_state['champion'] = champion
            st.session_state['history'] = history

    # 3. Display Results (Requirement 5 & 6)
    if 'fc_results' in st.session_state:
        res = st.session_state['fc_results']
        champ = st.session_state['champion']
        hist = st.session_state['history']
        
        st.success(f"Auto-selected: **{champ}**")
        
        # User Manual Override
        chosen_model = st.selectbox("Manual Model Override:", list(res.keys()), index=list(res.keys()).index(champ))
        
        # Plotting
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist.values, name="Actual History"))
        
        future_dates = pd.date_range(start=hist.index[-1], periods=13, freq='MS')[1:]
        fig.add_trace(go.Scatter(x=future_dates, y=res[chosen_model], name="Forecast", line=dict(dash='dash', color='red')))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Export
        out_df = pd.DataFrame({"Month": future_dates, "Forecast": res[chosen_model]})
        st.download_button("Download Forecast CSV", out_df.to_csv(index=False), f"{selected_sku}_forecast.csv")