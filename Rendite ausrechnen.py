#Rendite ausrechnen
df1 = df[['Cash', 'Defensiv', 'Offensiv', 'Ausgewogen']].iloc[[0, -1]]
df['cum_cash']= df['Cash'].cumprod()
df['cum_defensiv']= df['Defensiv'].cumprod()
df['cum_offensiv']= df['Offensiv'].cumprod()
df['cum_ausgewogen']= df['Ausgewogen'].cumprod()

print(df)
print(df['Cash'].iloc[[-1]])
print(df['Defensiv'].iloc[[-1]])
print(df['Offensiv'].iloc[[-1]])
print(df['Ausgewogen'].iloc[[-1]])
'''
df2 = (df[['Cash']].iloc[[-1]]*100/df[['Cash']].iloc[[0]])-100
print(df2)
df3 = df[['Defensiv']].iloc[[-1]]-df[['Defensiv']].iloc[[0]]
print(df3)
df4 = (df[['Offensiv']].iloc[[-1]]*100/df[['Offensiv']].iloc[[0]])-100
print(df4)
df5 = (df[['Ausgewogen']].iloc[[-1]]*100/df[['Ausgewogen']].iloc[[0]])-100
print(df5)
'''

#Html für Rendite
html.Div(f"{df['Cash'].iloc[-1]}"), 

    html.Div(f"{df['Defensiv'].iloc[-1]}"), 
    
    html.Div(f"{df['Offensiv'].iloc[-1]}"),
    
    html.Div(f"{df['Ausgewogen'].iloc[-1]}"),  
],                    

    style={'margin': 30}
)