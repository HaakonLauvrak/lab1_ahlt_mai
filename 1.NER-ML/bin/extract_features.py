#! /usr/bin/python3

import sys, os
import re
from xml.dom.minidom import parse
import spacy
   
## --------- get tag ----------- 
##  Find out whether given token is marked as part of an entity in the XML
def get_label(tks, tke, spans) :
    for (spanS,spanE,spanT) in spans :
        if tks==spanS and tke<=spanE+1 : return "B-"+spanT
        elif tks>spanS and tke<=spanE+1 : return "I-"+spanT
    return "O"
 
## --------- Feature extractor ----------- 
## -- Extract features for each token in given sentence

def extract_sentence_features(tokens) :

   # for each token, generate list of features and add it to the result
   sentenceFeatures = {}
   for i,tk in enumerate(tokens) :
      tokenFeatures = []
      t = tk.text
      # PoS tag and/or lemma could be used as feature, since spacy 
      # computes them by default
      #lem = tk.lemma_  
      #pos = tk.pos_   # coarse PoS. E.g.: NOUN, VERB, ADJ, ...
      #tag = tk.tag_   # finer PoS. E.g.:  NN (noun singular), NNS (noun plural), 
                       # VB (verb), VBS (verb 3rd person), VBD (verb past tense), ... 

      tokenFeatures.append("form="+t)
      tokenFeatures.append("suf3="+t[-3:])

      if i>0 :
         tPrev = tokens[i-1].text
         tokenFeatures.append("formPrev="+tPrev)
         tokenFeatures.append("suf3Prev="+tPrev[-3:])
      else :
         tokenFeatures.append("BoS")

      if i<len(tokens)-1 :
         tNext = tokens[i+1].text
         tokenFeatures.append("formNext="+tNext)
         tokenFeatures.append("suf3Next="+tNext[-3:])
      else:
         tokenFeatures.append("EoS")

      ### MY FEATURES ###

      #Is token all uppercase?
      if t.isupper():
         tokenFeatures.append("isAllUpper")
      
      #Does token start with a capital letter?
      if t[0].isupper():
         tokenFeatures.append("isCapital")
   
      #The first 3 characters of the token
      tokenFeatures.append("pref3="+t[:3])

      known_brands = read_file_to_list("lists/brand.txt")
      known_drugs = read_file_to_list("lists/drug.txt")
      known_groups = read_file_to_list("lists/group.txt")
      known_drug_n = read_file_to_list("lists/drug_n.txt")

      #Is token in list of known brands
      if t.lower() in known_brands:
         tokenFeatures.append("isBrand")
      
      #Is token in list of known drugs
      if t.lower() in known_drugs:
         tokenFeatures.append("isDrug")
      
      #Is token in list of known groups
      if remove_trailing_s(t.lower()) in remove_trailing_s(known_groups):
         tokenFeatures.append("isGroup")

      #Is token in list of known drug_n
      if t.lower() in known_drug_n:
         tokenFeatures.append("isDrug_n")

      #If the token is a mix of letters and numbers and dashes
      def has_letter_and_number_or_dash(t):
         # Check if string has at least one letter
         has_letter = bool(re.search(r'[a-zA-Z]', t))
         
         # Check if string has at least one number
         has_number = bool(re.search(r'[0-9]', t))
         
         # Check if string has at least one dash
         has_dash = bool(re.search(r'-', t))
         
         # Make sure string only contains allowed characters
         is_alphanumeric_dash = bool(re.match(r'^[a-zA-Z0-9-]+$', t))
         
         # Return true if it has at least one letter AND (at least one number OR at least one dash)
         return is_alphanumeric_dash and has_letter and (has_number or has_dash)

      # Add the check to your feature extraction
      if has_letter_and_number_or_dash(t):
         tokenFeatures.append("isAlphaNumDash")
    
      sentenceFeatures[i] = tokenFeatures


    
   return sentenceFeatures

## --------- Feature extractor ----------- 
## -- Extract features for each token in each
## -- sentence in given file

def extract_features(datafile, outfile) :

    # open output file
    outf = open(outfile, "w")
    
    # create analyzer. We don't need the parser now, it will be faster if disabled
    nlp = spacy.load("en_core_web_trf", disable=["parser"])
    
    # parse XML file, obtaining a DOM tree
    tree = parse(datafile)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences :
      sid = s.attributes["id"].value   # get sentence id
      print(f"extracting sentence {sid}        \r", end="")
      spans = []
      stext = s.attributes["text"].value   # get sentence text
      entities = s.getElementsByTagName("entity") # get gold standard entities
      for e in entities :
         # for discontinuous entities, we only get the first span
         # (will not work, but there are few of them)
         (start,end) = e.attributes["charOffset"].value.split(";")[0].split("-")
         typ =  e.attributes["type"].value
         spans.append((int(start),int(end),typ))

      # convert the sentence to a list of tokens
      tokens = nlp(stext)
      # extract sentence features
      features = extract_sentence_features(tokens)

      # print features in format expected by CRF/SVM/MEM trainers
      for i,tk in enumerate(tokens) :
         # see if the token is part of an entity
         tks,tke = tk.idx, tk.idx+len(tk.text)
         # get gold standard tag for this token
         tag = get_label(tks, tke, spans)
         # print feature vector for this token
         print (sid, tk.text, tks, tke-1, tag, "\t".join(features[i]), sep='\t', file=outf)

      # blank line to separate sentences
      print(file=outf)

    # close output file
    outf.close()

## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  baseline-NER.py target-dir outfile
## --
## -- Extracts Drug NE from all XML files in target-dir, and writes
## -- corresponding feature vectors to outfile
## --

if __name__ == "__main__" :
    # directory with files to process
    datafile = sys.argv[1]
    # file where to store results
    featfile = sys.argv[2]
    
    extract_features(datafile, featfile)

# Helper functions

def read_file_to_list(filename):
    entries = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # Strip whitespace and add non-empty lines to the list
                line = line.strip()
                if line:
                    entries.append(line)
    except UnicodeDecodeError:
        # Try another encoding if UTF-8 fails
        with open(filename, 'r', encoding='latin-1') as file:
            for line in file:
                line = line.strip()
                if line:
                    entries.append(line)
    
    return entries

def remove_trailing_s(word):
    if word and word[-1].lower() == 's':
        return word[:-1]
    return word
