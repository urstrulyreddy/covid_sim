import streamlit as smlt
import pandas as pd
from assignment2 import run 


try:
    smlt.title("COVID-19 Simulation")

    regionsdata = pd.read_csv('a2-countries.csv')
    regions = regionsdata['country'].tolist()

    smpscale = smlt.number_input("Sample Ratio", value=1e6, format="%.0e")
    st_dt = smlt.date_input("Start Date", value=pd.to_datetime("2021-04-01"))
    en_dt = smlt.date_input("End Date", value=pd.to_datetime("2022-04-30"))
    selectedregions = smlt.multiselect("Select Regions", regions)

    if smlt.button("Run Simulation"):
        if not selectedregions:
            smlt.warning("Please select regions to simulate. ")
        else:
            smlt.info(f"Running simulation on : {selectedregions}")
        run('a2-countries.csv', selectedregions, st_dt.strftime('%Y-%m-%d'), en_dt.strftime('%Y-%m-%d'), smpscale)
        smlt.image('a2-covid-simulation.png')
finally:
    print("Covid simulation is successful :)")
