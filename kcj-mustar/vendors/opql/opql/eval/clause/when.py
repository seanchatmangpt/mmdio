import datetime

import opql.eval.expression
import opql.eval.expression.tree
import opql.eval.querycontext


def eval_ex_at(ocel, context, expression, timestamp, objects_to_bind):
    prev_ts_val = None
    for object_ref in objects_to_bind:
        prev_ts_val = object_ref.timestamp
        object_ref.timestamp = timestamp

    result = opql.eval.expression.tree.evaluate_graphexpression(ocel, context, expression)

    for object_ref in objects_to_bind:
        object_ref.timestamp = None

    for object_ref in objects_to_bind:
        object_ref.timestamp = prev_ts_val

    return result

def find_undetermined_object_properties(expression, fill_in_symname):
    unbound_props = [obj for obj in opql.eval.expression.tree.get_all_objects(expression) if
                     obj.timestamp == fill_in_symname]
    return unbound_props

def do_when(ocel, candidate_endpoints, graphOrFilter):

    expression = graphOrFilter.expression

    new_endpoints = []

    unbound_props = find_undetermined_object_properties(expression, graphOrFilter.name)
    attrs_to_lookup = [(val_ref.name, val_ref.property) for val_ref in unbound_props]

    for context in candidate_endpoints:
        # small hack because object initialization does sometimes not have an appropriate changed field, but values!
        pts_in_time_to_eval = [datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)]
        for ocel_object, attr in attrs_to_lookup:
            ctx_bound_obj = context.lookupSymbol(ocel_object)

            if ctx_bound_obj is None:
                continue

            # TODO currently this is full history, although property dependent history would technically suffice
            attr_history = ocel.getObject(ctx_bound_obj).getAttributeHistory(attr)
            pts_in_time_to_eval += attr_history

        pts_in_time_to_eval = list(set(pts_in_time_to_eval))

        valid_points_in_time = []
        for timestamp in pts_in_time_to_eval:
            res = eval_ex_at(ocel, context, expression, timestamp, unbound_props)
            if res:
                valid_points_in_time.append(timestamp)

        if not valid_points_in_time:
            context.childrenSymbol = graphOrFilter.name
            context.children = [
                opql.eval.querycontext.QueryContext(parent=context, context_entity=None, children_symbol=None,
                                                    children=[])]
        else:
            context.childrenSymbol = graphOrFilter.name
            context.children = [
                opql.eval.querycontext.QueryContext(parent=context, context_entity=vpit, children_symbol=None,
                                                    children=[]) for vpit in valid_points_in_time]

        new_endpoints.extend(context.children)

    subject_to = graphOrFilter.filter
    if subject_to:
        new_endpoints = [ctx for ctx in new_endpoints if opql.eval.expression(ocel, ctx, subject_to)]

    return new_endpoints