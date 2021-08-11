from flask import Flask, render_template, session, request, redirect, url_for, escape
from flask_session import Session
import AWSfunctions
import os
import requests
from werkzeug.utils import secure_filename
# from scispaCyNER import createSpacyOutput
import pyperclip

uploads_bucket = "python-upload-target"
transcriptions_bucket = "python-transcribe-target"
spacy_bucket = "aks-spacy-destination"
import numpy as np

app = Flask(__name__)
Session(app)


@app.route('/updateSpacy')
def bulkSpacy():
    transcriptions = AWSfunctions.get_file_list(transcriptions_bucket)
    maps = AWSfunctions.get_file_list(spacy_bucket)
    transcriptKeys = []
    mapsKeys = []
    pyperclip.copy(str(transcriptions))
    print(transcriptions)
    for item in transcriptions:
        print(item["Key"])
        transcriptKeys.append(item['Key'])
    for item in maps:
        print(item["Key"])
        mapsKeys.append(item["Key"])
    needProcessing = set(transcriptKeys)-set(mapsKeys)
    print('\n\n')
    print(needProcessing)
    # for item in needProcessing:
    #     createSpacyOutput(transcriptions_bucket, item, spacy_bucket)
    return "hi"
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)