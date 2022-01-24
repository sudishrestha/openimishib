import xml.etree.ElementTree as ET
from django.core.exceptions import PermissionDenied
import core
from django.db import connection
from gettext import gettext as _

from .apps import ClaimConfig
from django.conf import settings


@core.comparable
class ClaimElementSubmit(object):
    def __init__(self, type, code, quantity, price=None):
        self.type = type
        self.code = code
        self.price = price
        self.quantity = quantity

    def add_to_xmlelt(self, xmlelt):
        item = ET.SubElement(xmlelt, self.type)
        ET.SubElement(item, "%sCode" % self.type).text = "%s" % self.code
        if self.price:
            ET.SubElement(item, "%sPrice" % self.type).text = "%s" % self.price
        ET.SubElement(item, "%sQuantity" %
                      self.type).text = "%s" % self.quantity


@core.comparable
class ClaimItemSubmit(ClaimElementSubmit):
    def __init__(self, code, quantity, price=None):
        super().__init__(type='Item',
                         code=code,
                         price=price,
                         quantity=quantity)


@core.comparable
class ClaimServiceSubmit(ClaimElementSubmit):
    def __init__(self, code, quantity, price=None):
        super().__init__(type='Service',
                         code=code,
                         price=price,
                         quantity=quantity)


@core.comparable
class ClaimSubmit(object):
    def __init__(self, date, code, icd_code, total, start_date,
                 insuree_chf_id, health_facility_code,
                 claim_admin_code,
                 item_submits=None, service_submits=None,
                 end_date=None,
                 icd_code_1=None, icd_code_2=None, icd_code_3=None, icd_code_4=None,
                 visit_type=None, guarantee_no=None,
                 comment=None,
                 nmcNo=None
                 ):
        self.date = date
        self.code = code
        self.icd_code = icd_code
        self.total = total
        self.start_date = start_date
        self.insuree_chf_id = insuree_chf_id
        self.health_facility_code = health_facility_code
        self.end_date = end_date
        self.icd_code_1 = icd_code_1
        self.icd_code_2 = icd_code_2
        self.icd_code_3 = icd_code_3
        self.icd_code_4 = icd_code_4
        self.claim_admin_code = claim_admin_code
        self.visit_type = visit_type
        self.guarantee_no = guarantee_no
        self.comment = comment
        self.items = item_submits
        self.services = service_submits
        self.nmcNo=nmcNo

    def _details_to_xmlelt(self, xmlelt):
        ET.SubElement(xmlelt, 'ClaimDate').text = self.date.to_ad_date().strftime(
            "%d/%m/%Y")
        ET.SubElement(
            xmlelt, 'HFCode').text = "%s" % self.health_facility_code
        if self.claim_admin_code:
            ET.SubElement(
                xmlelt, 'ClaimAdmin').text = "%s" % self.claim_admin_code
        ET.SubElement(xmlelt, 'ClaimCode').text = "%s" % self.code
        ET.SubElement(xmlelt, 'CHFID').text = "%s" % self.insuree_chf_id
        ET.SubElement(
            xmlelt, 'StartDate').text = self.start_date.to_ad_date().strftime("%d/%m/%Y")
        if self.end_date:
            ET.SubElement(xmlelt, 'EndDate').text = self.end_date.to_ad_date().strftime(
                "%d/%m/%Y")
        ET.SubElement(xmlelt, 'ICDCode').text = "%s" % self.icd_code
        if self.comment:
            ET.SubElement(xmlelt, 'Comment').text = "%s" % self.comment
        if self.nmcNo:
            ET.SubElement(xmlelt, 'nmcNo').text = "%s" % self.nmcNo
        ET.SubElement(xmlelt, 'Total').text = "%s" % self.total
        if self.icd_code_1:
            ET.SubElement(xmlelt, 'ICDCode1').text = "%s" % self.icd_code_1
        if self.icd_code_2:
            ET.SubElement(xmlelt, 'ICDCode2').text = "%s" % self.icd_code_2
        if self.icd_code_3:
            ET.SubElement(xmlelt, 'ICDCode3').text = "%s" % self.icd_code_3
        if self.icd_code_4:
            ET.SubElement(xmlelt, 'ICDCode4').text = "%s" % self.icd_code_4
        if self.visit_type:
            ET.SubElement(xmlelt, 'VisitType').text = "%s" % self.visit_type
        if self.guarantee_no:
            ET.SubElement(
                xmlelt, 'GuaranteeNo').text = "%s" % self.guarantee_no

    def add_elt_list_to_xmlelt(self, xmlelt, elts_name, elts):
        if elts and len(elts) > 0:
            elts_xml = ET.SubElement(xmlelt, elts_name)
            for item in elts:
                item.add_to_xmlelt(elts_xml)

    def add_to_xmlelt(self, xmlelt):
        details = ET.SubElement(xmlelt, 'Details')
        self._details_to_xmlelt(details)
        self.add_elt_list_to_xmlelt(xmlelt, 'Items', self.items)
        self.add_elt_list_to_xmlelt(xmlelt, 'Services', self.services)

    def to_xml(self):
        claim_xml = ET.Element('Claim')
        self.add_to_xmlelt(claim_xml)
        return ET.tostring(claim_xml, encoding='utf-8', method='xml').decode()


