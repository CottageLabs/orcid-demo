import requests, json

PUB_BASE_URL = "https://pub.orcid.org/v1.2/"
PUB_SEARCH_BASE_URL = "https://pub.orcid.org/v1.2/search/"

def load_creds():
    with open("creds.json") as f:
        return json.loads(f.read())

def get_credentials(system="pub", scope="/read-public", grant_type="client_credentials"):
    creds = load_creds()
    client_id = creds.get(system + "_client_id")
    client_secret = creds.get(system + "_client_secret")
    url = creds.get(system + "_oauth")

    headers = {
        "Accept" : "application/json"
    }

    data = {
        "client_id" : client_id,
        "client_secret" : client_secret,
        "scope" : scope,
        "grant_type" : grant_type,
    }

    resp = requests.post(url, data=data, headers=headers)
    return resp.json()

def get_orcid(token_data, id):
    url = PUB_BASE_URL + id + "/orcid-profile"

    headers = {
        "Content-Type" : "application/json",
        "Authorization:" : "Bearer " + token_data["access_token"]
    }

    resp = requests.get(url, headers=headers)
    return resp.json()

def bio_search(token_data, q, start=0, rows=10):
    url_args = {
        "q" : q,
        "start" : str(start),
        "rows" : str(rows)
    }
    url_query = "&".join([k + "=" + v for k, v in url_args.items()])

    url = PUB_SEARCH_BASE_URL + "orcid-bio/?" + url_query

    headers = {
        "Content-Type" : "application/json",
        "Authorization:" : "Bearer " + token_data["access_token"]
    }
    resp = requests.get(url, headers=headers)
    return resp.json()

def bio_search_iterator(token_data, q, batch_size=10):
    start = 0
    while True:
        results = bio_search(token_data, q, start=start, rows=batch_size)
        actual_results = results.get("orcid-search-results", {}).get("orcid-search-result", [])
        for result in actual_results:
            yield result

        start = start + batch_size
        num_found = results.get("orcid-search-results", {}).get("num-found", 0)
        if start >= num_found:
            break


