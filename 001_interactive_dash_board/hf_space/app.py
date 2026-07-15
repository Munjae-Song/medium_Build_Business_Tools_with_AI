import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import gradio as gr
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), 'quality_data_small.db')

def get_nominal_from_code(product_code):
    return int(product_code[:2]) * 0.1

def calculate_capability(data, usl, lsl):
    if len(data) < 2: return 0
    mu = np.mean(data)
    sigma = np.std(data, ddof=1)
    if sigma == 0: return 0
    cpu = (usl - mu) / (3 * sigma)
    cpl = (mu - lsl) / (3 * sigma)
    return max(0, min(cpu, cpl))

def run_analysis(selected_date_str, product_code):
    try:
        center_date = datetime.strptime(selected_date_str.split(' ')[0], '%Y-%m-%d')
        start_dt = center_date - timedelta(days=10)
        end_dt = center_date + timedelta(days=10)

        conn = sqlite3.connect(DB_PATH)
        years = sorted(list(set([start_dt.year, end_dt.year])))
        all_dfs = []
        for yr in years:
            table_name = f"DS_PRDT_{product_code}_{str(yr)[-2:]}"
            try:
                query = f"SELECT ins_date, dimension, thickness FROM {table_name}"
                all_dfs.append(pd.read_sql_query(query, conn))
            except: continue

        if not all_dfs: return None, None, None, None, "Error: No data found."

        df = pd.concat(all_dfs)
        df['ins_date'] = pd.to_datetime(df['ins_date'])
        mask = (df['ins_date'].dt.date >= start_dt.date()) & (df['ins_date'].dt.date <= end_dt.date()) & (df['dimension'] > 0) & (df['thickness'] > 0)
        df_clean = df.loc[mask].sort_values('ins_date').copy()
        df_clean['date_only'] = df_clean['ins_date'].dt.date

        nom_dim = get_nominal_from_code(product_code)
        dim_usl, dim_lsl = nom_dim * 1.1, nom_dim * 0.9
        thick_usl, thick_lsl = 0.7, 0.0

        daily = df_clean.groupby('date_only').agg({'dimension': ['mean', 'std'], 'thickness': ['mean', 'std']}).reset_index()
        daily.columns = ['date', 'd_mean', 'd_std', 't_mean', 't_std']

        d_ppk_list, t_ppk_list = [], []
        for d in daily['date']:
            window_mask = (df_clean['date_only'] <= d) & (df_clean['date_only'] > (d - timedelta(days=5)))
            window_data = df_clean[window_mask]
            d_ppk_list.append(calculate_capability(window_data['dimension'], dim_usl, dim_lsl))
            t_ppk_list.append(calculate_capability(window_data['thickness'], thick_usl, thick_lsl))

        daily['d_ppk_5d'] = d_ppk_list
        daily['t_ppk_5d'] = t_ppk_list
        daily['d_cpk'] = daily['date'].apply(lambda d: calculate_capability(df_clean[df_clean['date_only']==d]['dimension'], dim_usl, dim_lsl))
        daily['t_cpk'] = daily['date'].apply(lambda d: calculate_capability(df_clean[df_clean['date_only']==d]['thickness'], thick_usl, thick_lsl))

        overall_d_ppk = calculate_capability(df_clean['dimension'], dim_usl, dim_lsl)
        overall_t_ppk = calculate_capability(df_clean['thickness'], thick_usl, thick_lsl)

        # Get CPK for the selected date
        selected_day_mask = daily['date'] == center_date.date()
        selected_d_cpk = daily.loc[selected_day_mask, 'd_cpk'].values[0] if not daily[selected_day_mask].empty else 0
        selected_t_cpk = daily.loc[selected_day_mask, 't_cpk'].values[0] if not daily[selected_day_mask].empty else 0

        fig_trend = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Dimension", "Thickness"), specs=[[{"secondary_y": True}], [{"secondary_y": True}]])
        fig_trend.add_trace(go.Scatter(x=daily['date'], y=daily['d_mean'], name="Dim Mean"), row=1, col=1)
        fig_trend.add_trace(go.Scatter(x=daily['date'], y=daily['d_std'], name="Dim Std", line=dict(dash='dot')), row=1, col=1, secondary_y=True)
        fig_trend.add_trace(go.Scatter(x=daily['date'], y=daily['t_mean'], name="Thick Mean"), row=2, col=1)
        fig_trend.add_trace(go.Scatter(x=daily['date'], y=daily['t_std'], name="Thick Std", line=dict(dash='dot')), row=2, col=1, secondary_y=True)

        fig_cap = make_subplots(rows=1, cols=2, subplot_titles=("Dim Capability", "Thick Capability"))
        fig_cap.add_trace(go.Scatter(x=daily['date'], y=daily['d_cpk'], name="Dim Daily Cpk", line=dict(color='blue')), row=1, col=1)
        fig_cap.add_trace(go.Scatter(x=daily['date'], y=daily['d_ppk_5d'], name="Dim 5d Ppk", line=dict(color='green')), row=1, col=1)
        fig_cap.add_trace(go.Scatter(x=daily['date'], y=daily['t_cpk'], name="Thick Daily Cpk", line=dict(color='blue'), showlegend=False), row=1, col=2)
        fig_cap.add_trace(go.Scatter(x=daily['date'], y=daily['t_ppk_5d'], name="Thick 5d Ppk", line=dict(color='green'), showlegend=False), row=1, col=2)

        target_day_df = df_clean[df_clean['date_only'] == center_date.date()]
        fig_hist = make_subplots(rows=1, cols=2, subplot_titles=("Dim Distribution (Nominal ±10%)", "Thick Distribution (0-1.0)"))
        if not target_day_df.empty:
            fig_hist.add_trace(go.Histogram(x=target_day_df['dimension'], xbins=dict(start=dim_lsl, end=dim_usl, size=(dim_usl-dim_lsl)/100), name="Dim"), row=1, col=1)
            fig_hist.add_trace(go.Histogram(x=target_day_df['thickness'], xbins=dict(start=0.0, end=1.0, size=0.01), name="Thick"), row=1, col=2)

        fig_hist.update_xaxes(range=[dim_lsl, dim_usl], row=1, col=1)
        fig_hist.update_xaxes(range=[0, 1.0], row=1, col=2)

        summary_df = pd.DataFrame({
            "Metric": ["Dimension", "Thickness"],
            "Selected Date Cpk": [selected_d_cpk, selected_t_cpk],
            "Overall Ppk (21d)": [overall_d_ppk, overall_t_ppk],
            "OOS Count": [len(df_clean[(df_clean['dimension']>dim_usl)|(df_clean['dimension']<dim_lsl)]), len(df_clean[(df_clean['thickness']>thick_usl)|(df_clean['thickness']<thick_lsl)])]
        })
        conn.close()
        return summary_df, fig_trend, fig_cap, fig_hist, "Analysis Success"
    except Exception as e: return None, None, None, None, f"Error: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# Manufacturing Quality Dashboard")
    gr.Markdown(
        "Demo for the Medium series **Build Business Tools with AI** (episode 001). "
        "Sample data ranges — **805**: 2020-05-20 ~ 2020-07-10, 2021-01-04 ~ 2021-04-02 · "
        "**535**: 2020-01-03 ~ 2020-03-30, 2021-01-04 ~ 2021-04-02 · "
        "**905**: 2020-08-20 ~ 2020-11-20, 2021-01-04 ~ 2021-03-31. "
        "The default selection works as-is: just click **Generate**."
    )
    with gr.Row():
        date_input = gr.DateTime(label="Target Date", value="2020-06-15", include_time=False, type="string")
        prod_input = gr.Dropdown(choices=["805", "535", "905"], label="Product", value="805")
        btn = gr.Button("Generate")
    status = gr.Textbox(label="Status")
    table_out = gr.DataFrame()
    with gr.Tabs():
        with gr.TabItem("Trends"): plot_trend = gr.Plot()
        with gr.TabItem("Capability"): plot_cap = gr.Plot()
        with gr.TabItem("Distributions"): plot_hist = gr.Plot()
    btn.click(fn=run_analysis, inputs=[date_input, prod_input], outputs=[table_out, plot_trend, plot_cap, plot_hist, status])

if __name__ == "__main__":
    demo.launch()
