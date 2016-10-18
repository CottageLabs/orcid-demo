"""
In order to have a set of credentials, you need to register with:

http://orcid.org/content/register-client-application-2

"""

EMAIL_DOMAIN = "exeter.ac.uk"
#RINGGOLD = "6723"
#NAME = "LANCASHIRE"

# RINGGOLD = "3286"
# NAME = "EXETER"

RINGGOLD = "4914"
NAME = "BANK"

OUT = "lsbu.csv"

full_lookup_limit = 25
lookup_limit = 1000

import orcid
import csv, codecs
import cStringIO

def to_unicode(val):
    if isinstance(val, unicode):
        return val
    elif isinstance(val, basestring):
        try:
            return val.decode("utf8", "strict")
        except UnicodeDecodeError:
            raise ValueError(u"Could not decode string")
    else:
        return unicode(val)

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.encoding = encoding

    def writerow(self, row):
        encoded_row = []
        for s in row:
            if s is None:
                s = ''
            if not isinstance(s, basestring):
                s = str(s)
            encoded_row.append(s.encode(self.encoding))
        self.writer.writerow(encoded_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

token_data = orcid.get_credentials()
print token_data

ringgold_search = RINGGOLD + " AND " + NAME
email_search = "email:*@" + EMAIL_DOMAIN

full_lookup_count = 0
lookup_count = 0

users = []
profiles = orcid.bio_search_iterator(token_data, ringgold_search, batch_size=100)
for profile_wrapper in profiles:
    if lookup_count > lookup_limit:
        break

    profile = profile_wrapper.get("orcid-profile", {})
    bio = profile.get("orcid-bio", {})

    orcid_identifier = profile.get("orcid-identifier", {}).get("path")
    print orcid_identifier

    personal_details = bio.get("personal-details")
    family_name = personal_details.get("family-name", {}).get("value") if personal_details.get("family-name") is not None else None
    given_names = personal_details.get("given-names", {}).get("value") if personal_details.get("given-names") is not None else None

    email_addresses = []
    if bio.get("contact-details") is not None:
        emails = bio.get("contact-details", {}).get("email", [])
        if emails is not None:
            for email_record in emails:
                email_addresses.append(email_record.get("value"))

    user = {
        "name" : to_unicode(given_names) + " " + to_unicode(family_name),
        "other_names" : [],
        "email" : email_addresses,
        "orcid" : orcid_identifier,
        "work_count" : "-",
        "departments" : [],
        "full_query" : False
    }

    lookup_count += 1
    full_lookup_count += 1

    if full_lookup_count <= full_lookup_limit:
        user["full_query"] = True
        full_data = orcid.get_orcid(token_data, orcid_identifier)

        activities = full_data.get("orcid-profile", {}).get("orcid-activities", {})

        works = activities.get("orcid-works", {})
        if works is not None:
            work_list = works.get("orcid-work", [])

            # now we have a list of the user's works, just count how long the list is
            user["work_count"] = str(len(work_list))

        affiliations = activities.get("affiliations", {})
        if affiliations is not None:
            affiliation_list = affiliations.get("affiliation", [])
            if affiliation_list is not None:
                department_names = []

                for affiliation in affiliation_list:
                    # get the department name and record it
                    department_name = affiliation.get("department-name")
                    if department_name is not None:
                        department_names.append(department_name)

                user["departments"] = department_names

    users.append(user)

permission_url = orcid.get_permission_url(system="sandbox")

with codecs.open(OUT, "wb", "utf-8") as f:
    writer = UnicodeWriter(f)
    writer.writerow(["Name", "Email(s)", "ORCID", "Departments", "Work Count", "Authorisation URL", "Did we do a full query?"])

    for user in users:
        writer.writerow([to_unicode(user["name"]), to_unicode("|".join(user["email"])), to_unicode(user["orcid"]), to_unicode("|".join(user["departments"])),
                         to_unicode(user["work_count"]), to_unicode(permission_url), to_unicode(user["full_query"])])

    #for user in users:
    #    print user["name"] + ", " + "|".join(user["email"]) + ", " + user["orcid"] + ", " + "|".join(user["departments"]) + ", " + user["work_count"] + ", " + str(user["full_query"])
