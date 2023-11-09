import boto3
import json
import yaml

{'account-blocklist': [123456789012], 'accounts': {'ACCOUNT': {'filters': {'S3Bucket': [{'invert': 'true', 'type': 'exact', 'value': 'nuke-account-cleanser-config-930842625961-eu-west-3-4519c290'}]}}}, 'regions': ['eu-west-3'], 'resource-types': {'targets': ['S3Bucket']}}

S3_OBJECT = "nuke_generic_config.yaml"
S3_BUCKET = "nuke-account-cleanser-930842625961-eu-west-3-41d1db50"

def lambda_handler(event, context):
    print("start")
    s3 = boto3.client("s3")
    resource = event["resource"]
    identifier = event["name"]
      
    try:
        # Download the file from S3
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_OBJECT)

        try:
            configfile = yaml.safe_load(response['Body'])
            print(configfile)
        except yaml.YAMLError as exc:
            return exc
    except Exception as e:
        print(f"Error: {e}")
    filter_resource = configfile["accounts"]["ACCOUNT"]["filters"]
    if resource in filter_resource.keys():
        to_append = {
                "invert": "false",
                "type": "exact",
                "value": identifier
            }
        filter_resource[resource].append(to_append)
    else:
        configfile["accounts"]["ACCOUNT"]["filters"][resource] = {
                "invert": "false",
                "type": "exact",
                "value": identifier
        }
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
