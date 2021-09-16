package main

import (
	"fmt"

	"debricked.com/go-test-module/hello"
)

func main() {
	hello.Main()
	// Below, this CVE is demonstrated: https://github.com/golang/vulndb/blob/master/reports/GO-2020-0041.yaml
	//tz.PackTo("/home/teodor/debricked/go_test/helloworld", "/home/teodor/debricked/go_test/helloworld_tar")
	//tz.ExtractTo("/home/teodor/debricked/go_test/helloworld_tar", "/home/teodor/debricked/go_test/extracted")
	fmt.Println("Main function has runned")
}
