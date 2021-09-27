import pandas as pd 
import numpy as np 
import pathlib
from datetime import datetime
import math
from dateutil.relativedelta import relativedelta


def convert_to_qtr(df):

    x = df.resample('Q', convention='end').agg({'Forecast FTE':'mean', 
       'Forecast Work Items Per Head':'mean', 
       'Actual FTE':'mean',
       'Actual Work Items Completed':'sum', 
       'Forecast Business Volume':'sum',
       'Actual Business Volume':'sum',        
       'Forecast Work Items':'sum',
       'Actual Work Items Submitted':'sum', 
       'Budgeted FTE':'mean',
       'Budgeted Work Items Per Head':'mean', 
       'Budgeted Business Volume':'sum',
       'Budgeted Work Items':'sum', 
       'Forecast Available Capacity (Work Items)':'sum',
       'Actual Available Capacity (Work Items)':'sum', 
       'Actual Work Items Per Head':'mean',
       'Budgeted Available Capacity (Work Items)':'sum',       
       'Simulated Actual Business Volume':'sum',
       'Simulated Actual Work Items Submitted':'sum',
       'Simulated Forecast Work Item Per Head':'mean',
       'Simulated Actual FTE':'mean',
       'Simulated Forecast FTE':'mean',
       'Actual Required FTE':'mean',
       'Simulated Required FTE':'mean',
       'Actual FTE Gap':'mean',
       'Required FTE With Productivity Held Flat':'mean',
       'FTE Gap With Productivity Held Flat':'mean',
       'Simulated FTE Gap':'mean'})

    x['quarter'] = [pd.Period(x.index[i], freq='M').quarter for i in range(len(x))]
    
    return x


def init_simulator_fields_new(df):

    simdf = df.copy()
    simdf["Simulated Actual Business Volume"] = simdf["Actual Business Volume"]
    simdf['Simulated Actual Business Volume'].replace(to_replace=0,method='ffill',inplace=True)
    simdf['Simulated Actual Business Volume'] = np.where(simdf["Actual Business Volume"] > 0,simdf["Actual Business Volume"],0)
    simdf["Simulated Actual Work Items Submitted"] = simdf["Actual Work Items Submitted"]
    simdf["Simulated Forecast Work Item Per Head"] = 0
    simdf["Simulated Actual FTE"] = 0
    simdf["Simulated Forecast FTE"] = 0 
    simdf = simdf.round({"Actual Work Items Per Head": 2})
    simdf[simdf.eq(0)] = np.nan
    return simdf


def init_simulator_fields(df):

    simdf = df.copy()
        
    simdf["Simulated Actual Business Volume"] = simdf["Actual Business Volume"]
    simdf['Simulated Actual Business Volume'].replace(to_replace=0,method='ffill',inplace=True)
    #simdf['Simulated Actual Business Volume'] = np.where(simdf["Actual Business Volume"] == simdf["Simulated Actual Business Volume"],np.nan,simdf["Simulated Actual Business Volume"])

    simdf["Simulated Actual Work Items Submitted"] = simdf["Actual Work Items Submitted"]
    simdf['Simulated Actual Work Items Submitted'].replace(to_replace=0,method='ffill',inplace=True)

    simdf["Simulated Forecast Work Item Per Head"] = simdf["Forecast Work Items Per Head"]
    simdf['Simulated Forecast Work Item Per Head'].replace(to_replace=0,method='ffill',inplace=True)

    simdf["Simulated Actual FTE"] = simdf["Actual FTE"]
    simdf['Simulated Actual FTE'].replace(to_replace=0,method='ffill',inplace=True)

    simdf["Simulated Forecast FTE"] = simdf["Forecast FTE"]
    simdf['Simulated Forecast FTE'].replace(to_replace=0,method='ffill',inplace=True)

    simdf = simdf.round({"Actual Work Items Per Head": 2})

    return simdf


