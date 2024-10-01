#Valentin Sulzer, Nirmit Deshpande
#script to populate one-at-a-time parameter variation cycling,
#store results in a nested CSV format

from operator import index
import pybamm 
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from parameter_utils import get_parameter_values

pybamm.set_logging_level("NOTICE")  # comment out to remove logging messages

i=1 #index to name result.csv files
dfx=pd.DataFrame(columns=['Run', 'C_discharge',	'C_charge',	'V_min',	'V_max',	'T',	'k_SEI',
	'D_sei',	'b_LAM_n',	'b_LAM_p',	'90%',	'80%',	'70%',	'60%',	'First cycle',	'Last cycle', 'Results file'])										

#default values
#operating conditions
charge_rate = 1  # 0.05 to 5 C, linear
discharge_rate = 1  # 0.05 to 5 C, linear 
V_max = 4.2  # 3.9 to 4.2 V, linear
V_min = 3.0  # 2.8 to 3.5 V, linear
T = 25  # -5 to 45 degC, linear


# degradation variables
SEI_rate_constant = 1e-15  # 1e-17 to 1e-14, logarithmic
pos_LAM_term = 1e-6  # 1e-8 to 1e-5, logarithmic
neg_LAM_term = 1e-6  # 1e-8 to 1e-5, logarithmic
EC_diffusivity = 1e-18  # 1e-20 to 1e-16, logarithmic

i=1


#method to cycle for each row of the summary CSV format
def single_param_cycling(): 
 

 experiment = pybamm.Experiment(
    [
        (
            f"Discharge at {charge_rate}C until {V_min}V",
            f"Charge at {discharge_rate}C until {V_max}V",
            f"Hold at {V_max}V until C/50",
        )
    ]
    * 1000,
    termination="60% capacity",
 )

 # NMC532 parameter values with extra parameters for mechanical models
 parameter_values = get_parameter_values()
 parameter_values.update(
    {
        "Ambient temperature [K]": 273.15 + T,
        "SEI kinetic rate constant [m.s-1]": SEI_rate_constant,
        "EC diffusivity [m2.s-1]": EC_diffusivity,
    }
 )
 parameter_values.update(
    {
        "Positive electrode LAM constant proportional term [s-1]": pos_LAM_term,
        "Negative electrode LAM constant proportional term [s-1]": neg_LAM_term,
    },
    check_already_exists=False,
 )

 # Load model
 spm = pybamm.lithium_ion.SPM(
    {
        "SEI": "ec reaction limited",
        "loss of active material": "stress-driven",
    }
 )
 sim = pybamm.Simulation(spm, experiment=experiment, parameter_values=parameter_values)
 sol = sim.solve(initial_soc=1)

  #save inner cycling (one-parameter variation) to CSV files, sequentially named

 df = pd.DataFrame(sol.summary_variables, columns=["Cycle number",	"Time [h]",	
 "Capacity [A.h]",	"Measured capacity [A.h]",	"Loss of lithium inventory [%]",	
 "Loss of capacity to SEI [A.h]",	"Loss of active material in negative electrode [%]",
 "Negative electrode capacity [A.h]",	"Loss of active material in positive electrode [%]",
 "Positive electrode capacity [A.h]"])

 df.to_csv(("results/result_%s.csv" %i))
 str="result_%s.csv" %i

 #save row of results to outer cycling (summary CSV), while also calculating necessary values
 c90=0
 c80=0
 c70=0
 c60=0
 first_cyc = 100*(df['Capacity [A.h]'][0]-df['Capacity [A.h]'][1])/df['Capacity [A.h]'][0]
 last_cyc = 100*(df['Capacity [A.h]'][len(df.index)-2]-df['Capacity [A.h]'][len(df.index)-1])/df['Capacity [A.h]'][len(df.index)-2]

 for ind in df.index:
    if (df['Capacity [A.h]'][ind]/df['Capacity [A.h]'][0] >= 0.90):
        c90 = df['Cycle number'][ind]
    
    if (df['Capacity [A.h]'][ind]/df['Capacity [A.h]'][0] >= 0.80):
        c80 = df['Cycle number'][ind]
    
    if (df['Capacity [A.h]'][ind]/df['Capacity [A.h]'][0] >= 0.70):
        c70 = df['Cycle number'][ind]

    if (df['Capacity [A.h]'][ind]/df['Capacity [A.h]'][0] >= 0.60):
        c60 = df['Cycle number'][ind]
        
 #store all summary CSV values here

 dfx.loc[len(dfx.index)]=[i, discharge_rate, charge_rate, V_min, V_max, T, SEI_rate_constant, EC_diffusivity,
 neg_LAM_term, pos_LAM_term, c90, c80, c70, c60, first_cyc, last_cyc, str]

 i=i+1


#calling above function by passing one-at-a-time parameter variation

#operating conditions

#sampling using SOBOL?

#T, -5 to 45 degC, linear
a, b, n = -5, 45, 100 

for x in range(-5, 46, 2):
 T=x
 single_param_cycling()
T = 25 

#charge_rate, 0.05 to 5 C, linear
x=0.05
while (x<=5):
    charge_rate=x
    single_param_cycling()
    x=x+0.4
charge_rate=1

#discharge_rate, 0.05 to 5 C, linear
x=0.05
while (x<=5):
    discharge_rate=x
    single_param_cycling()
    x=x+0.4
discharge_rate=1

#V_max, 3.9 to 4.2 V, linear
x=3.9
while (x<=4.2):
    V_max=x
    single_param_cycling()
    x=x+0.1
V_max=4.2

#V_min = 3, 2.8 to 3.6 V, linear
x=2.8
while (x<=3.6):
    V_min=x
    single_param_cycling()
    x=x+0.1
V_min=3

# degradation variables

arr=np.logspace(-17, -14, 100)
for x in arr:
    SEI_rate_constant = x
    single_param_cycling()
SEI_rate_constant = 1e-15 

arr=np.logspace(-8, -5, 100)
for x in arr:
    pos_LAM_term = x
    single_param_cycling()
pos_LAM_term = 1e-6 

arr=np.logspace(-8, -5, 100)
for x in arr:
    neg_LAM_term = x
    single_param_cycling()
neg_LAM_term = 1e-6 

arr=np.logspace(-20, -16, 100)
for x in arr:
    EC_diffusivity = x
    single_param_cycling()
EC_diffusivity = 1e-18 


#replace steps and log after every save

dfx.to_csv("code/summary.csv")


