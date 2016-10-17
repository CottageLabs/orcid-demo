import orcid

def output(search_results):
    results = False
    for profile_wrapper in search_results.get("orcid-search-results", {}).get("orcid-search-result", []):
        results = True
        profile = profile_wrapper.get("orcid-profile", {})
        bio = profile.get("orcid-bio", {})

        family_name = "unknown"
        given_names = "unknown"

        personal_details = bio.get("personal-details")
        if personal_details is not None:
            family_name = personal_details.get("family-name", {}).get("value") if personal_details.get("family-name") is not None else None
            given_names = personal_details.get("given-names", {}).get("value") if personal_details.get("given-names") is not None else None

        email_addresses = []
        if bio.get("contact-details") is not None:
            emails = bio.get("contact-details", {}).get("email", [])
            if emails is not None:
                for email_record in emails:
                    email_addresses.append(email_record.get("value"))

        orcid_identifier = profile.get("orcid-identifier", {}).get("path")

        print family_name + ", " + given_names + " - " + "|".join(email_addresses) + " - " + orcid_identifier

    if not results:
        print "No results for this search"

name = raw_input("Give me a name or part of a name:")   # e.g. Molina
email = raw_input("Give me an email address:")  # e.g. nacho.molina@ed.ac.uk
domain = raw_input("Give me an institutional email domain:")    # e.g. ed.ac.uk

token_data = orcid.get_credentials()

name_search = "credit-name:*" + name + "* OR other-names:*" + name + "* OR given-names:*" + name + "* OR family-name:*" + name + "*"
email_search = "email:" + email
institution_limit = "email:*@" + domain

# 1. Just looking for a name globally

global_by_name = orcid.bio_search(token_data, name_search)
print "Global search on just the name"
output(global_by_name)


# 2. look for the name within the university

institution_by_name_search = "(" + name_search + ") AND " + institution_limit
institution_by_name = orcid.bio_search(token_data, institution_by_name_search)
print "Search on name within institution"
output(institution_by_name)


# 3. Look for the user by email address

global_by_email = orcid.bio_search(token_data, email_search)
print "Search on user's email address"
output(global_by_email)

