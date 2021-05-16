import copy
import random
import Person
from simulation.City import City
from simulation.Node import Node
from simulation.Type import Type, Infection
import numpy as np


class Simulation:
    def __init__(self, individuals, incubation, symptomatic, immunity, mortality, beacons, size_factor_city):
        self.elderly = []
        self.workers = []
        self.students = []
        self.immunity = immunity
        self.incubation = incubation
        self.symptomatic = symptomatic
        self.mortality = mortality
        self.infected = 0
        self.dead = 0
        self.immune = 0
        self.beacons = beacons
        self.population = self.generate_population(individuals)
        self.city = City(size_factor_city)
        self.generate_nodes()
        self.round = 0
        self.matrix_distance = None
        self.time_infection = 15 * 4  # 15 dies

    def generate_nodes(self):  # Our population is assigned
        # Workplaces
        count = self.create_assign_nodes(Type.WORKPLACE, self.workers, 20, 40, 0)

        # Homes
        count = self.create_assign_nodes(Type.HOME, self.population, 1, 5, count)

        # School
        count = self.create_assign_nodes(Type.SCHOOL, self.students, 100, 200, count)

        # Others
        self.create_assign_nodes(Type.OTHER, self.population, 50, 100, count)

    def generate_distance_matrix(self):
        nodesx = self.city.get_nodes()
        nodesy = self.city.others
        self.matrix_distance = np.zeros((len(nodesx), len(nodesy)))
        i = 0
        j = 0
        for nodex in nodesx:
            for nodey in nodesy:
                # CalcDistance
                aux2 = nodesy[nodey]
                aux1 = nodesx[nodex]
                distance = self.calc_distance(aux1, aux2)
                self.matrix_distance[i][j] = distance
                j += 1
            i += 1
            j = 0

    @staticmethod
    def calc_distance(node1, node2):
        return pow(pow((node1.x - node2.x), 2) + pow((node1.y - node2.y), 2), 0.5)

    def start_simulation(self):
        # Gen distance matrix
        self.generate_distance_matrix()
        # Move everyone to home
        for person in self.population:
            if person.home is not None:
                self.city.homes[person.home].add_person(person)
            else:
                print(person.id)
        self.round = 1

    def reduce_beacons_list(self):
        for person in self.population:
            for item in person.beacons:
                item['count'] -= 1
                if item['count'] <= 0:
                    person.beacons.remove(item)

    def advance_round(self):
        # calculate infec
        self.calculate_infections()
        self.run_agenda()
        self.round += 1
        if self.beacons:
            self.reduce_beacons_list()
        print("Infected people: " + str(self.infected))
        print("Dead people: " + str(self.dead))
        print("Immune people: " + str(self.immune))
        #print("Healthy people: " + str(sum(1 for p in self.population if p.infection is None)))
        #print("All people: " + str(self.infected + self.dead + self.immune + sum(1 for p in self.population if p.infection is None)))

    def calculate_infections(self):
        nodes = self.city.get_nodes()
        for node_aux in nodes:
            node = nodes[node_aux]
            self.calculate_infection_inside_node(node)

    def add_people_beacon(self, person, people_in_this_node):
        people_to_add = [p for p in people_in_this_node if p.id != person.id]
        aux_beacons_people = [p['person'] for p in person.beacons]
        for p_aux in people_to_add:
            if p_aux not in aux_beacons_people:
                person.beacons.append({'person': p_aux, 'count': copy.copy(self.incubation)})
            else:
                aux = [p for p in person.beacons if p['person'].id == p_aux.id]
                aux[0]['count'] = copy.copy(self.incubation)

    def calculate_infection_inside_node(self, node):
        # Itera sobre persones del node i infecta als que toqui
        # How many people occupy the room
        # Time
        # Tipus de lloc
        n_people = len(node.people_in_this_node)
        prob_infect = 0
        # Gather probability of getting infected
        for person in node.people_in_this_node:
            if person.infection is Infection.DEATH or person.infection is Infection.IMMUNE:
                continue
            self.detect_quarantine(person)
            self.detect_infected(person)
            state_person = person.infection
            if state_person == Infection.INCUBATION:
                prob_infect += 1
            elif state_person == Infection.INFECTION_SIMP:
                prob_infect += 2
            elif state_person == Infection.INFECTION_ASIMP:
                prob_infect += 1.5
            if self.beacons:
                self.add_people_beacon(person, node.people_in_this_node)

        if n_people != 0:
            if prob_infect > n_people:
                prob_infect = n_people
            prob_infect = (prob_infect / n_people) * 100  # Normalize to 1

            for person in node.people_in_this_node:
                if person.infection is None:
                    output = random.randint(0, 100)
                    if 0 <= output < prob_infect:
                        self.change_state(person)
                elif person.infection is not Infection.DEATH or person.infection is not Infection.IMMUNE:
                    person.time_start_infection += 1
                    self.change_state(person)
                # Process States of this person

    def detect_infected(self, person):
        if person.infection is Infection.INFECTION_SIMP and person.time_start_quarantine is None:
            if self.beacons:
                self.alert_people(person)
            person.set_quarantine()

    def detect_quarantine(self, person):
        if person.is_quarantine():
            if person.time_start_quarantine >= self.time_infection:
                person.init_agenda(person.type)
                self.change_state_person(person, Infection.IMMUNE)
                person.time_start_quarantine = None
            else:
                person.time_start_quarantine += 1

    def change_state_person(self, person, new_state):
        person.infection = new_state
        if new_state is Infection.INCUBATION:
            self.infected += 1
            person.time_start_infection = 0
        elif new_state is Infection.DEATH:
            self.dead += 1
            self.infected -= 1
        elif new_state is Infection.IMMUNE:
            self.immune += 1
            self.infected -= 1

    def change_state(self, person):
        # self.incubation = temps d'incubació
        if person.infection is Infection.INCUBATION:
            if person.time_start_infection >= self.incubation:
                # Change to infected (30% asimp 70% non asimp
                output = random.randint(0, 100)
                if 0 <= output < 30:
                    self.change_state_person(person, Infection.INFECTION_ASIMP)
                else:
                    self.change_state_person(person, Infection.INFECTION_SIMP)
        elif person.infection is None:
            self.change_state_person(person, Infection.INCUBATION)

        elif person.infection is Infection.INFECTION_SIMP:
            if person.time_start_infection >= self.incubation + self.time_infection:
                max_lim = self.mortality
                if person.type == 'elderly':
                    # Increment prob to die to 60%
                    max_lim = self.mortality * 2
                # Change to infected 10% death 90% alive
                output = random.randint(0, 100)
                if 0 <= output < max_lim:
                    self.change_state_person(person, Infection.DEATH)
                else:
                    self.change_state_person(person, Infection.IMMUNE)

        elif person.infection is Infection.INFECTION_ASIMP:
            if person.time_start_infection >= self.incubation + self.time_infection:
                self.change_state_person(person, Infection.IMMUNE)

    def run_agenda(self):
        nodes = self.city.get_nodes()
        for node_aux in nodes:
            node = nodes[node_aux]
            for person in node.people_in_this_node:
                move = self.round % 4
                node.people_in_this_node.remove(person)
                if person.agenda[move] == 'H':
                    self.city.homes[person.home].add_person(person)
                elif person.agenda[move] == 'W':
                    self.city.workplaces[person.workplace].add_person(person)
                elif person.agenda[move] == 'S':
                    self.city.schools[person.school].add_person(person)
                elif person.agenda[move] == 'R':
                    id_loc = node.id
                    aux = list(self.city.get_nodes().keys()).index(id_loc)
                    on_puc_anar_rec = self.matrix_distance[aux]
                    on_puc_anar_index = np.argsort(on_puc_anar_rec)
                    # Choose random 10
                    n = random.randint(0, 9)
                    key = list(self.city.others.keys())[on_puc_anar_index[n]]
                    node_dest = self.city.others[key]
                    node_dest.add_person(person)

    def create_assign_nodes(self, type_a, people, max_num, min_num, count):
        n_num_calc = int(len(people) / min_num) if int(len(people) / min_num) > 0 else 1  # set min to 1
        n_num_calc_max = int(len(people) / max_num) if int(len(people) / max_num) > 0 else 1  # set min to 1
        determine_num = random.randint(n_num_calc, n_num_calc_max)
        nodes = []
        for i in range(count, determine_num + count):
            node = Node(i, type_a)
            nodes.append(node)
        # Assigned people workplaces
        capacity = len(people) / len(nodes)
        count_people = 0
        for node in nodes:
            people_assignment = 0
            is_empty = True
            while people_assignment < int(capacity + 1) and count_people < len(people):
                if is_empty:
                    is_empty = False
                if type_a == Type.WORKPLACE:
                    people[count_people].set_workplace(node.id)
                elif type_a == Type.HOME:
                    people[count_people].set_home(node.id)
                elif type_a == Type.SCHOOL:
                    people[count_people].set_school(node.id)
                count_people += 1
                people_assignment += 1
            if not is_empty:
                self.city.add_node(type_a, node)
        return determine_num + count

    def generate_population(self, individuals):
        population = []
        i = 1
        while individuals > 0:
            rand = random.randint(0, 100)
            if 0 <= rand < 25:
                aux = Person.Person(i, 'student')
                self.students.append(aux)
            elif 25 <= rand < 80:
                aux = Person.Person(i, 'worker')
                self.workers.append(aux)
            else:
                aux = Person.Person(i, 'elderly')
                self.elderly.append(aux)
            self.assign_init_infection(aux)
            population.append(aux)

            individuals = individuals - 1
            i = i + 1
        return population

    def assign_init_infection(self, person):
        rand = random.randint(0, 100)
        if 0 <= rand < 5:
            person.infection = Infection.INCUBATION
            person.time_start_infection = 0
            self.infected += 1
        elif 5 <= rand < 10:
            person.infection = Infection.INFECTION_ASIMP
            person.time_start_infection = self.incubation
            self.infected += 1
        elif 10 <= rand < 10 + self.symptomatic:
            person.infection = Infection.INFECTION_SIMP
            person.time_start_infection = self.incubation
            self.infected += 1
        elif 10 + self.symptomatic <= rand < 10 + self.symptomatic + self.immunity:
            person.infection = Infection.IMMUNE
            self.immune += 1

    def alert_people(self, person):
        for item in person.beacons:
            if item['person'].infection is Infection.IMMUNE or item['person'].infection is Infection.DEATH:
                continue

            if not item['person'].is_quarantine():
                item['person'].set_quarantine()
            else:
                item['person'].time_start_quarantine = 0

            #Delete interaction
            for beacon in item['person'].beacons:
                if beacon['person'] == person:
                    item['person'].beacons.remove(beacon)

        #delete beacons tractat
        person.beacons = []

