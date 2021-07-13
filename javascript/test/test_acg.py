import sys
import os
sp = os.path.dirname(os.path.abspath(__file__)) + "/"
source_path = sp[:-1]
source_path = source_path[:(-(source_path[:-1][::-1].find("/") + 1))]
source_path += "src/"
sys.path.insert(1, source_path)
import gen_package_cg
import json
import pytest

def test_simple_module():

    gen_package_cg.gen_cg_for_package(sp + "simple_module/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "simple_module/node_mod/library.js/anonymous_from_2_to_5" in cg["simple_module/script.js/fun_from_18_to_21"]
    assert "simple_module/node_mod/library.js/anonymous_from_8_to_11" in cg["simple_module/script.js/fun_from_18_to_21"]

@pytest.mark.xfail
def test_simple_module_2():

    gen_package_cg.gen_cg_for_package(sp + "simple_module_2/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "simple_module_2/script.js/global" in cg
    assert "simple_module_2/node_mod/library.js/fun2_from_1_to_3" in cg["simple_module_2/script.js/global"]

def test_basics_assignment():
    gen_package_cg.gen_cg_for_package(sp + "basics_assignment/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "basics_assignment/assignment.js/main_from_2_to_9" in cg
    assert "basics_assignment/assignment.js/funcB_from_4_to_6" in cg["basics_assignment/assignment.js/main_from_2_to_9"]

def test_basics_arrow():
    gen_package_cg.gen_cg_for_package(sp + "basics_arrow/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "basics_arrow/arrow.js/global" in cg
    assert "basics_arrow/arrow.js/anonymous_from_1_to_1" in cg["basics_arrow/arrow.js/global"]

def test_basics_global_as_prop():
    gen_package_cg.gen_cg_for_package(sp + "basics_global-as-prop/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "basics_global-as-prop/global-as-prop.js/global" in cg
    assert "basics_global-as-prop/global-as-prop.js/anonymous_from_11_to_11" in cg["basics_global-as-prop/global-as-prop.js/global"]
    assert "basics_global-as-prop/global-as-prop.js/anonymous_from_12_to_12" in cg["basics_global-as-prop/global-as-prop.js/global"]
    
   
def test_basics_local_is_fine():
    gen_package_cg.gen_cg_for_package(sp + "basics_local_is_fine/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "basics_local_is_fine/local-is-fine.js/anonymous_from_2_to_7" in cg
    assert "basics_local_is_fine/local-is-fine.js/anonymous_from_3_to_3" in cg["basics_local_is_fine/local-is-fine.js/anonymous_from_2_to_7"]
    assert "basics_local_is_fine/local-is-fine.js/anonymous_from_4_to_4" in cg["basics_local_is_fine/local-is-fine.js/anonymous_from_2_to_7"]

def test_basics_method_def():
    gen_package_cg.gen_cg_for_package(sp + "basics_method_def/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "basics_method_def/method-def.js/global" in cg
    assert "basics_method_def/method-def.js/anonymous_from_2_to_4" in cg["basics_method_def/method-def.js/global"]
    assert "basics_method_def/method-def.js/anonymous_from_5_to_7" in cg["basics_method_def/method-def.js/global"]

@pytest.mark.xfail
def test_unhandled_classes_class_getter(): 

    gen_package_cg.gen_cg_for_package(sp + "unhandled_classes_class_getter/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "unhandled_classes_class_getter/class-getter.js/global" in cg
    assert "unhandled_classes_class_getter/class-getter.js/anonymous_from_7_to_9" in cg["unhandled_classes_class_getter/class-getter.js/global"]

@pytest.mark.xfail
def test_unhandled_limits_history():
    gen_package_cg.gen_cg_for_package(sp + "unhandled_limits_history/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "unhandled_limits_history/history.js/main_from_4_to_11" in cg
    assert "unhandled_limits_history/history.js/func1_from_5_to_5" not in cg["unhandled_limits_history/history.js/main_from_4_to_11"]

@pytest.mark.xfail
def test_overload():
    gen_package_cg.gen_cg_for_package(sp + "overload/", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "overload/overload.js/main_from_9_to_11" in cg
    assert "overload/overload.js/f_from_5_to_7" not in cg["overload/overload.js/main_from_9_to_11"]
   

def test_es6_module():
    gen_package_cg.gen_cg_for_package(sp + "es6_module", "./final_cg.json")
    with open("final_cg.json", "r") as f:
        cg = json.load(f)
    assert "es6_module/main.js/global" in cg
    assert "es6_module/lib.js/square_from_2_to_4" in cg["es6_module/main.js/global"]
    assert "es6_module/lib.js/diag_from_5_to_7" in cg["es6_module/main.js/global"]

