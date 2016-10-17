"""
A script to expose some of the key operations required for the Everywher use case.

This is basically a recipe for using the ORCID API as an autocomplete endpoint.

You will need a file called creds.json in the root of this code library, which follows the
structure defined by template.creds.json.  You get your client_id and client_secret from
the ORCID site as per the instructions here:

https://members.orcid.org/api/accessing-public-api

You need to do the same for the sandbox_client_id and sandbox_client_secret from here:

https://orcid.org/content/register-client-application-sandbox

"""
# import our common orcid client.  It's basic, but will do the job for demonstration
import orcid

# define a script for outputting the search results, which is something we're going to do a
# few times.  It's not interesting, it just will give us a view on some key information we may]
# be interested in including in an autocomplete pull-down
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

# ask the script user to give us some parameters.  At the end of each line the comments suggest some testable parameters, but you can
# enter whatever you like
name = raw_input("Give me a name or part of a name:")   # e.g. Molina
email = raw_input("Give me an email address:")  # e.g. nacho.molina@ed.ac.uk
domain = raw_input("Give me an institutional email domain:")    # e.g. ed.ac.uk

# get an access token.  This uses creds.json, and negotiates with ORCID for an access token for you
token_data = orcid.get_credentials()

# build the search queries.  These are fairly simple boolean queries, using the field parameters specified here:
# https://members.orcid.org/api/tutorial-searching-data-using-api
#
# In this case, the name search is complicated because there are a whole load of places you might find name information,
# while the others are relatively simple
name_search = "credit-name:*" + name + "* OR other-names:*" + name + "* OR given-names:*" + name + "* OR family-name:*" + name + "*"
email_search = "email:" + email
institution_limit = "email:*@" + domain


# 1. Just looking for a name globally
global_by_name = orcid.bio_search(token_data, name_search)
print "Global search on just the name"
output(global_by_name)


# 2. look for the name within the university
# we do this by building an even bigger query which includes the name search and the institution limitation.  Note
# we put the name search in brackets, as per a normal multi-part boolean query.
institution_by_name_search = "(" + name_search + ") AND " + institution_limit
institution_by_name = orcid.bio_search(token_data, institution_by_name_search)
print "Search on name within institution"
output(institution_by_name)


# 3. Look for the user by email address
global_by_email = orcid.bio_search(token_data, email_search)
print "Search on user's email address"
output(global_by_email)

