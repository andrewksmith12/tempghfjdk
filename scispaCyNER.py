## This file handles all of the natural language processing via the Sci-Spacy libraries and models. The function createSpacyOutput gets called by a function in main.py. 


import pandas as pd
import spacy
from spacy import displacy
from spacy.pipeline import EntityRecognizer
from spacy.tokens import Token
import json
import os
import AWSfunctions

# Import Models
import en_ner_craft_md
import en_ner_bc5cdr_md
import en_ner_jnlpba_md
import en_ner_bionlp13cg_md

# Load nlp model
nlp_cr = en_ner_craft_md.load()
nlp_bc = en_ner_bc5cdr_md.load()
nlp_bi = en_ner_bionlp13cg_md.load()
nlp_jn = en_ner_jnlpba_md.load()
modelList = [nlp_bc, nlp_bi, nlp_jn] # List of the extra models being used here beyond the base model (which in this case is NLP_CR)

# Creates master document with all the entities from our models. 
def createDoc(text):
    doc = nlp_cr(text)
    print("nlp_cr")
    for ent in doc.ents:
        print(ent.text, ent.label_)
    for model in modelList:
        print('\n\n')
        print(model.meta['name'])
        extraDoc = model(text)
        try:
            for ent in extraDoc.ents:
                print(ent.text, ent.label_)
                doc.ents = list(doc.ents) + [ent]
            doc.ents = list(doc.ents) + list(extraDoc.ents)
        except ValueError as e:
            print("Erorr on: " + str(ent))
            continue
    return doc

# Parse the AWS file output and generate the lists used in further steps. 
def parseAWSOutput(file):
    tokenList = []
    timestampList = []
    for token in file['results']['items']:
        tokenList.append(token['alternatives'][0]['content'])
        timestampList.append(token["start_time"] if "start_time" in token.keys() else timestampList[-1])
    return file['jobName'], file['results']['transcripts'][0]['transcript'], tokenList, timestampList

# Adds the timestamps from the AWS transcription output into a custom spacy field. 
def addTimestamps(doc, awsTokens, awsTimestamps):
    Token.set_extension('timestamp', default=0, force=True)
    aws_counter = 0
    for item in doc:
        if str(item)[0] == awsTokens[aws_counter][0]:
            item._.set('timestamp', float(awsTimestamps[aws_counter]))
            aws_counter +=1
        elif str(item)[0] == awsTokens[aws_counter+1][0]:
                item._.set('timestamp', float(awsTimestamps[aws_counter]))
                aws_counter +=2
        else:
            item._.set('timestamp', float(awsTimestamps[aws_counter-1]))


# #Methods to add entity/value pairs to table for display
def createEntityDiagramHTML(doc):
    entityDiagramHTML = '<div class="entityDiagram">\n'
    for item in doc:
        if item.ent_type_ == "":
            entityDiagramHTML = entityDiagramHTML + '<a class="word" onclick="setCurrentTime('+"'"+str(item._.timestamp)+"')"+'" href="#">'+str(item) + item.whitespace_+'</a>'
        else:
            entityDiagramHTML = entityDiagramHTML + '\n   <mark class="entity '+item.ent_type_+'">'+'<a class="word" onclick="setCurrentTime('+"'"+str(item._.timestamp)+"')"+'" href="#">'+str(item) + item.whitespace_+'</a>'+'\n<span class="entityClass">'+item.ent_type_+'</span>\n  </mark>'
    entityDiagramHTML = entityDiagramHTML + '\n</div>'
    return entityDiagramHTML

# Main function, takes in the source transcript location and generates and puts the spacy NLP output into S3. 
def createSpacyOutput(sourceBucket, sourceKey, destinationBucket, prefix, mediaPrefix):
    file=AWSfunctions.get_file(bucket=sourceBucket, key=sourceKey)
    print(file)
    name, transcript, awsTokens, awsTimestamps = parseAWSOutput(file)
    doc = createDoc(transcript)
    addTimestamps(doc, awsTokens, awsTimestamps)   
    entityDiagram = createEntityDiagramHTML(doc)
    output = {'name':mediaPrefix+name, 'entityDiagram':entityDiagram}
    ofile = open(name+".json", 'w')
    ofile.write(json.dumps(output))
    ofile.close()
    print(AWSfunctions.upload_file(name+".json", destinationBucket, object_name=prefix+name+".json"))
    os.remove(name+".json") 
    return output

# print(createSpacyOutput('python-transcribe-target', '06_Whatcha_Gonna_Do_When_There_Aint.mp3.json', 'aks-spacy-destination'))