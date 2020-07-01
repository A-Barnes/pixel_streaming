import os
import json
import boto3

asg = boto3.client('autoscaling')
dynamodb = boto3.client('dynamodb')
INSTANCE_THRESHOLD = os.getenv('INSTANCE_THRESHOLD', 2)
ASG_NAME = os.getenv('ASG_NAME', 'sample-ue4-asg')
TABLE_NAME = os.getenv('TABLE_NAME', 'pixel_streaming')

def lambda_handler(event, context):
    
    pixel_asg = asg.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            ASG_NAME
        ]
    )
    print(pixel_asg)
    min_size = pixel_asg['AutoScalingGroups'][0]['MinSize']
    max_size = pixel_asg['AutoScalingGroups'][0]['MaxSize']
    desired = pixel_asg['AutoScalingGroups'][0]['DesiredCapacity']
    print(desired)
    
    pixel_ips = dynamodb.scan(
        TableName=TABLE_NAME,
        Limit=1
    )['Items']
    
    if len(pixel_ips) == 0:
        print("No instances available - provisioning more.")
        asg_upd = asg.update_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            MaxSize=max_size+INSTANCE_THRESHOLD,
            MinSize=min_size+INSTANCE_THRESHOLD,
            DesiredCapacity=desired+INSTANCE_THRESHOLD
        )
        return {
            'statusCode': 500,
            'body': "No instances available - provisioning more."
        }
    
    pixel_ip = pixel_ips[0]['ip_address']['S']
    entry_epoch = pixel_ips[0]['entry_epoch']['N']
        
    dynamodb.delete_item(
        TableName=TABLE_NAME,
        Key={
            'ip_address': {
                'S': pixel_ip
            },
            'entry_epoch': {
                'N': entry_epoch
            }
        }
    )

    #Scale out more instances
    if len(pixel_ips)-1 < INSTANCE_THRESHOLD:
        print("Scale more instances out")
        asg_upd = asg.update_auto_scaling_group(
            AutoScalingGroupName=ASG_NAME,
            MaxSize=max_size+INSTANCE_THRESHOLD,
            MinSize=min_size+INSTANCE_THRESHOLD,
            DesiredCapacity=desired+INSTANCE_THRESHOLD
        )

    return {
        'statusCode': 200,
        'body': json.dumps(pixel_ip)
    }
