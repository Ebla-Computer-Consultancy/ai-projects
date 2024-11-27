from enum import Enum

class TextAnalyticsKEYS(Enum):
    ORGANIZATION = "Organization"
    DATETIME = "DateTime"
    IPADDRESS = "IPAddress"
    PERSON = "Person"
    PERSONTYPE = "PersonType"
    URL = "URL"
    EVENT = "Event"
    EMAIL = "Email"
    LOCATION = "Location"
    PHONENUMBER = "PhoneNumber"
    SKILL = "Skill"
    PRODUCT = "Product"
    QUANTITY = "Quantity"
    ADDRESS = "Address"
    ENTITIES = "entities"
    LANGUAGE_NAME = "name"
    LANGUAGE_ISO6391_NAME = "iso6391_name"
    
class TextAnalyticsCatigories:
    def __init__(self, organization: list = None, dateTime: list = None, IPAddress: list = None, 
                 person: list = None, personType: list = None, url: list = None, event: list = None, 
                 email: list = None, location: list = None, phoneNumber: list = None, skill: list = None, 
                 product: list = None, quantity: list = None, address: list = None, entities: list = None):
        
        self.organization = organization if organization is not None else []
        self.dateTime = dateTime if dateTime is not None else []
        self.IPAddress = IPAddress if IPAddress is not None else []
        self.person = person if person is not None else []
        self.personType = personType if personType is not None else []
        self.url = url if url is not None else []
        self.event = event if event is not None else []
        self.email = email if email is not None else []
        self.location = location if location is not None else []
        self.phoneNumber = phoneNumber if phoneNumber is not None else []
        self.skill = skill if skill is not None else []
        self.product = product if product is not None else []
        self.quantity = quantity if quantity is not None else []
        self.address = address if address is not None else []
        self.entities = entities if entities is not None else []


    def to_dict(self):
        
        return {
            TextAnalyticsKEYS.ORGANIZATION.value: self.organization,
            TextAnalyticsKEYS.DATETIME.value: self.dateTime,
            TextAnalyticsKEYS.IPADDRESS.value: self.IPAddress,
            TextAnalyticsKEYS.PERSON.value: self.person,
            TextAnalyticsKEYS.PERSONTYPE.value: self.personType,
            TextAnalyticsKEYS.URL.value: self.url,
            TextAnalyticsKEYS.EVENT.value: self.event,
            TextAnalyticsKEYS.EMAIL.value: self.email,
            TextAnalyticsKEYS.LOCATION.value: self.location,
            TextAnalyticsKEYS.PHONENUMBER.value: self.phoneNumber,
            TextAnalyticsKEYS.SKILL.value: self.skill,
            TextAnalyticsKEYS.PRODUCT.value: self.product,
            TextAnalyticsKEYS.QUANTITY.value: self.quantity,
            TextAnalyticsKEYS.ADDRESS.value: self.address,
            TextAnalyticsKEYS.ENTITIES.value: self.entities
        }
