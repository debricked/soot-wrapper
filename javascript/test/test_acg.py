import os
import json
import pytest
import subprocess

sp = os.path.dirname(os.path.abspath(__file__)) + "/"

def test_simple_module():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "simple_module/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "simple_module/node_mod/library.js/anonymous_at_2:11" in cg["simple_module/script.js/fun_at_18:0"]
    assert "simple_module/node_mod/library.js/anonymous_at_8:16" in cg["simple_module/script.js/fun_at_18:0"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_simple_module_2():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "simple_module_2/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "simple_module_2/script.js/global" in cg
    assert "simple_module_2/node_mod/library.js/fun2_at_1:17" in cg["simple_module_2/script.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_assignment():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_assignment/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "basics_assignment/assignment.js/func_at_2:0" in cg
    assert "basics_assignment/assignment.js/new_func_at_4:9" in cg["basics_assignment/assignment.js/func_at_2:0"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_arrow():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_arrow/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "basics_arrow/arrow.js/global" in cg
    assert "basics_arrow/arrow.js/anonymous_at_1:11" in cg["basics_arrow/arrow.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_global_as_prop():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_global-as-prop/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "basics_global-as-prop/global-as-prop.js/global" in cg
    assert "basics_global-as-prop/global-as-prop.js/anonymous_at_1:13" in cg["basics_global-as-prop/global-as-prop.js/global"]
    assert "basics_global-as-prop/global-as-prop.js/anonymous_at_2:25" in cg["basics_global-as-prop/global-as-prop.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")
   
def test_basics_local_is_fine():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_local_is_fine/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "basics_local_is_fine/local-is-fine.js/anonymous_at_1:1" in cg
    assert "basics_local_is_fine/local-is-fine.js/global" in cg
    assert "basics_local_is_fine/local-is-fine.js/anonymous_at_2:15" in cg["basics_local_is_fine/local-is-fine.js/anonymous_at_1:1"]
    assert "basics_local_is_fine/local-is-fine.js/anonymous_at_3:27" in cg["basics_local_is_fine/local-is-fine.js/anonymous_at_1:1"]
    assert "basics_local_is_fine/local-is-fine.js/anonymous_at_1:1" in cg["basics_local_is_fine/local-is-fine.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_method_def():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_method_def/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    
    print(cg)
    assert "basics_method_def/method-def.js/global" in cg
    assert "basics_method_def/method-def.js/anonymous_at_2:18" in cg["basics_method_def/method-def.js/global"]
    assert "basics_method_def/method-def.js/anonymous_at_5:20" in cg["basics_method_def/method-def.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_unhandled_classes_class_getter(): 

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "unhandled_classes_class_getter/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "unhandled_classes_class_getter/class-getter.js/global" in cg
    assert "unhandled_classes_class_getter/class-getter.js/anonymous_at_7:10" in cg["unhandled_classes_class_getter/class-getter.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_unhandled_limits_history():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "unhandled_limits_history/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "unhandled_limits_history/history.js/main_func_at_1:0" in cg
    assert "unhandled_limits_history/history.js/a_func_at_2:12" not in cg["unhandled_limits_history/history.js/main_func_at_1:0"]
    assert "unhandled_limits_history/history.js/b_func_at_4:8" in cg["unhandled_limits_history/history.js/main_func_at_1:0"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_overload():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "overload/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "overload/overload.js/main_at_9:0" in cg
    assert "overload/overload.js/func_at_5:0" not in cg["overload/overload.js/main_at_9:0"]
   
    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_es6_module():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "es6_module", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)
    assert "es6_module/main.js/global" in cg
    assert "es6_module/lib.js/square_at_2:7" in cg["es6_module/main.js/global"]
    assert "es6_module/lib.js/diag_at_5:7" in cg["es6_module/main.js/global"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")
