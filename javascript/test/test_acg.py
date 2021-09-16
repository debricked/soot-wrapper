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

    truth_file = os.path.join(sp, "simple_module", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_simple_module_2():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "simple_module_2/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)

    truth_file = os.path.join(sp, "simple_module_2", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_assignment():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_assignment/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)


    truth_file = os.path.join(sp, "basics_assignment", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_arrow():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_arrow/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)

    truth_file = os.path.join(sp, "basics_arrow", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_global_as_prop():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_global-as-prop/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)

    truth_file = os.path.join(sp, "basics_global-as-prop", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")
   
def test_basics_local_is_fine():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_local_is_fine/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)

    truth_file = os.path.join(sp, "basics_local_is_fine", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_basics_method_def():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "basics_method_def/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    
    print(cg)

    truth_file = os.path.join(sp, "basics_method_def", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_unhandled_classes_class_getter(): 

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "unhandled_classes_class_getter/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)

    truth_file = os.path.join(sp, "unhandled_classes_class_getter", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_unhandled_limits_history():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "unhandled_limits_history/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)

    truth_file = os.path.join(sp, "unhandled_limits_history", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])

    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")

@pytest.mark.xfail
def test_overload():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "overload/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)

    truth_file = os.path.join(sp, "overload", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])
   
    if os.path.isfile("cg.json"):
        os.remove("cg.json")

def test_es6_module():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "es6_module", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print(cg)

    truth_file = os.path.join(sp, "es6_module", "test_answer.truth")
    print(truth_file)
    assert os.path.isfile(truth_file), "Truth file missing"
    with open(truth_file, "r") as f:
        corr_cg = json.load(f)
    for i in range(len(cg['data'])):
        cg['data'][i][-1].sort(key= lambda x: x[0])
        corr_cg['data'][i][-1].sort(key= lambda x: x[0])
    assert sorted(cg['data'], key = lambda x: x[0]) == sorted(corr_cg['data'], key = lambda x: x[0])

    if os.path.isfile("cg.json"):
        os.remove("cg.json")
