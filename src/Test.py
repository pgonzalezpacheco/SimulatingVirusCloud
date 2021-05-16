from simulation.Simulation import Simulation


def test():
    simulation = Simulation(20000, 2, 4, 14, 10, True, 200)
    simulation.start_simulation()
    while True:
        simulation.advance_round()


if __name__ == "__main__":
    test()
