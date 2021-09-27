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
from ui import app_layout
from model import dy
from model import calculate_wi
from model import calculate_bv
from model import init_simulator_fields
from model import fill_data
from model import convert_to_qtr
import viz as bigraphs

todays_date = datetime.today()
todays_year = todays_date.year 
sim_yrs=4
tabledf = {}

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel":"stylesheet",
    }
]

app = dash.Dash(
        __name__,
        meta_tags=[{"name":"viewport","content":"width=device-width, initial-scale=1"}],
        external_stylesheets=external_stylesheets)

app.title = "Demand Capacity Forecasting & Scenario Analysis"
server = app.server
#app.config.supress_callback_exceptions = False

# Resolve Path 
BASE_PATH=pathlib.Path(__file__).parent.resolve()
DATA_PATH=BASE_PATH.joinpath("data").resolve()

# Read data
df = pd.read_excel(DATA_PATH.joinpath("sample3.xlsx"),sheet_name=1,header=0)

# Clean up data
nonadf = df.fillna(0) 

# Render all UI elements 
app.layout = app_layout(nonadf,app.get_asset_url('bn_logo.svg'))

# All callback & events 

@app.callback(
    Output('baseline-custom','style'),
    Input('baseline-initial','value')
)
def get_custom_baseline(selected_baseline):
    if selected_baseline == 'CUS':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('journey-filter', 'options'),
    Input('tc-filter', 'value'))
def set_journey_options(selected_tc):
    filtereddf = nonadf[nonadf['TC Name'] == selected_tc] 
    return [{'label': journey, 'value': journey} for journey in np.sort(filtereddf['Journey Description'].unique())]

@app.callback(
    Output('journey-filter', 'value'),
    Input('journey-filter', 'options'))
def set_journey_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('sub-journey-filter', 'options'),
    Input('journey-filter', 'value'))
def set_sub_journey_options(selected_journey):
    filtereddf = nonadf[nonadf['Journey Description'] == selected_journey] 
    return [{'label': journey, 'value': journey} for journey in np.sort(filtereddf['Journey Sub Group'].unique())]

@app.callback(
    Output('sub-journey-filter', 'value'),
    Input('sub-journey-filter', 'options'))
def set_sub_journey_value(available_options):
    return available_options[0]['value']

@app.callback(
    [
        Output("demand-vs-capacity","figure"),
        Output("productivity","figure"),
        Output("bcvsrc","figure"),        
        Output("fwiph_avg","children"),
        Output("table", "data"), 
        Output('table', 'columns'),
        Output('table-container', 'style'),
        #Output('board','figure')
        Output('dcvolume','figure')
    ],
    [
        Input("tc-filter","value"),
        Input("journey-filter","value"),
        Input("sub-journey-filter","value"),

        #Input("baseline-factor","value"),
        Input("baseline-initial","value"),
        Input("baseline-custom","value"),

        Input("gr","value"),
        Input("gr_frequency","value"),
        Input("gr_start_month","value"),
        Input("gr_start_month_yr","value"),
        Input("gr_end_month","value"),
        Input("gr_end_month_yr","value"),

        Input("cifte","value"),
        Input("cifte_start_month","value"),
        Input("cifte_start_month_yr","value"),
        Input("cifte_end_month","value"),
        Input("cifte_end_month_yr","value"),

        Input("wiphead","value"),
        Input("wiphead_start_month","value"),
        Input("wiphead_start_month_yr","value"),
        Input("wiphead_end_month","value"),
        Input("wiphead_end_month_yr","value"),
        Input("wiphead_frequency","value"),

        Input("bcpfte","value"),
        Input('show-table','on'),
        Input('show-qtrly','on'),

    ],
)

def draw_charts(tc,journey,subjourney,bi,bc,
    gr,gr_frequency,gr_start_month,gr_start_month_yr,gr_end_month,gr_end_month_yr,
    cifte,cifte_start_month,cifte_start_month_yr,cifte_end_month,cifte_end_month_yr,
    wiphead,wiphead_start_month,wiphead_start_month_yr,wiphead_end_month,wiphead_end_month_yr,wiphead_frequency,
    bcpfte,showtable,showqtrly):

    mask = (
          (nonadf['TC Name'] == tc ) 
        & (nonadf['Journey Description'] == journey)         
        & (nonadf['Journey Sub Group'] == subjourney)
    )
            
    if journey is None:
        return {},{},{}

    filtered_data = nonadf.loc[mask,:]
    #transformeddf = fill_data(filtered_data)

    transformeddf = filtered_data.iloc[:,[11,16,17,18,19,20,21,22,23,24,25,26,27]].set_index('Value Name').T
    transformeddf = transformeddf.set_index(pd.to_datetime(transformeddf.index))

    
    # -------------------------------------------------------------------------------------------
    # Simulator calculations 
    # -------------------------------------------------------------------------------------------

    gr_sm = dy(gr_start_month,gr_start_month_yr)
    gr_em = dy(gr_end_month,gr_end_month_yr,True)
        
    cifte_sm =  dy(cifte_start_month,cifte_start_month_yr)
    cifte_em = dy(cifte_end_month,cifte_end_month_yr,True)

    wiphead_sm =  dy(wiphead_start_month,wiphead_start_month_yr)
    wiphead_em = dy(wiphead_end_month,wiphead_end_month_yr,True)

    # Work items selected..... 
    # init_simulator_fields

    initdf = init_simulator_fields(transformeddf)

    bf="WI"
    
    if bf == "WI":
        simulateddf = calculate_wi(initdf,
                                    gr,gr_sm,gr_em,gr_frequency,
                                    cifte,cifte_sm,cifte_em,
                                    wiphead,wiphead_sm,wiphead_em,bcpfte,wiphead_frequency,showqtrly)
    if bf == "BV" :
        simulateddf = calculate_bv(initdf,
                                    gr,gr_sm,gr_em,gr_frequency,
                                    cifte,cifte_sm,cifte_em,
                                    wiphead,wiphead_sm,wiphead_em,bcpfte,wiphead_frequency,showqtrly)

    dcvolume_fig = bigraphs.wi_dcvolume(simulateddf,gr_start_month,gr_start_month_yr)
    demand_capacity_fig = bigraphs.wi_simulated_fte(simulateddf)
    productivity_fig = bigraphs.wi_simulated_productivity(simulateddf)
    ftegap_fig =  bigraphs.wi_simulated_ftegap(simulateddf)
    #board_fig = bigraphs.simulated_board(simulateddf)

    fwiph_avg = "Average forecasted work items per head " +  str(simulateddf['Forecast Work Items Per Head'].mean().round())  

    tabledf = simulateddf.copy()
    #tabledf = convert_to_qtr(tabledf)
   
    tabledf.reset_index(inplace=True)

    if showtable:
        tblcols=[{"name": i, "id": i} for i in tabledf.columns]
        tblrows = tabledf.to_dict('records')
        tblshow = {'display':'block'}
    else: 
        tblshow = {'display':'none'}
        tblcols=[]
        tblrows=[]

    return demand_capacity_fig,ftegap_fig,productivity_fig,fwiph_avg,tblrows,tblcols,tblshow,dcvolume_fig
    #return {},{},{},fwiph_avg,tblrows,tblcols,tblshow

######

if __name__ == "__main__":
    #app.run_server(debug=True)
    app.run_server(host='0.0.0.0',port=8005,debug=True)
    #app.run_server(debug=False)
    #app.run_server(debug=False,dev_tools_ui=False,dev_tools_props_check=False)