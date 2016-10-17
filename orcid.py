import requests, json

PUB_BASE_URL = "https://pub.orcid.org/v1.2/"
PUB_SEARCH_BASE_URL = "https://pub.orcid.org/v1.2/search/"

SANDBOX_BASE_URL = "https://api.sandbox.orcid.org/v1.2/"

def load_creds():
    with open("creds.json") as f:
        return json.loads(f.read())

def get_permission_url(system="pub", scope="/activities/update%20/orcid-bio/update", redirect_uri="https://developers.google.com/oauthplayground"):
    # https://sandbox.orcid.org/oauth/authorize?client_id=APP-NPXKK6HFN6TJ4YYI&response_type=code&scope=/activities/update&redirect_uri=https://developers.google.com/oauthplayground

    creds = load_creds()
    client_id = creds.get(system + "_client_id")
    url = creds.get(system + "_authorize")

    url_args = {
        "client_id" : client_id,
        "response_type": "code",
        "scope" : scope,
        "redirect_uri" : redirect_uri
    }

    url_query = "&".join([k + "=" + v for k, v in url_args.items()])

    return url + "?" + url_query

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

def exchange_code_for_token(code, system="pub", grant_type="authorization_code", redirect_uri="https://developers.google.com/oauthplayground"):
    # curl -i -L -H "Accept: application/json" --data "client_id=APP-NPXKK6HFN6TJ4YYI&client_secret=060c36f2-cce2-4f74-bde0-a17d8bb30a97&grant_type=authorization_code&code=Mo0WOt&redirect_uri=https://developers.google.com/oauthplayground" "https://sandbox.orcid.org/oauth/token"
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
        "code" : code,
        "grant_type" : grant_type,
        "redirect_uri" : redirect_uri
    }

    resp = requests.post(url, data=data, headers=headers)
    return resp.json()


def get_orcid(token_data, id):
    url = PUB_BASE_URL + id + "/orcid-profile"

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer " + token_data["access_token"]
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
        "Authorization" : "Bearer " + token_data["access_token"]
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

def put_bio(token_data, bio_xml, system="pub"):
    # curl -H "Content-Type: application/vnd.orcid+xml" -H "Authorization: Bearer aa466b4-04ff-4471-890d-71cf6bb8438e" -d "@/Documents/updated_bio.xml" -X PUT "https://api.sandbox.orcid.org/v1.2/0000-0002-2389-8429/orcid-bio"
    base = PUB_BASE_URL
    if system == "sandbox":
        base = SANDBOX_BASE_URL

    url = base + token_data["orcid"] + "/orcid-bio"

    headers = {
        "Content-Type" : "application/vnd.orcid+xml",
        "Authorization" : "Bearer " + token_data["access_token"]
    }

    resp = requests.put(url, data=bio_xml, headers=headers)
    return resp.content

def add_work(token_data, work_xml, system="pub"):
    # curl -H "Content-Type: application/orcid+xml" -H "Authorization: Bearer aa2c8730-07af-4ac6-bfec-fb22c0987348" -d "@/Documents/new_work.xml" -X POST "https://api.sandbox.orcid.org/v1.2/0000-0002-2389-8429/orcid-works"
    base = PUB_BASE_URL
    if system == "sandbox":
        base = SANDBOX_BASE_URL

    url = base + token_data["orcid"] + "/orcid-works"

    headers = {
        "Content-Type" : "application/vnd.orcid+xml",
        "Authorization" : "Bearer " + token_data["access_token"]
    }

    resp = requests.post(url, data=work_xml, headers=headers)
    return resp.content