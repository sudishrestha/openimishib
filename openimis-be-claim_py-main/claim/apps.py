from django.apps import AppConfig

MODULE_NAME = "claim"

DEFAULT_CFG = {
    "default_validations_disabled": False,
    "gql_query_claims_perms": ["111001"],
    "gql_query_claim_admins_perms": [],
    "gql_query_claim_officers_perms": [],
    "gql_query_claim_diagnosis_variance_only_on_existing": True,
    "gql_mutation_create_claims_perms": ["111002"],
    "gql_mutation_update_claims_perms": ["111010"],
    "gql_mutation_load_claims_perms": ["111005"],
    "gql_mutation_submit_claims_perms": ["111007"],
    "gql_mutation_select_claim_feedback_perms": ["111010"],
    "gql_mutation_bypass_claim_feedback_perms": ["111010"],
    "gql_mutation_skip_claim_feedback_perms": ["111010"],
    "gql_mutation_deliver_claim_feedback_perms": ["111009"],
    "gql_mutation_select_claim_review_perms": ["111010"],
    "gql_mutation_bypass_claim_review_perms": ["111010"],
    "gql_mutation_skip_claim_review_perms": ["111010"],
    "gql_mutation_deliver_claim_review_perms": ["111008"],
    "gql_mutation_process_claims_perms": ["111011"],
    "gql_mutation_delete_claims_perms": ["111004"],
    "claim_print_perms": ["111006"],
    "claim_attachments_root_path": None,
    "claim_uspUpdateClaimFromPhone_intermediate_sets": 2
}


class ClaimConfig(AppConfig):
    name = MODULE_NAME

    default_validations_disabled = False
    gql_query_claims_perms = []
    gql_query_claim_admins_perms = []
    gql_query_claim_officers_perms = []
    gql_query_claim_diagnosis_variance_only_on_existing: True
    gql_mutation_create_claims_perms = []
    gql_mutation_update_claims_perms = []
    gql_mutation_load_claims_perms = []
    gql_mutation_submit_claims_perms = []
    gql_mutation_select_claim_feedback_perms = []
    gql_mutation_bypass_claim_feedback_perms = []
    gql_mutation_skip_claim_feedback_perms = []
    gql_mutation_deliver_claim_feedback_perms = []
    gql_mutation_select_claim_review_perms = []
    gql_mutation_bypass_claim_review_perms = []
    gql_mutation_skip_claim_review_perms = []
    gql_mutation_deliver_claim_review_perms = []
    gql_mutation_process_claims_perms = []
    gql_mutation_delete_claims_perms = []
    claim_print_perms = []
    claim_attachments_root_path = None

    def _configure_perms(self, cfg):
        ClaimConfig.default_validations_disabled = cfg["default_validations_disabled"]
        ClaimConfig.gql_query_claims_perms = cfg["gql_query_claims_perms"]
        ClaimConfig.gql_query_claim_admins_perms = cfg["gql_query_claim_admins_perms"]
        ClaimConfig.gql_query_claim_officers_perms = cfg["gql_query_claim_officers_perms"]
        ClaimConfig.gql_query_claim_diagnosis_variance_only_on_existing = cfg[
            "gql_query_claim_diagnosis_variance_only_on_existing"]
        ClaimConfig.gql_mutation_create_claims_perms = cfg["gql_mutation_create_claims_perms"]
        ClaimConfig.gql_mutation_update_claims_perms = cfg["gql_mutation_update_claims_perms"]
        ClaimConfig.gql_mutation_load_claims_perms = cfg["gql_mutation_load_claims_perms"]
        ClaimConfig.gql_mutation_submit_claims_perms = cfg["gql_mutation_submit_claims_perms"]
        ClaimConfig.gql_mutation_select_claim_feedback_perms = cfg["gql_mutation_select_claim_feedback_perms"]
        ClaimConfig.gql_mutation_bypass_claim_feedback_perms = cfg["gql_mutation_bypass_claim_feedback_perms"]
        ClaimConfig.gql_mutation_skip_claim_feedback_perms = cfg["gql_mutation_skip_claim_feedback_perms"]
        ClaimConfig.gql_mutation_deliver_claim_feedback_perms = cfg["gql_mutation_deliver_claim_feedback_perms"]
        ClaimConfig.gql_mutation_select_claim_review_perms = cfg["gql_mutation_select_claim_review_perms"]
        ClaimConfig.gql_mutation_bypass_claim_review_perms = cfg["gql_mutation_bypass_claim_review_perms"]
        ClaimConfig.gql_mutation_skip_claim_review_perms = cfg["gql_mutation_skip_claim_review_perms"]
        ClaimConfig.gql_mutation_deliver_claim_review_perms = cfg["gql_mutation_deliver_claim_review_perms"]
        ClaimConfig.gql_mutation_process_claims_perms = cfg["gql_mutation_process_claims_perms"]
        ClaimConfig.gql_mutation_delete_claims_perms = cfg["gql_mutation_delete_claims_perms"]
        ClaimConfig.claim_print_perms = cfg["claim_print_perms"]
        ClaimConfig.claim_attachments_root_path = cfg["claim_attachments_root_path"]
        ClaimConfig.claim_uspUpdateClaimFromPhone_intermediate_sets = \
            cfg["claim_uspUpdateClaimFromPhone_intermediate_sets"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_perms(cfg)
