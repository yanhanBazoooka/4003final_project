import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for portfolio and watchlist
portfolio_data = pd.DataFrame([
    {'Stock': 'AAPL', 'Change': '+0.1%'},  # Apple
    {'Stock': 'TSLA', 'Change': '-10.2%'},  # Tesla
    {'Stock': 'NVDA', 'Change': '+900%'},  # Nvidia
    {'Stock': 'GOOGL', 'Change': '+0.1%'},  # Alphabet
    {'Stock': 'AMZN', 'Change': '+9.1%'}  # Amazon
])

watchlist_data = pd.DataFrame([
    {'Stock': 'AAPL', 'Change': '+0.1%'},
    {'Stock': 'TSLA', 'Change': '-10.2%'}
])

# Dropdown options
dropdown_options = [{'label': stock, 'value': stock} for stock in portfolio_data['Stock']]

def generate_table(dataframe, max_rows=10):
    return dash_table.DataTable(
        data=dataframe.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in dataframe.columns],
        style_as_list_view=True,
        style_header={
            'backgroundColor': 'rgb(191, 236, 223)',
            'color': 'black',
            'fontFamily': 'Monospace',
        },
        style_cell={
            'textAlign': 'left',
            'backgroundColor': 'white',
            'color': 'black',
            'fontFamily': 'Monospace',
        },
        page_size=max_rows
    )

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="#")),
            dbc.NavItem(dbc.NavLink("Date", href="#")),
            dbc.NavItem(dbc.NavLink("Search", href="#")),
        ],
        brand="Welcome to Simply Trade, ready to make some big bucks?",
        brand_href="#",
        color="rgb(191, 236, 223)",
        dark=False,
        className="mb-4",
    ),
    
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='stock-selector',
                options=dropdown_options,
                value='AAPL',  # Default value
                className="mb-2"
            ),
            dcc.Graph(id='overview-graph', style={'height': 300})
        ], md=8),
        
        dbc.Col([
            html.H4("My Portfolio:", className="text-center"),
            generate_table(portfolio_data),
            html.H4("Watchlist", className="text-center mt-4"),
            generate_table(watchlist_data)
        ], md=4),
    ]),
], fluid=True)

@app.callback(
    Output('overview-graph', 'figure'),
    [Input('stock-selector', 'value')]
)
def update_graph(selected_stock):
    # Fetch historical stock data
    df = yf.download(selected_stock, period='1mo', interval='1d')
    
    # Check if the dataframe is empty
    if df.empty:
        return go.Figure()
    
    # Create the candlestick plot
    figure = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    
    figure.update_layout(
        title=f'{selected_stock} Stock Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        margin={'l': 40, 'b': 40, 't': 40, 'r': 10},
        xaxis_rangeslider_visible=True  
    )
    
    
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
