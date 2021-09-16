package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"log"
	"os"
	"strconv"
)

// ast_parse_files parses all the files passed through files.
// The files are parsed using "go/parser" and then inspected using "go/ast.Inspect".
// All the ast.Node objects in the AST that have type *ast.Funcl and *ast.FuncLit are filtered out.
// These symbols are converted to json-format and printed to stdout.
func ast_parse_files(files []string) {

	// create a FileSet for all the files, this is used for tracking positions.
	fset := token.NewFileSet()
	// all symbols will be in the symbols variable
	var symbols []map[string]string
	// loop through all the given files and parse them
	for _, file_path := range files {
		file, err := parser.ParseFile(fset, file_path, nil, 0)
		if err != nil {
			log.Fatal(err)
		}
		// inspect (traverse) the AST, note that the 'footprint' is added at a later stage
		ast.Inspect(file, func(n ast.Node) bool {
			// Find Function declarations
			fn_dec, ok_dec := n.(*ast.FuncDecl)
			if ok_dec {

				symbol := map[string]string{"file": file_path, "line_start": strconv.Itoa(fset.Position(fn_dec.Name.Pos()).Line),
					"line_end": strconv.Itoa(fset.Position(fn_dec.End()).Line), "column_start": strconv.Itoa(fset.Position(fn_dec.Name.Pos()).Column),
					"type": "Function Declaration", "language": "go"}

				symbols = append(symbols, symbol)

				return true
			}
			// Find Function literals
			fn_lit, ok_lit := n.(*ast.FuncLit)
			if ok_lit {

				symbol := map[string]string{"file": file_path, "line_start": strconv.Itoa(fset.Position(fn_lit.Pos()).Line),
					"line_end": strconv.Itoa(fset.Position(fn_lit.End()).Line), "column_start": strconv.Itoa(fset.Position(fn_lit.Pos()).Column),
					"type": "Function literal", "language": "go"}

				symbols = append(symbols, symbol)
				return true
			}
			return true
		})
	}
	// print the output to stdout
	output, _ := json.Marshal(symbols)
	fmt.Print(string(output))

}

func main() {
	// read all files to be parsed from stdin
	scanner := bufio.NewScanner(os.Stdin)
	var files []string
	for scanner.Scan() {
		files = append(files, scanner.Text())
	}
	// call ast_parse_files for the files read from stdin
	ast_parse_files(files)
}
