from fastapi import FastAPI
from sqlalchemy import *   
import datetime
from pydantic import BaseModel
import json

app = FastAPI()
connect_args = {'ssl':{'mode':'REQUIRED'}}
engine = create_engine('mysql+pymysql://avnadmin:AVNS_TTsiC2_1m5LG1Uh7112@robert-football-database2025-robertthuo2004-f295.i.aivencloud.com:26666/football_data',connect_args =  connect_args)
                # engine  = create_engine('mysql+pymysql://root:robert@localhost/football')
metadata = MetaData()
matches = Table('matches',  metadata,
                    Column('id', Integer, primary_key=True),
                    Column('league', String(255), nullable=False,default='Unknown League'),
                    Column('hometeam', String(255)),
                    Column('awayteam', String(255)),
                    Column('hometeam_logo', String(500)),
                    Column('awayteam_logo', String(500)),
                    Column('hometeam_goals', String(50)),
                    Column('awayteam_goals', String(50)),
                    Column('kickoff', Date),
                    Column('match_url', String(500)),
                    Column('match_completion', String(500)),
                    Column('stadium',String(500)),
                    Column('match_time', String(500)),
                    Column('game_time', String(500)),
                )
match_events = Table('match_events',  metadata,
                    Column('id', Integer, primary_key=True),
                    Column('match_id', Integer, ForeignKey('matches.id')),
                    Column('team', String(255)),
                    Column('minute', Integer),
                    Column('type', String(100)),
                    Column('player_in', String(255)),
                    Column('player_out', String(255)),
                    Column('scorer', String(255)),
                    Column('assist', String(255)),
                    Column('player', String(255)),
                )
match_stats = Table('match_stats',  metadata,
                    Column('id', Integer, primary_key=True),
                    Column('match_id', Integer, ForeignKey('matches.id')),
                    Column('possession_home', String(50)),
                    Column('possession_away', String(50)),
                    Column('total_shots_home', String(50)),
                    Column('total_shots_away', String(50)),
                    Column('shots_on_target_home', String(50)),
                    Column('shots_on_target_away', String(50)),
                    Column('duels_won_home', String(50)),
                    Column('duels_won_away', String(50)),
                )
match_lineups = Table('match_lineups',  metadata,
                    Column('id', Integer, primary_key=True),
                    Column('match_id', Integer, ForeignKey('matches.id')),
                    Column('team', String(255)),
                    Column('lineup', String(2000)),
                    Column('formation', String(50)),
                )  

league_table = Table(
            'league_table', metadata,
            Column('id', Integer, primary_key=True),
            Column('group', String(500), nullable=True, default='?'),
            Column('league', String(255), nullable=False, default='?'),
            Column('position', String(255), nullable=False, default='?'),
            Column('team', String(255), nullable=False, default='?'),
            Column('team_logo', String(255), nullable=True, default='?'),
            Column('matches_played', Integer, nullable=False, default=0),
            Column('matches_won', Integer, nullable=False, default=0),
            Column('matches_drawn', Integer, nullable=False, default=0),
            Column('matches_lost', Integer, nullable=False, default=0),
            Column('goals_diff', Integer, nullable=False, default=0),
            Column('points', Integer, nullable=False, default=0),
            Column('position_change', Integer, nullable=False, default=0),
        )
metadata.create_all(engine)
connection = engine.connect()
@app.get("/api/matches")
def root():
        Date = datetime.date.today()
        with engine.begin() as conn:
            results = conn.execute(
                select( matches).where( matches.c.kickoff == Date)
            )
        datas = []
        if results is None:
            return {'message':'No matches found'    }
        for res in results:
            data = {
                'id':res.id,
                'league':res.league,
                'hometeam':res.hometeam,
                'awayteam':res.awayteam,
                'hometeam_logo':res.hometeam_logo,
                'awayteam_logo':res.awayteam_logo,
                'hometeam_goals':res.hometeam_goals,
                'awayteam_goals':res.awayteam_goals,
                'kickoff':res.kickoff.strftime('%Y-%m-%d'),
                'match_url':res.match_url,
                'match_completion':res.match_completion,
                'stadium':res.stadium,
                'match_time':res.match_time,
                'game_time':res.game_time,
            
            }
            datas.append(data)
            json_datas = json.dumps(datas)
        return {'matches':datas}
        
@app.get("/api/matches/{date}")
def matches_by_date(date:str):
        Date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        with engine.begin() as conn:
            results = conn.execute(
                select(matches).where(matches.c.kickoff == Date)
            )
        datas = []
        if results is None:
            return {'message':'No matches found'    }
        for res in results:
            data = {
                'id':res.id,
                'league':res.league,
                'hometeam':res.hometeam,
                'awayteam':res.awayteam,
                'hometeam_logo':res.hometeam_logo,
                'awayteam_logo':res.awayteam_logo,
                'hometeam_goals':res.hometeam_goals,
                'awayteam_goals':res.awayteam_goals,
                'kickoff':res.kickoff.strftime('%Y-%m-%d'),
                'match_url':res.match_url,
                'match_completion':res.match_completion,
                'stadium':res.stadium,
                'match_time':res.match_time,
                'game_time':res.game_time,
            
            }
            datas.append(data)
        return {'matches':datas}
