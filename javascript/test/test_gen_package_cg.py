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

    truth_file = os.path.join(sp, "import_from_inside", "test_answer.truth")
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

def test_import_from_outside():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "import_from_outside/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)

    truth_file = os.path.join(sp, "import_from_outside", "test_answer.truth")
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

def test_inside_priority():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "import_priority/", "cg.json"]
    subprocess.run(cmd)
    
    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)

    truth_file = os.path.join(sp, "import_priority", "test_answer.truth")
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

def test_ignore():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "ignore_specific_keyword/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)

    truth_file = os.path.join(sp, "ignore_specific_keyword", "test_answer.truth")
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

def test_recursive_dependencies():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "recursive_dependencies/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)

    truth_file = os.path.join(sp, "recursive_dependencies", "test_answer.truth")
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

def test_incorrect_script():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "incorrect_dep/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)

    truth_file = os.path.join(sp, "incorrect_dep", "test_answer.truth")
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

def test_one_way_call():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "one_way_call", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)
 
    truth_file = os.path.join(sp, "one_way_call", "test_answer.truth")
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


def test_no_name():

    cmd = ["python", sp + "../src/gen_package_cg.py", "-i", sp + "simple_module_no_name/", "cg.json"]
    subprocess.run(cmd)

    with open("cg.json", "r") as f:
        cg = json.load(f)
    print("cg:", cg)

    truth_file = os.path.join(sp, "simple_module_no_name", "test_answer.truth")
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