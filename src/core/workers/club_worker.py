
import logging


from .base_worker import BaseWorker
from src.core.game_types import (
    StaffRole,
    Position
)

from src.core.db.models import (
    ClubDB,
    SeasonDB,
)

from src.core.db.game_worker import GameDBWorker



class ClubWorker(BaseWorker):

    def __init__(self, club_id: int, game_worker: GameDBWorker):
        super().__init__(game_worker=game_worker)
        self._club_id = club_id

        self._club = None

    @property
    def club_id(self):
        return self._club_id
    
    @club_id.setter
    def club_id(self, new_id):
        if new_id != self._club_id:
            self._club_id = new_id
            self.refresh()

    @property
    def club(self):
        if not self._club:
            self._club = self.game_worker.worker.get_club(self._club_id)
        return self._club
    

    def refresh(self):
        logging.info(f"Refreshing ClubWorker for club id {self.club_id}")
        self._club = None

        if self._club:
            pass


class AbilityCalculator:
    def __init__(self, abilities):
        self._abilities = abilities

    def analyse(self):
        count = len(self._abilities)
        max_a = max(self._abilities)
        avg_a = sum(self._abilities) / count
        avg_dev = sum([abs(avg_a - a) for a in self._abilities]) / count
        
        return avg_a, avg_dev, max_a


class ClubAnalysisWorker:

    def __init__(self, club: ClubDB):
        self._club = club

    @property
    def club(self):
        return self._club
    
    @club.setter
    def club(self, new_club: ClubDB):
        self._club = new_club

    def _get_manager(self, staff_members):
        managers = [s for s in staff_members if s.role == StaffRole.Manager]
        if managers:
            return managers[0]
        return None
    
    def _all_abilities(self, players):
        return [p.ability for p in players]
    
    # def _average_ability(self, players):
    #     return sum([p.ability for p in players]) / len(players)
    
    # def _average_ability_devation(self, players):
    #     all_abls = self._all_abilities(players)
    #     max_abl = max(all_abls)
    #     avg_dev = sum([max_abl - a for a in all_abls]) / len(players)
    #     return self._average_ability(players), avg_dev

    def _get_players_position_groups(self, players):
        player_dict = {p: [] for p in Position}
        for p in players:
            player_dict[p.position].append(p)

        for v in player_dict.values():
            v.sort(key=lambda x: x.ability, reverse=True)

        best_players = sorted([v[0] for v in player_dict.values() if v], key=lambda x: x.ability, reverse=True)
        best_player = best_players[0] if best_players else None
        return player_dict, best_player


    def get_team_sheet(self, position_groups, formation):
        positions = [Position.Goalkeeper, Position.Defender, Position.Midfielder, Position.Attacker]
        team = []

        counts = [v for v in formation.value]
        counts.insert(0, 1)

        team_players = []
        for pos, count in zip(positions, counts):

            if not position_groups[pos]:
                raise RuntimeError(f"No players for {pos.name}")
            
            plys = position_groups[pos]
            plys.sort(key=lambda x: x.ability, reverse=True)
            selected_plys = plys[0:count]

            team.append((pos, selected_plys))
            team_players.extend(selected_plys)

        sub_players = []
        for v in position_groups.values():
            sub_players.extend(v)
        for p in team_players:
            sub_players.remove(p)
        sub_players.sort(key=lambda x: x.ability, reverse=True)

        
        return team, sub_players[:3]
                
                


    def analyse(self, season: SeasonDB):
        logging.info(f"Analysing club: {self.club.name} season: {season}")
        data = {}

        
        data["club"] = self.club
        club = self.club
        if club:
            data["name"] = club.name
            data["club_id"] = club.id
            data["staff"] = club.staff_members()
            data["players"] = club.players()
            data["competitions"] = club.competitions(season=season)

            data["num_players"] = len(data["players"])

            data["manager"] = self._get_manager(data["staff"])
            data["manager_ability"] = data["manager"].ability
            data["formation"] = data["manager"].prefered_formation

            # avgs, deviation_avg = self._average_ability_devation(data["players"])
            avg_a, avg_dev, max_a = AbilityCalculator([p.ability for p in data["players"]]).analyse()
            data["squad"] = {
                "avg": avg_a,
                "d_avg": avg_dev,
                "max_a": max_a
            }

            player_positions, best_player = self._get_players_position_groups(data["players"])
            data["position_groups"] = player_positions
            data["best_player"] = best_player

            best_team = self.get_team_sheet(player_positions, data["formation"])
            best_team_players = []
            for r in best_team[0]:
                best_team_players.extend(r[1])
            b_avg, b_avg_d, b_max = AbilityCalculator([p.ability for p in best_team_players]).analyse()
            data["best_team"] = best_team
            data["team_analysis"] = b_avg, b_avg_d, b_max
            
            logging.info(f'Sqaud Avg: {data["squad"]["avg"]:2.2f} dev: {data["squad"]["d_avg"]:2.2f}')

        return data
    