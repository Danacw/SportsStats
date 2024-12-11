from models import Seasons, Seasons_Table, Base, Teams, Teams_Table, Leagues, Leagues_Table, Standings, Standings_Table 
import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import db_user, db_password, db_host, db_name, db_port


pp = pprint.PrettyPrinter(indent=2)

############################################# SEASONS DATA CLASS ############################################ 

season_instance = Seasons(None, None, None, None)
season_instance.mlb_seasons()
season_instance.nba_seasons()
season_instance.nhl_seasons()

############################################# SEASONS TABLE CLASS ############################################ 
 
# Merge data from three dictionaries together
Seasons_Table.get_all_leagues()

# Set up engine and session through SQL alchemy
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', echo=True)
Seasons_Table.__table__.drop(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Commit and insert data
Seasons_Table.data_to_table(session)
session.commit()
print("SUCCESS")

######################################### TEAMS DATA CLASS ############################################ 
teams_instance = Teams(None, None, None, None)
teams_instance.mlb_league()
teams_instance.nba_league()
teams_instance.nhl_league() 

########################################## TEAMS TABLE CLASS ############################################ 
# Merge data from three dictionaries together
Teams_Table.get_all_teams()

# Set up engine and session through SQL alchemy
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', echo=True)
Teams_Table.__table__.drop(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Commit and insert data
Teams_Table.data_to_table(session)
session.commit()
print("SUCCESS")

########################################## LEAGUES DATA CLASS ############################################ 
leagues_instance = Leagues(None, None, None, None, None)
leagues_instance.mlb_league()
leagues_instance.nba_league()
leagues_instance.nhl_league()

########################################## LEAGUES TABLE CLASS ############################################ 

# Set up engine and session through SQL alchemy
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', echo=True)
Leagues_Table.__table__.drop(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Commit and insert data
Leagues_Table.data_to_table(session)
session.commit()
print("SUCCESS")

########################################## STANDINGS DATA CLASS ############################################ 
standings_instance = Standings(None, None, None, None, None, None, None, None, None)
standings_instance.mlb_standings()
standings_instance.nba_standings()
standings_instance.nhl_standings()

########################################## STANDINGS TABLE CLASS ############################################ 

# Set up engine and session through SQL alchemy
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}', echo=True)
Standings_Table.__table__.drop(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Commit and insert data
Standings_Table.data_to_table(session)
session.commit()
print("SUCCESS")
