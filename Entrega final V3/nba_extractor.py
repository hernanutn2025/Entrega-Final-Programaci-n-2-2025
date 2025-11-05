import pandas as pd
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from nba_api.stats.static import teams
from typing import Optional, List, Dict, Union

class NBADataExtractor:
    def __init__(self):
        print("NBADataExtractor inicializado.")
        pass

    def get_all_teams(self) -> Optional[List[Dict[str, Union[int, str]]]]:
        try:
            nba_teams = teams.get_teams()
            return nba_teams
        except Exception as e:
            print(f"Extractor Error: Fallo al obtener la lista de equipos: {e}")
            return None
        
