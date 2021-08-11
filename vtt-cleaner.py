import webvtt
import glob, os
def processDirectory(directory):
    os.chdir(directory)
    for file in glob.glob("*.vtt"):
        processSingleFile(file)
def processSingleFile(file):
    output = ""
    for caption in webvtt.read(file):
    # print(caption.start)  # start timestamp in text format
    # print(caption.end)  # end timestamp in text format
        output = output + caption.text.strip("-").strip(",")
        if output[-1] != " ":
            output = output + " "
    file = file[:-4]
    output = output.replace("\n", " ")
    output = output.replace(",", "")
    output = output.replace(".", "")
    output = output.replace("   ", " ")
    output = output.replace("  ", " ")
    output = output.replace("&amp;", "&")
    output = output.replace("Jo Stanford: ", "")
    file = open(file+".txt", 'w')
    file.write(output)
    file.close()


# processDirectory("youtube-files")
processSingleFile("youtube-files/Immunotherapy to treat cancer - Expert Q&A-Ttsj4k_ByPI.en.vtt")
