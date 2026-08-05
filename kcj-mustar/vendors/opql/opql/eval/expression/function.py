import datetime
import logging
from collections.abc import Callable

import pandas

from opql.exceptions import OPQLEvalError, OPQLTypeError

logger = logging.getLogger(__name__)

_REGISTRY: dict[str, Callable] = {}


def register_function(name: str, impl: Callable) -> None:
    """Register a custom OPQL function.

    impl must have the signature: (ocel, context, args: list) -> Any.
    Built-in scalar functions ignore ocel and context; OCEL-aware functions may use them.
    Registering under an existing name replaces the previous implementation.
    """
    _REGISTRY[name] = impl


def _register(name: str):
    def decorator(fn):
        _REGISTRY[name] = fn
        return fn
    return decorator


def normalize_type(rval):
    # pandas wraps Python scalars; unwrap them so callers work with native types
    if isinstance(rval, pandas.Timedelta):
        return rval.to_pytimedelta()
    if isinstance(rval, pandas.Timestamp):
        return rval.to_pydatetime()
    return rval


def _require_args(f_name: str, args: list, count: int) -> None:
    if len(args) != count:
        raise OPQLEvalError(
            f"{f_name}() requires exactly {count} argument(s), got {len(args)}"
        )


def _require_min_args(f_name: str, args: list, minimum: int) -> None:
    if len(args) < minimum:
        raise OPQLEvalError(
            f"{f_name}() requires at least {minimum} argument(s), got {len(args)}"
        )


def _require_dataframe(f_name: str, arg) -> None:
    if not isinstance(arg, pandas.DataFrame):
        raise OPQLTypeError(
            f"{f_name}() requires a subquery result (DataFrame),"
            f" got {type(arg).__name__}"
        )


def _require_datetime(f_name: str, arg) -> None:
    if not isinstance(arg, datetime.datetime):
        raise OPQLTypeError(
            f"{f_name}() requires a datetime value, got {type(arg).__name__}"
        )


# --- null ---

@_register("isnone")
def _isnone(ocel, context, args):
    _require_args("isnone", args, 1)
    return args[0] is None


# --- aggregates ---

@_register("count")
def _count(ocel, context, args):
    _require_args("count", args, 1)
    _require_dataframe("count", args[0])
    return args[0].shape[0]


@_register("avg")
def _avg(ocel, context, args):
    _require_args("avg", args, 1)
    _require_dataframe("avg", args[0])
    return normalize_type(args[0].mean().iloc[0])


@_register("median")
def _median(ocel, context, args):
    _require_args("median", args, 1)
    _require_dataframe("median", args[0])
    return normalize_type(args[0].median()[0])


@_register("sum")
def _sum(ocel, context, args):
    _require_args("sum", args, 1)
    _require_dataframe("sum", args[0])
    return normalize_type(args[0].sum()[0])


@_register("stddev")
def _stddev(ocel, context, args):
    _require_args("stddev", args, 1)
    _require_dataframe("stddev", args[0])
    return normalize_type(args[0].std().iloc[0])


@_register("max")
def _max(ocel, context, args):
    _require_args("max", args, 1)
    _require_dataframe("max", args[0])
    return normalize_type(args[0].max()[0])


@_register("min")
def _min(ocel, context, args):
    _require_args("min", args, 1)
    _require_dataframe("min", args[0])
    return normalize_type(args[0].min()[0])


# --- OCEL-specific ---

def _olaglead_impl(ocel, args: list, lag: bool):
    _require_min_args("olead/olag", args, 2)
    event = args[0]
    object_ = args[1]
    offset = 0
    etype = None
    if len(args) == 3:
        if isinstance(args[2], str):
            etype = args[2]
        elif isinstance(args[2], int):
            offset = args[2]
    result = ocel.olaglead(event, object_, lag, offset, etype)
    return result or None


@_register("olag")
def _olag(ocel, context, args):
    return _olaglead_impl(ocel, args, lag=True)


@_register("olead")
def _olead(ocel, context, args):
    return _olaglead_impl(ocel, args, lag=False)


# --- scalar / math ---

@_register("abs")
def _abs(ocel, context, args):
    _require_args("abs", args, 1)
    arg = args[0]
    if not isinstance(arg, int | float | datetime.timedelta):
        raise OPQLTypeError(
            f"abs() requires a numeric or duration value, got {type(arg).__name__}"
        )
    return abs(arg)


# --- datetime extraction ---
# The grammar allows an optional second timezone-string argument; it is accepted
# but ignored here — timestamps are already stored with timezone info.

@_register("day")
def _day(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"day() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("day", args[0])
    return args[0].day


@_register("month")
def _month(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"month() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("month", args[0])
    return args[0].month


@_register("year")
def _year(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"year() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("year", args[0])
    return args[0].year


@_register("hour")
def _hour(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"hour() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("hour", args[0])
    return args[0].hour


@_register("minute")
def _minute(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"minute() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("minute", args[0])
    return args[0].minute


@_register("second")
def _second(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"second() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("second", args[0])
    return args[0].second


@_register("dayOfWeek")
def _day_of_week(ocel, context, args):
    if len(args) not in (1, 2):
        raise OPQLEvalError(f"dayOfWeek() requires 1 or 2 arguments, got {len(args)}")
    _require_datetime("dayOfWeek", args[0])
    # Monday = 0, Sunday = 6 (Python datetime.weekday() convention)
    return args[0].weekday()


# --- dispatch ---

def evaluate_function(ocel, context, f_name: str, f_args: list):
    impl = _REGISTRY.get(f_name)
    if impl is None:
        raise OPQLEvalError(f"Unknown function: {f_name!r}")
    return impl(ocel, context, f_args)
