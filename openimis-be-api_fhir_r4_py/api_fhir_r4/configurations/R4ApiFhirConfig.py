from api_fhir_r4.configurations import BaseApiFhirConfiguration, R4IdentifierConfig, \
    R4LocationConfig, R4MaritalConfig, R4IssueTypeConfig, R4ClaimConfig, R4CoverageEligibilityConfiguration, \
    R4CommunicationRequestConfig
from api_fhir_r4.configurations.R4CoverageConfig import R4CoverageConfig


class R4ApiFhirConfig(BaseApiFhirConfiguration):

    @classmethod
    def get_identifier_configuration(cls):
        return R4IdentifierConfig

    @classmethod
    def get_location_type_configuration(cls):
        return R4LocationConfig

    @classmethod
    def get_marital_type_configuration(cls):
        return R4MaritalConfig

    @classmethod
    def get_issue_type_configuration(cls):
        return R4IssueTypeConfig

    @classmethod
    def get_claim_configuration(cls):
        return R4ClaimConfig

    @classmethod
    def get_coverage_eligibility_configuration(cls):
        return R4CoverageEligibilityConfiguration

    @classmethod
    def get_communication_request_configuration(cls):
        return R4CommunicationRequestConfig

    @classmethod
    def get_coverage_configuration(cls):
        return R4CoverageConfig
