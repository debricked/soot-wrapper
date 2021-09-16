package hello

import (
	"context"
	"fmt"
	"sort"

	"github.com/google/go-github/v36/github"
	"golang.org/x/example/stringutil"
)

type Fruit struct {
	name string
}

func (fruit *Fruit) GetName() string {
	return fruit.name
}

func init() {
	fmt.Print("Init hej\n")
}

func adder() func(int) int {
	sum := 0
	return func(x int) int {
		sum += x
		return sum
	}
}

func Main() {

	client := github.NewClient(nil)
	opt := &github.RepositoryListByOrgOptions{Type: "public"}
	repos, _, _ := client.Repositories.ListByOrg(context.Background(), "debricked", opt)
	for i := 0; i < len(repos); i++ {
		fmt.Print(repos[i].GetFullName())
		fmt.Print("\n\n")
	}
	fmt.Print("Hejsan\n")
	fmt.Print(stringutil.Reverse("\nnasjeH"))

	frukt := Fruit{"Äpple"}
	fmt.Println(frukt.GetName())

	people := []string{"Alice", "Bob", "Dave"}
	sort.Slice(people, func(i, j int) bool {
		return len(people[i]) < len(people[j])
	})
	fmt.Println(people)

	pos, neg := adder(), adder()
	for i := 0; i < 10; i++ {
		fmt.Println(
			pos(i),
			neg(-2*i),
		)
	}
}
