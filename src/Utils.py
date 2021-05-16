import simplejson as json

from simulation.Node import Node
from simulation.Person import Person
from simulation.Type import Type, Infection


def serialize_node(node):
    if node is None:
        return {}
    return {
        "type": str(node.type),
        "id": node.id,
        "people_in_this_node": serialize_people_node(node.people_in_this_node),
        "x": node.x,
        "y": node.y
    }

def serialize_people_node(people):
    res = []
    for person in people:
        val = {
            'id': person.id,
            'type': person.type,
            'agenda': json.dumps(person.agenda),
            'infection': str(person.infection),
            'time_start_infection': person.time_start_infection,
            'time_start_quarantine': person.time_start_quarantine,
            'beacons': serialize_beacons(person.beacons),
            'workplace': person.workplace,
            'home': person.home,
            'school': person.school
        }
        res.append(val)
    return res

def resum_persona(persona):
    return {
        'id': persona.id,
        'type': persona.type,
        'agenda': json.dumps(persona.agenda),
        'infection': str(persona.infection),
    }



def serialize_beacons(beacons):
    res = []
    for beacon in beacons:
        val = {
            'person': resum_persona(beacon['person']),
            'count': beacon['count']
        }
        res.append(val)
    return res

def de_serialize_node(data):
    new_type = data['type'].replace("Type.", "")
    node = Node(data['id'], Type[new_type])
    node.x = data['x']
    node.y = data['y']
    node.people_in_this_node = de_serialize_people(data['people_in_this_node'])
    return node

def de_serialize_people(data):
    res = []
    for person in data:
        pers = Person(person['id'], person['type'])
        pers.agenda = json.loads(person['agenda'])
        new_infection = person['infection'].replace("Infection.","")
        if new_infection != 'None':
            pers.infection = Infection[new_infection]
        else:
            pers.infection = None
        pers.time_start_infection = person['time_start_infection']
        pers.time_start_quarantine = person['time_start_quarantine']
        pers.beacons = json.loads(person['beacons'])
        pers.workplace = person['workplace']
        pers.home = person['home']
        pers.school = person['school']
        res.append(pers)
    return res