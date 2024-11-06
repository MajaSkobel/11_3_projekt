# tab2.py

from dash import html
from dash import dcc
import plotly.graph_objects as go

def render_products_tab(df):
    grouped = df[df['total_amt'] > 0].groupby('prod_cat')['total_amt'].sum()
    fig = go.Figure(data=[go.Pie(labels=grouped.index, values=grouped.values)],
                    layout=go.Layout(title='Udział grup produktów w sprzedaży'))

    layout = html.Div([
        html.H1('Produkty', style={'text-align': 'center'}),
        html.Div([
            dcc.Graph(id='pie-prod-cat', figure=fig, style={'width': '50%'}),
            dcc.Dropdown(id='prod_dropdown',
                         options=[{'label': prod_cat, 'value': prod_cat} for prod_cat in df['prod_cat'].unique()],
                         value=df['prod_cat'].unique()[0]),
            dcc.Graph(id='barh-prod-subcat', style={'width': '50%'})
        ], style={'display': 'flex'}),
    ])
    return layout