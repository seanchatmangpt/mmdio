import sqlite3
from pathlib import Path

import pytest

import opql.lang.querysolver
import opql.ocel.ocelimport
import opql.ocel.ocellog
import opql.SQLITEResolver

query = """
PATTERN E(event:"Create Goods Receipt")-[]-O(whatever)
SUBJECTTO event["ocel_time"] > T("2022-05-25T08:41:35.000Z") AND event["ocel_time"] < T("2022-08-25T08:41:35.000Z")
RETURN
event["ocel_id"] AS event_id, event["ocel_time"] AS event_time, event["ocel_type"] AS event_type, 
event["resource"] AS event_resource,
whatever["ocel_id"] AS whatever_id, whatever["ocel_type"] AS whatever_type
"""

query_filter = """
PATTERN  E(event:"Create Goods Receipt")-[]-O(whatever)
SUBJECTTO event["ocel_time"] < T("2022-05-25T08:41:35.000Z") OR event["ocel_time"] > T("2022-08-25T08:41:35.000Z")
FILTER event
PATTERN  E(event:"Create Goods Receipt")-[nextref]-O(whatever)-[notherref]-O(notherob)
RETURN event AS ev_id, 
       nextref AS nref_qual, 
       whatever AS whev_id, 
       notherref AS nothref_qual, 
       notherob AS notherob_id
"""

query_keep = """
PATTERN E(event:"Create Goods Receipt")-[]-O(whatever)
SUBJECTTO event["ocel_time"] > T("2022-05-25T08:41:35.000Z") AND event["ocel_time"] < T("2022-08-25T08:41:35.000Z")
KEEP event["ocel_id"] AS eventId, whatever AS whatever_id
RETURN eventId AS ev_id, whatever_id AS w_id
"""

query_dup_pay = """
PATTERN O(paym:"payment")-[]-E(event:"Execute Payment")-[ref_a]-O(gr1:"goods receipt"),
O(paym)-[]-E(event2:"Execute Payment")-[]-O(gr1)
SUBJECTTO event2["ocel_id"] != event["ocel_id"]
RETURN paym["ocel_id"] AS paym_id,
       paym["AmountDMBTR"@event] AS paym_am_dmbtr,
       event["ocel_id"] AS ev_id,
       gr1["ocel_id"] AS gr1_id
"""

query_dup_pay2 = """
PATTERN O(in_rec:"invoice receipt")-[]-E(event:"Execute Payment"),
O(in_rec)-[]-E(event2:"Execute Payment")
SUBJECTTO event2["ocel_id"] != event["ocel_id"]
RETURN in_rec["ocel_id"] AS ir_id, event["ocel_id"] AS ev_id, event["ocel_time"] AS ev_time,
       event2["ocel_id"] AS ev2_id, event2["ocel_time"] AS ev2_time
"""

# query_l_a_p = """
# PATTERN E(cr_purch_req:"Create Purchase Requisition")-[pr_rel:"purchase_requisition"]-O(pr:"purchase_requisition")
#                                       -[prr2:"purchase_requisition"]-E(ap_purch_req:"Approve Purchase Requisition")
# SUBJECTTO ap_purch_req["ocel_time"] - cr_purch_req["ocel_time"] > D("P0Y0M3DT12H00M0S")
# RETURN cr_purch_req["ocel_time"], ap_purch_req["ocel_time"]
# """

query_mat_agg = """
PATTERN E(apr:"Approve Purchase Requisition")

KEEP
apr AS keptApr,
count(
    PATTERN E(apr)-[]-O(smat:"material")
    RETURN smat["NetPriceEKPONETPR"@apr] AS netprice
) AS mat_count
ORDERBY apr["ocel_id"] ASC, mat_count DESC, keptApr["ocel_time"] ASC

RETURN
keptApr["ocel_id"] AS id,
mat_count AS mc,
keptApr["ocel_time"] AS DTS

"""

query_ordering = """
 PATTERN E(apr:"Approve Purchase Requisition")-[]-O(smat:"material")

 KEEP
 apr AS keptApr,
 smat["NetPriceEKPONETPR"@apr] AS netprice
 ORDERBY keptApr["ocel_time"] ASC, netprice DESC

 RETURN
 keptApr["ocel_id"] AS id,
 netprice AS netprice

 """

query_lag_lead = """
 PATTERN E(apo:"Approve Purchase Order")-[]-O(p_o:"purchase_order")
 
 KEEP DISTINCT olag(apo, p_o) AS previous, 
               apo AS event, 
               olead(apo, p_o) AS next
               
 RETURN previous["ocel_id"] AS pid, 
        previous["ocel_time"] AS pt,
        apo["ocel_id"] AS apoid, 
        apo["ocel_time"] AS apot,
        next["ocel_id"] AS nid, 
        next["ocel_time"] AS nt
 """

query_mat_avg_price = """
PATTERN E(apr:"Approve Purchase Requisition")

KEEP
apr AS keptApr,
avg(
    PATTERN E(apr)-[]-O(smat:"material")
    RETURN smat["NetPriceEKPONETPR"@apr] AS netprice
) AS mat_avg ORDERBY apr["ocel_id"] ASC, mat_avg DESC, keptApr["ocel_time"] ASC

RETURN
keptApr["ocel_id"] AS id,
mat_avg AS m_a,
keptApr["ocel_time"] AS DTS

"""

query_filter_ocel = """
PATTERN E(event:"Create Goods Receipt")-[]-O(whatever)
SUBJECTTO event["ocel_time"] < T("2022-05-25T08:41:35.000Z") OR event["ocel_time"] > T("2022-08-25T08:41:35.000Z")
FILTER event
PATTERN E(event:"Create Goods Receipt")-[]-O(whatever)-[notherref]-O(notherob)
RETURN OCEL
"""

