import random

from simulation.Type import Type


class City:

    def __init__(self, size):
        self.workplaces = {}
        self.homes = {}
        self.schools = {}
        self.others = {}
        self.size = size
        #Calc dimension
        self.dimx = size / 2
        self.dimy = size / 2
        if size % 2 != 0:
            if bool(random.getrandbits(1)):
                self.dimx += 1
            else:
                self.dimy += 1

    def add_node(self, type_a, node):
        if type_a == Type.HOME:
            self.homes[node.id] = node
        elif type_a == Type.SCHOOL:
            self.schools[node.id] = node
        elif type_a == Type.WORKPLACE:
            self.workplaces[node.id] = node
        else:
            self.others[node.id] = node
        #Assign dim
        node.set_x(random.randint(0, self.dimx-1))
        node.set_y(random.randint(0, self.dimy-1))

    def get_nodes(self):
        nodes = {}
        nodes.update(self.homes)
        nodes.update(self.others)
        nodes.update(self.workplaces)
        nodes.update(self.schools)
        return nodes
