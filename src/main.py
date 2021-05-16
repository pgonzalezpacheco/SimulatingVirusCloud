import Simulation


def main():
    simulation = Simulation.Simulation(100, 2, 4, 14, 10, False, 100)
    for individual in simulation.population:
        print(str(individual.id)+" "+str(individual.type))


if __name__ == "__main__":
    main()
