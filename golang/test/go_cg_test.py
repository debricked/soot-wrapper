import subprocess
import json
from os.path import expanduser


def test_call_graph():
    home = expanduser("~")
    cmd = ["./gen_callgraph.sh", "../test", "../test", home+"/go"]
    subprocess.run(cmd, cwd="../go_cg_extractor")
    cmd = ["mv", "cg.json", "../test"]
    subprocess.run(cmd, cwd="../go_cg_extractor")

    with open("cg.json", "r") as f:
        cg = json.load(f)
    
    # call to external library
    assert '(github.com/artdarek/go-unzip/pkg/unzip.Unzip).Extract' in cg['github.com/TeodorBucht1729/go-test-module.main']

    # call to closure function 
    assert "github.com/TeodorBucht1729/go-test-module/hello.adder$1" in cg["github.com/TeodorBucht1729/go-test-module/hello.Main"]

    # regular function call in different package
    assert "github.com/TeodorBucht1729/go-test-module/hello.Main" in cg["github.com/TeodorBucht1729/go-test-module.main"]

    # call to method 
    assert "(*github.com/TeodorBucht1729/go-test-module/hello.Fruit).GetName" in cg["github.com/TeodorBucht1729/go-test-module/hello.Main"]

    # call in external library
    assert "(github.com/artdarek/go-unzip/pkg/unzip.Unzip).extractAndWriteFile$1" in cg["(github.com/artdarek/go-unzip/pkg/unzip.Unzip).extractAndWriteFile"]
    assert "(github.com/artdarek/go-unzip/pkg/unzip.Unzip).extractAndWriteFile" in cg["(github.com/artdarek/go-unzip/pkg/unzip.Unzip).Extract"]

    # clean up
    subprocess.run(["rm", "cg.json"])