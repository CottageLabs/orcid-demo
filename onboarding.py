"""
A script to expose some of the key operations required for the Onboarding use case

You will need a file called creds.json in the root of this code library, which follows the
structure defined by template.creds.json.  You get your client_id and client_secret from
the ORCID site as per the instructions here:

https://members.orcid.org/api/accessing-public-api

You need to do the same for the sandbox_client_id and sandbox_client_secret from here:

https://orcid.org/content/register-client-application-sandbox

You will also need to have an account in the sandbox that you are happy to have this script mess
with.  You can make one here:

https://sandbox.orcid.org/signin

"""

# import our common orcid client.  It's basic, but will do the job for demonstration
import orcid

from datetime import datetime

# Adding data to a user's ORCID record requires their express permission.  This operation gets us a URL
# which will allow a user to give us that permission.  If you run this script and follow this URL, it will
# give access to YOUR orcid to this script.  (Don't worry, it's only this instance of the script that gets access
# and it's YOU that's running it with your creds.json file, no one else can access it).
permission_url = orcid.get_permission_url(system="sandbox")

print "Please visit the following URL in your browser and grant the application permissions"
print permission_url
print ""

# The user will need to give us back the code from the google oauth playground
code = raw_input("When you've done that, enter your authorisation code:")

# exchange the short code for a full access token
token_data = orcid.exchange_code_for_token(code, system="sandbox")
print token_data

# this is the bio XML that we're going to insert.  You can customise this to contain whatever you like.
# XML is formatted as per:
# https://members.orcid.org/api/xml-orcid-bio
#
bio_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<orcid-message xmlns="http://www.orcid.org/ns/orcid"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://raw.github.com/ORCID/ORCID-Source/master/orcid-model/src/main/resources/orcid-message-1.2.xsd">
    <message-version>1.2</message-version>

    <orcid-profile>
        <orcid-bio>
            <personal-details>
                <given-names>Richard</given-names>
                <family-name>Jones</family-name>
                <credit-name visibility="public">Richard Jones</credit-name>
            </personal-details>
            <biography visibility="public">Richard is the creator of this brief ORCID tutorial.  Updated [NOW]</biography>

            <contact-details>
                <email primary="true" visibility="public">orcidsandbox@oneoverzero.com</email>
                <address>
                    <country visibility="public">UK</country>
                </address>
            </contact-details>
        </orcid-bio>
    </orcid-profile>
</orcid-message>'''
bio_xml = bio_xml.replace("[NOW]", str(datetime.utcnow()))
print bio_xml

# put the bio information into the record.  After the script has run, go take a look at your orcid record,
# and you'll see the updated bio
resp1 = orcid.put_bio(token_data, bio_xml, system="sandbox")
print resp1

# this is the work XML that we're going to add.  You can customise this to contain whatever you like.
# XML is formatted as per:
# https://members.orcid.org/api/xml-orcid-works
#
work_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<orcid-message xmlns="http://www.orcid.org/ns/orcid"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.orcid.org/ns/orcid https://raw.github.com/ORCID/ORCID-Source/master/orcid-model/src/main/resources/orcid-message-1.2.xsd">
    <message-version>1.2</message-version>

    <orcid-profile>
        <orcid-activities>
            <orcid-works>
                <orcid-work>
                    <work-title>
                        <title>My New Work [NOW]</title>
                    </work-title>
                    <journal-title>Journal Title</journal-title>
                    <short-description>My Abstract</short-description>
                    <work-type>journal-article</work-type>
                    <publication-date>
                        <year>2010</year>
                        <month>11</month>
                    </publication-date>
                    <work-external-identifiers>
                        <work-external-identifier>
                            <work-external-identifier-type>doi</work-external-identifier-type>
                            <work-external-identifier-id>10.1234/alkdsjfaksdjf</work-external-identifier-id>
                        </work-external-identifier>
                    </work-external-identifiers>
                    <url>www.orcid.org</url>
                    <work-contributors>
                        <contributor>
                            <contributor-orcid>
                                <uri>http://orcid.org/[ORCID]</uri>
                            </contributor-orcid>
                            <credit-name>Jones, Richard</credit-name>
                            <contributor-attributes>
                                <contributor-sequence>first</contributor-sequence>
                                <contributor-role>author</contributor-role>
                            </contributor-attributes>
                        </contributor>
                    </work-contributors>
                </orcid-work>
            </orcid-works>
        </orcid-activities>
    </orcid-profile>
</orcid-message>
'''
work_xml = work_xml.replace("[NOW]", str(datetime.utcnow()))
work_xml = work_xml.replace("[ORCID]", token_data["orcid"])
print work_xml

# add the work to the user's orcid record.  Go look at your record after running this script to see the extra work appear.
resp2 = orcid.add_work(token_data, work_xml, system="sandbox")
print resp2
