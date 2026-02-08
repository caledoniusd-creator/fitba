from random import shuffle, randint

CLUB_NAMES = [
    "Red Lions",
    "AFC Tigers",
    "The Eagles",
    "Wolves",
    "Black Cats",
    "White Bulls",
    "Silverstone",
    "Dragonflies FC",
    "Purple Dragons",
    "Urban Rats",
    "Hawkshill Rovers",
    "Mountain Valley",
    "Riverside",
    "Forest FC",
    "Club Dolphins",
    "The Falcons",
    "Dark Valley",
    "The Iguanas",
    "The Coyotes",
    "Prairie Dogs FC",
    "Moongoose United",
    "The Stallions",
    "Redwood Rangers",
    "Trentishoe",
    "Cedar City FC",
    "Maple Leafs",
    "Oakwood Wanderers",
    "Pine Hill FC",
    "Birchwood United",
    "Willowbrook",
    "Ashford Athletic",
    "Elm City FC",
    "Hawthorn Rovers",
    "Sycamore Stars",
    "Chestnut Champions",
    "Poplar FC",
    "Cypress City",
    "Magnolia United",
    "Sequoia Strikers",
    "Juniper Jets",
    "Dogwood Dynamos",
    "Palm Beach FC",
    "Baobab Battalion",
    "Acacia Aces",
    "Eucalyptus Eagles",
    "Fir Fighters",
    "Hemlock Heroes",
    "Larch Legends",
    "Yew Youth",
    "Olive Olympians",
    "Cedarwood Cyclones",
    "Hickory Hawks",
    "Tamarack Titans",
    "Aspen Avengers",
    "Banyan Bears",
    "Catalpa Crusaders",
    "Ginkgo Giants",
    "City Spartans",
    "Metro Mariners",
    "Urban United",
    "Suburbia SC",
    "Downtown Dynamos",
    "Uptown United",
    "Central City FC",
    "Boston Devils",
    "Newcastle Nomads",
    "Liverpool Legends",
    "Manchester Mavericks",
    "Arsenal Attackers",
    "Chelsea Chargers",
    "Tottenham Titans",
    "Brighton Blaze",
    "Southampton Snipers",
    "Westham Warriors",
    "Everton Elite",
    "Fulham Flyers",
    "Crystal Palace Panthers",
    "Brentford Bullets",
    "Luton Lions",
    "Aston Villa Victors",
    "Wolverhampton Wanderers",
    "Ipswich Italics",
    "Leicester Legends",
    "Leeds Lancers",
    "Sheffield Steel",
    "Nottingham Nobles",
    "Derby Defenders",
    "Coventry Corsairs",
    "Stoke Strikers",
    "Sunderland Surge",
    "Norwich Navigators",
]


class Squad:
    @staticmethod
    def random():
        return Squad(randint(50, 200))

    def __init__(self, rating: int):
        self.rating = rating

    def __str__(self):
        return f"Squad: {self.rating:3d}"


class Club:
    def __init__(self, name, squad):
        self.name = name
        self.squad = squad

    def __str__(self):
        return f"Club: {self.name}"


class ClubFactory:
    @staticmethod
    def create_club(name):
        return Club(name, Squad.random())

    @staticmethod
    def create_clubs(count: int):
        names = list(CLUB_NAMES)
        shuffle(names)
        names = names[:count]
        return [Club(name, Squad.random()) for name in names]


class ClubPool:
    def __init__(self):
        self.clubs = set()

    def add_club(self, club: Club):
        self.clubs.add(club)

    def remove_club(self, club: Club):
        self.clubs.discard(club)

    def get_all_clubs(self):
        return list(self.clubs)

    @property
    def count(self):
        return len(self.clubs)
