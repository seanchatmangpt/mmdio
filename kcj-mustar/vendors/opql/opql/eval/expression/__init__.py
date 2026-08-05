import sys
import types

import opql.eval.expression.tree as expr_impl


# Replaces this module with a callable so callers can write opql.eval.expression(...)
class _CallableModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return expr_impl.evaluate_graphexpression(*args, **kwargs)


_mod = _CallableModule(__name__)
_mod.__dict__.update({k: v for k, v in globals().items() if not k.startswith('_mod')})
sys.modules[__name__] = _mod