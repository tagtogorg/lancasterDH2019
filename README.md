# lancasterDH2019

## Install

Preferably, use a virtual python environment such like:

```shell
python -m pip install -U venv
python -m venv .env
source .env/bin/activate
```

Then, install the dependencies:

```shell
pip install -r requirements.txt
```


## Run

```shell
# source .env/bin/activate
export FLASK_DEBUG=1; export FLASK_APP=my_ml.py; flask run
```
