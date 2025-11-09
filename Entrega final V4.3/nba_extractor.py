import pandas as pd
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
        
    def get_jugadores_por_equipo(self,team_name:str) -> Optional[list[dict[str,Union[int,str]]]]:
        
        id_equipos= None

        try:
            nba_equipos = teams.get_teams()
            info_equipo = next((team for team in nba_equipos if team["full_name"] == team_name),None)
            if info_equipo:
                id_equipos = info_equipo["id"]
            else:
                print(f"Extractor error: Equipo no encontrado: {team_name}")
                return None
        except Exception as e:
            print(f"Extractor error: Fallo al buscar el ID del equipo {e}")
            return None
        
        try:
            from nba_api.stats.endpoints import commonteamroster
            extraccion_jugadores = commonteamroster.CommonTeamRoster(team_id=id_equipos)  

            df = extraccion_jugadores.get_data_frames()[0]

            lista_jugadores=[]

            for index, row in df.iterrows():
                player_info = {
                    "name":row["PLAYER"],
                    "number": str(row['NUM']) if pd.notna(row['NUM']) else "N/A"}
                lista_jugadores.append(player_info)
            return lista_jugadores
        except Exception as e:
            print(f"Extractor error: Fallo al obtener el roster para {team_name}: {e}")    
        return None         