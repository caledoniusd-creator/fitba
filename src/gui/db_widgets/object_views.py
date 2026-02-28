from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


from .generic_widgets import TitledTreeWidget, TitledListWidget


class StaffTreeWidget(TitledTreeWidget):
    def __init__(self, parent=None):
        super().__init__(title="Staff", parent=parent)
        self.tree.setHeaderLabels(
            ["Role", "Name", "Ability", "Reputation", "Personality"]
        )

    def set_staff(self, staff_list):
        self.tree.clear()
        for staff in staff_list:
            item = QTreeWidgetItem(
                [
                    staff.role.name,
                    staff.person.full_name,
                    str(staff.ability),
                    staff.reputation_type.name,
                    staff.person.personality.name,
                ]
            )
            self.tree.addTopLevelItem(item)


class PlayerTreeWidget(TitledTreeWidget):
    def __init__(self, parent=None):
        super().__init__(title="Players", parent=parent)
        self.tree.setHeaderLabels(["Position", "Name", "Ability", "Personality"])

    def set_players(self, player_list):
        self.tree.clear()
        for player in player_list:
            item = QTreeWidgetItem(
                [
                    player.position.name,
                    player.person.full_name,
                    str(player.ability),
                    player.person.personality.name,
                ]
            )
            self.tree.addTopLevelItem(item)


class CompetitionListWidget(TitledListWidget):
    def __init__(self, parent=None):
        super().__init__(title="Competitions", parent=parent)

    def set_competitions(self, comp_list):
        self.list_widget.clear()
        for comp in comp_list:
            item = QListWidgetItem(comp.name)
            item.setData(Qt.UserRole, comp)
            self.list_widget.addItem(item)
