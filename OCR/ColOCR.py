import os
import io
import json
from google.cloud import vision
from google.protobuf.json_format import MessageToJson
from joblib import Parallel, delayed
import argparse

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
client = vision.ImageAnnotatorClient()

def main(imgdir, outputdir, index_OCR):
    print("processing "+imgdir)
    if not os.path.isdir(outputdir):
        os.mkdir(outputdir)
        print('creating directory ' + outputdir)

    clean_names = lambda x: [i for i in x if i[0] != '.']
    colImgs = sorted(clean_names(os.listdir(imgdir)))

    index_OCR[imgdir.split('/')[-1]]='/'.join(imgdir.split('/')[3:])

    for colImg in colImgs:
        imgpath = os.path.join(imgdir, colImg)
        with io.open(imgpath, 'rb') as image_file:
            col = image_file.read()
        col = vision.types.Image(content=col)
        col_context = vision.types.ImageContext(language_hints=["zh","ja"])
        response = client.document_text_detection(image=col, image_context=col_context)

        with open(os.path.join(outputdir,colImg.split('.')[0]+'.json'), 'w') as outfile:
            json.dump(MessageToJson(response), outfile)

if __name__ == '__main__':
    # construct the argument parse and parse the arguments
    parser = argparse.ArgumentParser(description='Page Detection')
    parser.add_argument('--imgdir', type=str)
    parser.add_argument('--outputdir', type=str)
    parser.add_argument('--indexfile', type=str)
    args = parser.parse_args()

    #create output file
    if not os.path.isdir(args.outputdir):
        os.mkdir(args.outputdir)
        print('creating directory ' + args.outputdir)

    clean_names = lambda x: [i for i in x if i[0] != '.']
    imgdir = os.listdir(args.imgdir)
    imgdir = sorted(clean_names(imgdir))

    outputdir = [os.path.join(args.outputdir, dir) for dir in imgdir]
    imgdir = [os.path.join(args.imgdir, dir) for dir in imgdir]

    if os.path.isfile(args.indexfile):
        with open(args.indexfile) as jsonfile:
            index_OCR=json.load(jsonfile)
    else:
        index_OCR = {}

    for i in range(len(imgdir)):
        main(imgdir[i], outputdir[i],index_OCR)

    with open((args.indexfile), 'w') as outfile:
        json.dump(index_OCR, outfile)