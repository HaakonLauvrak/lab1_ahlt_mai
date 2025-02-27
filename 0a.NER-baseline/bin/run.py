#! /usr/bin/python3

import sys, os
from drug_index import DrugIndex
from baseline_NER import NER_baseline

BINDIR=os.path.abspath(os.path.dirname(__file__)) # location of this file
NERDIR=os.path.dirname(BINDIR) # one level up
MAINDIR=os.path.dirname(NERDIR) # one level up
DATADIR=os.path.join(MAINDIR,"data") # down to "data"
RESOURCESDIR=os.path.join(MAINDIR,"resources") # down to "resources"
UTILDIR=os.path.join(MAINDIR,"util") # down to "util"

sys.path.append(UTILDIR)
from gold_extractor import GoldExtractor
from evaluator import evaluate

# if feature extraction is required, do it
print("Extracting drugs from train data")
gold = GoldExtractor(os.path.join(DATADIR,"train.xml"))
gold.extract_NER(os.path.join(RESOURCESDIR,"drugs-train.txt"))
print("Creating index with all known drug names")
idx = DrugIndex(resources=RESOURCESDIR)    
idxfile = os.path.join(RESOURCESDIR,"drug-index.json")
with open(idxfile,"w", encoding="utf-8") as jf: idx.dump(file=jf)

print("Applying index to predict drugs")
os.makedirs(os.path.join(NERDIR,"results"), exist_ok=True)
for ds in ["devel", "test"]:
   print(f"Running baseline on {ds}                   ")
   NER_baseline(os.path.join(DATADIR,f"{ds}.xml"), 
                idxfile, 
                os.path.join(NERDIR,"results",f"{ds}.out"))
   print(f"Evaluating baseline on {ds}                ")
   evaluate("NER",
            os.path.join(DATADIR,f"{ds}.xml"),
            os.path.join(NERDIR,"results",f"{ds}.out"),
            os.path.join(NERDIR,"results",f"{ds}.stats"))

