import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.express as px
import pandas as pd 
import numpy as np 
import pathlib
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dash_daq as daq
import dash_table
from dash.exceptions import PreventUpdate


def app_layout(nonadf,logo):
    return html.Div(
        id="app-container",    
        children=[
            #Banner
            html.Div(
                id="banner",
                className="banner",
                children=[html.Img(src=logo)]
            ),
            #Left column
            html.Div(
                id="left-column",
                className="four columns",
                children=[filter_description_card(),filter_control_card(nonadf)]            
                + [
                    html.Div(
                        ["initial child"], id="output-clientside", style={"display": "none"}
                    )
                ],
            ),
            #Right Column
            html.Div(
                id="right-column",
                className="eight columns",
                children=[
                    html.Div(
                        children=[
                            html.Br(),
                            daq.BooleanSwitch(
                                on=False,
                                label="Quaterly View",
                                labelPosition="bottom",
                                id="show-qtrly",
                                style={"float":"right",
                                    "align":"middle"                                    
                                }
                            ),
                        ]
                    ),
                    html.Div(
                        id="graph-card",
                        children=[
                            # html.Br(),
                            daq.BooleanSwitch(
                                on=False,
                                label="Show Table",
                                labelPosition="bottom",
                                id="show-table",
                                style={"float":"right",
                                    "align":"middle",
                                    "padding-right":"10px"                                    
                                }
                            ),
                            html.Br(),
                            html.Div(id="table-container", children= [
                                dash_table.DataTable(
                                    id='table',
                                    style_as_list_view=True,
                                    style_table={
                                        'height':'420px',
                                        'overflowY':'auto',
                                        'overflowX':'auto'},
                                    style_cell={
                                        'whiteSpace':'normal',
                                        'font' :'Courier',
                                        'fontSize':'11px',
                                    },
                                    page_size=20,                                        
                                    style_header={
                                        'backgroundColor': 'rgb(230, 230, 230)',
                                        'fontSize':'11px',
                                        'font' :'Courier',
                                        'fontWeight': 'bold'
                                    },
                                    data=[{}]
                                )              
                            ]),

                            html.Br(),
                            html.B("Demand ( Volume )"),
                            html.Hr(),
                            dcc.Graph(id="dcvolume"),

                            html.Br(),
                            html.B("Required Vs Actual FTE"),
                            html.Hr(),
                            dcc.Graph(id="demand-vs-capacity"),

                            html.Br(),                            
                            html.B("Productivity"),
                            html.Hr(),
                            dcc.Graph(id="bcvsrc"),

                            html.Br(),
                            html.B("FTE Gap"),
                            html.Hr(),
                            dcc.Graph(id="productivity"),

                            # html.Br(),                            
                            # html.B("Board Submission"),
                            # html.Hr(),
                            # dcc.Graph(id="board")
                        ]
                    )
                ]
            )
        ]
    )


# Filter Title 
def filter_description_card():
    return html.Div(
        id="description-card",
        children=[
            html.H5("Service Consumption - Forecasting & Scenario Analysis"),            
            html.Div(
                id="intro",
                children="Explore demand and capacity volatility. Forecast volume and analyze scenarios with regards to service consumption"
            ),
        ]
    )


