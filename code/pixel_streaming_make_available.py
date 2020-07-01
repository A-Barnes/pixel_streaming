import json
import boto3
import os
from datetime import datetime
from pprint import pprint

dynamodb = boto3.client('dynamodb')
TABLE_NAME = os.getenv('TABLE_NAME', 'pixel_streaming')

def lambda_handler(event, context):
    
    print(event)
    
    ip_address = event['ip_address']
    
    dynamodb.put_item(
        Key={
            'ip_address': {
                'S': ip_address
            },
            'entry_epoch': {
                'N': str(datetime.now().timestamp())
            }
        }
    )
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('IP Address added')
    }

