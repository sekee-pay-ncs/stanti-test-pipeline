#!/usr/bin/env python
# coding: utf-8

# # Generic preprocessing step for all VA models
# 
# 1. [R script](#Script)
# 2. [Docker](#Docker)
# 3. [Run Preprocessing job](#Run)

import boto3
import sagemaker
from sagemaker import get_execution_role

# ## Script
session = sagemaker.Session()
session.upload_data(path='docker_preprocess/preprocess.R', 
                    bucket='sagemaker-ap-southeast-1-361503357449', 
                    key_prefix='R-Processing-Script')


# configurable variables
account_id = boto3.client('sts').get_caller_identity().get('Account')
region = boto3.session.Session().region_name
ecr_repository = 'sagemaker-r-processing-general'
tag = ':latest'
uri_suffix = 'amazonaws.com'
processing_repository_uri = '{}.dkr.ecr.{}.{}/{}'.format(account_id, region, uri_suffix, ecr_repository + tag)

# ## Run
# configurable variables
from time import gmtime, strftime 
from sagemaker import get_execution_role

role = get_execution_role()
bucket = 'sagemaker-ap-southeast-1-361503357449'
s3_object = 'R-Processing-Input'
input_uri = 's3://{}/{}/data/raw/'.format(bucket, s3_object)
output_destination = 's3://{}/{}/data/raw/'.format(bucket, s3_object) # best to put in same folder

image_uri = processing_repository_uri
processing_instance_type = 'ml.t3.medium'
processing_job_name = "R-Processing-General-{}".format(strftime("%y-%m-%d-%H-%M-%S", gmtime()))
script_name = 's3://sagemaker-ap-southeast-1-361503357449/R-Processing-Script/preprocess.R' # use s3 uri to prevent multiple uploads and folder creations to S3


# In[10]:


from sagemaker.processing import ScriptProcessor, ProcessingInput, ProcessingOutput

script_processor = ScriptProcessor(command=['Rscript'],
                                   image_uri=image_uri,
                                   role=role,
                                   instance_count=1,
                                   instance_type=processing_instance_type)

script_processor.run(code=script_name,
                      job_name=processing_job_name,
                      inputs=[ProcessingInput(source=input_uri,
                                              destination='/opt/ml/processing/input')],
                      outputs=[ProcessingOutput(output_name='csv',
                                                source='/opt/ml/processing/output',
                                                destination=output_destination)]
                    )

preprocessing_job_description = script_processor.jobs[-1].describe()






