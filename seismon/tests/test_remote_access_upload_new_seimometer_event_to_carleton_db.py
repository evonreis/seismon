# Sample script to upload to Carleton Database


from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine  
import pandas as pd
from argparse import ArgumentParser
import datetime

from argparse import ArgumentParser
parser = ArgumentParser()


# if event already exists then 
if_exists_then = 'append' #{'append','replace'}


# Specify path csv file
db_catalogue_name = 'llo_catalogues' #{'llo_catalogues','lho_catalogues','virgo_catalogues'}

server = SSHTunnelForwarder(
    ('virgo.physics.carleton.edu', 22),
    ssh_username="nmukund",
    ssh_pkey="~/.ssh/id_rsa.pub",
    ssh_private_key_password="",
    remote_bind_address=('127.0.0.1', 5432))

server.start()
engine = create_engine(f'postgresql+psycopg2://seismon:seismon@{server.local_bind_address[0]}:{server.local_bind_address[1]}/seismon')


# Connect DataBase
conn = engine.connect()
print('Remote connection to Carleton database successful')


parser.add_argument( '--event_id', default='us20003j2v', type=str,help='unique ID assigned by USGS')
parser.add_argument( '--time', default='12-Sep-2015 20:32:26', type=str,help='EQ event time [UTC]')
parser.add_argument( '--created_at', default='Mon Jun 07 22:56:39  2021',type=str, help='created at [UTC]')
parser.add_argument( '--modified',   default='Mon Jun 07 22:56:39  2021',type=str, help='modified [UTC]')
parser.add_argument( '--place',   default='153km SSE of L\'Esperance Rock, New Zealand',type=str, help='EQ event location')
parser.add_argument( '--latitude', default=-32.6066, type=float,help='EQ latitude')
parser.add_argument( '--longitude', default=-178.0287, type=float, help='EQ longitude')
parser.add_argument( '--mag', default=5.9, type=float, help='EQ magnitude')
parser.add_argument( '--depth', default=8, type=float, help='EQ depthh [km]')
parser.add_argument( '--SNR', default=19.9, type=float, help='SNR of PeakAmplitude estimation')
parser.add_argument( '--peak_data_um_mean_subtracted', default=0.33, type=float, help='EQ estimated peak amplitude [um/s]')
args = parser.parse_args()


data_dict = {
    'event_id':[args.event_id],
    'time':[args.time],
    'created_at':[args.created_at],
    'modified':[args.modified],
    'place':[args.place],
    'latitude':[args.latitude],
    'longitude':[args.longitude],
    'mag':[args.mag],
    'depth':[args.depth],
    'SNR':[args.SNR],
    'peak_data_um_mean_subtracted':[args.peak_data_um_mean_subtracted]
    }
data_df_filtered = pd.DataFrame(data_dict)

"""
# OLD-testing
csv_file_path='../input/LLO_processed_USGS_global_EQ_catalogue.csv'
# load to dataframe from CSV file
data_df = pd.read_csv(csv_file_path)
# Select few columns [unique_id, peak_data_um-pers-sec_mean_subtracted]
data_df_filtered = data_df.filter(['id','time','place','latitude','longitude','mag','depth','SNR','peak_data_um_mean_subtracted'],axis=1)
data_df_filtered = data_df_filtered.rename(columns={'id':'event_id'})
# get current UTC time
created_at_value = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")
modified_value = datetime.datetime.utcnow().strftime("%a %b %d %H:%M:%S %Z %Y")
# add created_at &  modified time
data_df_filtered.insert(2,'created_at',created_at_value,True)
data_df_filtered.insert(3,'modified',modified_value,True)
# Only keep initial entries (to speed up the test)
data_df_filtered = data_df_filtered.loc[0:1,:]
"""


# upload dataframe remotely to database
data_df_filtered.to_sql('{}'.format(db_catalogue_name), con=engine,  if_exists=if_exists_then, index=False)

print('Remote upload successful')

# Check if things worked (load remotely)
print('Attempting to read table remotely...')
processed_catalogue_db = pd.read_sql_query('select * from public.{}'.format(db_catalogue_name),con=engine)
print(processed_catalogue_db)

# close connection
conn.close()