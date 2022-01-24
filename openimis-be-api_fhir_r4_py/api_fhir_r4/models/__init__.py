import inspect
import json
import sys

import math
from api_fhir_r4.exceptions import PropertyTypeError, PropertyError, PropertyMaxSizeError, InvalidAttributeError, \
    UnsupportedFormatError, FHIRException
from django.utils.translation import gettext


SUPPORTED_FORMATS = ['json']


class PropertyDefinition(object):

    def __init__(self, name, property_type, count_max=1, count_min=0, required=False):
        assert name.find(' ') < 0, gettext("property shouldn't contain space in `{}`.").format(name)
        self.name = name
        self.type = property_type
        self.count_max = math.inf if count_max == '*' else int(count_max)
        self.count_min = int(count_min)
        self.required = required


def eval_type(type_name):
    result = object
    if isinstance(type_name, str):
        result = getattr(sys.modules[__name__], type_name)
    return result


class PropertyMixin(object):

    def validate_type(self, value):
        if value is not None:
            local_type = self.eval_property_type()
            if local_type is FHIRDate and not FHIRDate.validate_type(value):
                raise ValueError(gettext('Value "{}" is not a valid value of FHIRDate').format(value))
            elif issubclass(local_type, PropertyMixin) and (not inspect.isclass(local_type) or
                                                            not isinstance(value, local_type)):
                raise PropertyTypeError(value.__class__.__name__, self.definition)
        elif self.definition.required:
            raise PropertyError(gettext("The value of property {} could't be none").format(self.definition.name))

    def eval_property_type(self):
        property_type = self.definition.type
        return eval_type(property_type)


class PropertyList(list, PropertyMixin):

    def __init__(self, definition, *args, **kwargs):
        super(PropertyList, self).__init__(*args, **kwargs)
        self.definition = definition

    def append(self, value):
        self.validate_type(value)
        if len(self) >= self.definition.count_max:
            raise PropertyMaxSizeError(self.definition)

        super(PropertyList, self).append(value)

    def insert(self, i, value):
        self.validate_type(value)
        if len(self) >= self.definition.count_max:
            raise PropertyMaxSizeError(self.definition)

        super(PropertyList, self).insert(i, value)


class Property(PropertyMixin):

    def __init__(self, name, property_type, count_max=1, count_min=0, required=False):
        assert name.find(' ') < 0, gettext("property shouldn't contain space in `{}`.").format(name)
        self.definition = PropertyDefinition(name, property_type, count_max, count_min, required)

    def __get__(self, instance, owner):
        if instance is None:  # instance attribute is accessed on the class
            return self
        if self.definition.count_max > 1:
            instance._values.setdefault(self.definition.name, PropertyList(self.definition))
        return instance._values.get(self.definition.name)

    def __set__(self, instance, value):
        if self.definition.count_max > 1:
            if isinstance(value, list):
                instance._values.setdefault(self.definition.name, PropertyList(self.definition))
                del instance._values[self.definition.name][:]
                for item in value:
                    instance._values[self.definition.name].append(item)
            else:
                raise PropertyError(gettext("The value of property `{}` need to be a list").format(self.definition.name))
        else:
            if isinstance(value, list):
                raise PropertyError(gettext("The value of property `{}` shouldn't be a list").format(self.definition.name))
            else:
                self.validate_type(value)
                instance._values[self.definition.name] = value


