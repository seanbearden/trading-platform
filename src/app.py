import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import os
from pandas import json_normalize
from tools.ameritrade_helper import get_specified_account_with_aws, analyze_tda, get_quotes_with_aws

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

df1 = pd.DataFrame({
    'x': [1, 2, 3, 4],
    'y': [10, 11, 12, 13]
})

load_dotenv()
chrome_driver_path = '../chromedriver'
token_path = '../res/token.json'

display_style = {"width": "36rem", "color": "#aea7f1"}

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.title = "Ameritrade Investment Dashboard"

server = app.server

# Is this necessary?
app.config.suppress_callback_exceptions = False


def create_card(title, id, style):
    """
    :param title: to display
    :param id: for reference
    :param style: display style
    :return: A Card for Div
    """
    return dbc.Card(
        dbc.CardBody([
            html.H4(title, className="card-title"),
            html.H2(id=id, className="card-subtitle"),
        ]),
        style=style,
    )


def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5(app.title),
            html.Div(
                id="intro",
                children="A dashboard for evaluating Ameritrade portfolio performance.",
            ),
        ],
    )


def generate_control_card():
    """
    :return: A Div containing controls for analysis.
    """
    return html.Div(
        id="control-card",
        children=[
            dbc.Row([
                dbc.Col(create_card("Net Liquidation Value", "net-liquidation-value", display_style), width=6),
                dbc.Col(create_card("Daily Change", "net-liquidation-value-change", display_style), width=6),
            ]),
            dbc.Row([
                dbc.Col(create_card("Call Market Value", "call-value", display_style), width=6),
                dbc.Col(create_card("Call PNL", "call-value-change", display_style), width=6),
            ]),
            dbc.Row([
                dbc.Col(create_card("Put Market Value", "put-value", display_style), width=6),
                dbc.Col(create_card("Put PNL", "put-value-change", display_style), width=6),
            ]),
            dbc.Row([
                dbc.Col(create_card("Equity Value", "equity-value", display_style), width=6),
                dbc.Col(create_card("Equity PNL", "equity-value-change", display_style), width=6),
            ]),
            html.Br(),
            dcc.Dropdown(
                id='dropdown',
                options=[{'label': 'Major Indices', 'value': 'MAJOR_INDICES'},
                         {'label': 'Bar Plot', 'value': 'BAR'}],
                value='MAJOR_INDICES'  # Default value
            ),
            html.Div(
                className='padding-top-bot',
                children=[
                    html.Div(
                        id="refresh-btn-outer",
                        children=html.Button(id="refresh-btn", children="Refresh Data"),
                    )]
            ),
        ]
    )


@app.callback(
    [
        Output("account-data", "data"),
        Output('net-liquidation-value', 'children'),
        Output('net-liquidation-value-change', 'children'),
        Output('call-value', 'children'),
        Output('call-value-change', 'children'),
        Output('put-value', 'children'),
        Output('put-value-change', 'children'),
        Output('equity-value', 'children'),
        Output('equity-value-change', 'children')
    ],
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=False,
)
def retrieve_account_data(refresh_btn__click):
    print('Retrieving investment data')
    account = get_specified_account_with_aws()
    account_data = analyze_tda(account)
    net_liquidating_value = account['securitiesAccount']['currentBalances']['liquidationValue']
    net_liquidating_value_change = (
            net_liquidating_value - account['securitiesAccount']['initialBalances']['liquidationValue'])

    net_liquidating_value_str = f"${net_liquidating_value:,.0f}"
    net_liquidating_value_change_str = f"${net_liquidating_value_change:,.0f}"
    call_value_str = f"${account_data['OPTION']['long_market_value']:,.0f}"
    call_value_change_str = f"${account_data['OPTION']['current_day_long_pnl']:,.0f}"
    put_value_str = f"${account_data['OPTION']['short_market_value']:,.0f}"
    put_value_change_str = f"${account_data['OPTION']['current_day_short_pnl']:,.0f}"
    equity_value_str = f"${account_data['EQUITY']['total_market_value']:,.0f}"
    equity_value_change_str = \
        f"${account_data['EQUITY']['current_day_long_pnl'] + account_data['EQUITY']['current_day_short_pnl']:,.0f}"

    return (account_data, net_liquidating_value_str, net_liquidating_value_change_str, call_value_str,
            call_value_change_str, put_value_str, put_value_change_str, equity_value_str, equity_value_change_str)


