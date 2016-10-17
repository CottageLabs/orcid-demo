import orcid
from datetime import datetime


permission_url = orcid.get_permission_url(system="sandbox")

print "Please visit the following URL in your browser and grant the application permissions"
print permission_url
print ""

code = raw_input("When you've done that, enter your authorisation code:")

token_data = orcid.exchange_code_for_token(code, system="sandbox")
print token_data

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

resp1 = orcid.put_bio(token_data, bio_xml, system="sandbox")
print resp1


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

resp2 = orcid.add_work(token_data, work_xml, system="sandbox")
print resp2
