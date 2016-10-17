"""
A script to expose some of the key operations required for the Dashboard use case

You will need a file called creds.json in the root of this code library, which follows the
structure defined by template.creds.json.  You get your client_id and client_secret from
the ORCID site as per the instructions here:

https://members.orcid.org/api/accessing-public-api

You need to do the same for the sandbox_client_id and sandbox_client_secret from here:

https://orcid.org/content/register-client-application-sandbox

"""

# import our common orcid client.  It's basic, but will do the job for demonstration
import orcid

# get an access token.  This uses creds.json, and negotiates with ORCID for an access token for you
token_data = orcid.get_credentials()
users = []

# Iterate over the search results for anyone with the specified email domain.  Change this as you
# like to whatever email address domain
profiles = orcid.bio_search_iterator(token_data, "email:*@ed.ac.uk")

# This section of code iterates over the search results, and extracts some useful information for
# the purposes of demoing the data available.
for profile_wrapper in profiles:
    profile = profile_wrapper.get("orcid-profile", {})
    bio = profile.get("orcid-bio", {})

    personal_details = bio.get("personal-details")
    family_name = personal_details.get("family-name", {}).get("value") if personal_details.get("family-name") is not None else None
    given_names = personal_details.get("given-names", {}).get("value") if personal_details.get("given-names") is not None else None

    email_addresses = []
    emails = bio.get("contact-details", {}).get("email", [])
    for email_record in emails:
        email_addresses.append(email_record.get("value"))

    orcid_identifier = profile.get("orcid-identifier", {}).get("path")

    # we create a user record in memory, and make space to count their works and attach their departments
    users.append({
        "name" : str(given_names) + " " + str(family_name),
        "email" : email_addresses,
        "orcid" : orcid_identifier,
        "work_count" : 0,
        "departments" : []
    })

# for each user, go off to orcid and get their full orcid record, then mine that for the number
# of publications, and their department names
for user in users:
    # ask the orcid client to get the full orcid record for this user
    full_data = orcid.get_orcid(token_data, user["orcid"])
    profile = full_data.get("orcid-profile", {})
    if profile is not None:
        activities = profile.get("orcid-activities", {})
        if activities is not None:
            works = activities.get("orcid-works", {})
            if works is not None:
                work_list = works.get("orcid-work", [])

                # now we have a list of the user's works, just count how long the list is
                user["work_count"] = len(work_list)

            department_names = []
            affiliations = activities.get("affiliations", {})
            if affiliations is not None:
                affiliation_list = affiliations.get("affiliation", [])
                if affiliation_list is not None:
                    for affiliation in affiliation_list:
                        # get the department name and record it
                        department_name = affiliation.get("department-name")
                        if department_name is not None:
                            department_names.append(department_name)

            user["departments"] = department_names

# finally, just print out the contents of our user object, demonstrating the beginnings of a dashboard listing institutional
# users, the number of works, and the departments they are affiliated with.
for user in users:
    print user["name"] + ", " + "|".join(user["email"]) + ", " + user["orcid"] + ", " + "|".join(user["departments"]) + ", work count: " + str(user["work_count"])