@core.comparable
class ClaimSubmitError(Exception):
    ERROR_CODES = {
        -1: "Fatal Error",
        1: "Invalid HF Code",
        2: "Duplicate Claim Code",
        3: "Invalid Insuree CHFID",
        4: "End date is smaller than start date",
        5: "Invalid ICDCode",
        6: "Claimed amount is 0",
        7: "Invalid ItemCode",
        8: "Invalid ServiceCode",
        9: "Invalid Claim Admin",
    }

    def __init__(self, code, msg=None):
        self.code = code
        self.msg = ClaimSubmitError.ERROR_CODES.get(
            self.code, msg or "Unknown exception")

    def __str__(self):
        return "ClaimSubmitError %s: %s" % (self.code, self.msg)


class ClaimSubmitService(object):

    def __init__(self, user):
        self.user = user

    def hf_scope_check(self, claim_submit):
        from location.models import UserDistrict, HealthFacility
        dist = UserDistrict.get_user_districts(self.user._u)
        hf = HealthFacility.filter_queryset()\
            .filter(code=claim_submit.health_facility_code)\
            .filter(location_id__in=[l.location_id for l in dist])\
            .first()
        if not hf and settings.ROW_SECURITY:
            raise ClaimSubmitError("Invalid health facility code or health facility not allowed for user")

    def submit(self, claim_submit):
        self.hf_scope_check(claim_submit)
        with connection.cursor() as cur:
            sql = """\
                DECLARE @ret int;
                EXEC @ret = [dbo].[uspUpdateClaimFromPhone] @XML = %s;
                SELECT @ret;
            """

            cur.execute(sql, (claim_submit.to_xml(),))
            for i in range(int(ClaimConfig.claim_uspUpdateClaimFromPhone_intermediate_sets)):
                cur.nextset()
            if cur.description is None:  # 0 is considered as 'no result' by pyodbc
                return
            res = cur.fetchone()[0]  # FETCH 'SELECT @ret' returned value
            raise ClaimSubmitError(res)


def formatClaimService(s):
    return {
        "service": str(s.service),
        "quantity": s.qty_provided,
        "price": s.price_asked,
        "explanation": s.explanation
    }


def formatClaimItem(i):
    return {
        "item": str(i.item),
        "quantity": i.qty_provided,
        "price": i.price_asked,
        "explanation": i.explanation
    }


class ClaimReportService(object):
    def __init__(self, user):
        self.user = user

    def fetch(self, uuid):
        from .models import Claim
        queryset = Claim.objects.filter(*core.filter_validity())
        if settings.ROW_SECURITY:
            from location.models import UserDistrict
            dist = UserDistrict.get_user_districts(self.user._u)
            queryset = queryset.filter(
                health_facility__location__id__in=[l.location_id for l in dist]
            )
        claim = queryset\
            .select_related('health_facility') \
            .select_related('insuree') \
            .filter(uuid=uuid)\
            .first()
        if not claim:
            raise PermissionDenied(_("unauthorized"))
        return {
            "code": claim.code,
            "visitDateFrom": claim.date_from.isoformat() if claim.date_from else None,
            "visitDateTo":  claim.date_to.isoformat() if claim.date_to else None,
            "claimDate": claim.date_claimed.isoformat() if claim.date_claimed else None,
            "healthFacility": str(claim.health_facility),
            "insuree": str(claim.insuree),
            "claimAdmin": str(claim.admin) if claim.admin else None,
            "icd": str(claim.icd),
            "icd1": str(claim.icd1) if claim.icd_1 else None,
            "icd2": str(claim.icd1) if claim.icd_2 else None,
            "icd3": str(claim.icd1) if claim.icd_3 else None,
            "icd4": str(claim.icd1) if claim.icd_4 else None,
            "guarantee": claim.guarantee_id,
            "visitType": claim.visit_type,
            "claimed": claim.claimed,
            "services": [formatClaimService(s) for s in claim.services.all()],
            "items": [formatClaimItem(i) for i in claim.items.all()],
        }
