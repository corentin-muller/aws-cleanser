import boto3
import json
import yaml

S3_OBJECT = "nuke_generic_config.yaml"
S3_BUCKET = "nuke-account-cleanser-930842625961-eu-west-3-41d1db50"

def lambda_handler(event, context):
    print("start")
    s3 = boto3.client("s3")
    resource = event["resource"]
      
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
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
