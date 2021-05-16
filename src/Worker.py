import copy
import random
import time
import simulation.Utils as utils
import numpy as np

import simplejson as json

import boto3

from simulation.Person import Person
from simulation.Type import Infection

sqs = boto3.resource('sqs')
client_sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')


class Simulation:
    def __init__(self, id_simulacio, node):
        self.node = node
        self.sim_data = None
        self.id_simulacio = self.get_simulacio(id_simulacio)
        self.round = int(self.sim_data['round'])
        self.beacons = int(self.sim_data['beacons'])
        self.time_infection = int(self.sim_data['time_infection'])
        self.incubation = int(self.sim_data['incubation'])
        self.mortality = int(self.sim_data['mortality'])
        self.immunity = int(self.sim_data['immunity'])
        self.start_others = int(self.sim_data['start_other_places'])
        self.end_others = int(self.sim_data['end_other_places'])
        #Stats
        self.infected = 0
        self.dead = 0
        self.immune = 0


    def get_simulacio(self, id_simulacio):
        table = dynamodb.Table('Simulations')
        response = table.get_item(Key={'id': int(id_simulacio)})
        self.sim_data = response['Item']
        print('He trobat una simulacio')

    def save_stats_dynamodb(self):
        table = dynamodb.Table('Simulations')
        response = table.update_item(
            Key={
                'id': self.id_simulacio,
            },
            UpdateExpression="SET stats.infected = :inf + stats.infected, stats.dead = :dead + stats.dead, "
                             "stats.immune = :immune + stats.immune",
            ExpressionAttributeValues={
                ":inf": self.infected,
                ":dead": self.dead,
                ":immune": self.immune,
            },
            ReturnValues="NONE"
        )
        print(response)

    def save_node_dynamodb(self):
        table = dynamodb.Table("City1")
        resp = table.put_item(Item=utils.serialize_node(self.node))
        print(resp)


    def advance_round(self):
        # calculate infec
        self.calculate_infection_inside_node(self.node)
        self.run_agenda()
        self.round += 1
        if self.beacons:
            self.reduce_beacons_list()

        #Save Stats to dynamoDB (update simulation stats)
        #TODO REVISAR
        #self.save_stats_dynamodb()

        self.save_node_dynamodb()

        #Save node to dynamodb
        print("Infected people: " + str(self.infected))
        print("Dead people: " + str(self.dead))
        print("Immune people: " + str(self.immune))
        #print("Healthy people: " + str(sum(1 for p in self.population if p.infection is None)))
        #print("All people: " + str(self.infected + self.dead + self.immune + sum(1 for p in self.population if p.infection is None

    def run_agenda(self):
        for person in self.node.people_in_this_node:
            move = self.round % 4
            self.node.people_in_this_node.remove(person)
            if person.agenda[move] == 'H':
                self.add_person_remote_node(person, person.home)
            elif person.agenda[move] == 'W':
                self.add_person_remote_node(person, person.workplace)
            elif person.agenda[move] == 'S':
                self.add_person_remote_node(person, person.school)
            elif person.agenda[move] == 'R':
                n = random.randint(self.start_others, self.end_others)
                #N id to move
                self.add_person_remote_node(person, n)

    @staticmethod
    def add_person_remote_node(person, remote_node_id):
        table = dynamodb.Table('City1')
        person_ser = utils.serialize_people_node([person])[0]
        response = table.update_item(
            Key={
                'id': remote_node_id,
            },
            UpdateExpression="SET people_in_this_node = list_append(people_in_this_node, :val)",
            ExpressionAttributeValues={
                ":val": [person_ser]
            },
            ReturnValues="NONE"
        )
        print(response)


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

    def reduce_beacons_list(self):
        for person in self.node.people_in_this_node:
            for item in person.beacons:
                item['count'] -= 1
                if item['count'] <= 0:
                    person.beacons.remove(item)




def listen_jobs():
    queue = sqs.get_queue_by_name(QueueName='workers.fifo')
    while(True):
        response = client_sqs.receive_message(QueueUrl=queue.url, MessageAttributeNames=['All'], WaitTimeSeconds=20)
        if 'Messages' not in response:
            time.sleep(10)
        else:
            messages = response['Messages']
            if len(messages) == 0:
                time.sleep(10)
            else:
                sim = Simulation(messages[0]['MessageAttributes']['idSimulacio']['StringValue'],
                                 utils.de_serialize_node(json.loads(messages[0]['Body'])),)
                sim.advance_round()

if __name__ == "__main__":
    listen_jobs()



