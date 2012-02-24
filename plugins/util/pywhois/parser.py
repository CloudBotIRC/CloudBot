# parser.py - Module for parsing whois response data
# Copyright (c) 2008 Andrey Petrov
#
# This module is part of pywhois and is released under
# the MIT license: http://www.opensource.org/licenses/mit-license.php

import re
import time
   

class PywhoisError(Exception):
    pass


def cast_date(date_str):
    """Convert any date string found in WHOIS to a time object.
    """
    known_formats = [
        '%d-%b-%Y',                             # 02-jan-2000
        '%Y-%m-%d',                             # 2000-01-02
        '%d-%b-%Y %H:%M:%S %Z',         # 24-Jul-2009 13:20:03 UTC
        '%a %b %d %H:%M:%S %Z %Y',  # Tue Jun 21 23:59:59 GMT 2011
        '%Y-%m-%dT%H:%M:%SZ',       # 2007-01-26T19:10:31Z
    ]

    for format in known_formats:
        try:
            return time.strptime(date_str.strip(), format)
        except ValueError, e:
            pass # Wrong format, keep trying
    return None


class WhoisEntry(object):
    """Base class for parsing a Whois entries.
    """
    # regular expressions to extract domain data from whois profile
    # child classes will override this
    _regex = {
        'domain_name':      'Domain Name:\s?(.+)',
        'registrar':        'Registrar:\s?(.+)',
        'whois_server':     'Whois Server:\s?(.+)',
        'referral_url':     'Referral URL:\s?(.+)', # http url of whois_server
        'updated_date':     'Updated Date:\s?(.+)',
        'creation_date':    'Creation Date:\s?(.+)',
        'expiration_date':  'Expiration Date:\s?(.+)',
        'name_servers':     'Name Server:\s?(.+)', # list of name servers
        'status':           'Status:\s?(.+)', # list of statuses
        'emails':           '[\w.-]+@[\w.-]+\.[\w]{2,4}', # list of email addresses
    }

    def __init__(self, domain, text, regex=None):
        self.domain = domain
        self.text = text
        if regex is not None:
            self._regex = regex


    def __getattr__(self, attr):
        """The first time an attribute is called it will be calculated here.
        The attribute is then set to be accessed directly by subsequent calls.
        """
        whois_regex = self._regex.get(attr)
        if whois_regex:
            setattr(self, attr, re.findall(whois_regex, self.text))
            return getattr(self, attr)
        else:
            raise KeyError('Unknown attribute: %s' % attr)

    def __str__(self):
        """Print all whois properties of domain
        """
        return '\n'.join('%s: %s' % (attr, str(getattr(self, attr))) for attr in self.attrs())


    def attrs(self):
        """Return list of attributes that can be extracted for this domain
        """
        return sorted(self._regex.keys())


    @staticmethod
    def load(domain, text):
        """Given whois output in ``text``, return an instance of ``WhoisEntry`` that represents its parsed contents.
        """
        if text.strip() == 'No whois server is known for this kind of object.':
            raise PywhoisError(text)

        if '.com' in domain:
            return WhoisCom(domain, text)
        elif '.net' in domain:
            return WhoisNet(domain, text)
        elif '.org' in domain:
            return WhoisOrg(domain, text)
        elif '.ru' in domain:
            return WhoisRu(domain, text)
        elif '.name' in domain:
                return WhoisName(domain, text)
        elif '.us' in domain:
                return WhoisUs(domain, text)
        elif '.me' in domain:
                return WhoisMe(domain, text)
        elif '.uk' in domain:
                return WhoisUk(domain, text)
        else:
            return WhoisEntry(domain, text)



class WhoisCom(WhoisEntry):
    """Whois parser for .com domains
    """
    def __init__(self, domain, text):
        if 'No match for "' in text:
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text) 

class WhoisNet(WhoisEntry):
    """Whois parser for .net domains
    """
    def __init__(self, domain, text):
        if 'No match for "' in text:
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text) 

