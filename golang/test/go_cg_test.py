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
    
    # call to external library
    assert 'github.com/google/go-github/v36/github.NewClient' in cg['debricked.com/go-test-module/hello.Main']

    # call to closure function 
    assert "debricked.com/go-test-module/hello.adder$1" in cg["debricked.com/go-test-module/hello.Main"]

    # regular function call in different package
    assert "debricked.com/go-test-module/hello.Main" in cg["debricked.com/go-test-module.main"]

    # call to method 
    assert "(*debricked.com/go-test-module/hello.Fruit).GetName" in cg["debricked.com/go-test-module/hello.Main"]

    # call in external library
    assert "github.com/google/go-github/v36/github.sanitizeURL" in cg["(*github.com/google/go-github/v36/github.AbuseRateLimitError).Error"]

    # internal call to used code
    assert "debricked.com/go-test-module/hello.Main$1" in cg["sort.doPivot_func"]

    # clean up
    subprocess.run(["rm", str(path_to_src / "cg.json")])