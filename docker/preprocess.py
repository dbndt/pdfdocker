
import pandas as pd
import os, glob
import requests
import sys, argparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.high_level import extract_pages, extract_text
import flask
from flask import Flask, jsonify, request
import json
import texthero as hero
from texthero import preprocessing

app = Flask(__name__)

def cleanText(df):
    """
    texthero is a text preprocessing library 
    the library leverages the pandas pipe to chain 
    various preprocessing functions  
    """
    custom_pipeline = [preprocessing.fillna,
                       preprocessing.lowercase,
                       preprocessing.remove_whitespace,
                       preprocessing.remove_punctuation,
                       preprocessing.remove_diacritics,
                       preprocessing.remove_stopwords]

    df['clean_text'] = hero.clean(df['Text'], custom_pipeline)
    df['clean_text'] = [n.replace('{','') for n in df['clean_text']]
    df['clean_text'] = [n.replace('}','') for n in df['clean_text']]
    df['clean_text'] = [n.replace('(','') for n in df['clean_text']]
    df['clean_text'] = [n.replace(')','') for n in df['clean_text']]
    df = df[['PDF_Name','clean_text']]
    return df

def pdf_to_text(args):
    """"
    Overview: 
    1. loop through the pdfs and run pdfminer extract_text 
    2. Place data in a dataframe, zip and compress the file
    """
    PATH = args.folder_path
    ext = "*.pdf"
    files = []
    for root, dirs, names in os.walk(PATH):
        files += glob.glob(os.path.join(root, ext))  
    df = pd.DataFrame(columns=('PDF_Name','Text'))
    """"
    3. enumerate files, and remove spaces
    4. add compression and zip the files
    5. save the zipped files to the local directory
    """
    for k,v in enumerate(files):
        text = extract_text(v)
        text = text.replace("\n","")
        df.loc[k] = [v,text] 
    """
    clean the text using texthero to make suitable for machine learning models
    process: lowercase, remove: whitespaces, punctuation, diacritics, stopwords
    """
    ## clean the text
    df = df.pipe(cleanText)
    ## zip and compress the data files
    compression_opts = dict(method='zip', archive_name='out.csv')  
    df.to_csv('out.zip',sep=',', index=True, compression=compression_opts) 
    ## print the records as a dictionary
    return df.to_dict('records')

@app.route("/")
def main(args):
    """"
    1. enter the url to parse
    2. add the file path
    3. extract and parse the url using requests
    """
    base_url = args.url
    if args.folder_path:
        folder_path = args.folder_path
    else:
        folder_path = args.folder_path
        if not os.path.exists(args.folder_path):
            os.mkdir(args.folder_path)
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")     
    for link in soup.select("a[href$='.pdf']"):
        filename = os.path.join(folder_path,link['href'].split('/')[-1])
        with open(filename, 'wb') as f:
            f.write(requests.get(urljoin(base_url,link['href'])).content)
    """
    4. extract the text and place in local file
    5. run application
    """
    print(pdf_to_text(args))
    app.run(host="0.0.0.0", port=int("5000"), debug=True)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help='enter url to parse', type=str)
    parser.add_argument("--folder_path",help='store storage path', type=str)
    args = parser.parse_args()
    main(args)