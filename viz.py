import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from pkg_resources import DefaultProvider
import plotly.express as px
import pandas as pd 
import numpy as np 
import pathlib
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import math
from  model import dy

def xwi_simulated_fte(df):

    df.round(1)
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=df.index, y=df['Simulated Required FTE'], name='Simulated Required FTE',marker_color="#03254c"),
        secondary_y=False,
    )

    # Add traces
    fig.add_trace(
        go.Bar(x=df.index, y=df['Simulated Actual FTE'], name='Simulated Actual FTE',marker_color="#1167b1"),        
        secondary_y=False,
    )    
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Actual FTE'],name='Actual FTE',marker_color="black",marker_line_width=4),
        secondary_y=False,
    )
    # Add figure title
    #fig.update_layout(
    #        title_text="FTE Gap vs Productivity"
    #)
    # Set x-axis title
    fig.update_xaxes(title_text="Month",
        dtick="M1",
        nticks=12,
        tickformat="%b\n%Y",
        ticklabelmode="period" )

    # # Set y-axes titles
    # fig.update_yaxes(
    #        title_text="FTE", 
    #        secondary_y=False)
    # fig.update_yaxes(
    #        title_text="FTE", 
    #        secondary_y=True) 

    
    fig.update_layout(
        plot_bgcolor='white',
        legend=dict(title="Legend:",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        #bargap=0.15, # gap between bars of adjacent location coordinates.
        #bargroupgap=0.1, # gap between bars of the same location coordinate.
        xaxis=dict(
                title="",
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(82, 82, 82)',
                ),
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=True,
                showline=True,
                showticklabels=True,
            )        
    )

    return fig


def wi_simulated_fte(df):
    
    df.rename({"Simulated Actual FTE": "Available FTE",'Simulated Required FTE':'Required FTE'},inplace=True,axis=1)
    df = df.round(1)

    fig = px.bar(df, x=df.index, y=['Available FTE','Required FTE'],barmode='group',
                 labels={
                      "value": "Represented in number of FTE",
                      "index": "Month",
                  },                  
             color_discrete_map={"Required FTE":"#03254c","Available FTE":"rgb(17, 157, 255)"})
                 
    # fig.update_layout(legend=dict(title="Legend:",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1))
    # fig.update_xaxes(dtick="M1",nticks=12,tickformat="%b\n%Y",ticklabelmode="period")    

    df.round(2)
    text=[df['Available FTE'].to_list(),df['Required FTE'].to_list()]
    for i, t in enumerate(text):
        fig.data[i].text=t
        fig.data[i].textfont={'color':'black','size':12,'family':'Arial'}
        fig.data[i].textposition='outside'

        #fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    

    fig.update_layout(plot_bgcolor='white',
            legend=dict(title="Legend:",            
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1),
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            xaxis=dict(
                title="",
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(82, 82, 82)',
                ),
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=True,
                showline=True,
                showticklabels=True,
            ))
    #fig.update_xaxes(nticks=12,ticklabelmode="period")
    #fig.update_xaxes(dtick="M1",nticks=12,tickformat="%b\n%Y",ticklabelmode="period")
    fig.update_xaxes(dtick="M1",nticks=12,tickformat="%b\n%Y",ticklabelmode="period")

    return fig


def wi_simulated_ftegap(df):

    df = df.fillna(0)
    df.rename({"Simulated FTE Gap": "FTE Gap"},inplace=True,axis=1)
    df = df.round(1)

    fig = px.bar(df, x=df.index, y=['FTE Gap','FTE Gap With Productivity Held Flat'],barmode='group',            
           labels={
                      "value": "Represented in number of FTE",
                      "index": "Month",
                  },            
             color_discrete_map={"FTE Gap":"#03254c",'FTE Gap With Productivity Held Flat':'#ccc'})

    text=[df['FTE Gap'].to_list(),df['FTE Gap With Productivity Held Flat'].to_list()]
    for i, t in enumerate(text):
        fig.data[i].text=t
        fig.data[i].textposition='outside'    

    fig.update_layout(plot_bgcolor='white',
        legend=dict(title="(Negative = Surplus), Legend:",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis=dict(
                title="",
                showline=True,
                showgrid=False,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=1,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='rgb(82, 82, 82)',
                ),
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=True,
                showline=True,
                showticklabels=True,
        ))        
        
    fig.update_xaxes(dtick="M1",nticks=12,tickformat="%b\n%Y",ticklabelmode="period")    


    return fig

