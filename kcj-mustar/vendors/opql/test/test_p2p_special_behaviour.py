import sqlite3
from pathlib import Path

import pytest

import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.ocel.ocellog
import opql.SQLITEResolver


@pytest.fixture(scope="module")
def p2p_log():
    p2p_json_path = Path(__file__).parent / "artifacts" / "ocel-p2p" / "ocel2-p2p.json"
    target_db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    opql.ocel.ocelimport.load_json_file(p2p_json_path, target_db)
    return opql.ocel.ocellog.OCELLog(target_db)


def _run(ocel, q):
    return opql.SQLITEResolver.resolve_query(ocel, opql.lang.querysolver.scan_query(q))


def test_dup_payments(p2p_log):
    result = _run(p2p_log, """
        PATTERN O(invoice:"invoice receipt")
        SUBJECTTO count(
            PATTERN O(invoice)-[]-E(ep:"Execute Payment")
            RETURN ep AS ep
        ) >= 2
        PATTERN O(invoice)-[]-E(ep:"Execute Payment")-[]-O(payment:"payment")
        RETURN invoice AS invoice_id,
               ep AS execute_payment_id,
               ep["ocel_time"] AS execute_payment_time,
               payment AS payment_id,
               payment["AmountDMBTR"@T("1970-01-01T08:41:35.000Z")] AS amount
    """)
    assert result.shape == (427, 5)


def test_dup_payments_total_count(p2p_log):
    result = _run(p2p_log, """
        RETURN count(
            PATTERN O(pm:"payment")
            SUBJECTTO count(
                PATTERN O(pm)-[]-E(ep:"Execute Payment")
                RETURN 0 AS zero
            ) >= 2
            RETURN pm AS affected_payment
        ) AS total_number_of_transgressions
    """)
    assert result.shape == (1, 1)
    assert result["total_number_of_transgressions"].iloc[0] == 188


def test_dup_payments_per_payment_flag(p2p_log):
    result = _run(p2p_log, """
        PATTERN O(pm:"payment")
        RETURN pm AS payment_id,
        count(
            PATTERN O(pm)-[]-E(ep:"Execute Payment")
            RETURN 0 AS zero
        ) >= 2 AS nonConformant
    """)
    assert result.shape == (927, 2)
    assert result[result["nonConformant"]].shape[0] == 188


def test_maverick_buying(p2p_log):
    result = _run(p2p_log, """
        PATTERN E(cgr:"Create Purchase Order")-[]-O(quot:"quotation")-[]-O(pr:"purchase_requisition")
        SUBJECTTO count(PATTERN O(pr)-[]-E(cpr:"Create Purchase Requisition")
                        RETURN cpr AS cpr
        ) == 0
        RETURN cgr AS cgr,
               quot AS quot,
               pr AS pr
    """)
    assert result.shape == (344, 3)


def test_lengthy_approval(p2p_log):
    result = _run(p2p_log, """
        KEEP avg(
            PATTERN E(cpr:"Create Purchase Requisition")-[pr_r]-O(pr:"purchase_requisition")
            KEEP cpr AS cpr, olead(cpr,pr,"Approve Purchase Requisition") AS ap_purch_req
            SUBJECTTO NOT isnone(ap_purch_req)
            RETURN ap_purch_req["ocel_time"] - cpr["ocel_time"] AS approval_duration
        ) AS avg_approval_time,
        stddev(
            PATTERN E(cpr:"Create Purchase Requisition")-[pr_r]-O(pr:"purchase_requisition")
            KEEP cpr AS cpr, olead(cpr,pr,"Approve Purchase Requisition") AS ap_purch_req
            SUBJECTTO NOT isnone(ap_purch_req)
            RETURN ap_purch_req["ocel_time"] - cpr["ocel_time"] AS approval_duration
        ) AS approval_time_stddev
        KEEP *, avg_approval_time + approval_time_stddev AS upper_limit

        PATTERN E(cpr:"Create Purchase Requisition")-[pr_r]-O(pr:"purchase_requisition")
        KEEP upper_limit AS upper_limit, cpr AS cpr, olead(cpr,pr,"Approve Purchase Requisition") AS ap_purch_req
        SUBJECTTO NOT isnone(ap_purch_req)
        RETURN ap_purch_req["ocel_time"] - cpr["ocel_time"] AS approval_duration, 
               approval_duration > upper_limit AS needs_review
    """)
    assert result.shape == (607, 2)
    assert result[result["needs_review"]].shape[0] == 78
