import pandas as pd
import random as rdm
from datetime import datetime as dti
import helper as hpr
import sim_parameters as smps

if not all(hasattr(smps, attr) for attr in ['TRANSITION_PROBS', 'HOLDING_TIMES']):
    raise ValueError("Transitions probabilities and holding times not there.")

trans_probs = smps.TRANSITION_PROBS
withhold_tenure = smps.HOLDING_TIMES

class Covid19:
    def __init__(self, regionsdata, regionslist, st_dt, en_dt, smpscale):
        #Intialising the countries data, start date and end date of the simulation, and the sample ratio
        self.regionslist, self.st_dt, self.en_dt, self.smpscale = (
            [r.strip() for r in regionslist #remove empty space in the region names
            if isinstance(r, str)] 
            if isinstance(regionslist, list)
            else [regionslist],
            #map function is to normalise the datetime object without getting time format
            *map(lambda dt: pd.to_datetime(dt).normalize() 
                 if isinstance(dt, (str, dti)) 
                 else pd.Timestamp.min, [st_dt, en_dt]), 
            
                 smpscale 
                 if isinstance(smpscale, (int, float)) and smpscale > 0 # checks the sample ratio is greater than 0 and is the instance of integer and float.
                 else 1
            )
        self.regionData = pd.read_csv(hpr.get_filepath(regionsdata)).query('country in @self.regionslist') if isinstance(regionsdata, str) else pd.DataFrame() #reads the csv file and filters the rows of the dataframe which matches with the country column in the @self.regionslist
        self.days_range = pd.date_range(self.st_dt, self.en_dt) if isinstance(self.st_dt, pd.Timestamp) and isinstance(self.en_dt, pd.Timestamp) else pd.date_range(pd.Timestamp.min, pd.Timestamp.max) #gives days range using .days_range() between start_date and end_date

    def simulate(self):
        model_outcome, daily_summaries = [], [] #initialize to store each day detailed results
        
        for country_name in self.regionslist: #iterate for the region, get data from the dataset and calculate sample size
            regionData = self.regionData.query("country == @country_name").iloc[0]
            smplen = int(regionData['population'] / self.smpscale) 
            population_df = self._initiate_people_dtf(regionData, smplen) # store the initial population state for this region, create dataframe

            for current_date in self.days_range: #iterate days as given in simulation period, and save before transition
                population_df['prev_state'] = population_df['state']  
                population_df['state'], population_df['staying_days'] = zip(
                    *population_df.apply(lambda persona: self._phase_shift(persona), axis=1)
                    )  # determine new states and staying days for every person,using _phase_shift method

                date_str = current_date.strftime('%Y-%m-%d') # converting datetime into yyyy-mm-dd  
                model_outcome.append(population_df.assign(date=date_str, country=country_name))# combining person with country along with date, count the people in each health state
                daily_summary = population_df['state'].value_counts().to_dict() 
                daily_summary.update({'date': date_str, 'country': country_name}) 
                daily_summaries.append(daily_summary) ##store in list

        self._capture_outcome(model_outcome, daily_summaries) #save results to csv usiing capture outcome

    def _initiate_people_dtf(self, regionData, smplen): #create a dataframe based on age and population for the region
        
        agesDict = {'less_5': 'less_5', 
                    '5_to_14': '5_to_14', 
                    '15_to_24': '15_to_24', 
                    '25_to_64': '25_to_64', 
                    'over_65': 'over_65'}
        groupValues = map(lambda group: int(smplen * (regionData[group] / 100)), 
                          agesDict.keys()
                          ) #number of people in each group
        peopledt = pd.concat([  #create a dataframe and iterate to get one age group along with attributes
            pd.DataFrame({
                'persona_id': range(len(peopledt), len(peopledt) + count),
                'age_group_name': group,
                'state': 'H',  
                'staying_days': 0,
                'prev_state': 'H'
            })
            for group, count in zip(agesDict.values(), groupValues) #loop age group along with count
            for peopledt in [[]] #get a empty list to accumulate data and concatenate all dataframes into one
        ], ignore_index=True)

        return peopledt

    def _phase_shift(self, persona): #check if a person is staying more than holding time in current state, determine using random choice, get new state
        if persona['staying_days'] >= withhold_tenure[persona['age_group_name']][persona['state']]:
            comingPhase = rdm.choices(
                list(trans_probs[persona['age_group_name']]
                                [persona['state']].keys()),
                list(trans_probs[persona['age_group_name']]
                                [persona['state']].values())
            )[0]
            return comingPhase, 0 #start count as 0
        return persona['state'], persona['staying_days'] + 1  # if not, increase by 1

    def _capture_outcome(self, model_outcome, daily_summaries): #save the result in csv along with daily counts, generate plot
        completedf = pd.concat(model_outcome) # concatenate the list, each dataframe for one day
        completedf = completedf[['persona_id', 
                                 'age_group_name', 
                                 'country', 
                                 'date', 
                                 'state', 
                                 'staying_days',
                                 'prev_state']]
        completedf.to_csv(hpr.get_filepath('a2-covid-simulated-timeseries.csv'), index=False) #save location
        
        abstractdf = pd.DataFrame(daily_summaries).fillna(0) # fill any missing values
        abstractdf = abstractdf[['date', 'country', 'D', 'H', 'I', 'S', 'M']]
        abstractdf.to_csv(hpr.get_filepath('a2-covid-summary-timeseries.csv'), index=False)
        
        hpr.create_plot('a2-covid-summary-timeseries.csv', self.regionslist) #generate a summary plot

def run(countries_csv_name, countries, start_date, end_date, sample_ratio): #main run function to be imported in the test.py
    sim = Covid19(countries_csv_name, countries, start_date, end_date, sample_ratio) #initialising Covid19 object to simulate the data
    sim.simulate()