#!/usr/bin/env python3

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

import opql.lang.querysolver
import opql.ocel.ocellog
import opql.SQLITEResolver
from opql.exceptions import OPQLError
from opql.ocel.ocelimport import make_inmemory_db

logger = logging.getLogger(__name__)

OUTPUT_FORMAT_CSV = "csv"
OUTPUT_FORMAT_EXCEL = "xlsx"
OUTPUT_FORMAT_PICKLE = "pickle"
OUTPUT_FORMAT_HTML = "html"

def copy_db(source_db, target_db):
    query = "".join(line for line in source_db.iterdump())
    target_db.executescript(query)

def parse_args():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("ocelfile", type=str, help="OCEL 2.0 file in sqlite3 format")
    arg_parser.add_argument("queryfile", type=str, help="Text file containing a query", nargs='+')

    arg_parser.add_argument("-tof", "--tableoutformat", type=str,
                            choices=[OUTPUT_FORMAT_CSV, OUTPUT_FORMAT_EXCEL, OUTPUT_FORMAT_PICKLE, OUTPUT_FORMAT_HTML],
                            help="output format for tabular returns", default=OUTPUT_FORMAT_CSV)
    arg_parser.add_argument("-sep", "--seperator", type=str, default=",",
                            help="seperator for CSV output")
    arg_parser.add_argument("-v", "--verbose", action="store_true",
                            help="enable verbose logging (INFO level)")

    return arg_parser.parse_args()


def main():
    arguments = parse_args()

    log_level = logging.INFO if arguments.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    logger.info("OCEL: %s", arguments.ocelfile)
    logger.info("Output format: %s", arguments.tableoutformat)
    if arguments.tableoutformat == OUTPUT_FORMAT_CSV:
        logger.info("Separator char: %s", arguments.seperator)

    try:
        input_ocel = sqlite3.connect(arguments.ocelfile, detect_types=sqlite3.PARSE_DECLTYPES)
        dump = "".join(line for line in input_ocel.iterdump())

        for query_file_path in arguments.queryfile:
            with Path(query_file_path).open() as query_file:
                logger.info("Running query: %s", query_file_path)
                query_string = query_file.read()

                log_db = make_inmemory_db()
                log_db.executescript(dump)

                log = opql.ocel.ocellog.OCELLog(log_db)
                query_struct = opql.lang.querysolver.scan_query(query_string)
                result = opql.SQLITEResolver.resolve_query(log, query_struct)

                print(result)  # noqa: T201

                outfilepath = query_file_path + "." + arguments.tableoutformat

                if arguments.tableoutformat == OUTPUT_FORMAT_CSV:
                    result.to_csv(outfilepath, sep=arguments.seperator)
                elif arguments.tableoutformat == OUTPUT_FORMAT_EXCEL:
                    result.to_excel(outfilepath)
                elif arguments.tableoutformat == OUTPUT_FORMAT_PICKLE:
                    result.to_pickle(outfilepath)
                elif arguments.tableoutformat == OUTPUT_FORMAT_HTML:
                    result.to_html(outfilepath)

    except OPQLError as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        sys.exit(1)


if __name__ == '__main__':
    main()
