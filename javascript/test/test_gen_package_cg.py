import sys
import os
import json
import subprocess

sp = os.path.dirname(os.path.abspath(__file__)) + "/"

def test_import_from_inside():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "import_from_inside/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "import_from_inside/script.js/fun_at_14:0" in cg
    assert "lib1/index.js/anonymous_at_1:15" in cg["import_from_inside/script.js/fun_at_14:0"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_import_from_outside():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "import_from_outside/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "import_from_outside/script.js/fun_at_14:0" in cg
    assert "lib2/index.js/anonymous_at_1:15" in cg["import_from_outside/script.js/fun_at_14:0"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_inside_priority():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "import_priority/", "cg.json"]
    subprocess.run(cmd)
    
    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "import_priority/script.js/fun_at_14:0" in cg
    assert "lib1/index.js/anonymous_at_1:15" in cg["import_priority/script.js/fun_at_14:0"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_ignore():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "ignore_specific_keyword/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "test_answer.truth" in os.listdir(sp + "ignore_specific_keyword/"), "truth file missing"
    with open(sp + "ignore_specific_keyword/test_answer.truth", "r") as f:
        correct_cg = json.load(f)

    for key in correct_cg.keys():
        assert key in cg
        assert sorted(cg[key]) == sorted(correct_cg[key])
        
    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_recursive_dependencies():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "recursive_dependencies/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "test_answer.truth" in os.listdir(sp + "recursive_dependencies/"), "truth file missing"
    with open(sp + "recursive_dependencies/test_answer.truth", "r") as f:
        correct_cg = json.load(f)

    for key in correct_cg.keys():
        assert key in cg
        assert sorted(cg[key]) == sorted(correct_cg[key])
    
    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_incorrect_script():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "incorrect_dep/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "test_answer.truth" in os.listdir(sp + "incorrect_dep/"), "truth file missing"
    with open(sp + "incorrect_dep/test_answer.truth", "r") as f:
        correct_cg = json.load(f)

    for key in correct_cg.keys():
        assert key in cg
        assert sorted(cg[key]) == sorted(correct_cg[key])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_one_way_call():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "one_way_call", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
 
    assert "lib1/index.js/anonymous_at_1:15" in cg
    assert "one_way_call/script.js/fun_at_14:0" not in cg["lib1/index.js/anonymous_at_1:15"]

    if os.path.isfile("cg.json"):
        os.remove("cg.json")


def test_no_name():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "simple_module_no_name/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
    assert "test_answer.truth" in os.listdir(sp + "simple_module_no_name/"), "truth file missing"
    with open(sp + "simple_module_no_name/test_answer.truth", "r") as f:
        correct_cg = json.load(f)

    for key in correct_cg.keys():
        assert key in cg
        assert sorted(cg[key]) == sorted(correct_cg[key])
    
    if os.path.isfile("cg.json"):
        os.remove("cg.json")