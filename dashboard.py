import orcid

token_data = orcid.get_credentials()
users = []

# without the iterator (i.e. paging is not handled):
# results = orcid.bio_search(token_data, "email:*@ed.ac.uk")
# profiles = results.get("orcid-search-results", {}).get("orcid-search-result", [])

# with an iterator, which seamlessly handles the paging
profiles = orcid.bio_search_iterator(token_data, "email:*@ed.ac.uk")

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

    users.append({
        "name" : str(given_names) + " " + str(family_name),
        "email" : email_addresses,
        "orcid" : orcid_identifier,
        "work_count" : 0,
        "departments" : []
    })

for user in users:
    full_data = orcid.get_orcid(token_data, user["orcid"])
    profile = full_data.get("orcid-profile", {})
    if profile is not None:
        activities = profile.get("orcid-activities", {})
        if activities is not None:
            works = activities.get("orcid-works", {})
            if works is not None:
                work_list = works.get("orcid-work", [])
                user["work_count"] = len(work_list)

            department_names = []
            affiliations = activities.get("affiliations", {})
            if affiliations is not None:
                affiliation_list = affiliations.get("affiliation", [])
                if affiliation_list is not None:
                    for affiliation in affiliation_list:
                        department_name = affiliation.get("department-name")
                        if department_name is not None:
                            department_names.append(department_name)

            user["departments"] = department_names

for user in users:
    print user["name"] + ", " + "|".join(user["email"]) + ", " + user["orcid"] + ", " + "|".join(user["departments"]) + ", work count: " + str(user["work_count"])