#!/usr/bin/env python
# coding: utf-8

# # Using R in SageMaker Processing
# 
# Amazon SageMaker Processing is a capability of Amazon SageMaker that lets you easily run your preprocessing, postprocessing and model evaluation workloads on fully managed infrastructure. The workflow for using R with SageMaker Processing involves the following steps:
# 
# - Writing a R script.
# - Building a Docker container.
# - Creating a SageMaker Processing job.
# - Retrieving and viewing job results.  

import os
import argparse
import sys
import boto3
import sagemaker
from sagemaker import get_execution_role
from time import gmtime, strftime 
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

def process_data(
    country_to_run,
    account_id,
    region,
    role,
    data_dir
):
    '''
    Function to get docker image of country and create sagemaker processing job for country
    '''
    
    ecr_repository = 'sagemaker-r-processing-{}'.format(country_to_run)
    tag = ':latest'

    uri_suffix = 'amazonaws.com'
    processing_repository_uri = '{}.dkr.ecr.{}.{}/{}'.format(account_id, region, uri_suffix, ecr_repository + tag)
    image_uri = processing_repository_uri

    s3_object = 'stanti-test-pipeline'
    s3_object_data = 'DataFiles'
    s3_object_script = 'ProcessingScripts'
    s3_bucket = 'stanti-test-pipeline-artifact-ap-southeast-1-361503357449'

    processing_instance_type = 'ml.t3.medium'
    processing_job_name = "R-Processing-{}-{}".format(country_to_run.capitalize(), strftime("%y-%m-%d-%H-%M-%S", gmtime()))

    input_uri = 's3://{}/{}/{}/raw/'.format(s3_bucket, s3_object, s3_object_data)
    output_destination = 's3://{}/{}/{}/csv/{}'.format(s3_bucket, s3_object, s3_object_data, country_to_run)
    script_name = 's3://{}/{}/{}/{}_preprocess.R'.format(s3_bucket, se_object, s3_object_script, country_to_run)

    # ## Create SageMaker Processing job
    script_processor = ScriptProcessor(command=['Rscript'],
                                       image_uri=image_uri,
                                       role=role,
                                       instance_count=1,
                                       instance_type=processing_instance_type,
                                       volume_size_in_gb=1)

    script_processor.run(code=script_name,
                          job_name=processing_job_name,
                          inputs=[ProcessingInput(source=input_uri,
                                                  destination='/opt/ml/processing/input')],
                          outputs=[ProcessingOutput(destination=output_destination,
                                                    source='/opt/ml/processing/csv')]
                        )

    preprocessing_job_description = script_processor.jobs[-1].describe()

    # delete temp s3 objects created for datafiles
    s3 = boto3.resource('s3')
    bucket = s3.Bucket("sagemaker-{}-{}".format(region, account_id))
    bucket.objects.filter(Prefix=processing_job_name+"/").delete()
    
    return

def main(
    data_dir
):
    session = sagemaker.Session()
    role = get_execution_role()

    # configurable variables
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    region = boto3.session.Session().region_name
    
    # set country malaysia and run job
    country_to_run = 'malaysia'
    process_data(country_to_run, account_id, region, role, data_dir)
    
    #set country indonesia and run job
    country_to_run = 'indonesia'
    process_data(country_to_run, account_id, region, role, data_dir)
    
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load parameters")
    parser.add_argument("--data-dir", required=True)
    args = vars(parser.parse_args())
    print("args: {}".format(args))
    main(**args)














