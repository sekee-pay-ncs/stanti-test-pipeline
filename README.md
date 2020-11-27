# stanti-test-pipeline
stanti-test-pipeline

## Introduction

This is a sample solution to build a safe deployment pipeline for Amazon SageMaker.  This example could be useful for any organization looking to operationalize machine learning with native AWS development tools such as AWS CodePipeline, AWS CodeBuild and AWS CodeDeploy.

This solution provides as *safe* deployment by creating an AWS Lambda API that calls into an Amazon SageMaker Endpoint for real-time inference.

##  Architecture

Following is a diagram of the continuous delivery stages in the AWS Code Pipeline.

1. Build Artifacts: Runs a AWS CodeBuild job to create AWS CloudFormation templates.
2. Train: Trains an Amazon SageMaker pipeline and Baseline Processing Job
3. Deploy Dev: Deploys a development Amazon SageMaker Endpoint
4. Deploy Prod: Deploys an AWS API Gateway Lambda in front of Amazon SageMaker Endpoints using AWS CodeDeploy for blue/green deployment and rollback.
