import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc  # You'll need to install dash-bootstrap-components
from dotenv import load_dotenv
import os
from pandas import json_normalize
from tools.ameritrade_helper import get_specified_account, analyze_tda

load_dotenv()

net_liquidating_value = 0

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "Ameritrade Investment Dashboard"

server = app.server

# Is this necessary?
app.config.suppress_callback_exceptions = False

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
            dbc.Card(
                dbc.CardBody([
                    html.H4("Net Liquidation Value", className="card-title"),
                    html.H2(id="net-liquidation-value", className="card-subtitle"),
                ]),
                style={"width": "36rem", "color": "green"},
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H4("Call Market Value", className="card-title"),
                    html.H2(id="call-value", className="card-subtitle"),
                ]),
                style={"width": "36rem", "color": "green"},
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H4("Put Market Value", className="card-title"),
                    html.H2(id="put-value", className="card-subtitle"),
                ]),
                style={"width": "36rem", "color": "green"},
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H4("Equity Value", className="card-title"),
                    html.H2(id="equity-value", className="card-subtitle"),
                ]),
                style={"width": "36rem", "color": "green"},
            ),
            html.Br(),
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
        Output('call-value', 'children'),
        Output('put-value', 'children'),
        Output('equity-value', 'children')
    ],
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=False,
)
def retrieve_account_data(refresh_btn__click):
    print('Retrieving investment data')
    tda_api_key = os.getenv('TDA_API_KEY')
    tda_account_id = os.getenv('TDA_ACCOUNT_ID')
    account = get_specified_account(account_id=tda_account_id,
                                    api_key=tda_api_key,
                                    chrome_driver_path='../tools/chromedriver',
                                    token_path='../res/token.json')
    account_data = analyze_tda(account)
    net_liquidating_value = account['securitiesAccount']['currentBalances']['liquidationValue']

    net_liquidating_value_str = f"${net_liquidating_value:,.0f}"
    call_value_str = f"${account_data['OPTION']['long_market_value']:,.0f}"
    put_value_str = f"${account_data['OPTION']['short_market_value']:,.0f}"
    equity_value_str = f"${account_data['EQUITY']['total_market_value']:,.0f}"
    # df = pd.DataFrame(investments['OPTION']['positions'])
    return account_data, net_liquidating_value_str, call_value_str, put_value_str, equity_value_str


@app.callback(
    [Output("datatable-interactivity", "data"),
     Output("datatable-interactivity", "columns")],
    Input("account-data", "data"),
    prevent_initial_call=True,
)
def process_account_data(account_data):
    df = json_normalize(account_data['OPTION']['positions'], sep='_')
    # df = pd.DataFrame(account_data['OPTION']['positions'])#[['shortQuantity', 'averagePrice']]
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]


style_data_conditional=[
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
            children=[html.Img(src=app.get_asset_url("bearden_logo.png"))],
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
                html.B("Account"),
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
                    # page_size=10,
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
