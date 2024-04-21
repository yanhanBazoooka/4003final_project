import dash
from dash import dcc, html, Input, Output, dash_table, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Stocks for portfolio and watchlist
portfolio_stocks = ['AAPL', 'TSLA', 'NVDA', 'GOOGL', 'AMZN']
watchlist_stocks = ['MSFT', 'BABA', 'NFLX', 'INTC', 'AMD'] 

# Function to generate tables for Portfolio and Watchlist
def generate_table(stock_list, interval='1mo', table_id='portfolio-table'):
    portfolio_data = pd.DataFrame(columns=['Stock', 'Change'])
    for stock in stock_list:
        df = yf.download(stock, period=interval, interval='1d')
        if not df.empty:
            change = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
            new_row = pd.DataFrame({'Stock': [stock], 'Change': [f"{change:.2f}%"]})
            portfolio_data = pd.concat([portfolio_data, new_row], ignore_index=True)
    return dash_table.DataTable(
        id=table_id,
        data=portfolio_data.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in portfolio_data.columns],
        style_as_list_view=True,
        style_header={
            'backgroundColor': 'rgb(191, 236, 223)',
            'color': 'black',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            'backgroundColor': 'white',
            'color': 'black'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'Stock'},
                'cursor': 'pointer'  
            }
        ],
        page_size=5 
    )

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[],
        brand="Welcome to Simply Trade💹",
        brand_href="#",
        color="rgb(191, 236, 223)",
        dark=False,
        className="mb-4 w-100 justify-content-center",  
    ),
    
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id='stock-selector-top',
                        options=[{'label': stock, 'value': stock} for stock in portfolio_stocks],
                        value='AAPL',
                        className="mb-2"
                    ),
                    dcc.Graph(id='overview-graph-top', style={'height': '45vh'})
                ], width=12),
                dbc.Col([
                    dcc.Dropdown(
                        id='stock-selector-bottom',
                        options=[{'label': stock, 'value': stock} for stock in watchlist_stocks],
                        value='MSFT',
                        className="mb-2"
                    ),
                    dcc.Graph(id='overview-graph-bottom', style={'height': '45vh'})
                ], width=12)
            ]),
            dcc.Dropdown(
                id='interval-selector',
                options=[
                    {'label': '1 Month', 'value': '1mo'},
                    {'label': '3 Months', 'value': '3mo'},
                    {'label': '6 Months', 'value': '6mo'},
                    {'label': '1 Year', 'value': '1y'}
                ],
                value='1mo',
                className="mt-2"
            )
        ], md=8),
        
        dbc.Col([
            dbc.Row([
                dbc.Col(html.H4("My Portfolio🐂", className="text-center"), width=12),
                dbc.Col(html.Div(id='portfolio-container', children=generate_table(portfolio_stocks, '1mo', 'portfolio-table')), width=12, style={'height': '45vh'}),
            ], className="mb-2"),
            dbc.Row([
                dbc.Col(html.H4("My Watchlist👀", className="text-center"), width=12),
                dbc.Col(html.Div(id='watchlist-container', children=generate_table(watchlist_stocks, '1mo', 'watchlist-table')), width=12, style={'height': '45vh'})
            ])
        ], md=4, style={'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between'}),
    ]),
], fluid=True)

@app.callback(
    [Output('overview-graph-top', 'figure'),
     Output('overview-graph-bottom', 'figure'),
     Output('stock-selector-top', 'value'),
     Output('stock-selector-bottom', 'value')],
    [Input('portfolio-table', 'active_cell'),
     Input('watchlist-table', 'active_cell'),
     Input('stock-selector-top', 'value'),
     Input('stock-selector-bottom', 'value'),
     Input('interval-selector', 'value')]
)
def update_graphs(portfolio_cell, watchlist_cell, stock_top, stock_bottom, interval):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'portfolio-table' and portfolio_cell:
        stock_top = portfolio_stocks[portfolio_cell['row']]
    elif trigger_id == 'watchlist-table' and watchlist_cell:
        stock_bottom = watchlist_stocks[watchlist_cell['row']]

    figure_top = create_figure(stock_top, interval)
    figure_bottom = create_figure(stock_bottom, interval)
    return figure_top, figure_bottom, stock_top, stock_bottom

def create_figure(stock, interval):
    df = yf.download(stock, period=interval, interval='1d')
    if df.empty:
        return go.Figure()
    figure = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color='green', 
        decreasing_line_color='red'
    )])
    figure.update_layout(
        title=f'{stock} Candlestick Chart📈📉',
        xaxis_title='Date',
        yaxis_title='Price',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='grey'),
        yaxis=dict(showgrid=True, gridcolor='grey'),
        font=dict(color="black")
    )
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