class WhoisOrg(WhoisEntry):
    """Whois parser for .org domains
    """
    regex = {
        'domain_name':      'Domain Name:\s?(.+)',
        'registrar':        'Registrar:\s?(.+)',
        'whois_server':     'Whois Server:\s?(.+)',
        'referral_url':     'Referral URL:\s?(.+)', # http url of whois_server
        'updated_date':     'Last Updated On:\s?(.+)',
        'creation_date':    'Created On:\s?(.+)',
        'expiration_date':  'Expiration Date:\s?(.+)',
        'name_servers':     'Name Server:\s?(.+)', # list of name servers
        'status':           'Status:\s?(.+)', # list of statuses
        'emails':           '[\w.-]+@[\w.-]+\.[\w]{2,4}', # list of email addresses
    }
    def __init__(self, domain, text):
        if text.strip() == 'NOT FOUND':
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text, self.regex) 

class WhoisRu(WhoisEntry):
    """Whois parser for .ru domains
    """
    regex = {
        'domain_name': 'domain:\s*(.+)',
        'registrar': 'registrar:\s*(.+)',
        'creation_date': 'created:\s*(.+)',
        'expiration_date': 'paid-till:\s*(.+)',
        'name_servers': 'nserver:\s*(.+)',  # list of name servers
        'status': 'state:\s*(.+)',  # list of statuses
        'emails': '[\w.-]+@[\w.-]+\.[\w]{2,4}',  # list of email addresses
    }

    def __init__(self, domain, text):
        if text.strip() == 'No entries found':
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text, self.regex)

class WhoisName(WhoisEntry):
    """Whois parser for .name domains
    """
    regex = {
        'domain_name_id':  'Domain Name ID:\s*(.+)',
        'domain_name':     'Domain Name:\s*(.+)',
        'registrar_id':    'Sponsoring Registrar ID:\s*(.+)',
        'registrar':       'Sponsoring Registrar:\s*(.+)',
        'registrant_id':   'Registrant ID:\s*(.+)',
        'admin_id':        'Admin ID:\s*(.+)',
        'technical_id':    'Tech ID:\s*(.+)',
        'billing_id':      'Billing ID:\s*(.+)',
        'creation_date':   'Created On:\s*(.+)',
        'expiration_date': 'Expires On:\s*(.+)',
        'updated_date':    'Updated On:\s*(.+)',
        'name_server_ids': 'Name Server ID:\s*(.+)',  # list of name server ids
        'name_servers':    'Name Server:\s*(.+)',  # list of name servers
        'status':          'Domain Status:\s*(.+)',  # list of statuses
        }
    def __init__(self, domain, text):
        if 'No match.' in text:
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text, self.regex) 
            
