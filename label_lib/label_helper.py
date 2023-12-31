import sys
from itertools import chain, combinations
import label_lib.symbolic_tuple as st_lib

import solver

def label_leq_label(_left_label, _right_label):
    for left_st in _left_label.st_set:
        result, reason = st_leq_label(left_st, generate_joins(_right_label))
        if (not result):
            return False, reason
    return True, "Secure"

def st_leq_label(_left_st, _join_sets):
    res = ""
    for _right_st in _join_sets:
        result, reason = st_leq_st(_left_st, _right_st)
        if (result):
            return True, "Secure"
        else:
            res += "\n\t"+str(_left_st)+" ⋢ "+str(_right_st) + "\n\t\tReason "+ reason+"\n"

    return False, res



def st_leq_st(_left_st, _right_st):
    # Check if the _right_st is well-formed
    if (not is_well_formed(_right_st)):
        return False, "Symbolic tuple " + str(_right_st) + " is not well-formed!"

    # Check leftTables ⊆ rightTables
    if (not _left_st.table_names.issubset(_right_st.table_names)):
        return False, str(_left_st.table_names) + " is not a subset of " + str(_right_st.table_names)

    # Check leftColumns ⊆ rightColumns
    if (not _left_st.columns.issubset(_right_st.columns)):
        return False, str(_left_st.columns) + " is not a subset of " + str(_right_st.columns)

    # Check dep(leftPhi) ∪ leftColumns ⊆ rightColumns
    left_total = set()
    left_total = left_total.union(_left_st.phi.get_vars())
    left_total = left_total.union(_left_st.columns)

    if (not left_total.issubset(_right_st.columns)):
        return False, "dep("+ str(_left_st.phi) +") ∪ "+ str(_left_st.columns) +" ⊄ " + str(_right_st.columns)

    # check ~(leftPhi -> rightPhi) unsat
    impl = check_formula(_left_st.phi, _right_st.phi)
    if (not impl):
        return True, "Secure"
    else:
        return False, str(_left_st.phi) +" ⊭ "+ str(_right_st.phi) 
    # return the negation because checkFormula is true if ~(leftPhi -> rightPhi) is sat
    # while isLessThan method should return false if ~(leftPhi -> rightPhi) is sat 
    # because that means (leftPhi |= rightPhi) does not hold.


########### Checks dep(Phi) ⊆ Columns ###########
def is_well_formed(_st):
    if (_st.phi.get_vars().issubset(_st.columns)):
        return True
        
    return False


def check_formula(_left_phi, _right_phi):
    slv = solver.Z3Solver()
    result = slv.check_not_implication_sat(_left_phi, _right_phi)

    return result


################# Generate Joins #################
def generate_joins(_label):
    power_set = generate_power_set(_label.st_set.copy())
    result_set = set()

    for st_set in power_set:
        if (st_set and is_disjoint(st_set)):
            tmp_st = generate_merged_st(st_set)
            if (is_well_formed(tmp_st)):
                result_set.add(tmp_st)

    return result_set


def generate_power_set(_st_set):
    power_set = list(chain.from_iterable(combinations(_st_set, r) for r in range(len(_st_set)+1)))
    return power_set


def is_disjoint(_st_set):
    if (len(_st_set) == 1):
        return True

    list_of_table_names = []
    for st in _st_set:
        list_of_table_names.append(st.table_names)

    return are_disjoint_sets(list_of_table_names)


def generate_merged_st(_sts):
    total_table_names = set()
    total_phi = []
    total_columns = set()

    for st in _sts:
        total_table_names = total_table_names.union(st.table_names)
        total_columns = total_columns.union(st.columns)
        for exp in st.phi.expressions:
            total_phi.append(exp)

    return st_lib.SymbolicTuple(total_columns, total_table_names, total_phi)

def are_disjoint_sets(set_list):
    for i in range(len(set_list)):
        for j in range(i + 1, len(set_list)):
            if not set_list[i].isdisjoint(set_list[j]):
                return False
    return True