from enum import Enum

from api_fhir_r4.models import Element, Property


class ContactPoint(Element):

    system = Property('system', str)  # ContactPointSystem (phone | fax | email | pager | url | sms | other)
    value = Property('value', str)
    use = Property('use', str)  # ContactPointUse (home | work | temp | old | mobile)
    rank = Property('rank', int)  # 1 = highest
    period = Property('period', 'Period')


class ContactPointSystem(Enum):
    PHONE = "phone"
    FAX = "fax"
    EMAIL = "email"
    PAGER = "pager"
    URL = "url"
    SMS = "sms"
    OTHER = "other"


class ContactPointUse(Enum):
    HOME = "home"
    WORK = "work"
    TEMP = "temp"
    OLD = "old"
    MOBILE = "mobile"