def fill_data(vdf):

    df = vdf.copy()
    start=df.columns[len(df.columns)-1]
    start=start + relativedelta(months=1)
    todays_date = datetime.today()
    end_date_yr = todays_date.year + 3
    end_date_mn = 12
    num_months = (end_date_yr - start.year) * 12 + (end_date_mn - start.month)

    for i in pd.date_range(start, periods=num_months + 1,freq='M').tolist():    
        df[i.strftime("%Y-%m-%d %H:%M:%S")] = df.iloc[:,len(df.columns)-1]    
    
    cols = [11]
    for i in range(16,len(df.columns)):
        cols.append(i)

    transformeddf = df.iloc[:,cols].set_index('Value Name').T
    transformeddf = transformeddf.set_index(pd.to_datetime(transformeddf.index))

    return transformeddf

#---------------------------------------------------------
# Apply volume drivers - Change growth by x% MoM
#---------------------------------------------------------
def apply_volume_drivers(df,gr,gr_sm,gr_em,gr_frequency,bv_or_wi):

    # Check if growth rate is null and default to zero
    if gr is None:        
        gr = 0

    if gr == 0:
        return df

    if bv_or_wi == "bv":
        filter="Actual Business Volume"
        simfld="Simulated Actual Business Volume"

    if bv_or_wi == "wi":
        filter='Simulated Actual Work Items Submitted' 
        simfld=filter

    gr_pm = gr_sm #- relativedelta(months=1)
    prior_outsidefilterdf = df[df.index < gr_pm].copy()
    prior_month_df = df.loc[gr_pm:pd.Period(gr_sm,freq='M').end_time.date()].copy()
    simulateddf =  df.loc[gr_sm:gr_em].copy()

    # Retain actual values for prior months
    prior_month_df[simfld] = prior_month_df[filter]
    prior_outsidefilterdf[simfld] = prior_outsidefilterdf[filter]

    pcnt = int(gr) / 100

    awis=[prior_month_df[filter][0]]

    for i in range(1,len(simulateddf.index)):
        if gr_frequency == "Y":            
            awis.append(awis[i-1] * (1 + pcnt / 12))        
        else:
            awis.append(awis[i-1] * (1 + pcnt))

    simulateddf[simfld]=awis
    simulateddf = simulateddf.round({simfld: 2})

    after_outsidefilterdf =  df[df.index > gr_em].copy()
    after_outsidefilterdf[simfld] = simulateddf.iloc[[-1]][simfld][0]
    simulateddf = simulateddf.append([prior_outsidefilterdf,after_outsidefilterdf]).sort_index()
    
    return simulateddf

#---------------------------------------------------------
# Apply Revised Work Item Drivers
#---------------------------------------------------------
def apply_productivity(df,wiphead,wiphead_sm,wiphead_em,wiphead_frequency):

    if wiphead is None:
        wiphead = 0
    
    if wiphead == 0:
        return df
    
    simfld="Simulated Forecast Work Item Per Head"
    filter=simfld

    wiphead_pm = wiphead_sm - relativedelta(months=1)    

    prior_outsidefilterdf = df[df.index < wiphead_pm].copy()
    prior_month_df = df.loc[wiphead_pm:wiphead_sm].copy()
    simulateddf =  df.loc[wiphead_sm:wiphead_em].copy()

    # Retain actual values for prior months
    prior_month_df[simfld] = prior_month_df[filter]
    prior_outsidefilterdf[simfld] = prior_outsidefilterdf[filter]    
    
    pcnt = int(wiphead) / 100

    if wiphead_frequency == "Y":            
        wiph=[prior_month_df[filter][0] * (1 + pcnt / 12) ]
    else:
        wiph=[prior_month_df[filter][0] * (1 + pcnt) ]

    for i in range(1,len(simulateddf.index)):
        if wiphead_frequency == "Y":            
            wiph.append(wiph[i-1] * (1 + pcnt / 12))        
        else:
            wiph.append(wiph[i-1] * (1 + pcnt))

    simulateddf[simfld]=wiph
    simulateddf = simulateddf.round({simfld: 2})

    after_outsidefilterdf =  df[df.index > wiphead_em].copy()
    after_outsidefilterdf[simfld] = simulateddf.iloc[[-1]][simfld][0]
    simulateddf = simulateddf.append([prior_outsidefilterdf,prior_month_df,after_outsidefilterdf]).sort_index()

    return simulateddf
  
