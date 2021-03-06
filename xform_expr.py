# ScratchABlock - Program analysis and decompilation framework
#
# Copyright (c) 2015-2018 Paul Sokolovsky
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Transformation passes on expressions"""

import logging

from core import *
from xform_expr_basic import *
import xform_expr_infer
import arch


log = logging.getLogger(__name__)


def is_expr_2args(e):
    return is_expr(e) and len(e.args) == 2


def mod_add(a, b, bits=arch.BITNESS):
    "Addition modulo power of 2, but preserve sign."
    s = a + b
    if s < 0:
        return s % 2**bits - 2**bits
    else:
        return s % 2**bits


def expr_xform(e, func):
    """Transform expression using a function. A function is called with
    each recursive subexpression of expression (in depth-first order),
    then with expression itself. A function can either return new expression
    to replace original one with, or None to keep an original (sub)expression.
    """
    if isinstance(e, MEM):
        new = expr_xform(e.expr, func)
        if new:
            e = MEM(e.type, new)
        e = func(e) or e
        return e

    if isinstance(e, EXPR):
        new = [expr_xform(a, func) or a for a in e.args]
        e = EXPR(e.op, new)
        return func(e) or e

    if isinstance(e, COND):
        new = expr_xform(e.expr, func)
        if new:
            e.expr = new
        return e

    return func(e) or e


def add_vals(a, b):
    val = a.val + b.val
    base = max(a.base, b.base)
    return VALUE(val, base)


def expr_sub_const_to_add(e):
    if is_expr_2args(e):
        if e.op == "-" and is_value(e.args[1]):
            return EXPR("+", [e.args[0], expr_neg(e.args[1])])


def expr_sub_to_add(e):
    if is_expr(e) and e.op == "-":
        new_args = [expr_neg(x) for x in e.args[1:]]
        return EXPR("+", [e.args[0]] + new_args)


def expr_commutative_normalize(e):
    if not is_expr(e):
        return
    if e.op not in ("+", "&", "|", "^"):
        return
    e.args.sort()


def expr_associative_add(e):
    "Turn (a + b) + c into a + b + c."
    if is_expr(e) and e.op == "+":
        if is_expr(e.args[0]) and e.args[0].op == "+":
            new_args = e.args[0].args.copy()
            new_args.extend(e.args[1:].copy())
            return EXPR("+", new_args)


def expr_simplify_add(e):
    if is_expr(e) and e.op == "+":
        new_args = []
        val = 0
        base = 0
        for a in e.args:
            if is_value(a):
                val = mod_add(val, a.val)
                base = max(base, a.base)
            else:
                new_args.append(a)
        if new_args:
            if val != 0:
                new_args.append(VALUE(val, base))
            if len(new_args) == 1:
                return new_args[0]
            new_args.sort()
            return EXPR("+", new_args)
        else:
            return VALUE(val, base)


def expr_simplify_lshift(e):
    if is_expr(e) and e.op == "<<":
        assert is_expr_2args(e)

        if is_value(e.args[1]):
            val = e.args[1].val
            if val == 0:
                return e.args[0]
            # Try to convert usages which are realistic address calculations,
            # otherwise we may affect bitfield, etc. expressions.
            if val < 5:
                return EXPR("*", [e.args[0], VALUE(1 << val, 10)])


def expr_simplify_neg(e):
    if is_expr(e) and e.op == "NEG":
        new = expr_neg_if_possible(e.args[0])
        return new


def expr_simplify_bitfield(e):
    "Simplify bitfield() to an integer cast if possible."
    if is_expr(e) and e.op == "SFUNC" and e.args[0] == SFUNC("bitfield"):
        assert is_value(e.args[2]) and is_value(e.args[3])
        if e.args[2].val == 0:
            sz = e.args[3].val
            type = {8: "u8", 16: "u16", 32: "u32"}.get(sz)
            if type:
                return EXPR("CAST", [TYPE(type), e.args[1]])
            return EXPR("&", e.args[1], VALUE((1 << sz) - 1))

def expr_simplify_cast(e):
    if is_expr(e) and e.op == "CAST":
        assert is_expr_2args(e)

        if is_value(e.args[1]):
            val = e.args[1].val

            tname = e.args[0].name
            is_signed = tname[0] == "i"
            bits = int(tname[1:])
            mask = (1 << bits) - 1
            val &= mask
            if is_signed:
                if val & (1 << (bits - 1)):
                    val -= mask + 1

            return VALUE(val, e.args[1].base)


def unsignize_logical_ops(e):
    "Operands of &, |, ^ should be unsigned."
    if is_expr(e) and e.op in ("&", "|", "^"):
        assert is_expr_2args(e)

        if is_value(e.args[1]):
            val = e.args[1].val
            if val >= 0:
                return
            val = val & (2**arch.BITNESS - 1)
            # Force hex
            return EXPR(e.op, e.args[0], VALUE(val, 16))


def simplify_expr(expr):
    new_expr = expr_xform(expr, expr_sub_to_add)
    expr_commutative_normalize(new_expr)
    new_expr = expr_xform(new_expr, expr_associative_add)
    new_expr = expr_xform(new_expr, expr_simplify_add)
    new_expr = expr_xform(new_expr, expr_simplify_lshift)
    new_expr = expr_xform(new_expr, expr_simplify_bitfield)
    new_expr = expr_xform(new_expr, expr_simplify_cast)
    new_expr = expr_xform(new_expr, expr_simplify_neg)
    new_expr = expr_xform(new_expr, unsignize_logical_ops)

    expr_commutative_normalize(new_expr)
    new_expr = expr_xform(new_expr, xform_expr_infer.simplify)
    return new_expr


def expr_struct_access(m):
    import progdb
    structs = progdb.get_struct_types()
    struct_addrs = progdb.get_struct_instances()

    if is_mem(m) and is_value(m.expr):
        addr = m.expr.val
        for (start, end), struct_name in struct_addrs.items():
            if start <= addr < end:
                offset = addr - start
                field = structs[struct_name][offset]
                return SFIELD(struct_name, hex(start), field)


def struct_access_expr(expr):
    new_expr = expr_xform(expr, expr_struct_access)
    return new_expr


# Should transform inplace
def simplify_cond(e):
    # TODO: Replaced with inference rule, remove
    if e.is_relation():
        arg1 = e.expr.args[0]
        arg2 = e.expr.args[1]
        if is_expr_2args(arg1) and arg1.op == "+" and is_value(arg1.args[1]) and is_value(arg2):
            assert 0, "Should be replaced by fb730b7de49"
            e.expr = EXPR(e.expr.op, arg1.args[0], add_vals(expr_neg(arg1.args[1]), arg2))


def expr_subst(expr, subst_dict):

    if isinstance(expr, (VALUE, STR, ADDR, SFUNC, TYPE)):
        return None

    if isinstance(expr, REG):
        new = subst_dict.get(expr)
        if new and expr in new:
            log.debug("Trying to replace %s with recursively referring %s, not doing" % (expr, new))
            return None
        if new and len(new) > 10:
            log.debug("Trying to replace %s with complex [len=%d] %s, not doing" % (expr, len(new), new))
            return None
        return new

    if isinstance(expr, MEM):
        new = expr_subst(expr.expr, subst_dict)
        if new:
            return MEM(expr.type, new)
        return

    if isinstance(expr, COND):
        # This performs substituations in-place, because the same
        # COND instance is referenced in inst (to be later removed
        # by remove_trailing_jumps) and in out edges in CFG.
        new = expr_subst(expr.expr, subst_dict)
        if new:
            expr.expr = new
            simplify_cond(expr)
        return

    if isinstance(expr, EXPR):
        new_args = []
        was_new = False
        for a in expr.args:
            new = expr_subst(a, subst_dict)
            if new is None:
                new = a
            else:
                was_new = True
            new_args.append(new)
        if not was_new:
            return None

        new_expr = EXPR(expr.op, new_args)
        new_expr = simplify_expr(new_expr)
        return new_expr

    assert 0, repr((expr, type(expr)))
