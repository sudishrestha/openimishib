from api_fhir_r4.models import Element, Property


class Range(Element):

    high = Property('high', 'Quantity')
    low = Property('low', 'Quantity')
