#!/usr/bin/env python3

import webbrowser
from tempfile import NamedTemporaryFile

import OPQL.ocelimport
import OPQL.ocellog
import OPQL.querysolver
import OPQL.SQLITEResolver
from OPQL.ocelimport import make_inmemory_db


def main():
    # Create an in-memory sqlite database to
    target_db = make_inmemory_db()
    # TODO: Edit this to reflect your on disk path!
    sqlite_path = ("/path/to/log/ocel2-p2p.sqlite")

    OPQL.ocelimport.loadSQLITE(sqlite_path, target_db)

    # Create log object to execute query upon.
    log = OPQL.ocellog.OCELLog(target_db)

    # This query returns process instances from the ocel2-p2p log that take longer than average to complete
    query_string = """
    KEEP avg(
        PATTERN E(cpr:"Create Purchase Requisition")-[]-O(pr:"purchase_requisition")
        KEEP cpr AS cpr, olead(cpr,pr,"Approve Purchase Requisition") AS apr
        SUBJECTTO NOT isnone(apr)
        RETURN apr["ocel_time"] - cpr["ocel_time"] AS approval_duration
    ) AS avg_approval_time

    KEEP *, avg_approval_time + D(7,0,0,27.0) AS upper_limit
    PATTERN E(cpr:"Create Purchase Requisition")-[]-O(pr:"purchase_requisition")
    KEEP upper_limit AS upper_limit, cpr AS cpr,
         olead(cpr,pr,"Approve Purchase Requisition") AS apr
    SUBJECTTO NOT isnone(apr)
    RETURN cpr AS creation_id, cpr["ocel_time"] AS creation_time, apr AS approval_id,
           apr["ocel_time"] - cpr["ocel_time"] AS approval_duration,
           upper_limit AS upper_limit,
           approval_duration > upper_limit AS needs_review
    SUBJECTTO needs_review       
    
    """

    query_struct = OPQL.querysolver.scan_query(query_string)

    result = OPQL.SQLITEResolver.resolve_query(log, query_struct)

    print(result)  # noqa: T201

    def df_window(df):
        with NamedTemporaryFile(delete=False, suffix='.html') as f:
            f.write(
                bytes(df.to_html(),'utf-8')
            )

        webbrowser.open(f.name)

    df_window(result)

main()
