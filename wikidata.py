import requests
import json
import wptools

def find_values(id, json_repr):
  results = []

  def _decode_dict(a_dict):
      try: results.append(a_dict[id])
      except KeyError: pass
      return a_dict

  json.loads(json_repr, object_hook=_decode_dict)  # Return value ignored.
  return results

def getParamsAnn(id):
  return {'project':'Rome', 'owner': 'lancaster2019', 'ids':id, 'output':'ann.json'}

tagtogAPIUrl = "https://www.tagtog.net/-api/documents/v1"
wikipediaUrl = "https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&ppprop=wikibase_item&redirects=1&format=json"
wikidataUrl = "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
coordinatesPropName = 'coordinate location (P625)'
coordinatesPropId = 'P625'
normalizationId = 'n_9'
entityTypeId = 'e_2'

#Get your collection of docs
auth = requests.auth.HTTPBasicAuth(username='lancaster2019', password='YOUR_PASSWORD')
paramsTagtog = {'project':'Rome', 'owner': 'lancaster2019', 'search':'*'}
responseSearch = requests.get(tagtogAPIUrl, params=paramsTagtog, auth=auth)
docList = ""
setLocations = set([])
listCoords = []
listLatLong = []

#Iterate over docs
for doc in json.loads(responseSearch.text)['docs']:
  responseAnnJson = requests.get(tagtogAPIUrl, params=getParamsAnn(doc['id']), auth=auth)
  #Iterate over entities and get the location Id
  for entity in json.loads(responseAnnJson.text)['entities']:
    if entity['classId'] == entityTypeId and entity['normalizations'] and entity['normalizations'][normalizationId]["source"]["id"]!="":
      setLocations.add(entity['normalizations'][normalizationId]["source"]["id"])

#Iterate the locations and get the coordinates
for loc in setLocations:
  page = wptools.page(loc)
  page.wanted_labels([coordinatesPropId])
  page.get_wikidata()
  if (coordinatesPropName in page.data['wikidata']):
    listCoords.append(page.data['wikidata'][coordinatesPropName])

#clean data
for coord in listCoords:
  del coord['altitude']

print (listCoords)
