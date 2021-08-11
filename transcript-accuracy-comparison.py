# import main
import os
import glob
import requests
import AWSfunctions
import pyperclip
from jiwer import wer
# os.chdir('youtube-files/source-truth')
# output = ""
# fileList = []
# for file in glob.glob("*.txt"):
#     fileList.append(file)
# fileList.sort()
# print(fileList)


# uploads_bucket = "python-upload-target"
# medical_transcriptions_bucket = "python-medical-transcribe"

# items = AWSfunctions.get_file_list(uploads_bucket)
# for item in items:
#     print(item['Key'])
#     s3Location = str("s3://"+uploads_bucket+"/"+item['Key'])
#     r = AWSfunctions.create_transcript_custom(s3Location, medical_transcriptions_bucket, item["Key"]+"-customModel")
#     print(r)
bucket1 = "python-transcribe-target"
bucket2 = "python-medical-transcribe"

transcribe = [
'Artificial_Intelligence__the_future_of_Cancer_Distinguished_Lecture___University_of_Southampton-rMDllCXnlBE.mp3.json',
'Breast_Cancer_101_-_Our_Oncologists_Answer_Questions_On_Breast_Cancer-3nR3ByevwyY.mp4.json',
'Immunotherapy_to_treat_cancer_-_Expert_QA-Ttsj4k_ByPI.mp3.json',
'Keynote_Address_How_can_we_introduce_innovative_treatments_into_publicly_funded_healthcare_systems_D-iSmRnWn4Ib4.mp4.json',
'Learn_all_about_PARP_inhibitors_with_Dr_Jon_Krell_Consultant_Medical_Oncologist-i8Gy5OQMAlE.mp4.json',
'Nanomaterials_for_Cancer_therapy-6kmfDNVjRdw.mp4.json',
'Rethinking_Cancer_Medicine_a_lecture_by_Dr._Janowitz-FPJfGsJgzcs.mp4.json',
'The_21st_Century_Cures_Act_-_Implications_for_Research_and_Drug_Development-43jnxPb0WFc.mp4.json']

custom_transcribe = [
'Artificial_Intelligence__the_future_of_Cancer_Distinguished_Lecture___University_of_Southampton-rMDllCXnlBE.mp3-customModel.json',
'Breast_Cancer_101_-_Our_Oncologists_Answer_Questions_On_Breast_Cancer-3nR3ByevwyY.mp4-customModel.json',
'Immunotherapy_to_treat_cancer_-_Expert_QA-Ttsj4k_ByPI.mp3-customModel.json',
'Keynote_Address_How_can_we_introduce_innovative_treatments_into_publicly_funded_healthcare_systems_D-iSmRnWn4Ib4.mp4-customModel.json',
'Learn_all_about_PARP_inhibitors_with_Dr_Jon_Krell_Consultant_Medical_Oncologist-i8Gy5OQMAlE.mp4-customModel.json',
'Nanomaterials_for_Cancer_therapy-6kmfDNVjRdw.mp4-customModel.json',
'Rethinking_Cancer_Medicine_a_lecture_by_Dr._Janowitz-FPJfGsJgzcs.mp4-customModel.json',
'The_21st_Century_Cures_Act_-_Implications_for_Research_and_Drug_Development-43jnxPb0WFc.mp4-customModel.json']

transcribe_medical = [
'medical/Artificial_Intelligence__the_future_of_Cancer_Distinguished_Lecture___University_of_Southampton-rMDllCXnlBE.mp3.json',
'medical/Breast_Cancer_101_-_Our_Oncologists_Answer_Questions_On_Breast_Cancer-3nR3ByevwyY.mp4.json',
'medical/Immunotherapy_to_treat_cancer_-_Expert_QA-Ttsj4k_ByPI.mp3.json',
'medical/Keynote_Address_How_can_we_introduce_innovative_treatments_into_publicly_funded_healthcare_systems_D-iSmRnWn4Ib4.mp4.json',
'medical/Learn_all_about_PARP_inhibitors_with_Dr_Jon_Krell_Consultant_Medical_Oncologist-i8Gy5OQMAlE.mp4.json',
'medical/Nanomaterials_for_Cancer_therapy-6kmfDNVjRdw.mp4.json',
'medical/Rethinking_Cancer_Medicine_a_lecture_by_Dr._Janowitz-FPJfGsJgzcs.mp4.json',
'medical/The_21st_Century_Cures_Act_-_Implications_for_Research_and_Drug_Development-43jnxPb0WFc.mp4.json']

truth_list = ['Artificial Intelligence & the future of Cancer, Distinguished Lecture _ University of Southampton-rMDllCXnlBE.en-GB.txt', 
'Breast Cancer 101 - Our Oncologists Answer Questions On Breast Cancer-3nR3ByevwyY.en.txt', 
'Immunotherapy to treat cancer - Expert Q&A-Ttsj4k_ByPI.en.txt', 
'Keynote Address How can we introduce innovative treatments into publicly funded healthcare systems D-iSmRnWn4Ib4.en.txt', 
'Learn all about PARP inhibitors with Dr Jon Krell, Consultant Medical Oncologist-i8Gy5OQMAlE.en-GB.txt', 
'Nanomaterials for Cancer therapy-6kmfDNVjRdw.en.txt', 
'Rethinking Cancer Medicine – a lecture by Dr. Janowitz-FPJfGsJgzcs.en.txt', 
'The 21st Century Cures Act - Implications for Research and Drug Development-43jnxPb0WFc.en.txt' 
]

print(len(transcribe))
print(len(transcribe_medical))
print(len(custom_transcribe))
print(len(truth_list))

def cleanup(output):
    output = output.replace("\n", " ")
    output = output.replace(",", "")
    output = output.replace(".", "")
    output = output.replace("   ", " ")
    output = output.replace("  ", " ")
    return output

os.chdir('youtube-files/source-truth')
output_file = open('transcribe-results.csv', 'w')
output_file.write('filename, transcribe_accuracy, medical_transcribe_accuracy, custom_model_accuracy\n')
for i in range(0, len(transcribe)):
    transcript = cleanup(AWSfunctions.get_file(bucket1, transcribe[i])['results']['transcripts'][0]['transcript'])
    medical = cleanup(AWSfunctions.get_file(bucket2, transcribe_medical[i])['results']['transcripts'][0]['transcript'])
    custom = cleanup(AWSfunctions.get_file(bucket2, custom_transcribe[i])['results']['transcripts'][0]['transcript'])
    file = open(truth_list[i])
    truth = file.read()
    output_file.write('"'+truth_list[i]+'",'+str(1-wer(transcript, truth))+","+str(1-wer(medical, truth))+","+str(1-wer(custom, truth))+'\n')
    print("File: "+truth_list[i])
    print("Transcribe Accuracy: "+ str(1-wer(transcript, truth)))
    print("Medical Transcribe Accuracy: "+ str(1-wer(medical, truth)))
    print("Custom Accuracy: "+ str(1-wer(custom, truth)))
    print("\n\n")
output_file.close()