@app.callback(
    [Output("datatable-interactivity", "data"),
     Output("datatable-interactivity", "columns")],
    Input("account-data", "data"),
    prevent_initial_call=True,
)
def process_account_data(account_data):
    df = json_normalize(account_data['OPTION']['positions'], sep='_')
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]


@app.callback(
    Output('graph', 'figure'),
    [Input('dropdown', 'value'),
     Input("account-data", "data")],
    prevent_initial_call=False,
)
def update_graph(selected_value, account_data):
    if selected_value == 'BAR':
        call_options = account_data['OPTION']['long_market_value']
        put_options = account_data['OPTION']['short_market_value']
        equity = account_data['EQUITY']['total_market_value']
        fig = px.bar(
            x=['CALL', 'PUT', 'EQUITY'],
            y=[call_options, put_options, equity],
            labels={'x': 'Asset Type', 'y': 'Market Value'}
        )
    elif selected_value == 'MAJOR_INDICES':
        symbols = ['$DJI', '$NDX.X', '$SPX.X']
        quotes = get_quotes_with_aws(symbols)

        fig = make_subplots(rows=1, cols=len(symbols),
                            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]])
        for i, symbol in enumerate(symbols):
            fig.add_trace(go.Indicator(
                mode="number+delta",
                value=float(quotes[symbol]['lastPrice']),
                title={'text': symbol},
                delta={'reference': quotes[symbol]['closePrice'], 'relative': True, 'valueformat': ".2%"},
            ),
                row=1, col=i + 1
            )

    else:
        fig = px.line(df1, x='x', y='y')
    return fig


style_data_conditional = [
    {
        'if': {
            'filter_query': '{{{}}} < {}'.format('currentDayProfitLoss', 0),
            'column_id': 'currentDayProfitLoss'
        },
        'backgroundColor': 'tomato',
        'color': 'white'
    },
    {
        'if': {
            'filter_query': '{{{}}} > {}'.format('currentDayProfitLoss', 0),
            'column_id': 'currentDayProfitLoss'
        },
        'backgroundColor': 'rgb(76,187,23)',
        'color': 'white'
    },
    {
        'if': {
            'filter_query': '{{{}}} = {}'.format('instrument_putCall', 'PUT'),
            'column_id': 'instrument_putCall'
        },
        'backgroundColor': 'tomato',
        'color': 'white'
    },
    {
        'if': {
            'filter_query': '{{{}}} = {}'.format('instrument_putCall', 'CALL'),
            'column_id': 'instrument_putCall'
        },
        'backgroundColor': 'rgb(76,187,23)',
        'color': 'white'
    },
]

app.layout = html.Div(
    id="app-container",
    children=[
        html.Div(id="error-message"),
        html.Div(id="error-message-automation-upload"),
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("logo.png"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[
                description_card(),
                generate_control_card(),
                html.Div(["initial child"], id="output-clientside", style={"display": "none"})
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                dcc.Graph(id='graph'),
                html.Br(),
                dash_table.DataTable(
                    id='datatable-interactivity',
                    editable=True,
                    filter_action='native',
                    sort_action='native',
                    sort_mode='multi',
                    column_selectable='single',
                    # row_selectable='multi',
                    row_deletable=True,
                    # selected_columns=[port_col],
                    selected_rows=[],
                    style_data_conditional=style_data_conditional,
                    # page_action='native',
                    # page_current=0,
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                ),

                dcc.Store(id="account-data", storage_type="memory", data='dict'),
            ],
        ),
    ],
)
# Run the server
if __name__ == "__main__":
    app.run_server(port=8052, debug=True)
