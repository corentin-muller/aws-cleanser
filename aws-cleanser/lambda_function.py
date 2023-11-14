import boto3
import json
import yaml

S3_OBJECT = "nuke_delete.yaml"
S3_BUCKET = "nuke-account-cleanser-930842625961-eu-west-3-41d1db50"


def lambda_handler(event, context):
    """
    Trigger step function to delete provided resource
    :param event
    :param context

    :returns: 0
    """
    configfile = {"account-blocklist": ["999999999999"]}
    s3 = boto3.client("s3")

    region_clean = event.get("region", "eu-west-3")
    resource_clean = event["resource"]
    service_name = event["name"]
    dry_run = event.get("dry_run", "true")
    version = event.get("version", "8.1")

    configfile["regions"] = [region_clean]
    configfile["resource-types"] = {"targets": [resource_clean]}
    configfile["accounts"] = {
        "ACCOUNT": {
            "filters": {
                resource_clean: [
                    {"type": "exact", "value": service_name, "invert": "true"}
                ]
            }
        }
    }
    print(configfile)
    config_output = yaml.dump(configfile)
    s3.put_object(Bucket=S3_BUCKET, Key=S3_OBJECT, Body=config_output)
    sf = boto3.client("stepfunctions", region_name="eu-west-3")
    input_dict = {
        "InputPayLoad": {
            "invocation_type": "lambda",
            "nuke_dry_run": dry_run,
            "nuke_version": version,
            "region_list": [region_clean],
        }
    }
    response = sf.start_execution(
        stateMachineArn="arn:aws:states:eu-west-3:930842625961:stateMachine:aws-account-clean-codebuild-state-machine",
        input=json.dumps(input_dict),
    )
    return 0
