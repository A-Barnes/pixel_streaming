import json
import boto3
from pprint import pprint
from datetime import datetime

dynamodb = boto3.client('dynamodb')
ec2 = boto3.client('ec2')
INSTANCE_THRESHOLD = os.getenv('INSTANCE_THRESHOLD', 2)
TABLE_NAME = os.getenv('TABLE_NAME', 'pixel_streaming')

def lambda_handler(event, context):
    
    pprint(event['Records'])

    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    
    print(sns_message['EC2InstanceId'])
    instance_id = sns_message['EC2InstanceId']

    instances = ec2.describe_instances(
        InstanceIds=[instance_id]
    )
    
    if sns_message['Event'] == "autoscaling:EC2_INSTANCE_LAUNCH":
        print(
            instances['Reservations'][0]['Instances'][0]['PublicIpAddress']
        )
        public_ip = instances['Reservations'][0]['Instances'][0]['PublicIpAddress']

        print("Creating new instance")
    
        put_item = dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "ip_address": {
                    "S": public_ip
                },
                "entry_epoch": {
                    "N": str(datetime.now().timestamp())
                }
            }
        )
        print(put_item)
        
        return {
            'statusCode': 200
        }
    else:
        #Unsupported operation
        return {
            'statusCode': 500,
            'body': json.dumps('Unsupported operation')
        }
