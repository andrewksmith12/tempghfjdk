# Main flask program, all the functions in this demo are triggered from URL endpoints in this file. 

from flask import Flask, render_template, session, request, redirect, url_for, escape
from flask_session import Session
import spacy
import AWSfunctions
import os
from werkzeug.utils import secure_filename
from scispaCyNER import createSpacyOutput

# Static variables describing where the data is.
s3_bucket = "amat-single-bucket-pipeline"
source_prefix = "source/"
transcribe_prefix = "transcribe/"
spacy_prefix = "spacy/"

app = Flask(__name__)
Session(app)

# Allowed file extensions by the Transcribe API. 
ALLOWED_EXTENSIONS = ['mp3', 'mp4', 'flac', 'ogg', 'webm', 'amr', 'wav']
app.config['UPLOAD_FOLDER'] = 'uploads'

# Checks file extensions is allowed so that invalid files aren't put in S3. 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route('/')
# def index():
#     transcriptions = AWSfunctions.get_file_list(s3_bucket, transcribe_prefix)
#     maps = AWSfunctions.get_file_list(s3_bucket, spacy_prefix)
#     transcriptKeys = []
#     mapsKeys = []
#     for item in transcriptions:
#         print(item)
#         strKey = str(item["Key"]).strip(transcribe_prefix)
#         transcriptKeys.append(item['Key'])

#         # if strKey[0] != ".":
#     for item in maps:
#         print(item)
#         strKey = str(item['Key']).strip(spacy_prefix)
#         mapsKeys.append(item["Key"])
#     needProcessing = set(transcriptKeys)-set(mapsKeys)
#     for item in needProcessing:
#         print(item)
#         createSpacyOutput(s3_bucket, transcribe_prefix+item, s3_bucket, spacy_prefix, source_prefix)
#     linkFunction = "spacyItem"
#     return render_template('index.html', fileList = maps, prefix="s3://"+s3_bucket+spacy_prefix, linkFunction=linkFunction)

# Returns list of completed transcripts from Amazon Transcribe. 
@app.route('/transcribeList')
def transcribeList():
    items = AWSfunctions.get_file_list(s3_bucket, transcribe_prefix)
    linkFunction = "itemDetail"
    return render_template('transcribeList.html', fileList = items, prefix="s3://"+s3_bucket, linkFunction=linkFunction)

# Returns list of completed spacy transcripts. 
@app.route('/')
def index():
    items = AWSfunctions.get_file_list(s3_bucket, spacy_prefix)
    linkFunction = "spacyItem"
    return render_template('index.html', fileList = items, prefix="s3://"+s3_bucket, linkFunction=linkFunction)

# Returns amazon transcribe un-enritched transcript. 
@app.route('/itemDetail/'+transcribe_prefix+'/<string:id>', methods=['GET'])
def itemDetail(id):
    print(id)
    body = AWSfunctions.get_file(s3_bucket, transcribe_prefix+id)
    return render_template("itemDetail.html", body=body)

# Returns spacy enritched transcript. 
@app.route('/spacyOutput/'+spacy_prefix+'<string:id>', methods=['GET'])
def spacyItem(id):
    body = AWSfunctions.get_file(s3_bucket, spacy_prefix+id)
    title = cleanText(body["name"])
    mediaURL = AWSfunctions.getSignedURL(body['name'], s3_bucket)
    mediaType = body['name'].rsplit('.', 1)[1].lower()
    print(mediaType)
    return render_template('itemDetail-spaCy.html', body=body, mediaURL=mediaURL, mediaType=mediaType, title=title)

# Initiates the functions to create a spacy output, then redirects to the spacy item. 
@app.route('/createSpacy/'+transcribe_prefix+'<string:key>', methods=['GET'])
def createSpacy(key):
    createSpacyOutput(s3_bucket, transcribe_prefix+key, s3_bucket, spacy_prefix, source_prefix)
    return redirect(url_for('spacyItem', id=key))

# I'd rather not have this as a seperate function, but medical transcribe is weird. 
@app.route('/itemDetail/medical/<string:fileName>', methods=['GET'])
def parseMedicalKey(fileName):
    fileName = "medical/"+fileName
    body = AWSfunctions.get_file(s3_bucket, fileName)
    return render_template("itemDetail.html", body=body)

# Uploads file to s3 and starts transcription on said file. 
@app.route('/upload', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('uploadFile'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('uploadFile'))
        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            s3FileName = source_prefix+str(file.filename)
            AWSfunctions.upload_fileObject(file, s3_bucket, s3FileName)
            s3Location = str("s3://"+s3_bucket+"/"+s3FileName)
            transcribeOutputKey = transcribe_prefix+str(file.filename)+".json"
            result = AWSfunctions.create_transcript(s3Location, s3_bucket, transcribeOutputKey, str(file.filename))
            print(result)
            return redirect(url_for('index'))
        else:
            return "Invalid File."
    if request.method == 'GET':
        return render_template('uploadItem.html', allowedTypes = ALLOWED_EXTENSIONS)

# Cleans text for presentation purposes. 
def cleanText(text):
    text = text.replace('__', ': ')
    text = text.replace('_', ' ')
    return text

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)