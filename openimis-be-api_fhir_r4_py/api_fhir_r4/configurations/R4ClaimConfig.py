from api_fhir_r4.configurations import ClaimConfiguration


class R4ClaimConfig(ClaimConfiguration):

    @classmethod
    def build_configuration(cls, cfg):
        cls.get_config().R4_fhir_claim_config = cfg['R4_fhir_claim_config']

    @classmethod
    def get_fhir_claim_information_guarantee_id_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_information_guarantee_id_code', "guarantee_id")

    @classmethod
    def get_fhir_claim_information_explanation_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_information_explanation_code', "explanation")

    @classmethod
    def get_fhir_claim_item_explanation_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_item_explanation_code', "item_explanation")

    @classmethod
    def get_fhir_claim_item_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_item_code', "item")

    @classmethod
    def get_fhir_claim_service_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_service_code', "service")

    @classmethod
    def get_fhir_claim_status_rejected_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_status_rejected_code', "rejected")

    @classmethod
    def get_fhir_claim_status_entered_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_status_entered_code', "entered")

    @classmethod
    def get_fhir_claim_status_checked_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_status_checked_code', "checked")

    @classmethod
    def get_fhir_claim_status_processed_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_status_processed_code', "processed")

    @classmethod
    def get_fhir_claim_status_valuated_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_status_valuated_code', "valuated")

    @classmethod
    def get_fhir_claim_item_status_passed_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_item_status_passed_code', "passed")

    @classmethod
    def get_fhir_claim_item_status_rejected_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_item_status_rejected_code', "rejected")

    @classmethod
    def get_fhir_claim_item_general_adjudication_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_item_general_adjudication_code', "general")

    @classmethod
    def get_fhir_claim_item_rejected_reason_adjudication_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_item_rejected_reason_adjudication_code',
                                                         "rejected_reason")

    @classmethod
    def get_fhir_claim_organization_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_organization_code', "openIMIS")  # has to be updated when 'Organization' is created

    @classmethod
    def get_fhir_claim_attachment_code(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_attachment_code', "attachment")

    @classmethod
    def get_fhir_claim_attachment_system(cls):
        return cls.get_config().R4_fhir_claim_config.get('fhir_claim_information_category_system',
                                                         "http://terminology.hl7.org/CodeSystem/claiminformationcategory")

    @classmethod
    def get_allowed_fhir_claim_attachment_mime_types_regex(cls):
        return cls.get_config().R4_fhir_claim_config.get(
            'fhir_claim_allowed_mime_types_regex',
            '|'.join(['text\/.*', 'image\/png', 'image\/jpe?g', 'application\/msword', '.*doc.*'])
        )
