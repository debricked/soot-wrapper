import subprocess
import json
import os
from pathlib import Path

def test_call_graph():
    path_to_src = Path(os.path.realpath(__file__)).parent.parent / "src"
    path_to_src = path_to_src.resolve()

    path_to_test = Path(os.path.realpath(__file__)).parent

    cmd = [str(path_to_src / "gen_callgraph.sh"), str(path_to_test), "cg.json"]
    subprocess.run(cmd)

    with open(str(path_to_src / "cg.json"), "r") as f:
        cg = json.load(f)

    data = cg['data']
    interesting_called_funcs = {}
    for func in data:
        if func[0] in ["github.com/google/go-github/v36/github.NewClient", \
            "debricked.com/go-test-module/hello.adder$1", \
            "debricked.com/go-test-module/hello.Main", \
            "(*debricked.com/go-test-module/hello.Fruit).GetName", \
            "github.com/google/go-github/v36/github.sanitizeURL", \
            "debricked.com/go-test-module/hello.Main$1"]:
            interesting_called_funcs[func[0]] = func
    
    # call to external library
    assert 'github.com/google/go-github/v36/github.NewClient' in interesting_called_funcs
    assert 'debricked.com/go-test-module/hello.Main' in [x[0] for x in interesting_called_funcs['github.com/google/go-github/v36/github.NewClient'][-1]]

    # call to closure function 
    assert "debricked.com/go-test-module/hello.adder$1" in interesting_called_funcs
    assert 'debricked.com/go-test-module/hello.Main' in [x[0] for x in interesting_called_funcs["debricked.com/go-test-module/hello.adder$1"][-1]]

    # regular function call in different package
    assert "debricked.com/go-test-module/hello.Main" in interesting_called_funcs
    assert 'debricked.com/go-test-module.main' in [x[0] for x in interesting_called_funcs["debricked.com/go-test-module/hello.Main"][-1]]

    # call to method 
    assert "(*debricked.com/go-test-module/hello.Fruit).GetName" in interesting_called_funcs
    assert 'debricked.com/go-test-module/hello.Main' in [x[0] for x in interesting_called_funcs["(*debricked.com/go-test-module/hello.Fruit).GetName"][-1]]

    # call in external library
    assert "github.com/google/go-github/v36/github.sanitizeURL" in interesting_called_funcs
    assert '(*github.com/google/go-github/v36/github.AbuseRateLimitError).Error' in [x[0] for x in interesting_called_funcs["github.com/google/go-github/v36/github.sanitizeURL"][-1]]

    # internal call to user written code
    assert "debricked.com/go-test-module/hello.Main$1" in interesting_called_funcs
    assert 'sort.doPivot_func' in [x[0] for x in interesting_called_funcs["debricked.com/go-test-module/hello.Main$1"][-1]]

    # clean up
    subprocess.run(["rm", str(path_to_src / "cg.json")])