# Filter controls
def filter_control_card(nonadf):
    
    todays_date = datetime.today()
    todays_year = todays_date.year 
    sim_yrs=4

    return html.Div(
        id="control-card",
        children=[            
            html.P("Select Transaction Cycle"),
            dcc.Dropdown(
                id="tc-filter",
                options=[
                    {"label":tc,"value":tc}
                    for tc in np.sort(nonadf['TC Name'].unique())
                ],
                value="Barclays Payments Merchant Services",
                clearable=False,
                className="dropdown"
            ),
            html.Br(),            
            html.Div(className="three-cols",
                children=[
                    html.Div(
                        style={"width":"100%"},
                        children=[
                            html.P("Select Journey"),
                            dcc.Dropdown(
                                id="journey-filter",
                                clearable=False,
                                className="dropdown"
                            ),
                        ]
                    ),
                    html.Div(
                        style={"width":"100%"},
                        children=[            
                            html.P("Select Sub Journey"),
                            dcc.Dropdown(
                                id="sub-journey-filter",
                                clearable=False,
                                className="dropdown"
                            ),
                        ]
                    )
                ]
            ),
            html.Br(),
            html.Hr(className="mainhr"),
            html.H5("Simulator"),
            html.P(id="lbl-bi",children=["Baseline Factors"],
                title="Baseline factors can be either be business volume or work items"
            ),            
            # dcc.RadioItems(
            #     id="baseline-factor",
            #     options=[
            #         {'label': 'Work Items', 'value': 'WI'},
            #         {'label': 'Business Volume', 'value': 'BV'},                       
            #     ],
            #     value='WI',
            #     labelStyle={'display': 'inline-block'}
            # ),
            # html.Br(),            
            html.Div(className="labelSmall",children=["Initial baseline value"]),        
            dcc.Dropdown(
                id="baseline-initial",
                options=[
                    {"label":"Use last month actuals" ,"value":"LMA"},
                    {"label":"Use budget" ,"value":"BUD"},
                    {"label":"Use forecast" ,"value":"FOR"},
                    {"label":"Custom value" ,"value":"CUS"},                    
                ],
                value="LMA",
                clearable=False,
                className="dropdown"
            ),
            dcc.Input(
                id="baseline-custom",
                placeholder='Enter a value...',
                type='number',
                value=''
            ),            
            html.Div(
                style={'padding-top':'3px'},
                className="labelSmall",
                children=["This is the starting value for the simulation. Use last month actuals: Will automatically use the actual volume of the previous month as the starting value and then apply any growth factors to that value. Use forecast: Will automatically use the forecasted volume for that month as the starting value. Use budget: Will automatically use the budgeted volume for that month as the starting value. Use custom value: A custom value for the initial volume level can be input manually"]),
            html.Hr(className="subhr"),            
            html.P("Volume Drivers"),
            html.Div(className="three-cols",            
                children=[                    
                    html.Div(
                        style={"width":"100%"},
                        children=[                
                            html.P(className="labelSmall",children=["Growth rate (%)"],),
                            dcc.Slider(
                                id="gr",                                
                                min=-100,
                                max=100,
                                tooltip={'always_visible':True,'placement':'top'},
                                step=1,
                                marks={
                                    -100:{'label':'-100%','style':{'fontSize':'10px'}},
                                    -50:{'label':'-50%','style':{'fontSize':'10px'}},
                                    0:{'label':'0%','style':{'fontSize':'10px'}},
                                    50:{'label':'50%','style':{'fontSize':'10px'}},
                                    100:{'label':'100%','style':{'fontSize':'10px'}},
                                },
                                value=0
                            )                              
                            # dcc.Input(
                            #     id="gr",
                            #     placeholder='value..',
                            #     type='number',
                            #     value=5,
                            #      style={"width":"100%"},
                            # )                                                                
                        ]
                    ),
                    html.Div(
                        style={"width":"100%"},
                        children=[                
                            html.P(className="labelSmall",children=["Frequency"]),
                            dcc.Dropdown(                                
                                id="gr_frequency",
                                options=[
                                    {'label': 'Monthly', 'value': 'M'},
                                    {'label': 'Annual', 'value': 'Y'},
                                ],
                                clearable=False,
                                value='Y',
                            )
                        ]
                    )
                ]
            ),

            html.Div(className="three-cols",
            children=[
                html.Div(
                    style={"width":"100%"},
                    children=[                
                        html.P(className="labelSmall",children=["Start Month"]),
                        html.Div(
                            style={
                                "display":"flex",
                                "gap":"0.2em",
                                "width":"100%"
                            },
                            children=[                
                                dcc.Dropdown(
                                    id="gr_start_month",
                                    style={"width":"100%"},
                                    options=[
                                        {'label': 'Jan', 'value': 'Jan' },
                                        {'label': 'Feb', 'value': 'Feb' },
                                        {'label': 'Mar', 'value': 'Mar' },
                                        {'label': 'Apr', 'value': 'Apr' },
                                        {'label': 'May', 'value': 'May' },
                                        {'label': 'Jun', 'value': 'Jun' },
                                        {'label': 'Jul', 'value': 'Jul' },
                                        {'label': 'Aug', 'value': 'Aug' },
                                        {'label': 'Sep', 'value': 'Sep' },
                                        {'label': 'Oct', 'value': 'Oct' },
                                        {'label': 'Nov', 'value': 'Nov' },
                                        {'label': 'Dec', 'value': 'Dec' },
                                    ],
                                    clearable=False,
                                    value='Mar',                            
                                ),
                                dcc.Dropdown(
                                    id="gr_start_month_yr",
                                    style={"width":"100%"},
                                    clearable=False,
                                    value=todays_year,
                                    options=[{'label':x, 'value': x} for x in range(todays_year, todays_year+sim_yrs)])
                            ]
                        )
                    ]
                ),
                html.Div(
                    style={"width":"100%"},
                    children=[                
                        html.P(className="labelSmall",children=["End Month"]),
                        html.Div(
                            style={
                                "display":"flex",
                                "gap":"0.2em",
                                "width":"100%"
                            },
                            children=[
                                dcc.Dropdown(
                                    id="gr_end_month",
                                    style={"width":"100%"},
                                    options=[
                                        {'label': 'Jan', 'value': 'Jan' },
                                        {'label': 'Feb', 'value': 'Feb' },
                                        {'label': 'Mar', 'value': 'Mar' },
                                        {'label': 'Apr', 'value': 'Apr' },
                                        {'label': 'May', 'value': 'May' },
                                        {'label': 'Jun', 'value': 'Jun' },
                                        {'label': 'Jul', 'value': 'Jul' },
                                        {'label': 'Aug', 'value': 'Aug' },
                                        {'label': 'Sep', 'value': 'Sep' },
                                        {'label': 'Oct', 'value': 'Oct' },
                                        {'label': 'Nov', 'value': 'Nov' },
                                        {'label': 'Dec', 'value': 'Dec' },
                                    ],
                                    clearable=False,
                                    value='Dec',
                                ),
                                dcc.Dropdown(
                                    id="gr_end_month_yr",
                                    style={"width":"100%"},
                                    clearable=False,                                    
                                    options=[{'label':x, 'value': x} for x in range(todays_year, todays_year+sim_yrs)],
                                    value=todays_year+(sim_yrs-1))
                            ]
                        )
                    ]
                ),                             
            ]),
            html.Div(
                style={'padding-top':'3px'},
                className="labelSmall",
                children=["This section allows you to adjust the growth rate applied to the initial baseline volume for simulation purposes.  Growth rates can be applied between specific start and end months. If an end month is selected, subsequent months volume will be then held constant."]),
            html.Hr(className="subhr"),
            html.P("FTE Drivers"),
            html.Div(className="three-cols",
            children=[
                html.Div(
                     style={"width":"100%"},
                    children=[                
                        html.P(className="labelSmall",children=["FTE Δ"]),
                        dcc.Input(
                            id="cifte",
                            placeholder='Enter a value...',
                            type='number',
                            value=0
                        )
                    ]
                ),
                html.Div(
                    style={"width":"100%","padding-bottom":"5px"},
                    children=[                
                        html.P(className="labelSmall",children=["Start Month"]),
                        html.Div(
                            style={
                                "display":"flex",
                                "gap":"0.2em",
                                "width":"100%"
                            },
                            children=[
                                dcc.Dropdown(
                                    id="cifte_start_month",
                                    style={"width":"100%"},
                                    options=[
                                        {'label': 'Jan', 'value': 'Jan' },
                                        {'label': 'Feb', 'value': 'Feb' },
                                        {'label': 'Mar', 'value': 'Mar' },
                                        {'label': 'Apr', 'value': 'Apr' },
                                        {'label': 'May', 'value': 'May' },
                                        {'label': 'Jun', 'value': 'Jun' },
                                        {'label': 'Jul', 'value': 'Jul' },
                                        {'label': 'Aug', 'value': 'Aug' },
                                        {'label': 'Sep', 'value': 'Sep' },
                                        {'label': 'Oct', 'value': 'Oct' },
                                        {'label': 'Nov', 'value': 'Nov' },
                                        {'label': 'Dec', 'value': 'Dec' },
                                    ],
                                    clearable=False,
                                    value='Mar',                            
                                ),
                                dcc.Dropdown(
                                    id="cifte_start_month_yr",
                                    style={"width":"100%"},
                                    clearable=False,
                                    value=todays_year,
                                    options=[{'label':x, 'value': x} for x in range(todays_year, todays_year+sim_yrs)])
                            ]
                        )
                    ]
                ),
                html.Div(
                    style={"width":"100%","padding-bottom":"5px"},
                    children=[                                        
                        html.P(className="labelSmall",children=["End Month"]),
                        html.Div(
                            style={
                                "display":"flex",
                                "gap":"0.2em",
                                "width":"100%"
                            },
                            children=[
                                dcc.Dropdown(
                                    id="cifte_end_month",
                                    style={"width":"100%"},
                                    options=[
                                        {'label': 'Jan', 'value': 'Jan' },
                                        {'label': 'Feb', 'value': 'Feb' },
                                        {'label': 'Mar', 'value': 'Mar' },
                                        {'label': 'Apr', 'value': 'Apr' },
                                        {'label': 'May', 'value': 'May' },
                                        {'label': 'Jun', 'value': 'Jun' },
                                        {'label': 'Jul', 'value': 'Jul' },
                                        {'label': 'Aug', 'value': 'Aug' },
                                        {'label': 'Sep', 'value': 'Sep' },
                                        {'label': 'Oct', 'value': 'Oct' },
                                        {'label': 'Nov', 'value': 'Nov' },
                                        {'label': 'Dec', 'value': 'Dec' },                                    ],
                                    clearable=False,
                                    value='Dec',                            
                                ),
                                dcc.Dropdown(
                                    id="cifte_end_month_yr",
                                    style={"width":"100%"},
                                    clearable=False,
                                    value=todays_year+(sim_yrs-1),
                                    options=[{'label':x, 'value': x} for x in range(todays_year, todays_year+sim_yrs)])
                            ]
                        )                        
                    ]
                ),
            ]),
            html.Br(),
            html.Div(className="three-cols",
            children=[
                html.Div(
                    style={"width":"100%"}, 
                    children=[                
                        html.P(className="labelSmall",children=["Productivity"]),
                        html.Div(
                            style={"width":"100%"}, 
                            children=[     
                                dcc.Slider(
                                    id="wiphead",                                
                                    min=-100,
                                    max=100,
                                    tooltip={'always_visible':True,'placement':'top'},
                                    step=1,
                                    marks={
                                        -100:{'label':'-100%','style':{'fontSize':'10px'}},
                                        -50:{'label':'-50%','style':{'fontSize':'10px'}},
                                        0:{'label':'0%','style':{'fontSize':'10px'}},
                                        50:{'label':'50%','style':{'fontSize':'10px'}},
                                        100:{'label':'100%','style':{'fontSize':'10px'}},
                                    },
                                    value=0
                                )                             
                            ]
                        ),                        
                        # dcc.Input(
                        #     id="wiphead",
                        #     placeholder='Enter a value...',
                        #     type='number',
                        #     value=158
                        # )
                    ]
                ),
                html.Div(
                    style={"width":"100%"},
                    children=[                
                        html.P(className="labelSmall",children=["Frequency"]),
                        dcc.Dropdown(                                
                            id="wiphead_frequency",
                            options=[
                                {'label': 'Monthly', 'value': 'M'},
                                {'label': 'Annual', 'value': 'Y'},
                            ],
                            clearable=False,
                            value='Y',
                        )
                    ]
                ),                            
            ]),

            html.Div(className="three-cols",
            children=[
                html.Div(
                    style={"width":"100%"},
                    children=[                
                        html.P(className="labelSmall",children=["Start Month"]),
                        html.Div(
                            style={
                                "display":"flex",
                                "gap":"0.2em",
                                "width":"100%"
                            },
                            children=[                
                                dcc.Dropdown(
                                    id="wiphead_start_month",
                                    style={"width":"100%"},
                                    options=[
                                        {'label': 'Jan', 'value': 'Jan' },
                                        {'label': 'Feb', 'value': 'Feb' },
                                        {'label': 'Mar', 'value': 'Mar' },
                                        {'label': 'Apr', 'value': 'Apr' },
                                        {'label': 'May', 'value': 'May' },
                                        {'label': 'Jun', 'value': 'Jun' },
                                        {'label': 'Jul', 'value': 'Jul' },
                                        {'label': 'Aug', 'value': 'Aug' },
                                        {'label': 'Sep', 'value': 'Sep' },
                                        {'label': 'Oct', 'value': 'Oct' },
                                        {'label': 'Nov', 'value': 'Nov' },
                                        {'label': 'Dec', 'value': 'Dec' },
                                    ],
                                    clearable=False,
                                    value='Mar',                            
                                ),
                                dcc.Dropdown(
                                    id="wiphead_start_month_yr",
                                    style={"width":"100%"},
                                    clearable=False,
                                    value=todays_year,
                                    options=[{'label':x, 'value': x} for x in range(todays_year, todays_year+sim_yrs)])
                            ]
                        )
                    ]
                ),
                html.Div(
                    style={"width":"100%"},
                    children=[                
                        html.P(className="labelSmall",children=["End Month"]),
                        html.Div(
                            style={
                                "display":"flex",
                                "gap":"0.2em",
                                "width":"100%"
                            },
                            children=[
                                dcc.Dropdown(
                                    id="wiphead_end_month",
                                    style={"width":"100%"},
                                    options=[
                                        {'label': 'Jan', 'value': 'Jan' },
                                        {'label': 'Feb', 'value': 'Feb' },
                                        {'label': 'Mar', 'value': 'Mar' },
                                        {'label': 'Apr', 'value': 'Apr' },
                                        {'label': 'May', 'value': 'May' },
                                        {'label': 'Jun', 'value': 'Jun' },
                                        {'label': 'Jul', 'value': 'Jul' },
                                        {'label': 'Aug', 'value': 'Aug' },
                                        {'label': 'Sep', 'value': 'Sep' },
                                        {'label': 'Oct', 'value': 'Oct' },
                                        {'label': 'Nov', 'value': 'Nov' },
                                        {'label': 'Dec', 'value': 'Dec' },
                                    ],
                                    clearable=False,
                                    value='Dec',                            
                                ),
                                dcc.Dropdown(
                                    id="wiphead_end_month_yr",
                                    style={"width":"100%"},
                                    clearable=False,
                                    value=todays_year+(sim_yrs-1),
                                    options=[{'label':x, 'value': x} for x in range(todays_year, todays_year+sim_yrs)])
                            ]
                        )
                    ]
                ),                             
            ]),

            html.Div(id='fwiph_avg',
                    className="labelSmall",
                    style={"font-weight":"bold"}
            ),

            html.Div(
                style={'padding-top':'3px'},
                className="labelSmall",
                children=["This section allows you to adjust FTE capacity  between specific start and end months. FTE delta: Will adjust the available FTE by that amount. Productivity: Will adjust the productivity per FTE by that %. For months where actual volume is available (historic), productivity changes will be applied to actual productivity. For Future months, productivity changes will be applied to forecast productivity levels."]),
            html.Hr(className="subhr"),
            html.P("Cost Drivers"),
            html.Div(
                style={
                    "display":"flex",
                    "gap":"0.5em",
                    "width":"100%"
                },
                children=[             
                    html.Div(            
                        style={"width":"100%"},
                        children=[       
                            html.P(className="labelSmall",children=["Budgeted Annual Cost Per FTE (£)"],),
                            dcc.Input(
                                style={"width":"100%"},
                                id="bcpfte",
                                placeholder='Enter a value...',
                                type='number',
                                value=75000
                            )
                        ]
                    ),                   
                ]
            ),
            html.Br(),
            html.Div(
                id='reset-btn-outer',
                children=[html.Button(id="reset-btn",children="Reset",n_clicks=0)],
            )
        ]
    )