@app.get("/api/match/{id}")
def matches_by_id(id:int):
    global matches,match_events,match_stats,match_lineups
    
    with engine.begin() as conn:
            result_proxy = conn.execute(
                select(matches).where(matches.c.id == id)
            )
            database_match_events = conn.execute(
                select(match_events).where(match_events.c.match_id == id).order_by(match_events.c.minute)
            )
            database_match_stats = conn.execute(
                select(match_stats).where(match_stats.c.match_id == id).order_by(match_stats.c.id).limit(1)
            )
            database_match_lineups = conn.execute(
                select(match_lineups).where(match_lineups.c.match_id == id).order_by(match_lineups.c.id.desc()).limit(2
            )
            )
            result = result_proxy.first()
            if not result:
                return {'message':'No matches found'    }
            the_match_events = []
            if database_match_events:
                for event in database_match_events:
                    event = {
                        'team':event.team,
                        'minute':event.minute,
                        'type':event.type,
                        'player_in':event.player_in,
                        'player_out':event.player_out,
                        'scorer':event.scorer,
                        'assist':event.assist,
                        'player':event.player,
                    
                    }
                    the_match_events.append(event)
            else:
                the_match_events = []
            the_match_stats = {}
            stats_row = database_match_stats.first()
            if stats_row:
                the_match_stats = {
                    'possession_home':stats_row.possession_home,
                    'possession_away':stats_row.possession_away,
                    'total_shots_home':stats_row.total_shots_home,
                    'total_shots_away':stats_row.total_shots_away,
                    'shots_on_target_home':stats_row.shots_on_target_home,
                    'shots_on_target_away':stats_row.shots_on_target_away ,
                    'duels_won_home':stats_row.duels_won_home,
                    'duels_won_away':stats_row.duels_won_away,

                }
            else:
                the_match_stats = {}
            the_match_lineups = []
            if database_match_lineups.rowcount > 0:
                    for lineup in database_match_lineups:
                        team = lineup.team
                        the_lineup = json.loads(lineup.lineup) if lineup.lineup != 'no available lineup' else 'no available lineup'
                        formation = lineup.formation
                        team_match_lineups = {
                            'team':team,
                            'lineup':the_lineup,
                            'formation':formation
                        }
                        the_match_lineups.append(team_match_lineups)
            else:
                the_match_lineups = []
            
            match_data = {
                'id':result.id,
                'league':result.league,
                'hometeam':result.hometeam,
                'awayteam':result.awayteam,
                'hometeam_logo':result.hometeam_logo,
                'awayteam_logo':result.awayteam_logo,
                'hometeam_goals':result.hometeam_goals,
                'awayteam_goals':result.awayteam_goals,
                'kickoff':result.kickoff.strftime('%Y-%m-%d'),
                'match_url':result.match_url,
                'match_completion':result.match_completion,
                'stadium':result.stadium,
                'match_time':result.match_time,
                'game_time':result.game_time,
            
            }
    return {'match':{
            'match_data':match_data,
            'match_events':the_match_events,
            'match_stats':the_match_stats,
            'match_lineups':the_match_lineups,
        }}
    
@app.get('/api/league/{league}')
def matches_by_league(league:str):
    global matches,league_table
    with engine.begin() as conn:
            results = conn.execute(
                select(matches).where(and_(
                    matches.c.league == league  ,
                    matches.c.match_completion == 'Full time'
                )).order_by(matches.c.kickoff.desc()).limit(50)
            )
            fixtures = conn.execute(
                select(matches).where(and_(
                    matches.c.league == league  ,
                    matches.c.match_completion != 'Full time'
                )).order_by(matches.c.kickoff.asc()).limit(50)
            )
            league_table = conn.execute(
                select(league_table).where(league_table.c.league == league).order_by(league_table.c.position.desc())
            )
    datas = []
    the_fixtures = []
    the_league_table = []
    if results is None:
        datas = []
    if fixtures is None:
        the_fixtures = []
    if league_table is None:
        league_table = []
    
    for res in results:
            data = {
                'id':res.id,
                'league':res.league,
                'hometeam':res.hometeam,
                'awayteam':res.awayteam,
                'hometeam_logo':res.hometeam_logo,
                'awayteam_logo':res.awayteam_logo,
                'hometeam_goals':res.hometeam_goals,
                'awayteam_goals':res.awayteam_goals,
                'kickoff':res.kickoff.strftime('%Y-%m-%d'),
                'match_url':res.match_url,
                'match_completion':res.match_completion,
                'stadium':res.stadium,
                'match_time':res.match_time,
                'game_time':res.game_time,
            
            }
            datas.append(data)
    for row in fixtures:
            data = {
                'id':row.id,
                'league':row.league,
                'hometeam':row.hometeam,
                'awayteam':row.awayteam,
                'hometeam_logo':row.hometeam_logo,
                'awayteam_logo':row.awayteam_logo,
                'hometeam_goals':row.hometeam_goals,
                'awayteam_goals':row.awayteam_goals,
                'kickoff':row.kickoff.strftime('%Y-%m-%d'),
                'match_url':row.match_url,
                'match_completion':row.match_completion,
                'stadium':row.stadium,
                'match_time':row.match_time,
                'game_time':row.game_time,
            
            }
            the_fixtures.append(data)
    for row in league_table:
            data = {
                'group':row.group,
                'league':row.league,
                'position':row.position,
                'team':row.team,
                'team_logo':row.team_logo,
                'played':row.matches_played,
                'won':row.matches_won,
                'draw':row.matches_drawn,
                'lost':row.matches_lost,
                'goals_diff':row.goals_diff,
                'points':row.points,
                'position_change':row.position_change,
            }
            the_league_table.append(data)
    
    return {'league_info':{
        'league_table':the_league_table,
        'fixtures':the_fixtures,
        'results':datas
    }}