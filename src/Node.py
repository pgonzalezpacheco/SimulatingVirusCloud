class Node:

    def __init__(self, id, type):
        self.type = type
        self.id = id
        self.people_in_this_node = []
        self.x = None
        self.y = None

    def assign_people(self, people):
        self.people_in_this_node = people

    def add_person(self, person):
        self.people_in_this_node.append(person)

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y
