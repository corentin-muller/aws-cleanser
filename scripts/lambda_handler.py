import boto3
import json
import yaml

S3_OBJECT = "nuke_generic_config.yaml"
S3_BUCKET = "nuke-account-cleanser-930842625961-eu-west-3-41d1db50"

def lambda_handler(event, context):
    print("start")
    s3 = boto3.client("s3")

      
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

    region_clean = event["region"]
    resource_clean = event["resource"]
    service_name = event["name"]
    key = event["attribute"]
    
    configfile["regions"] = [region_clean]
    configfile["resource-types"] = {"targets": [resource_clean]}
    configfile["accounts"] = {
        "ACCOUNT": {
            "filters": {
                resource_clean: [{'property': key, 'value': service_name, 'invert': 'true'}]
            }
        }
    }
    print(configfile)
    config_output = yaml.dump(configfile)
    s3.put_object(
        Bucket=S3_BUCKET, 
        Key=S3_OBJECT,
        Body=config_output
    )
    sf = boto3.client('stepfunctions', region_name = 'eu-west-3')
    input_dict = {"InputPayLoad": {
        "nuke_dry_run": "true",
        "nuke_version": "v4.4",
        "region_list": [region_clean]
    }
    }
    response = sf.start_execution(
    stateMachineArn = 'arn:aws:states:eu-west-3:930842625961:stateMachine:aws-account-clean-codebuild-state-machine',
    input = json.dumps(input_dict))
    return 0
