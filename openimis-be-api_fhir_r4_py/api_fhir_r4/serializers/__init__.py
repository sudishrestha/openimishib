from core.models import User, TechnicalUser
from django.http.response import HttpResponseBase

from api_fhir_r4.configurations import GeneralConfiguration
from rest_framework import serializers
from api_fhir_r4.converters import BaseFHIRConverter, OperationOutcomeConverter
from api_fhir_r4.models import FHIRBaseObject


class BaseFHIRSerializer(serializers.Serializer):
    fhirConverter = BaseFHIRConverter()

    def to_representation(self, obj):
        if isinstance(obj, HttpResponseBase):
            return OperationOutcomeConverter.to_fhir_obj(obj).toDict()
        elif isinstance(obj, FHIRBaseObject):
            return obj.toDict()
        return self.fhirConverter.to_fhir_obj(obj).toDict()

    def to_internal_value(self, data):
        audit_user_id = self.get_audit_user_id()
        if isinstance(data, dict):
            data = FHIRBaseObject.fromDict(data)
        return self.fhirConverter.to_imis_obj(data, audit_user_id).__dict__

    def create(self, validated_data):
        raise NotImplementedError('`create()` must be implemented.')  # pragma: no cover

    def update(self, instance, validated_data):
        raise NotImplementedError('`update()` must be implemented.')  # pragma: no cover

    def get_audit_user_id(self):
        request = self.context.get("request")
        # Taking the audit_user_id from the query doesn't seem wise but there might be a use for it
        # audit_user_id = request.query_params.get('auditUserId', None)
        audit_user_id = request.user.id_for_audit if request.user else None
        if audit_user_id is None:
            audit_user_id = GeneralConfiguration.get_default_audit_user_id()
        if isinstance(audit_user_id, int):
            return audit_user_id
        else:
            return self.__get_technical_audit_user(audit_user_id)

    def __get_technical_audit_user(self, technical_user_uuid):
        technical_user = TechnicalUser.objects.get(id=technical_user_uuid)
        core_user = User.objects.get(t_user=technical_user_uuid)
        interactive_user = core_user.i_user
        return interactive_user.id if interactive_user else technical_user.id_for_audit

from api_fhir_r4.serializers.patientSerializer import PatientSerializer
from api_fhir_r4.serializers.contractSerializer import ContractSerializer
from api_fhir_r4.serializers.locationSerializer import LocationSerializer
from api_fhir_r4.serializers.locationSiteSerializer import LocationSiteSerializer
from api_fhir_r4.serializers.practitionerRoleSerializer import PractitionerRoleSerializer
from api_fhir_r4.serializers.practitionerSerializer import PractitionerSerializer
from api_fhir_r4.serializers.claimSerializer import ClaimSerializer
from api_fhir_r4.serializers.coverageEligibilityRequestSerializer import CoverageEligibilityRequestSerializer
from api_fhir_r4.serializers.policyCoverageEligibilityRequestSerializer import PolicyCoverageEligibilityRequestSerializer
from api_fhir_r4.serializers.claimResponseSerializer import ClaimResponseSerializer
from api_fhir_r4.serializers.communicationRequestSerializer import CommunicationRequestSerializer
from api_fhir_r4.serializers.medicationSerializer import MedicationSerializer
from api_fhir_r4.serializers.conditionSerializer import ConditionSerializer
from api_fhir_r4.serializers.activityDefinitionSerializer import ActivityDefinitionSerializer
from api_fhir_r4.serializers.healthcareServiceSerializer import HealthcareServiceSerializer
