
from simulation.Simulation import Simulation
import boto3
import simulation.Utils as utils


client = boto3.client('dynamodb')
dynamodb = boto3.resource('dynamodb')


def create_table_dynamodb():
    # Crear taula dynamodb
    response = client.create_table(
        TableName='City1',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            "WriteCapacityUnits": 10,
            "ReadCapacityUnits": 10
        }
    )
    print(response)


def store_city_dynamodb():
    city = allocate_city()
    # Write city content to dynamodb
    table = dynamodb.Table('City1')
    with table.batch_writer() as batch:
        for node in city.get_nodes().values():
            json_str = utils.serialize_node(node)
            print(json_str)
            batch.put_item(Item=json_str)

def save_simulation(simulation):
    table = dynamodb.Table("Simulations")
    table.put_item(Item={
        'id': 1,
        'max_rounds': 30*4,
        'immunity': simulation.immunity,
        'incubation': simulation.incubation,
        'symptomatic': simulation.symptomatic,
        'mortality': simulation.mortality,
        'beacons': simulation.beacons,
        'round': simulation.round,
        'time_infection': simulation.time_infection,
        'start_other_places': min(simulation.city.others, key=int),
        'end_other_places': max(simulation.city.others, key=int),
        'stats':{
            'dead': 0,
            'immune': 0,
            'infected': 0
        }
    })


def allocate_city():
    individuals = 2000
    incubation = 2
    symptomatic = 4
    immunity = 14
    mortality = 10
    beacons = True
    scale_city = 200
    simulation = Simulation(individuals, incubation, symptomatic, immunity, mortality, beacons, scale_city)
    save_simulation(simulation)
    simulation.start_simulation()
    return simulation.city

if __name__ == "__main__":
    create_table_dynamodb()
    store_city_dynamodb()