class WhoisUs(WhoisEntry):
    """Whois parser for .us domains
    """
    regex = {
        'domain_name':                    'Domain Name:\s*(.+)',
        'domain__id':                     'Domain ID:\s*(.+)',
        'registrar':                      'Sponsoring Registrar:\s*(.+)',
        'registrar_id':                   'Sponsoring Registrar IANA ID:\s*(.+)',
        'registrar_url':                  'Registrar URL \(registration services\):\s*(.+)',        
        'status':                         'Domain Status:\s*(.+)',  # list of statuses
        'registrant_id':                  'Registrant ID:\s*(.+)',
        'registrant_name':                'Registrant Name:\s*(.+)',
        'registrant_address1':            'Registrant Address1:\s*(.+)',
        'registrant_address2':            'Registrant Address2:\s*(.+)',
        'registrant_city':                'Registrant City:\s*(.+)',
        'registrant_state_province':      'Registrant State/Province:\s*(.+)',
        'registrant_postal_code':         'Registrant Postal Code:\s*(.+)',
        'registrant_country':             'Registrant Country:\s*(.+)',
        'registrant_country_code':        'Registrant Country Code:\s*(.+)',
        'registrant_phone_number':        'Registrant Phone Number:\s*(.+)',
        'registrant_email':               'Registrant Email:\s*(.+)',
        'registrant_application_purpose': 'Registrant Application Purpose:\s*(.+)',
        'registrant_nexus_category':      'Registrant Nexus Category:\s*(.+)',
        'admin_id':                       'Administrative Contact ID:\s*(.+)',
        'admin_name':                     'Administrative Contact Name:\s*(.+)',
        'admin_address1':                 'Administrative Contact Address1:\s*(.+)',
        'admin_address2':                 'Administrative Contact Address2:\s*(.+)',
        'admin_city':                     'Administrative Contact City:\s*(.+)',
        'admin_state_province':           'Administrative Contact State/Province:\s*(.+)',
        'admin_postal_code':              'Administrative Contact Postal Code:\s*(.+)',
        'admin_country':                  'Administrative Contact Country:\s*(.+)',
        'admin_country_code':             'Administrative Contact Country Code:\s*(.+)',
        'admin_phone_number':             'Administrative Contact Phone Number:\s*(.+)',
        'admin_email':                    'Administrative Contact Email:\s*(.+)',
        'admin_application_purpose':      'Administrative Application Purpose:\s*(.+)',
        'admin_nexus_category':           'Administrative Nexus Category:\s*(.+)',
        'billing_id':                     'Billing Contact ID:\s*(.+)',
        'billing_name':                   'Billing Contact Name:\s*(.+)',
        'billing_address1':               'Billing Contact Address1:\s*(.+)',
        'billing_address2':               'Billing Contact Address2:\s*(.+)',
        'billing_city':                   'Billing Contact City:\s*(.+)',
        'billing_state_province':         'Billing Contact State/Province:\s*(.+)',
        'billing_postal_code':            'Billing Contact Postal Code:\s*(.+)',
        'billing_country':                'Billing Contact Country:\s*(.+)',
        'billing_country_code':           'Billing Contact Country Code:\s*(.+)',
        'billing_phone_number':           'Billing Contact Phone Number:\s*(.+)',
        'billing_email':                  'Billing Contact Email:\s*(.+)',
        'billing_application_purpose':    'Billing Application Purpose:\s*(.+)',
        'billing_nexus_category':         'Billing Nexus Category:\s*(.+)',
        'tech_id':                        'Technical Contact ID:\s*(.+)',
        'tech_name':                      'Technical Contact Name:\s*(.+)',
        'tech_address1':                  'Technical Contact Address1:\s*(.+)',
        'tech_address2':                  'Technical Contact Address2:\s*(.+)',
        'tech_city':                      'Technical Contact City:\s*(.+)',
        'tech_state_province':            'Technical Contact State/Province:\s*(.+)',
        'tech_postal_code':               'Technical Contact Postal Code:\s*(.+)',
        'tech_country':                   'Technical Contact Country:\s*(.+)',
        'tech_country_code':              'Technical Contact Country Code:\s*(.+)',
        'tech_phone_number':              'Technical Contact Phone Number:\s*(.+)',
        'tech_email':                     'Technical Contact Email:\s*(.+)',
        'tech_application_purpose':       'Technical Application Purpose:\s*(.+)',
        'tech_nexus_category':            'Technical Nexus Category:\s*(.+)',
        'name_servers':                   'Name Server:\s*(.+)',  # list of name servers
        'created_by_registrar':           'Created by Registrar:\s*(.+)',
        'last_updated_by_registrar':      'Last Updated by Registrar:\s*(.+)',
        'creation_date':                  'Domain Registration Date:\s*(.+)',
        'expiration_date':                'Domain Expiration Date:\s*(.+)',
        'updated_date':                   'Domain Last Updated Date:\s*(.+)',
        }
    def __init__(self, domain, text):
        if 'Not found:' in text:
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text, self.regex)
            