class FHIRBaseObject(object):
    def __init__(self, **kwargs):
        self._set_properties(**kwargs)
        self._values = dict()

    def _set_properties(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def __setattr__(self, attr, value):
        self.valid_fhir_attribute(attr)
        super().__setattr__(attr, value)

    @classmethod
    def _get_properties(cls):
        properties_names = []
        for attr in dir(cls):
            attribute = getattr(cls, attr)
            if cls.is_property(attribute):
                properties_names.append(attribute.definition.name)
        return properties_names

    @classmethod
    def is_property(cls, object_):
        return isinstance(object_, Property)

    @classmethod
    def _get_property_details_for_name(cls, name):
        cls.valid_fhir_attribute(name)
        property_ = getattr(cls, name)
        type_ = property_.definition.type
        if isinstance(type_, str):
            type_ = eval_type(type_)

        return property_, type_

    @classmethod
    def valid_fhir_attribute(cls, name):
        if name not in cls._get_properties() and not name.startswith('_'):
            raise InvalidAttributeError(name, cls.__name__)

    @classmethod
    def loads(cls, string, format_='json'):
        if format_ in SUPPORTED_FORMATS:
            format_ = format_.upper()
            func = getattr(cls, 'from' + format_)
            return func(string)

        raise UnsupportedFormatError(format_)

    @classmethod
    def fromJSON(cls, json_string):
        json_dict = json.loads(json_string)
        resource_type = json_dict.pop('resourceType')

        if resource_type != cls.__name__:
            class_ = eval_type(resource_type)
            if class_ is object or not issubclass(class_, cls):
                raise FHIRException(gettext('Cannot marshall a {} from a {}: not a subclass!').format(class_,
                                                                                                      cls.__name__))
            return class_()._fromDict(json_dict)
        return cls()._fromDict(json_dict)

    @classmethod
    def fromDict(cls, object_dict):
        if not object_dict.get('resourceType'):
            raise FHIRException(gettext('Missing `resourceType` attribute'))
        resource_type = object_dict.pop('resourceType')
        class_ = eval_type(resource_type)
        return class_()._fromDict(object_dict)

    def _fromDict(self, object_dict):
        for attr, obj in object_dict.items():

            prop, prop_type = self._get_property_details_for_name(attr)
            value = None
            if inspect.isclass(prop_type) and issubclass(prop_type, Resource):
                resourceType = obj.pop('resourceType')
                class_ = eval_type(resourceType)
                value = class_()._fromDict(obj)
            elif isinstance(obj, dict):
                # Complex type
                value = prop_type()
                value._fromDict(obj)
            elif isinstance(obj, list):
                # Could be a list of dicts or simple values;
                value = []
                for i in obj:
                    if issubclass(prop_type, FHIRBaseObject):
                        value.append(prop_type()._fromDict(i))
                    else:
                        value.append(i)
            elif prop_type is FHIRDate:
                value = obj
            elif obj is not None:
                try:
                    value = prop_type(obj)
                except TypeError:
                    raise PropertyTypeError(type(obj).__name__, prop.definition)

            if value is not None:
                setattr(self, prop.definition.name, value)
        return self

    def dumps(self, format_='json'):
        if format_ in SUPPORTED_FORMATS:
            format_ = format_.upper()
            func = getattr(self, 'to' + format_)
            return func()
        raise UnsupportedFormatError(format_)

    def toJSON(self):
        return json.dumps(self.toDict(), indent=2)

    def toDict(self):
        retval = dict()

        if isinstance(self, Resource):
            retval['resourceType'] = self.__class__.__name__

        for attr in self._get_properties():
            value = getattr(self, attr)

            if isinstance(value, FHIRBaseObject):
                json_dict = value.toDict()
                if json_dict:
                    retval[attr] = json_dict
            elif isinstance(value, PropertyList):
                results = list()
                for v in value:
                    if isinstance(v, FHIRBaseObject):
                        results.append(v.toDict())
                    else:
                        results.append(v)
                if results:
                    retval[attr] = results
            else:
                if value is not None:
                    retval[attr] = value
        return retval


from api_fhir_r4.models.element import Element
from api_fhir_r4.models.quantity import Quantity
from api_fhir_r4.models.resource import Resource
from api_fhir_r4.models.address import Address, AddressType, AddressUse
from api_fhir_r4.models.administrative import AdministrativeGender
from api_fhir_r4.models.age import Age
from api_fhir_r4.models.annotation import Annotation
from api_fhir_r4.models.attachment import Attachment
from api_fhir_r4.models.backboneElement import BackboneElement
from api_fhir_r4.models.coding import Coding
from api_fhir_r4.models.codeableConcept import CodeableConcept
from api_fhir_r4.models.contactPoint import ContactPoint, ContactPointSystem, ContactPointUse
from api_fhir_r4.models.count import Count
from api_fhir_r4.models.distance import Distance
from api_fhir_r4.models.domainResource import DomainResource
from api_fhir_r4.models.duration import Duration
from api_fhir_r4.models.extension import Extension
from api_fhir_r4.models.fhirdate import FHIRDate
from api_fhir_r4.models.humanName import HumanName, NameUse
from api_fhir_r4.models.identifier import Identifier, IdentifierUse
from api_fhir_r4.models.imisModelEnums import ImisMaritalStatus, ImisClaimIcdTypes, ImisLocationType, ImisHfLevel
from api_fhir_r4.models.location import LocationPosition, LocationMode, Location, LocationStatus, \
    LocationHoursOfOperation
from api_fhir_r4.models.meta import Meta
from api_fhir_r4.models.money import Money
from api_fhir_r4.models.narrative import Narrative
from api_fhir_r4.models.patient import Patient, PatientCommunication, PatientContact, PatientLink
from api_fhir_r4.models.period import Period
from api_fhir_r4.models.range import Range
from api_fhir_r4.models.ratio import Ratio
from api_fhir_r4.models.reference import Reference
from api_fhir_r4.models.sampledData import SampledData
from api_fhir_r4.models.signature import Signature
from api_fhir_r4.models.timing import Timing, TimingRepeat
from api_fhir_r4.models.operationOutcome import OperationOutcome, OperationOutcomeIssue, IssueSeverity
from api_fhir_r4.models.daysOfWeek import DaysOfWeek
from api_fhir_r4.models.endpoint import Endpoint
from api_fhir_r4.models.practitionerRole import PractitionerRole, PractitionerAvailableTime, PractitionerNotAvailable
from api_fhir_r4.models.practitioner import Practitioner, PractitionerQualification
from api_fhir_r4.models.bundle import Bundle, BundleEntry, BundleEntryRequest, BundleEntryResponse, BundleEntrySearch, \
    BundleLink, BundleType, BundleLinkRelation
from api_fhir_r4.models.claim import Claim, ClaimAccident, ClaimCareTeam, ClaimDiagnosis, ClaimSupportingInfo, \
    ClaimInsurance, ClaimItem, ClaimItemDetail, ClaimItemDetailSubDetail, ClaimPayee, ClaimProcedure, ClaimRelated
from api_fhir_r4.models.coverageEligibilityRequest import CoverageEligibilityRequest, \
    CoverageEligibilityRequestSupportingInfo, CoverageEligibilityRequestInsurance, CoverageEligibilityRequestItem
from api_fhir_r4.models.coverageEligibilityResponse import CoverageEligibilityResponse, \
    CoverageEligibilityResponseInsurance, CoverageEligibilityResponseInsuranceItem, \
    CoverageEligibilityResponseInsuranceItemBenefit, CoverageEligibilityResponseError
from api_fhir_r4.models.claimResponse import ClaimResponse, ClaimResponseAddItemDetailSubDetail, ClaimResponseError, \
    ClaimResponseItem, ClaimResponseTotal, ClaimResponseAddItem, ClaimResponseAddItemDetail, ClaimResponseInsurance, \
    ClaimResponseItemAdjudication, ClaimResponseItemDetail, ClaimResponseItemDetailSubDetail, ClaimResponsePayment, \
    ClaimResponseProcessNote
from api_fhir_r4.models.communicationRequest import CommunicationRequest, CommunicationRequestPayload
from api_fhir_r4.models.requestStatus import RequestStatus
from api_fhir_r4.models.contract import Contract, ContractFriendly, ContractLegal, ContractRule, ContractSigner, \
    ContractTerm, ContractTermAction, ContractTermAsset, ContractTermOffer, ContractContentDefinition, \
    ContractTermActionSubject, ContractTermAssetContext, ContractTermAssetValuedItem, ContractTermOfferAnswer, \
    ContractTermOfferParty, ContractTermSecurityLabel
from api_fhir_r4.models.coverage import Coverage, CoverageClass, CoverageCostToBeneficiary, \
    CoverageCostToBeneficiaryException
from api_fhir_r4.models.condition import Condition, ConditionClinicalStatusCodes, ConditionEvidence, ConditionStage, \
    ConditionVerificationStatus
from api_fhir_r4.models.medication import MedicationBatch, Medication, MedicationIngredient, MedicationStatusCodes
from api_fhir_r4.models.dosage import Dosage, DosageDoseAndRate
from api_fhir_r4.models.expression import Expression
from api_fhir_r4.models.usageContext import UsageContext, UsageContextType
from api_fhir_r4.models.activityDefinition import ActivityDefinition, ActivityDefinitionDynamicValue, \
    ActivityDefinitionParticipant, PublicationStatus, RequestIntent, RequestPriority, RequestResourceType
from api_fhir_r4.models.contactDetail import ContactDetail
from api_fhir_r4.models.relatedArtifact import RelatedArtifact, RelatedArtifactType
from api_fhir_r4.models.healthcareService import HealthcareNotAvailable, HealthcareService, \
    HealthcareServiceAvailableTime, HealthcareServiceEligibility, DaysOfWeek
