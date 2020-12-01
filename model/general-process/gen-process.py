#!/usr/bin/env python
# coding: utf-8

# # Generic preprocessing step for all VA models
# 
# 1. [R script](#Script)
# 2. [Docker](#Docker)
# 3. [Run Preprocessing job](#Run)

import os
import argparse
import sys
import boto3
import sagemaker
from sagemaker import get_execution_role
from time import gmtime, strftime 
from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

def main(
    data_dir
):
    session = sagemaker.Session()

    # configurable variables for dkr image
    account_id = boto3.client('sts').get_caller_identity().get('Account')
    region = boto3.session.Session().region_name
    ecr_repository = 'sagemaker-r-processing-general'
    tag = ':latest'
    uri_suffix = 'amazonaws.com'
    processing_repository_uri = '{}.dkr.ecr.{}.{}/{}'.format(account_id, region, uri_suffix, ecr_repository + tag)
    image_uri = processing_repository_uri

    # configurable variables for input data
    role = get_execution_role()
    bucket = 'stanti-test-pipeline-artifact-ap-southeast-1-361503357449'
    s3_object = 'stanti-test-pipeline'
    input_uri = 's3://{}/{}/DataFiles/raw/'.format(bucket, s3_object)
    output_destination = 's3://{}/{}/DataFiles/raw/'.format(bucket, s3_object) # best to put in same folder

    processing_instance_type = 'ml.t3.medium'
    processing_job_name = "R-Processing-General-{}".format(strftime("%y-%m-%d-%H-%M-%S", gmtime()))
    script_name ='s3://stanti-test-pipeline-artifact-ap-southeast-1-361503357449/stanti-test-pipeline/ProcessingScripts/preprocess.R' # use s3 uri to prevent multiple uploads and folder creations to S3
    
    # run processing job
    script_processor = ScriptProcessor(command=['Rscript'],
                                       image_uri=image_uri,
                                       role=role,
                                       instance_count=1,
                                       instance_type=processing_instance_type)

    script_processor.run(code=script_name,
                          job_name=processing_job_name,
                          inputs=[ProcessingInput(source=data_dir,
                                                  destination='/opt/ml/processing/input')],
                          outputs=[ProcessingOutput(output_name='csv',
                                                    source='/opt/ml/processing/output',
                                                    destination=output_destination)]
                        )

    preprocessing_job_description = script_processor.jobs[-1].describe()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load parameters")
    parser.add_argument("--data-dir", required=True)
    args = vars(parser.parse_args())
    print("args: {}".format(args))
    main(**args)





