# tab3.py

from dash import html
from dash import dcc
import plotly.graph_objects as go

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_mapping = {
    'Monday': 'Poniedziałek',
    'Tuesday': 'Wtorek',
    'Wednesday': 'Środa',
    'Thursday': 'Czwartek',
    'Friday': 'Piątek',
    'Saturday': 'Sobota',
    'Sunday': 'Niedziela'}

def render_store_tab(df):

    df['day_of_week'] = df['tran_date'].dt.day_name()

    heatmap_data = df.pivot_table(index='day_of_week',columns='Store_type',values='total_amt',
                                  aggfunc='sum').reindex(days_order)
    heatmap_data.index = heatmap_data.index.map(day_mapping)

    gender_store = df.groupby('Gender')['Store_type'].value_counts(normalize=True).unstack()

    my_heatmap = go.Figure(data=[go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorbar=dict(title='Przychody')
    )],layout=go.Layout(title='Zależność sprzedaży od kanału sprzedaży i dnia tygodnia'))

    my_bar_chart = go.Figure(data=[go.Bar(
        x=gender_store.index,
        y=gender_store[store_type],
        name=store_type,
        text=store_type
    ) for store_type in gender_store.columns],
    layout=go.Layout(title='Procentowy udział płci w poszczególnych kanałach sprzedaży',
        xaxis=dict(title='Płeć')))

    layout = html.Div([html.H1('Kanały sprzedaży',style={'text-align':'center'}),
                        html.Div([
                        dcc.Graph(id='heatmap', figure=my_heatmap, style={'width': '50%'}),
                        dcc.Dropdown(id='store-type-dropdown', options=[{'label': store, 'value': store}
                                    for store in df['Store_type'].unique()],
                                    value=df['Store_type'].unique(),
                                    multi=True,
                                    style={'width': '50%'}),
                        dcc.Graph(id='bar-chart', figure=my_bar_chart, style={'width': '50%'})],
                        style={'display':'flex'})
                        ])
    return layout