# TODO check and reenable
#
# (query_when,(4514,2)),
#
# query_when = """
# PATTERN O(i_r:"invoice receipt")
# KEEP i_r AS i_r
# WHEN i_r["CreditAmountBSEGWRBTR"@eq_am_ts] == i_r["DebitAmountBSEGDMBTR"@eq_am_ts] AS eq_am_ts
# RETURN i_r["ocel_id"] AS ir_id, eq_am_ts AS eq_am_ts
# """

query_mat_agg = """
 PATTERN E(apr:"Approve Purchase Requisition")-[]-O(obj:"material")

 KEEP
 apr AS keptApr,
 count(
     PATTERN E(apr)-[]-O(smat:"material")
     RETURN smat["NetPriceEKPONETPR"@apr] AS netprice
 ) AS mat_count ORDERBY apr["ocel_id"] ASC, mat_count DESC, keptApr["ocel_time"] ASC

 RETURN
 keptApr["ocel_id"] AS id,
 mat_count AS mc,
 keptApr["ocel_time"] AS DTS

 """

query_olag = """
 PATTERN E(apr:"Approve Purchase Requisition")-[]-O(obj:"material")

 RETURN
 olag(apr,obj) AS simplelag,
 olag(apr,obj,"Create Purchase Requisition") AS typelag,
 olag(apr,obj,0) AS posoffsetlag
 """

query_olead = """
 PATTERN E(apr:"Create Purchase Requisition")-[]-O(obj:"material")

 RETURN
 olead(apr,obj) AS simplelead,
 olead(apr,obj,"Approve Purchase Requisition") AS typelead,
 olead(apr,obj,0) AS posoffsetlead
 """

#  apr["ocel_id"] ASC, mat_count DESC, keptApr["ocel_time"] ASC
# should return 607 rows (num of apr events)
query_mat_distinct_binning = """
 PATTERN E(apr:"Approve Purchase Requisition")-[]-O(obj:"material")

 KEEP DISTINCT
 apr AS keptApr,
 count(
     PATTERN E(apr)-[]-O(smat:"material")
     RETURN smat["NetPriceEKPONETPR"@apr] AS netprice
 )
 AS mat_count BINNED( [1,2) AS "A_LOW", [2,3) AS "B_MID", [3,999] AS "C_HIGH" )
 ORDERBY mat_count DESC

 RETURN
 keptApr["ocel_id"] AS id,
 mat_count AS mc,
 keptApr["ocel_time"] AS DTS
 """

@pytest.mark.parametrize("query, expected_result",
    [
        (query, (872,6)),
        (query_keep,(872,2)),
        (query_dup_pay,(1224,4)),
        (query_dup_pay2,(600,5)),
        (query_mat_agg,(1499,3)),
        (query_mat_avg_price,(607,3)),
        (query_ordering,(1499,2)),
        (query_mat_distinct_binning,(607,3)),
    ])
def test_p2p(p2p_log_fixture, query, expected_result):
    query_struct = opql.lang.querysolver.scan_query(query)

    result = opql.SQLITEResolver.resolve_query(p2p_log_fixture, query_struct)
    assert "Error" not in str(result)
    assert result.shape == expected_result
    #return log, result

# TODO: query_l_a_p
# TODO: 'str' object has no attribute 'ocel_id': query_lag_lead, query_mat_agg, query_olead, query_olag

def test_p2p_filter(p2p_log_mutable):
    """FILTER removes the matched events from the log.

    Expected values were derived independently of the engine (raw SQL + set
    logic over event/event_object/object_object, joined against the entity
    tables since dangling relation rows cannot bind): 3606 of the 4042
    "Create Goods Receipt" events lie outside the SUBJECTTO window and get
    deleted; the second PATTERN over the filtered log then yields 3333 rows.
    FILTER only removes the bound entities and their relations - objects are
    never deleted when filtering an event symbol.

    (An older pinned value of (31177, 5) was recorded while FILTER was a
    silent no-op, i.e. against the unfiltered log.)
    """
    events_before = p2p_log_mutable.numEvents()
    objects_before = p2p_log_mutable.numObjects()

    query_struct = opql.lang.querysolver.scan_query(query_filter)
    result = opql.SQLITEResolver.resolve_query(p2p_log_mutable, query_struct)

    assert events_before - p2p_log_mutable.numEvents() == 3606
    assert objects_before - p2p_log_mutable.numObjects() == 0
    assert result.shape == (3333, 5)


# These queries return an object that is expected to be of a specific type.
# query_filter_ocel mutates the log, hence the function-scoped fixture.
@pytest.mark.parametrize("query, expected_type", [(query_filter_ocel,sqlite3.Connection)])
def test_connection(p2p_log_mutable, query, expected_type):
    query_struct = opql.lang.querysolver.scan_query(query)

    result = opql.SQLITEResolver.resolve_query(p2p_log_mutable, query_struct)
    assert isinstance(result, expected_type)


def _load_p2p_log():
    p2p_json_path = Path(__file__).parent / "artifacts" / "ocel-p2p" / "ocel2-p2p.json"

    target_db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    opql.ocel.ocelimport.load_json_file(p2p_json_path, target_db)
    log = opql.ocel.ocellog.OCELLog(target_db)
    return log


# shared by the read-only queries; tests must not mutate this log
@pytest.fixture(scope="module")
def p2p_log_fixture():
    return _load_p2p_log()


# fresh log per test for queries that FILTER (i.e. mutate) the log
@pytest.fixture
def p2p_log_mutable():
    return _load_p2p_log()



