# A collection of functions that use the boto3 library to interact with AWS services such as transcribe and S3 as needed by the other python files. 

import boto3
import logging
import ast
import os
from botocore.exceptions import ClientError
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')
# uploads_bucket = "python-upload-target"
# transcriptions_bucket = "python-transcribe-target"

# Takes in a local file name, uploads to a target S3 bucket. 
def upload_file(file, bucket, object_name=None):
    if object_name==None:
        object_name=file
    try:
        response = s3.upload_file(Filename=file, Bucket=bucket, Key=object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return response

# Takes in a python file object and puts it in the target s3 bucket with the provided object name/key. 
def upload_fileObject(file, bucket, object_name):
    try:
        response = s3.upload_fileobj(
            file, bucket, object_name
        )
        print(response)
    except ClientError as e:
        print(e)
        logging.error(e)
        return False
    return response

# Gets a URL to download the file requested via a Singed URL. Used to allowing access to source files for display in the output. 
def getSignedURL(key, bucket):
    try:
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=3600)
    except ClientError as e:
        logging.error(e)
        return False
    return url

# Starts transcription job given S3 information for input and output. 
def create_transcript(source, bucket, outputKey, job_name=None):
    if job_name==None:
        job_name=source
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaSampleRateHertz=44100,
            MediaFormat=source.rsplit('.', 1)[1].lower(),
            Media={
                'MediaFileUri':source
            },
            OutputBucketName=bucket,
            OutputKey=outputKey
            )
        print(response)
    except ClientError as e:
        logging.error(e)
        print(e)
        return False
    return response

# A modified version of the above create_transcript function that uses a custom model (just an extra parameter)
def create_transcript_custom(source, bucket, job_name=None):
    if job_name==None:
        job_name=source
    try:
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaSampleRateHertz=44100,
            MediaFormat=source.rsplit('.', 1)[1].lower(),
            Media={
                'MediaFileUri':source
            },
            ModelSettings={
                'LanguageModelName': "aks-oncology"
            },
            OutputBucketName=bucket
            )
    except ClientError as e:
        logging.error(e)
        return False
    return response

# A modified version of the above create_transcript function that uses medical transcribe. This has a different API endpoint. 
def create_transcript_medical(source, bucket, job_name=None):
    if job_name==None:
        job_name=source
    try:
        response = transcribe.start_medical_transcription_job(
            MedicalTranscriptionJobName=job_name,
            LanguageCode='en-US',
            MediaSampleRateHertz=44100,
            MediaFormat=source.rsplit('.', 1)[1].lower(),
            Media={
                'MediaFileUri':source
            },
            OutputBucketName=bucket,
            Specialty="PRIMARYCARE",
            Type="CONVERSATION"
            )
    except ClientError as e:
        logging.error(e)
        return False
    return response

# Gets file list from S3 with a given prefix and bucket name. 
def get_file_list(s3Bucket, prefix):
    try:
        response = s3.list_objects_v2(
            Bucket=s3Bucket,
            Prefix=prefix
        )
        print(response)
        itemList = []
        for item in response["Contents"]:
            itemList.append(item)
        return itemList
    except ClientError as e:
        logging.log(e)
        return False

# Returns file from s3 given bucket and key. 
def get_file(bucket, key):
    try:
        response = s3.get_object(
            Bucket=bucket, 
            Key=key
        )
        body = ast.literal_eval(response['Body'].read().decode('utf-8'))
    except ClientError as e:
        logging.log(e)
        return False
    return body
# print(upload_file("us_accent_cancer.mp3", uploads_bucket))
# print(create_transcript_medical("s3://aks-learning-2021/us_accent_cancer.mp3", transcriptions_bucket, "python-transcribe-medical"))
# print(create_transcript("s3://aks-learning-2021/us_accent_cancer.mp3", transcriptions_bucket, "python-transcribe-normal"))
# response = get_file(transcriptions_bucket, "python-transcribe-normal.json")
# # print(response)
# body = ast.literal_eval(response['Body'].read().decode('utf-8'))
# print(type(body))
# for item in body['results']['items']:
#     # if item['type'] == "pronunciation":
#     #     print(item['alternatives'][0]['content'], end=" ")
#     # else:
#     #     print(item['alternatives'][0]['content'], end="")
#     print(item)
# for item in body['items']:
#     print(item)

# print(get_file_list("python-transcribe-target", "medical/"))