#---------------------------------------------------------
# Apply Business Volume to work item ratio
#---------------------------------------------------------
def apply_bv_to_wi_ratio(df): # rename to ratio...
    df["Average Forecast Business Volume Ratio"]= df["Forecast Business Volume"] / df["Forecast Work Items"]
    df = df.round({'Average Forecast Business Volume': 2})
    return df

#---------------------------------------------------------
# Simulate work items
#---------------------------------------------------------
def simulate_work_items(df):
    df["Simulated Work Items"] = df["Average Forecast Business Volume Ratio"] * df["Actual Business Volume"]
    df = df.round({'Simulated Work Items': 2})
    return df

#---------------------------------------------------------
# Apply FTE Drivers
#---------------------------------------------------------
def apply_fte_drivers(df,wiphead,wiphead_sm,wiphead_em,wiphead_frequency,cifte,cifte_sm,cifte_em,bv_or_wi):

    widf = apply_productivity(df,wiphead,wiphead_sm,wiphead_em,wiphead_frequency)

    cifte_pm = cifte_sm
    pmdf = widf.loc[cifte_pm:pd.Period(cifte_sm,freq='M').end_time.date()]


    widf = widf.copy()
    widf["Simulated Actual FTE"] = widf["Actual FTE"]
    widf['Simulated Actual FTE'].replace(to_replace=0,method='ffill',inplace=True)

    prior=widf[widf.index < cifte_pm].copy()
    after=widf[widf.index > cifte_em].copy()

     #widf.loc[widf.index > pd.Period(cifte_sm,freq='M').end_time.date()].copy()

    if cifte > 0:
        current = widf.loc[cifte_sm:cifte_em].copy() 
        current['Simulated Actual FTE'] = pmdf['Simulated Actual FTE'][0] + cifte
        ftedf = current.append([prior,after]).sort_index()
    else:
        ftedf = widf

    if bv_or_wi == "wi":
        ftedf["Simulated Required FTE"] = ftedf["Simulated Actual Work Items Submitted"] / ftedf["Simulated Forecast Work Item Per Head"]
        ftedf = ftedf.round({"Simulated Required FTE":1})

        ftedf["Required FTE With Productivity Held Flat"] = np.where(ftedf.index > wiphead_sm,ftedf["Simulated Actual Work Items Submitted"] / ftedf["Forecast Work Items Per Head"], np.nan)
        ftedf = ftedf.round({"Required FTE With Productivity Held Flat":1})

        ftedf["Actual Required FTE"] = ftedf["Actual Work Items Submitted"] / ftedf["Forecast Work Items Per Head"]
        ftedf = ftedf.round({"Actual Required FTE":1})
        
    
    #if bv_or_wi == "bv":
    #    ftedf["Required FTE"] = ftedf["Simulated Work Items"] / ftedf["Forecast Work Items Per Head"]
    #    ftedf = ftedf.round({"Required FTE":2})

    
    ftedf["Actual FTE Gap"] = ftedf["Actual Required FTE"] - np.where(ftedf["Actual FTE"] > 0,ftedf["Actual FTE"],np.nan)
    ftedf["Simulated FTE Gap"] = ftedf["Simulated Required FTE"] - ftedf["Simulated Actual FTE"]

    ftedf["FTE Gap With Productivity Held Flat"] = ftedf["Required FTE With Productivity Held Flat"] - ftedf["Simulated Actual FTE"]

    ftedf = ftedf.round({"Actual FTE Gap":1})
    ftedf = ftedf.round({"Simulated FTE Gap":1})
    ftedf = ftedf.round({"FTE Gap With Productivity Held Flat":1})
        
    #ftedf['Simulated Actual FTE'].replace(to_replace=0,method='ffill',inplace=True)
    #ftedf['FTE Gap'] = np.where(ftedf["Actual FTE"] > 0,ftedf['Required FTE'] - ftedf['Simulated Actual FTE'], ftedf['Required FTE'] - ftedf['Simulated Forecast FTE'] )
    #ftedf["Actual FTE" > 0 ]  ## ftedf['FTE Gap'] = 
    #ftedf["Actual FTE" = 0 ] ## ftedf['FTE Gap'] = 
    #ftedf['Forecast FTE Gap'] = ftedf['Required FTE'] - ftedf['Simulated Forecast FTE']
    #ftedf = ftedf.round({'FTE Gap':2})
    #ftedf = ftedf.round({'Forecast FTE Gap':2})

    return ftedf

