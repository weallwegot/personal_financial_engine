"""
Module for orchestrating the deployment of various AWS
programs

Variables:
    ALIAS -- name of the branch to deploy from
    RESOURCE_ROLE -- aws arn for the role of the resource
"""
import configparser
import json
import logging
import subprocess
import sys


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)


def deploy_s3_frontend(stage):
    """
    deply front end pages static html
    """
    BUCKETPATHS = {"master": "s3://financial-engine-frontend",
                   "develop": "s3://staging-financial-engine-frontend",
                   "CI-test-alias": "s3://staging-financial-engine-frontend"}
    bashCommand = "bash CI/aws-s3-deploy.sh {bucket}".format(bucket=BUCKETPATHS[stage])

    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if error:
        logging.error(error)


def is_func_new(funcname):
    """
    determine if function being deployed is brand new or just needs updates
    """
    bashCommand = "aws lambda get-function \
    --function-name {fname}".format(
        fname=funcname
    )

    try:
        subprocess.check_output(bashCommand.split())
    except subprocess.CalledProcessError as e:
        # if the error is raised it means the functions does not exist
        logging.error(e)
        print("returning True")
        return True
    print("returning False")
    return False


def deploy_lambda(new, folder_name):
    """
    ISNEW=$1
    RESOURCE_ROLE=$2
    ALIAS=$3

    FNAME=$4
    HANDLER=$5
    TIMEOUT=$6
    MEMSIZE=$7
    DESC=$8
    ENV=$9
    RUNTIME=${10}
    REGION=${11}
    FOLDER_NAME=${12}
    """
    bashCommand = "bash CI/aws-lambda-deploy.sh \
    {isnew} \
    {AWS_LAMBDA_ROLE} \
    {alias} \
    {funcname} {handler} {timeout} {memsize} '{desc}' '{env}' '{runtime}' '{region}' {folder_name}".format(
        AWS_LAMBDA_ROLE=RESOURCE_ROLE,
        isnew=new,
        alias=ALIAS,
        funcname=CONFIG_PARAMS['function-name'],
        desc=CONFIG_PARAMS['description'],
        runtime=CONFIG_PARAMS['runtime'],
        handler=CONFIG_PARAMS['handler'],
        region=CONFIG_PARAMS['region'],
        timeout=CONFIG_PARAMS['timeout'],
        memsize=CONFIG_PARAMS['memory-size'],
        env=VARS_STR,
        folder_name=folder_name)

    process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    # print(output)
    if error:
        logging.error(error)

LAMBDAS2DEPLOY = ["budget-handler", "compute-forecast", "projected-totals"]

# read parameters passed into the script
ALIAS = sys.argv[1]
RESOURCE_ROLE = sys.argv[2]


cfg = configparser.ConfigParser()
# override the automatic lower casing of variables read in
cfg.optionxform = str
cfg.read('deployment_config.ini')

# loop through each lambda to deploy

for folder_name in LAMBDAS2DEPLOY:

    LOGGER.info(f"deploying {folder_name}")

    # parse lambda configuration parameters
    CONFIG_PARAMS = {}
    for config_tuple in cfg.items(f'configuration-{folder_name}'):
        name = config_tuple[0]
        val = config_tuple[1]
        CONFIG_PARAMS[name] = val

    # https://stackoverflow.com/questions/5466451/how-can-i-print-literal-curly-brace-characters-in-python-string-and-also-use-fo#5466478
    VARS_STR_TEMPLATE = "Variables={{{}}}"
    env_vars = ""
    for config_tuple in cfg.items(f'environment-{folder_name}'):
        env_vars += "{k}={v},".format(k=config_tuple[0], v=config_tuple[1])

    if env_vars.endswith(","):
        env_vars = env_vars[:-1]
    VARS_STR = VARS_STR_TEMPLATE.format(env_vars)
    LOGGER.info(f"Parsed environment variables:\n{VARS_STR}")

    deploy_lambda(new=is_func_new(CONFIG_PARAMS['function-name']), folder_name=folder_name)

deploy_s3_frontend(stage=ALIAS)
