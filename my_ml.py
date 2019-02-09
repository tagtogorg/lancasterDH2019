import flask
from flask import Flask
from flask import request
import json
import requests
from textgenrnn import textgenrnn
import random

import logging


app = Flask(__name__)

tagtog_docs_api_url = "http://localhost:9000/-api/documents/v1"

auth = requests.auth.HTTPBasicAuth(username="demo", password="YOUR_PASSWORD")

corpus = [
    "It's f*cking good!",
    "NIcceeee!",
    "I was rather disappointed",
    "Meh",
    "DISGUSTING :-("
]

textgen = textgenrnn()
random_samples = textgen.generate(10, return_as_list=True)

corpus = iter(corpus + random_samples)


@app.route("/tagtog_webhook", methods=['PUT', 'POST'])
def tagtog_webhook():

    # Train with newly saved document

    body = request.get_json()

    tagtogID = body["tagtogID"]
    params = {"owner": body["owner"], "project": body["project"], "ids": tagtogID}

    params["output"] = "ann.json"
    annjson = (requests.get(tagtog_docs_api_url, params=params, auth=auth)).json()

    if not annjson["anncomplete"]:
        print("The annotations were changed, but they are not confirmed: {}".format(tagtogID))
        return ""

    else:
        label = parse_label(annjson)

    params["output"] = "text"
    text = (requests.get(tagtog_docs_api_url, params=params, auth=auth)).text

    train((text, label))


    # Upload newly predicted document

    unseen_unlabeled_sample = collect_unlabeled_sample()
    (label, probability, who) = predict(unseen_unlabeled_sample)
    predicted_annjson = format_label_as_annjson(label, probability, who)

    files = [('file', ('text.txt', unseen_unlabeled_sample)), ('file', ('text.ann.json', predicted_annjson))]

    print(unseen_unlabeled_sample, predicted_annjson)

    params['format'] = 'default-plus-annjson'
    params['output'] = 'weburl'
    response = requests.put(tagtog_docs_api_url, params=params, auth=auth, files=files)

    print(response.text)

    return tagtogID


def parse_label(annjson):
    return next(iter(annjson["metas"].values()))["value"]


def format_label_as_annjson(label, probability, who):
    format = {
      "annotatable": {
        "parts": [
        ]
      },
      "anncomplete": False,
      "sources": [],
      "metas": {
        "m_1": {
          "value": label,
          "confidence": {
            "state": "pre-added",
            "who": [
              who
            ],
            "prob": probability
          }
        }
      },
      "entities": [],
      "relations": []
    }

    format_as_json = json.dumps(format, ensure_ascii=False)

    return format_as_json


def train(new_labeled_sample):
    # Do my ML magic
    # ...
    print("Train with: {}".format(new_labeled_sample))


def collect_unlabeled_sample():
    # Where is your data?
    # Active Learning -- select samples that are INTERESTING
    output = next(corpus)
    return output


def predict(text):
    # Call your ML
    # ...
    possible_labels=["❤️", "😐", "😢"]
    prediction = random.choice(possible_labels)
    probability = 1/len(possible_labels)
    who = "ml:my_ml"

    return (prediction, probability, who)
