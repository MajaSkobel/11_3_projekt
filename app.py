# app.py

import dash
import pandas as pd
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from db import db  
import plotly.graph_objects as go
from tab1 import render_sales_tab  
from tab2 import render_products_tab
from tab3 import render_store_tab
from tab3 import days_order, day_mapping
import dash_auth

db_instance = db()
df = db_instance.merge()

USERNAME_PASSWORD = [['user','pass']]
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,suppress_callback_exceptions=True)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD)

app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Sprzedaż globalna', value='tab-1'),
        dcc.Tab(label='Produkty', value='tab-2'),
        dcc.Tab(label='Kanały sprzedaży', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'), [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return render_sales_tab(df)  
    elif tab == 'tab-2':
        return render_products_tab(df)
    elif tab == 'tab-3':
        return render_store_tab(df)  
    
@app.callback(Output('bar-sales', 'figure'),
              [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')])
def update_bar_chart(start_date, end_date):
    truncated = df[(df['tran_date'] >= start_date) & (df['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby([pd.Grouper(key='tran_date', freq='M'), 'Store_type'])['total_amt'].sum().round(2).unstack()

    traces = []
    for col in grouped.columns:
        traces.append(go.Bar(x=grouped.index, y=grouped[col], name=col, hoverinfo='text',
                             hovertext=[f'{y/1e3:.2f}k' for y in grouped[col].values]))

    fig = go.Figure(data=traces, layout=go.Layout(title='Przychody', legend=dict(x=0, y=-0.5)))
    return fig

@app.callback(Output('choropleth-sales', 'figure'),
              [Input('sales-range', 'start_date'), Input('sales-range', 'end_date')])
def update_choropleth_sales(start_date, end_date):
    truncated = df[(df['tran_date'] >= start_date) & (df['tran_date'] <= end_date)]
    grouped = truncated[truncated['total_amt'] > 0].groupby('country')['total_amt'].sum().round(2)

    trace = go.Choropleth(colorscale='Viridis', reversescale=True,
                           locations=grouped.index, locationmode='country names',
                           z=grouped.values, colorbar=dict(title='Sales'))

    fig = go.Figure(data=[trace], layout=go.Layout(title='Mapa', geo=dict(showframe=False, projection={'type': 'natural earth'})))
    return fig

@app.callback(Output('barh-prod-subcat', 'figure'),
              [Input('prod_dropdown', 'value')])
def update_product_chart(chosen_cat):
    grouped = df[(df['total_amt'] > 0) & (df['prod_cat'] == chosen_cat)].pivot_table(index='prod_subcat', columns='Gender', values='total_amt', aggfunc='sum').assign(_sum=lambda x: x['F'] + x['M']).sort_values(by='_sum').round(2)

    traces = []
    for col in ['F', 'M']:
        traces.append(go.Bar(x=grouped[col], y=grouped.index, orientation='h', name=col))

    fig = go.Figure(data=traces, layout=go.Layout(barmode='stack', margin={'t': 20}))
    return fig

@app.callback([Output('heatmap', 'figure'), Output('bar-chart', 'figure')],
              [Input('store-type-dropdown', 'value')])
def update_graphs(selected_store_type):

    if not selected_store_type:
        filtered_df = df
    else:
        filtered_df = df[df['Store_type'].isin(selected_store_type)]

    heatmap_data = filtered_df.pivot_table(index='day_of_week',columns='Store_type',
                                           values='total_amt',aggfunc='sum').reindex(days_order)
    heatmap_data.index = heatmap_data.index.map(day_mapping)

    my_heatmap = go.Figure(data=[go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorbar=dict(title='Przychody')
    )],layout=go.Layout(title='Zależność sprzedaży od kanału sprzedaży i dnia tygodnia'))

    gender_store = filtered_df.groupby('Gender')['Store_type'].value_counts(normalize=True).unstack()

    traces = []
    for col in gender_store.columns:
        traces.append(go.Bar(x=gender_store.index, y=gender_store[col], name=col))

    my_bar_chart = go.Figure(data=traces, layout=go.Layout(title='Procentowy udział płci w poszczególnych kanałach sprzedaży',
                                                           xaxis=dict(title='Płeć')))

    return my_heatmap, my_bar_chart


if __name__ == '__main__':
    app.run_server(debug=True)
