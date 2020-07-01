import json
import boto3
from pprint import pprint
from datetime import datetime

dynamodb = boto3.client('dynamodb')
INSTANCE_THRESHOLD = os.getenv('INSTANCE_THRESHOLD', 2)
IDLE_THRESHOLD = os.getenv('IDLE_THRESHOLD', 300)
ASG_NAME = os.getenv('ASG_NAME', 'sample-ue4-asg')
TABLE_NAME = os.getenv('TABLE_NAME', 'pixel_streaming')

def lambda_handler(event, context):
    pprint(event)
    
    current_epoch_threshold = float(datetime.now().timestamp()) - IDLE_THRESHOLD
    
    old_servers = dynamodb.scan(
        TableName=TABLE_NAME,
        FilterExpression="entry_epoch < :current_epoch_threshold",
        ExpressionAttributeValues={
            ":current_epoch_threshold": { "N": str(current_epoch_threshold) },
        }
    )

    print(old_servers)
    removed_servers = []
    for server in old_servers['Items']:
        ip_address = server['ip_address']['S']

        delete_item = dynamodb.delete_item(
            TableName=TABLE_NAME,
            Key={
                'ip_address': {
                    'S': ip_address
                },
                'entry_epoch': {
                    'N': server['entry_epoch']['N']
                }
            }
        )
        
        removed_servers.append(ip_address)

    return {
        'statusCode': 200,
        'body': json.dumps(removed_servers)
    }

