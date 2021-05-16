class Person:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.init_agenda(type)
        self.infection = None  # Incubació (asimptomatic), Infecció (asimptomatic o simptomàtic), Inmune, Mort
        self.time_start_infection = 0
        self.time_start_quarantine = 0
        self.beacons = []
        self.workplace = None
        self.home = None
        self.school = None

    def init_agenda(self, type):
        if type == 'student':
            self.agenda = ['H', 'S', 'R', 'H']
        elif type == 'worker':
            self.agenda = ['H', 'W', 'R', 'H']
        elif type == 'elderly':
            self.agenda = ['H', 'R', 'H', 'H']

    def set_workplace(self, workplace):
        self.workplace = workplace

    def set_home(self, home):
        self.home = home

    def set_school(self, school):
        self.school = school

    def set_quarantine(self):
        self.agenda = ['H', 'H', 'H', 'H']
        self.time_start_quarantine = 0

    def is_quarantine(self):
        return self.agenda == ['H', 'H', 'H', 'H']