def simulated_board(df):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Bar(x=df.index, y=df['Simulated Actual Work Items Submitted'],marker_color="#2a9df4"),
        secondary_y=False,
    ) 
    # Add traces
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Simulated Actual FTE']),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Required FTE']),
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title")
    # Set y-axes titles
    fig.update_yaxes(
            title_text="<b>primary</b> yaxis title", 
            secondary_y=False)
    fig.update_yaxes(
            title_text="<b>secondary</b> yaxis title", 
            secondary_y=True)

    return fig


def wi_dcvolume(df,gr_sm,gr_sy):

    df[df.eq(0)] = np.nan
    df.rename({"Simulated Actual Business Volume": "Simulated Business Volume"},inplace=True,axis=1)

    fig = go.Figure()


    if 'quarter' in df.columns:                                    
        act = df[df.quarter <= math.ceil(float(dy(gr_sm,gr_sy,True).month) / 3)] 
    else:
        act =  df[df.index <= dy(gr_sm,gr_sy,True)]

    fig.add_trace(go.Scatter(x=act.index, y=act["Actual Business Volume"], name='Actual Business Volume',
                         connectgaps=True,
                         line=dict(color='#1167b1', width=4)))

    if 'quarter' in df.columns:
        sim = df[df.quarter >= math.ceil(float(dy(gr_sm,gr_sy,True).month) / 3)] 
    else:
        sim = df[df.index >= dy(gr_sm,gr_sy,False)]

    fig.add_trace(go.Scatter(x=sim.index, y=sim["Simulated Business Volume"], name = 'Simulated Business Volume',
                          #connectgaps=True,
                          line={'dash': 'dash', 'color': 'rgb(17, 157, 255)','width':2}))
                          #line=dict(color='rgb(42,157,244)', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df["Forecast Business Volume"], name = 'Forecast Business Volume',
                         line=dict(color='rgb(150,150,150)', width=2)))

    fig.update_layout(
        xaxis=dict(
            title="",
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
        plot_bgcolor='white',
        legend=dict(title="Legend:",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        annotations=[dict(xref='paper', yref='paper', x=0.5, y=-0.1,
                              xanchor='center', yanchor='top',
                              text='Source: Service Portal ' +
                                   '(Service Consumption data)',
                              font=dict(family='Arial',
                                        size=12,
                                        color='rgb(150,150,150)'),
                    showarrow=False)
        ]
    )
    
    fig.update_xaxes(dtick="M1",nticks=12,tickformat="%b\n%Y",ticklabelmode="period")
    
    return fig

def wi_simulated_productivity(df):

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.index, y=df["Actual Work Items Per Head"], name='Actual Work Items Per Head',
                         line=dict(color='#1167b1', width=4)))

    fig.add_trace(go.Scatter(x=df.index, y=df["Forecast Work Items Per Head"], name='Forecast Work Items Per Head',
                         line=dict(color='rgb(150,150,150)', width=2)))
    
    fig.add_trace(go.Scatter(x=df.index, y=df["Simulated Forecast Work Item Per Head"], name='Simulated Forecast Work Item Per Head',                         
                         line={'dash': 'dash', 'color': 'rgb(17, 157, 255)','width':2}))
                         #line=dict(color='#1167b1', width=2)))                                                  


    fig.update_layout(
        xaxis=dict(
            title="",
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=1,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=True,
            showline=True,
            showticklabels=True,
        ),
    plot_bgcolor='white'
    )
    fig.update_layout(legend=dict(title="Legend:",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),uniformtext_minsize=8,uniformtext_mode='hide')
    
    # fig = px.bar(df, x=df.index, y=['Actual Work Items Per Head','Forecast Work Items Per Head','Simulated Forecast Work Item Per Head'],barmode='group',    
    #         labels={
    #                   "value": "Represented Work Items Per Head",
    #                   "index": "Month",
    #               },            
    #          color_discrete_map={"Actual Work Items Per Head":"#03254c","Forecast Work Items Per Head":"#1167b1","Simulated Forecast Work Item Per Head":"#00bfd8"})

    # df.round(2)
    # text=[df['Actual Work Items Per Head'].to_list(),df['Forecast Work Items Per Head'].to_list(),df['Simulated Forecast Work Item Per Head'].to_list()]
    # for i, t in enumerate(text):
    #     fig.data[i].text=t
    #     fig.data[i].textposition='inside'    
    
    # fig.update_layout(legend=dict(title="Legend:",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),uniformtext_minsize=8,uniformtext_mode='hide')
    # fig.update_xaxes(dtick="M1",nticks=12,tickformat="%b\n%Y",ticklabelmode="period")

    return fig    