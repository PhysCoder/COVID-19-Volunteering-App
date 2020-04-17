
APP_DESCRIPTION = """
                    This Web Application is here to offer help and comforts to the neighbours around us \
                    whose lives are impacted by COVID-19. 
                    
                    - User can select a collection of tasks such as grocery pickup, virtual reader, golves making, etc. \
                      and find nearby State Farm volunteers who happen to be available or share similar trips
                    - The app will provide the best match based on the user's input, but the user still have the option \
                      to select their preferred volunteer by clicking on the map
                    - Detailed contact information for local agent office and the selected volunteer will appear \
                      at the botoom of the page.
                    - State Farm volunteers will be rewarded and recognized for their kind actions, as part of our ***100forGood*** Program. 
                  """

APP_TITLE = "***100forGood*** Volunteering Map for COVID-19"

REQUEST_TYPES = dict(grocery='G', 
                     medical='M', 
                     education='E', 
                     home='H')

REQUEST_SUBTYPES = dict(G=['home goods', 'food'],
                        M=['cloth masks', 'disinfectants', 'medication'],
                        E=['book reader', 'virtual playground'],
                        H=['lawn mowing', 'misc. repairs', ])


# fake data
import plotly.express as px

def generate_data():
  NY_loc = {"Times Square": {"lat": 40.7589, "lon": -73.9851}}
  df = px.data.carshare()
  df.rename(columns={"car_hours": "availability"}, inplace=True)
  df['availability'] = (df['availability'] - df['availability'].min()) / (df['availability'].max() - df['availability'].min()) * 7
  df['availability'] = df['availability'].apply(int)
  mean_lat = df['centroid_lat'].mean()
  mean_lon = df['centroid_lon'].mean()
  df['centroid_lat'] = df['centroid_lat'] - mean_lat + NY_loc['Times Square']['lat']
  df['centroid_lon'] = df['centroid_lon'] - mean_lon + NY_loc['Times Square']['lon']

  return df

volunteer_data = generate_data()

# agent information
# name, location, phone, email
import pandas as pd

agent_info = pd.DataFrame({'Name': ['Henry Barber', 'Nora Fanshaw'], 
                           'Office': ["31 W 8th Street New York, NY 10011-9064", "39 Broadway, New York, NY 10006"],
                           'Phone': ['212-253-2228', '212-514-8259']
                           })
# volunteer information
# name, phone, availability, going to stores
match_volunteer_info = pd.DataFrame({'Name': ['Charlie'],
                               'Phone': ['212-384-4890'],
                               'Availability': [['2020-05-01', '2020-05-02']],
                               'Going to Stores': [['Walmart', 'Walgreens', 'Costco']]
                              })
select_volunteer_info = pd.DataFrame({'Name': ['Nicole'],
                               'Phone': ['212-683-2818'],
                               'Availability': [['2020-05-03', '2020-05-05']],
                               'Going to Stores': [['Target', 'Costco']]
                              })


import dash_html_components as html

def df_to_table(df):
    df = df.copy()

    for col in df.columns:
      if type(df[col][0]) == list:
        df[col] = df[col].apply(lambda row: '; '.join(row))

    return df.to_dict('records')
    
    # return html.Table(
    #     [html.Tr([html.Th(col) for col in df.columns])]
    #     + [
    #         html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
    #         for i in range(len(df))
    #     ]
    # )