#---------------------------------------------------------
# Cost drivers
#---------------------------------------------------------
def apply_cost_drivers(df,bcpfte):
    
    # Additional fields for graphs 
    gf = df.copy()
    gf["Actual Productivity"] = gf["Actual Work Items Completed"] / gf["Actual FTE"]
    gf["Budgeted cost"] = gf["Budgeted FTE"] * bcpfte
    gf["Required cost"] = gf["Required FTE"] * bcpfte

    return gf

#Convert date
def dy(m,y,end=False):
    d='1'
    if end:
        d = pd.Period('1-' + m + '-2021',freq='M').end_time.date().day    
    return datetime.strptime(m + ' '+ str(d) + ' ' + str(y), '%b %d %Y')


#---------------------------------------------------------
# Simulate Work Items 
#---------------------------------------------------------
def calculate_wi(transformeddf, gr,gr_sm,gr_em,gr_frequency,
                                cifte,cifte_sm,cifte_em,
                                wiphead,wiphead_sm,wiphead_em,bcpfte,wiphead_frequency,showqtrly):
    
    if gr is None:
        gr = 0

    if cifte is None:
        cifte = 0 # Need to change and default to the forecast fte for the startmonth
    
    if wiphead is None:
        wiphead = 0 # Need to change to Avg if non specified 

    gr_pm = gr_sm - relativedelta(months=1)
    pmdf = transformeddf.loc[gr_pm:gr_sm]
    
    voldf = apply_volume_drivers(transformeddf, gr,gr_sm,gr_em,gr_frequency,'wi')
    voldf = apply_volume_drivers(voldf, gr,gr_sm,gr_em,gr_frequency,'bv')
    simulateddf = apply_fte_drivers(voldf,wiphead,wiphead_sm,wiphead_em,wiphead_frequency,cifte,cifte_sm,cifte_em,'wi')
    #simulateddf = apply_cost_drivers(simulateddf,bcpfte)

    if showqtrly:
        simulateddf = convert_to_qtr(simulateddf)
        idx2 = simulateddf.index.strftime('%b %Y')
        idx1 = (simulateddf.index - pd.offsets.MonthBegin(3)).strftime('%b')
        simulateddf.index = ['{0[0]}-{0[1]}'.format(x) for x in zip(idx1, idx2)]

    return simulateddf

#---------------------------------------------------------
# Simulate Business Volume
#---------------------------------------------------------
def calculate_bv(transformeddf, gr,gr_sm,gr_em,gr_frequency,
                                cifte,cifte_sm,cifte_em,
                                wiphead,wiphead_sm,wiphead_em,bcpfte,wiphead_frequency,showqtrly):

    if gr is None:
        gr = 0

    if cifte is None:
        cifte = 0
    
    if wiphead is None:
        wiphead = 0

    gr_pm = gr_sm - relativedelta(months=1)
    pmdf = transformeddf.loc[gr_pm:gr_sm]
    
    voldf = apply_volume_drivers(transformeddf, gr,gr_sm,gr_em,gr_frequency,'bv')
    bvdf = apply_bv_to_wi_ratio(voldf)
    swidf = simulate_work_items(bvdf)
    simulateddf = apply_fte_drivers(swidf,pmdf,wiphead,wiphead_sm,wiphead_em,wiphead_frequency,cifte,cifte_sm,cifte_em,'bv')
    simulateddf = apply_cost_drivers(simulateddf,bcpfte)

    return simulateddf