############################################################################ IMPORTS ############################################################################ 


import statsapi
# from nba_api.stats.endpoints._base import Endpoint
# from nba_api.stats.library.http import NBAStatsHTTP
# from nba_api.stats.library.parameters import (
#     LeagueID,
#     Season,
#     SeasonType,
#     SeasonNullable,
# )
# import pynhlapi
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String 
import pprint
import requests
from datetime import datetime
import time
import re
import time
import json
import numpy as np
import pandas as pd
# from nba_api.stats.endpoints import playercareerstats


############################################################################ SEASONS DATA ############################################################################ 

pp = pprint.PrettyPrinter(indent=2)

Base = declarative_base()

class Seasons():

    mlb_data = {}
    nhl_data = {}
    nba_data = {}

    def __init__(self, unique_id, league_id, start_date, end_date):
        self.unique_id = 0
        self.league_id = None
        self.start_date = None
        self.end_date = None

    def mlb_seasons(self):
        all_seasons = {}

        all_seasons['2020'] = statsapi.get('seasons', {'sportId':1, 'season':2020})
        time.sleep(2)
        all_seasons['2021'] = statsapi.get('seasons', {'sportId':1, 'season':2021})
        time.sleep(2)
        all_seasons['2022'] = statsapi.get('seasons', {'sportId':1, 'season':2022})
        time.sleep(2)
        all_seasons['2023'] = statsapi.get('seasons', {'sportId':1, 'season':2023})
        time.sleep(2)
        all_seasons['2024'] = statsapi.get('seasons', {'sportId':1, 'season':2024})

        for season, all_data in all_seasons.items():
            #unique_id: iterate by one, league_id assisgn 1  
            self.unique_id += 1
            unique_id = self.unique_id
            seasons_dates = all_data['seasons']
            for season in seasons_dates:
                Seasons.mlb_data[unique_id] = season

        # Remove unnecessary data and change names of fields 
        for unique_id, item in Seasons.mlb_data.items():
            item['league_id'] = 1
            item['unique_id'] = unique_id
            del item['seasonLevelGamedayType']
            del item['gameLevelGamedayType']
            del item['qualifierPlateAppearances']
            del item['qualifierOutsPitched']
            del item['hasWildcard']
            del item['offSeasonEndDate']
            del item['offseasonStartDate']
            del item['regularSeasonEndDate']
            del item['regularSeasonStartDate']
            del item['preSeasonEndDate']
            del item['lastDate1stHalf']
            item['season_years'] = item.pop('seasonId')
            item['spring_start'] = item.pop('springStartDate')
            item['spring_end'] = item.pop('springEndDate')
            item['season_start'] = item.pop('seasonStartDate')
            item['season_end'] = item.pop('seasonEndDate')
            item['second_half_start'] = item.pop('firstDate2ndHalf')
            item['post_season_start'] = item.pop('postSeasonStartDate')
            item['post_season_end'] = item.pop('postSeasonEndDate')
            item['pre_season_start'] = item.pop('preSeasonStartDate')

    def nba_seasons(self):
        all_seasons = {}
        years = [2020, 2021, 2022, 2023, 2024]
        for i, year in enumerate(years):
            all_seasons[i+6] = {
                'unique_id': i+6,
                'league_id': 2,
                'season_start': year,
                'season_end': year + 1,
                'season_years': f'{year}-{year+1}'
            }
        Seasons.nba_data = all_seasons

    # Function to convert string to datetime for nhl
    def convert(date_time):
        format = "%Y-%m-%dT%H:%M:%S"
        datetime_str = datetime.strptime(date_time, format)

        return datetime_str 
    
    def nhl_seasons(self):
        all_seasons = {}
        nhl_seasons = requests.get('https://api.nhle.com/stats/rest/en/season').json()
        id_start = 10
        for i, seasons in nhl_seasons.items():
            if i == 'data':
                sorted_seasons = sorted(seasons, key = lambda x: x['id'])
                seasons_needed = ['2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
                # for i, season in enumerate(seasons[102:108]):
                for season_listitem in seasons_needed:
                    for i, season in enumerate(sorted_seasons):
                        if season['formattedSeasonId'] in seasons_needed:
                            if season['formattedSeasonId'] == season_listitem:
                                id_start += 1
                            if type(season['preseasonStartdate']) == str:
                                preseason_start = Seasons.convert(season['preseasonStartdate'])
                            else:
                                preseason_start = season['preseasonStartdate']
                            if type(season['startDate']) == str:
                                season_start = Seasons.convert(season['startDate'])
                            else:
                                season_start = season['startDate']
                            if type(season['regularSeasonEndDate']) == str:
                                season_end = Seasons.convert(season['regularSeasonEndDate'])
                            else:
                                season_end = season['regularSeasonEndDate']
                            all_seasons[id_start] = {
                                'unique_id': id_start,
                                'league_id': 3,
                                'season_years': season['formattedSeasonId'],
                                'pre_season_start':preseason_start,
                                'season_start': season_start,
                                'season_end': season_end
                            }
            Seasons.nhl_data = all_seasons
        pp.pprint(Seasons.nhl_data)

############################################################################ SEASONS TABLE ############################################################################ 
class Seasons_Table(Base):

    all_leagues = {}

    # Create seasons table in sports_stats database
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key = True) 
    league_id = Column(Integer)
    season_years = Column(String)
    spring_start = Column(String)
    spring_end = Column(String)
    pre_season_start = Column(String)
    season_start = Column(String)
    season_end = Column(String)
    second_half_start = Column(String)
    post_season_start = Column(String)
    post_season_end = Column(String)
    
    def get_all_leagues():
    # Function to combine mlb_date, nba_data, and nhl_data
        Seasons_Table.all_leagues = Seasons.mlb_data.copy()
        new_nba = Seasons.nba_data.copy()
        new_nhl = Seasons.nhl_data.copy()
        merges = Seasons_Table.all_leagues.update(new_nba)
        merges2 = Seasons_Table.all_leagues.update(new_nhl)

        for index, data in Seasons_Table.all_leagues.items():
            for key, value in data.items():
                if key == 'unique_id' or key == 'league_id':
                    data[key] = int(value)

    # Function to add values to seasons table
    def data_to_table(session):
        for index, item in Seasons_Table.all_leagues.items():
                if 'spring_start' not in item:
                    item['spring_start'] = None
                if 'spring_end' not in item:
                    item['spring_end'] = None 
                if 'second_half_start' not in item:
                    item['second_half_start'] = None
                if 'pre_season_start' not in item:
                    item['pre_season_start'] = None 
                if 'post_season_start' not in item:
                    item['post_season_start'] = None
                if 'post_season_end' not in item: 
                    item['post_season_end'] = None 

                new_row = Seasons_Table (
                    id = item['unique_id'],
                    league_id = item['league_id'],
                    season_years = item['season_years'],
                    spring_start = item['spring_start'],
                    spring_end = item['spring_end'],
                    pre_season_start = item['pre_season_start'],
                    season_start = item['season_start'],
                    season_end = item['season_end'],
                    second_half_start = item['second_half_start'],
                    post_season_start = item['post_season_start'],
                    post_season_end = item['post_season_end']
                )
                session.add(new_row)

