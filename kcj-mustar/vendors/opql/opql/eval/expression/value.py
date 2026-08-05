import datetime
import logging

import opql.eval.querycontext
import opql.lang.query
import opql.ocel.ocellog
from opql.exceptions import OPQLEvalError, OPQLTypeError

logger = logging.getLogger(__name__)

# looks up to what value a symbolic name is bound in a context
def get_value(ocel: opql.ocel.ocellog.OCELLog, context, var_ref: opql.lang.query.ValueReference):
    if var_ref is None:
        logger.warning("get_value called with var_ref=None")
        return None
    if var_ref.name is None:
        return None

    context_binding = context.lookupSymbol(var_ref.name)

    if context_binding is None:
        # print(f"Error: Symbol {var_ref.name} could not be resolved.")
        return None

    if isinstance(context_binding, opql.eval.querycontext.ContextEvent):
        if var_ref.timestamp:
            logger.warning("Event properties do not support evaluation timestamps — ignoring")

        if var_ref.property == "ocel_id":
            return context_binding.ocel_id

        event_binding: opql.eval.querycontext.ContextEvent = context_binding
        event = ocel.getEvent(event_binding.ocel_id)

        if not var_ref.property:
            return context_binding.ocel_id

        if event is None:
            return None

        if var_ref.property == "ocel_type":
            return event.getType()

        val = event.getPropertyValue(var_ref.property)

        return val

    if isinstance(context_binding, opql.eval.querycontext.ContextObject):
        object_binding: opql.eval.querycontext.ContextObject = context_binding

        if not var_ref.property:
            return object_binding.ocel_id

        if var_ref.property == "ocel_id":
            return context_binding.ocel_id

        if var_ref.property == "ocel_type":
            return context_binding.ocel_type

        if not var_ref.timestamp:
            raise OPQLEvalError("Object property lookup requires a timestamp (except ocel_id and ocel_type)")

        ocelobject = ocel.getObject(object_binding.ocel_id)
        if ocelobject is None:
            return None

        # if timestamp is actual timestamp, go on, if its event, lookup event time and use that
        # if type(timestamp)
        version_ts = None
        if isinstance(var_ref.timestamp, datetime.datetime):
            version_ts = var_ref.timestamp
        elif isinstance(var_ref.timestamp, str):
            # if string, must be reference to event
            ctx_entity = context.lookupSymbol(var_ref.timestamp)
            if not isinstance(ctx_entity, opql.eval.querycontext.ContextEvent):
                raise OPQLTypeError(f"Symbol {var_ref.timestamp!r} is not an event; cannot infer timestamp")

            ctx_event: opql.eval.querycontext.ContextEvent = ctx_entity
            event = ocel.getEvent(ctx_event.ocel_id)
            if event is None:
                return None
            version_ts = event.getPropertyValue("ocel_time")
        else:
            raise OPQLTypeError(
                f"Invalid version timestamp {var_ref.timestamp!r} for property {var_ref.name}.{var_ref.property}"
            )

        value = ocelobject.getPropertyValue(var_ref.property, version_ts)

        return value

    if isinstance(context_binding, opql.eval.querycontext.ContextOORelation):
        ctxb: opql.eval.querycontext.ContextOORelation = context_binding
        if var_ref.property == "qualifier":
            return ctxb.ocel_qualifier

        raise OPQLEvalError(f"Cannot evaluate OO-relation context for {var_ref}")

    if isinstance(context_binding, opql.eval.querycontext.ContextEORelation):
        ctxb: opql.eval.querycontext.ContextEORelation = context_binding
        if var_ref.property == "qualifier":
            return ctxb.ocel_qualifier

        if var_ref.property is None and var_ref.timestamp is None:
            return ctxb.ocel_qualifier

        raise OPQLEvalError(f"Cannot evaluate EO-relation context for {var_ref}")

    if isinstance(context_binding, opql.eval.querycontext.ContextGraphBegin):
        ctxb: opql.eval.querycontext.ContextGraphBegin = context_binding
        return ctxb.fullrep

    # simply return whatever value is behind said context
    if not var_ref.property and not var_ref.timestamp:
        return context_binding

    if isinstance(context_binding, str):
        if var_ref.property == "ocel_id":
            return context_binding

        if var_ref.property == "ocel_type":
            event = ocel.getEvent(context_binding)

            if event:
                return event.getType()

            ctx_object = ocel.getObject(context_binding)
            if ctx_object:
                return ctx_object.getType()

            return None

        if var_ref.property == "ocel_time":
            event = ocel.getEvent(context_binding)

            if event:
                return event.getPropertyValue("ocel_time")

            return None

        if var_ref.property is not None and var_ref.timestamp is None:
                event = ocel.getEvent(context_binding)
                if event is None:
                    return None
                event_prop = event.getPropertyValue(var_ref.property)

                return event_prop



        if var_ref.property is not None and var_ref.timestamp is not None:
            object = ocel.getObject(context_binding)
            if object is None:
                return None

            lookup_ts = var_ref.timestamp

            if isinstance(lookup_ts, datetime.datetime):
                pass
            elif isinstance(lookup_ts, str):
                # timestamp is symbolic name, need to evaluate.
                ts_binding = context.lookupSymbol(var_ref.timestamp)

                # is a timestamp bound to that symbolic name, use it to evaluate.
                if isinstance(ts_binding, datetime.datetime):
                    lookup_ts = ts_binding
                # if a string is bound to that symbolic name, it must be an event id to work. use that events timestamp
                elif isinstance(ts_binding, str):
                    bound_event = ocel.getEvent(ts_binding)

                    if bound_event is None:
                        return None

                    lookup_ts = bound_event.getPropertyValue("ocel_time")
            else:
                raise OPQLTypeError(f"Invalid timestamp type {type(lookup_ts).__name__} for {var_ref}")

            object_attr = object.getPropertyValue(var_ref.property,lookup_ts)
            return object_attr
            # should be an event, or else, error

    raise OPQLEvalError(
        f"Cannot evaluate value for {var_ref}: unrecognized context entity type {type(context_binding).__name__}"
    )