class WhoisMe(WhoisEntry):
    """Whois parser for .me domains
    """
    regex = {
        'domain_id':                   'Domain ID:(.+)',
        'domain_name':                 'Domain Name:(.+)',
        'creation_date':               'Domain Create Date:(.+)',
        'updated_date':                'Domain Last Updated Date:(.+)',
        'expiration_date':             'Domain Expiration Date:(.+)',
        'transfer_date':               'Last Transferred Date:(.+)',
        'trademark_name':              'Trademark Name:(.+)',
        'trademark_country':           'Trademark Country:(.+)',
        'trademark_number':            'Trademark Number:(.+)',
        'trademark_application_date':  'Date Trademark Applied For:(.+)',
        'trademark_registration_date': 'Date Trademark Registered:(.+)',
        'registrar':                   'Sponsoring Registrar:(.+)',
        'created_by':                  'Created by:(.+)',
        'updated_by':                  'Last Updated by Registrar:(.+)',
        'status':                      'Domain Status:(.+)',  # list of statuses
        'registrant_id':               'Registrant ID:(.+)',
        'registrant_name':             'Registrant Name:(.+)',
        'registrant_org':              'Registrant Organization:(.+)',
        'registrant_address':          'Registrant Address:(.+)',
        'registrant_address2':         'Registrant Address2:(.+)',
        'registrant_address3':         'Registrant Address3:(.+)',
        'registrant_city':             'Registrant City:(.+)',
        'registrant_state_province':   'Registrant State/Province:(.+)',
        'registrant_country':          'Registrant Country/Economy:(.+)',
        'registrant_postal_code':      'Registrant Postal Code:(.+)',
        'registrant_phone':            'Registrant Phone:(.+)',
        'registrant_phone_ext':        'Registrant Phone Ext\.:(.+)',
        'registrant_fax':              'Registrant FAX:(.+)',
        'registrant_fax_ext':          'Registrant FAX Ext\.:(.+)',
        'registrant_email':            'Registrant E-mail:(.+)',
        'admin_id':                    'Admin ID:(.+)',
        'admin_name':                  'Admin Name:(.+)',
        'admin_org':                   'Admin Organization:(.+)',
        'admin_address':               'Admin Address:(.+)',
        'admin_address2':              'Admin Address2:(.+)',
        'admin_address3':              'Admin Address3:(.+)',
        'admin_city':                  'Admin City:(.+)',
        'admin_state_province':        'Admin State/Province:(.+)',
        'admin_country':               'Admin Country/Economy:(.+)',
        'admin_postal_code':           'Admin Postal Code:(.+)',
        'admin_phone':                 'Admin Phone:(.+)',
        'admin_phone_ext':             'Admin Phone Ext\.:(.+)',
        'admin_fax':                   'Admin FAX:(.+)',
        'admin_fax_ext':               'Admin FAX Ext\.:(.+)',
        'admin_email':                 'Admin E-mail:(.+)',
        'tech_id':                     'Tech ID:(.+)',
        'tech_name':                   'Tech Name:(.+)',
        'tech_org':                    'Tech Organization:(.+)',
        'tech_address':                'Tech Address:(.+)',
        'tech_address2':               'Tech Address2:(.+)',
        'tech_address3':               'Tech Address3:(.+)',
        'tech_city':                   'Tech City:(.+)',
        'tech_state_province':         'Tech State/Province:(.+)',
        'tech_country':                'Tech Country/Economy:(.+)',
        'tech_postal_code':            'Tech Postal Code:(.+)',
        'tech_phone':                  'Tech Phone:(.+)',
        'tech_phone_ext':              'Tech Phone Ext\.:(.+)',
        'tech_fax':                    'Tech FAX:(.+)',
        'tech_fax_ext':                'Tech FAX Ext\.:(.+)',
        'tech_email':                  'Tech E-mail:(.+)',
        'name_servers':                'Nameservers:(.+)',  # list of name servers
        }
    def __init__(self, domain, text):
        if 'NOT FOUND' in text:
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text, self.regex) 

class WhoisUk(WhoisEntry):
    """Whois parser for .uk domains
    """
    regex = {
        'domain_name':                    'Domain name:\n\s*(.+)',
        'registrar':                      'Registrar:\n\s*(.+)',
        'registrar_url':                  'URL:\s*(.+)',
        'status':                         'Registration status:\n\s*(.+)',  # list of statuses
        'registrant_name':                'Registrant:\n\s*(.+)',
        'creation_date':                  'Registered on:\s*(.+)',
        'expiration_date':                'Renewal date:\s*(.+)',
        'updated_date':                   'Last updated:\s*(.+)',
        }
    def __init__(self, domain, text):
        if 'Not found:' in text:
            raise PywhoisError(text)
        else:
            WhoisEntry.__init__(self, domain, text, self.regex)