############################################################################ TEAMS DATA ############################################################################ 

class Teams():
    
    #class level dictionaries
    mlb_team_data = {}
    nhl_team_data = {}
    nba_team_data = {}

    def __init__(self, id, league_name, div_name, total_teams):
        self.unique_id = 0

    def mlb_league(self):
        standings_data = statsapi.standings_data(leagueId="103, 104", division="all")
        for league_index, all_data in standings_data.items():
            league_id = 1
            league = 'MLB'
            conference = (' '.join(all_data['div_name'].split()[:2]))
            division = (all_data['div_name'])

            for x in all_data['teams']:
                team_name = x['name']
                #cities: keep first word or keep first two words, change state teams to thier respective cities
                state_teams = ['Texas Rangers', 'Arizona Diamondbacks', 'Colorado Rockies', 'Minnesota Twins']
                two_word_city_teams = ['New York Yankees', 'Tampa Bay Rays',  'Kansas City Royals', 'Los Angeles Angels','New York Mets', 'St. Louis Cardinals', 'Los Angeles Dodgers', 'San Diego Padres','San Francisco Giants']
                if team_name in state_teams:
                    if team_name == 'Texas Rangers':
                        city = 'Dallas'
                    if team_name == 'Arizona Diamondbacks':
                        city = 'Phoenix'
                    if team_name == 'Colorado Rockies':
                        city = 'Denver'
                    if team_name == 'Minnesota Twins':
                        city = 'Minneapolis'
                elif team_name in two_word_city_teams:
                    city = ' '.join(team_name.split()[:2])
                else:
                    city = ''.join(team_name.split()[:1])
                self.unique_id += 1
                id = self.unique_id
                Teams.mlb_team_data[id] = {
                    'team': team_name,
                    'city': city, 
                    'league_id': league_id,
                    'league': league,
                    'conference': conference,
                    'division': division,
                }
        
    def nba_league(self, game_date=None):

        # url = 'https://stats.nba.com/stats/leaguestandingsv3'
        url = 'https://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season=2024-25&SeasonType=Regular+Season&SeasonYear='

        headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Accept': 'application/json, text/plain, */*',
        'x-nba-stats-token': 'true',
        'X-NewRelic-ID': 'VQECWF5UChAHUlNTBwgBVw==',
        'DNT': '1', 
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Origin': 'https://www.nba.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.nba.com/',
        'x-nba-stats-origin': 'stats',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '1',
        'sec-ch-ua-platform': "Android"   
        }
        
        response = requests.get(url=url, headers=headers).json()

        # Serializing json
        json_object = json.dumps(response, indent=4)
        with open("nba_2024.json", "w") as outfile:
            outfile.write(json_object)
                       
        with open('nba_2024.json') as f:
            d = json.load(f)
            results_set = d['resultSets']
        
        for result in results_set:
            list_item = (result['rowSet'])
            for item in list_item:
                self.unique_id += 1
                id = self.unique_id 
                Teams.nba_team_data[id] = {
                    'league': 'NBA',
                    'league_id': 2, 
                    'city': item[3],
                    'team': item[4],
                    'conference': item[6],
                    'division' : item[10]
                }

    def nhl_league(self):
        url = "https://api.sportradar.com/nhl/trial/v7/en/league/hierarchy.json?api_key=VyXaDhbMXnVcAwoOcJoJlzr3TXLjikgTCkPlatVM"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers).json()
        json_object = json.dumps(response, indent=4)
        
        with open('nhl_divisions.json', 'w') as outfile:
            outfile.write(json_object)

        with open('nhl_divisions.json') as read_file:
            nhl_leagues = json.load(read_file)
            league = nhl_leagues['league']['name']
            conferences = nhl_leagues['conferences']
        
        for x in conferences:
            conference = x['name']
            divisions = x['divisions']
            for dic in divisions:
                division = dic['name']
                for team in dic['teams']:
                    city = team['market']
                    team_name = team['name']
                    self.unique_id += 1
                    id = self.unique_id
                    Teams.nhl_team_data[id] = {
                        'league': league,
                        'league_id':3,
                        'conference': conference,
                        'division': division,
                        'city': city,
                        'team': team_name
                    }

############################################################################ TEAMS TABLE ############################################################################ 
class Teams_Table(Base):
    
    # Merge data from three dictionaries together
    all_teams = {}

    # Create teams table in sports_stats database
    __tablename__ = 'teams'

    id = Column(Integer, primary_key = True)
    league_id = Column(Integer)
    city = Column(String)
    team = Column(String)
    division = Column(String)
    conference = Column(String)

    def get_all_teams():
        Teams_Table.all_teams = Teams.mlb_team_data.copy()
        new_nba = Teams.nba_team_data.copy()
        new_nhl = Teams.nhl_team_data.copy()
        merges = Teams_Table.all_teams.update(new_nba)
        merges2 = Teams_Table.all_teams.update(new_nhl)

        for index, data in Teams_Table.all_teams.items():
            for key, value in data.items():
                if key == 'league_id':
                    data[key] = int(value)

    def data_to_table(session):
        for index, item in Teams_Table.all_teams.items():
            new_row = Teams_Table (
            id = index,
            league_id = item['league_id'],
            team = item['team'],
            city = item['city'],
            division = item['division'],
            conference = item['conference']
            )
            session.add(new_row)
        
############################################################################ LEAGUES DATA ############################################################################ 
            
class Leagues():

    #class level dictionary
    league_data = {}

    def __init__(self, id, league_name, total_teams, total_conferences, total_divisions):
        self.id = 0
        self.league_name = None 
        self.total_teams = None
        self.total_conferences = None 
        self.total_divisions = None 
    
    def mlb_league(self):
        standings_data = statsapi.standings_data(leagueId="103, 104", division="all")
        conferences = []
        divisions = []
        teams = [] 
        for league_index, all_data in standings_data.items():
            conference = (' '.join(all_data['div_name'].split()[:2]))
            if conference not in conferences:
                conferences.append(conference)
            division = (all_data['div_name'])
            if division not in divisions:
                divisions.append(division)
            for x in all_data['teams']:
                team_name = x['name']
                teams.append(team_name)
        self.id += 1
        Leagues.league_data[self.id] = {
            'league':'mlb',
            'total_conferences': len(conferences),
            'total_divisions': len(divisions),
            'total_teams': len(teams)
        }

    def nba_league(self):
        
        teams = []
        conferences = []
        divisions = []

        with open('nba_2024.json') as f:
            d = json.load(f)
            results_set = d['resultSets']
        
        for result in results_set:
            list_item = (result['rowSet'])
            for item in list_item:
                team = item[4]
                division = item[10]
                conference = item[6]
                teams.append(team)
                if conference not in conferences:
                    conferences.append(conference)
                if division not in divisions:
                    divisions.append(division)

        self.id += 1 
        Leagues.league_data[self.id] = {
            'league':'nba',
            'total_conferences': len(conferences),
            'total_divisions': len(divisions),
            'total_teams': len(teams)
        }

    def nhl_league(self):

        team_list = []
        conference_list = []
        division_list = []
        
        with open('nhl_divisions.json') as f:
            nhl_leagues = json.load(f)
            conference = nhl_leagues['conferences']

        for x in conference:
            conference = x['name']
            conference_list.append(conference)
            div_data = x['divisions']
            for x in div_data:
                division = x['name']
                division_list.append(division)
                teams = x['teams']
                for team in teams:
                    name = team['name']
                    team_list.append(name)
        
        self.id += 1
        Leagues.league_data[self.id] = {
            'league': 'nhl',
            'total_conferences': len(conference_list),
            'total_divisions': len(division_list),
            'total_teams': len(team_list)
        }

############################################################################ LEAGUES TABLE ############################################################################ 

class Leagues_Table(Base):
    
    __tablename__ = 'leagues'

    id = Column(Integer, primary_key = True)
    league = Column(String)
    total_conferences = Column(Integer)
    total_divisions = Column(Integer)
    total_teams = Column(Integer)

    def data_to_table(session):
        for index, item in Leagues.league_data.items():
            new_row = Leagues_Table (
                id = index,
                league = item['league'],
                total_conferences = item['total_conferences'],
                total_divisions = item['total_divisions'],
                total_teams = item['total_teams']
            )
            session.add(new_row)

############################################################################ STANDINGS DATA ############################################################################ 

class Standings():

    standings_data = {}

    def __init__(self, id, league_id, season_id, team_id, wins, lossess, div_rank, conference_rank, league_rank):
        id = 0 
        league_id = None 
        season_id = 0
        team_id = None 
        wins = None
        lossess = None 
        div_rank = None 
        conference_rank = None 
        league_rank = None

    def mlb_standings(self):
        seasons = [2020, 2021, 2022, 2023, 2024]

        for season in seasons:
            if f'mlb_standings_{season}' not in locals():
                standings_data = statsapi.standings_data(leagueId="103,104", division="all", season=season)
                json_object = json.dumps(standings_data, indent=4)

                with open(f'standings/mlb/mlb_standings_{season}', 'w') as outfile:
                    outfile.write(json_object)
        
        for season in seasons:
            with open(f'standings/mlb/mlb_standings_{season}') as read_file:
                mlb_data = json.load(read_file)

            #for each season, find team_name w, and l 
            for index, all_data in mlb_data.items():
                conference = all_data['div_name']
                teams = all_data['teams']
                for team in teams:
                    league_id = 1
                    for key, value in Teams_Table.all_teams.items():
                        if team['name'] == value['team']:
                            team_id = key
                    for key, value in Seasons_Table.all_leagues.items():
                        if league_id == value['league_id'] and season == int(value['season_years']):
                                season_id = key 
                    # Ensure the nested structure exists
                    Standings.standings_data.setdefault('mlb', {}).setdefault(season, {})
                    Standings.standings_data['mlb'][season][team['name']] = {
                            'league_id': league_id,
                            'team_id': team_id,
                            'season_id': season_id, 
                            'wins':team['w'],
                            'losses': team['l'],
                            'div_rank': team['div_rank'],
                            'conference_rank': team['league_rank'],
                            'league_rank': team['sport_rank']
                    }        
    
    def nba_standings(self):
        
        seasons = ['2020-21','2021-22','2022-23','2023-24','2024-25']

        for season in seasons:
            if f'nba_stands_{season}' not in locals():
                url = f'https://stats.nba.com/stats/leaguestandings?LeagueID=00&Season={season}&SeasonType=Regular+Season&SeasonYear='

                headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Accept': 'application/json, text/plain, */*',
                'x-nba-stats-token': 'true',
                'X-NewRelic-ID': 'VQECWF5UChAHUlNTBwgBVw==',
                'DNT': '1', 
                'Connection': 'keep-alive',
                'Host': 'stats.nba.com',
                'Origin': 'https://www.nba.com',
                'Pragma': 'no-cache',
                'Referer': 'https://www.nba.com/',
                'x-nba-stats-origin': 'stats',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
                'sec-ch-ua-mobile': '1',
                'sec-ch-ua-platform': "Android"   
                }
                
                response = requests.get(url=url, headers=headers, timeout=30).json()

                # Serializing json
                json_object = json.dumps(response, indent=4)
                with open(f'standings/nba/nba_standings_{season}.json', "w") as outfile:
                    outfile.write(json_object)
            
        for season in seasons:
            with open(f'standings/nba/nba_standings_{season}.json') as read_file:
                nba_data = json.load(read_file)
                results_set = nba_data['resultSets']
                league_id = 2
                for result in results_set:
                    list_item = (result['rowSet'])
                    for item in list_item:
                        for key, value in Teams_Table.all_teams.items():
                            if item[4] == value['team']: 
                                team_id = key
                        for key, value in Seasons_Table.all_leagues.items():
                            short_year = value['season_years'][:5] + value['season_years'][7:]
                            if league_id == value['league_id'] and season == short_year:
                                season_id = key 
                    # Ensure the nested structure exists
                        Standings.standings_data.setdefault('nba', {}).setdefault(season, {})
                        Standings.standings_data['nba'][season][item[4]] = {
                            'league_id': league_id, 
                            'team_id': team_id,
                            'season_id': season_id,
                            'wins': item[12],
                            'losses': item[13],
                            'div_rank': item[11],
                            'conference_rank': None,
                            'league_rank': item[15]
                }
                
    def nhl_standings(self):

        seasons = ['2020', '2021', '2022', '2023', '2024']

        for season in seasons:
            url = f"https://api.sportradar.com/nhl/trial/v7/en/seasons/{season}/REG/standings.json?api_key=VyXaDhbMXnVcAwoOcJoJlzr3TXLjikgTCkPlatVM"
            headers = {"accept": "application/json"}
            response = requests.get(url, headers=headers).json()
            time.sleep(30)

            # Serializing json
            json_object = json.dumps(response, indent=4)
            with open(f'standings/nhl/nhl_standings_{season}.json', 'w') as outfile:
                outfile.write(json_object)
        
        for season in seasons:
            
            with open(f'standings/nhl/nhl_standings_{season}.json') as read_file:
                nhl_data = json.load(read_file)
                conferences = nhl_data['conferences']
                league_id = 3
                for conference in conferences:
                    divisions = conference['divisions']
                    for division in divisions:
                        teams = division['teams']
                        for team in teams:
                            wins = team['wins']
                            losses = team['losses']
                            div_rank = team['rank']['division']
                            conf_rank = team['rank']['conference']
                            team_name = team['name']
                            for key, value in Teams_Table.all_teams.items():
                                if team['name'] == value['team']:
                                    team_id = key            
                            for key, value in Seasons_Table.all_leagues.items():
                                if league_id == value['league_id'] and season == value['season_years'][:4]:
                                    season_id = key
                            # Ensure the nested structure exists
                            Standings.standings_data.setdefault('nhl', {}).setdefault(season, {})
                            Standings.standings_data['nhl'][season][team_name] = {
                                'league_id': league_id,
                                'team_id': team_id,
                                'season_id': season_id,
                                'wins': wins,
                                'losses': losses,
                                'div_rank': div_rank,
                                'conference_rank': conf_rank,
                                'league_rank': None 
                            }

############################################################################ STANDINGS TABLE ############################################################################ 

class Standings_Table(Base):

    __tablename__ = 'standings'

    id = Column(Integer, primary_key = True)
    league_id = Column(Integer)
    season_id = Column(Integer)
    team_id = Column(Integer)
    league_rank = Column(Integer) 
    div_rank = Column(Integer)
    conference_rank = Column(Integer)
    wins = Column(Integer)
    losses = Column(Integer)

    def data_to_table(session):
        count = 0 
        for league, seasons in Standings.standings_data.items():
            for season, teams in seasons.items():
                for team, standings in teams.items():
                    count += 1
                    new_row = Standings_Table (
                        id = count,
                        league_id = standings['league_id'],
                        season_id = standings['season_id'],
                        team_id = standings['team_id'],
                        league_rank = standings['league_rank'],
                        div_rank = standings['div_rank'],
                        conference_rank = standings['conference_rank'],
                        wins = standings['wins'],
                        losses = standings['losses']
                    )
                    session.add(new_row)
