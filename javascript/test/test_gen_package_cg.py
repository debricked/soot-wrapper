import sys
import os
sp = os.path.dirname(os.path.abspath(__file__)) + "/"
source_path = sp[:-1]
source_path = source_path[:(-(source_path[:-1][::-1].find("/") + 1))]
source_path += "src/"
sys.path.insert(1, source_path)
import gen_package_cg
import json

def test_import_from_inside():
    gen_package_cg.gen_cg_for_package(sp + "import_from_inside/", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "import_from_inside/script.js/fun_from_14_to_18" in cg
    assert "lib1/index.js/anonymous_from_1_to_3" in cg["import_from_inside/script.js/fun_from_14_to_18"]

def test_import_from_outside():
    gen_package_cg.gen_cg_for_package(sp + "import_from_outside/", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "import_from_outside/script.js/fun_from_14_to_18" in cg
    assert "lib2/index.js/anonymous_from_1_to_3" in cg["import_from_outside/script.js/fun_from_14_to_18"]


def test_inside_priority():
    gen_package_cg.gen_cg_for_package(sp + "import_priority/", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "import_priority/script.js/fun_from_14_to_18" in cg
    assert "lib1/index.js/anonymous_from_1_to_3" in cg["import_priority/script.js/fun_from_14_to_18"]

def test_ignore():
    gen_package_cg.gen_cg_for_package(sp + "ignore_specific_keyword/", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "ignore_specific_keyword/test_something.js/global" not in cg
    assert "ignore_specific_keyword/tests/script.js/global" not in cg

def test_recursive_dependencies():
    gen_package_cg.gen_cg_for_package(sp + "recursive_dependencies/", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "test_answer.truth" in os.listdir(sp + "recursive_dependencies/"), "truth file missing"
    with open(sp + "recursive_dependencies/test_answer.truth", "r") as f:
        correct_cg = json.load(f)

    for key in correct_cg.keys():
        assert key in cg
        assert sorted(cg[key]) == sorted(correct_cg[key])
    
def test_incorrect_script():
    gen_package_cg.gen_cg_for_package(sp + "incorrect_dep/", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "test_answer.truth" in os.listdir(sp + "incorrect_dep/"), "truth file missing"
    with open(sp + "incorrect_dep/test_answer.truth", "r") as f:
        correct_cg = json.load(f)

    for key in correct_cg.keys():
        assert key in cg
        assert sorted(cg[key]) == sorted(correct_cg[key])

def test_one_way_call():
    gen_package_cg.gen_cg_for_package(sp + "one_way_call", "./cg.json")
    with open("cg.json", "r") as f:
        cg = json.load(f)
    assert "lib1/index.js/global" in cg
    assert "one_way_call/script.js/fun_from_14_to_18" not in cg["lib1/index.js/global"]
