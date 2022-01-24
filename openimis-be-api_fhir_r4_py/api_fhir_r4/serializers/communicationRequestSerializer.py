from api_fhir_r4.converters import CommunicationRequestConverter
from api_fhir_r4.serializers import BaseFHIRSerializer


class CommunicationRequestSerializer(BaseFHIRSerializer):

    fhirConverter = CommunicationRequestConverter
