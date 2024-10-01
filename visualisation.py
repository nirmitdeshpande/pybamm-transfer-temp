import pandas as pd, numpy as np, matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()


from operator import index

df = pd.read_csv('code/summary.csv')
#df = pd.read_csv('summary.csv')

#currently using 10 interval loops to separate one-at-a-time parameter cycling


for i in range(0,85):
    
    plt.scatter(df['T'][i], df['Last cycle'][i], c='red')
    

plt.xlabel("Temperature 'T (ºC)'")
plt.ylabel("First Cycle Capacity Loss '%'")

#fig, ax = plt.subplots()
#ax.plot(df["Cycle number"], df["Capacity [A.h]"])

plt.show()
#
#include seabprn where?
