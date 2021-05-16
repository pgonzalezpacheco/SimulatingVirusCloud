import simplejson as json
import time
import boto3

sqs = boto3.resource('sqs')
client_sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

def wait_until_queue_end(url):
    end = False
    while not end:
        time.sleep(10)
        response = client_sqs.get_queue_attributes(QueueUrl=url, AttributeNames=['ApproximateNumberOfMessages'])
        n_messages = int(response['Attributes']['ApproximateNumberOfMessages'])
        end = n_messages == 0



def retrieve_nodes(tableName):
    finish = False
    items = []
    start_key = None
    table = dynamodb.Table(tableName)
    while not finish:
        if start_key:
            response = table.scan(ExclusiveStartKey=start_key)
        else:
            response = table.scan()
        items.extend(response['Items'])
        if 'LastEvaluatedKey' not in response:
            finish = True
        else:
            start_key = response['LastEvaluatedKey']
    return items

def run_round(params):
    queue = sqs.get_queue_by_name(QueueName='workers.fifo')
    nodes = retrieve_nodes(params['city'])
    contador = 0
    for node in nodes:
        #Jobs
        response = queue.send_message(MessageBody=json.dumps(node),
                                      MessageDeduplicationId=str(params['idSimulacio']) + '_' + str(contador)
                                      ,MessageGroupId='workers', MessageAttributes={
            'idSimulacio': {
                'StringValue': str(params['idSimulacio']),
                'DataType': 'String'
            }
        })
        contador += 1
        print(response)
    wait_until_queue_end(queue.url)
    # Update dynamo round number



def start_simulation(params):
    #Info de la simulació (n maxim rondes)
    table = dynamodb.Table('Simulations')
    response = table.get_item(Key={'id': params['idSimulacio']})
    simParams = response['Item']
    for i in range(0, int(simParams['max_rounds'])):
        run_round(params)
        response = table.update_item(
            Key={
                'id': params['idSimulacio'],
            },
            UpdateExpression="ADD round",
            ReturnValues="NONE"
        )
        print(response)







if __name__ == "__main__":
    params = {}
    params['city'] = "City1"
    params['idSimulacio'] = 1
    start_simulation(params)
