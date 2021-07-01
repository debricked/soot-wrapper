lib = require('./library');
lib2 = require('lib2');

var a = ['a', 'b', 'c', 'd'];
var b = ['b', 'c'];

// console.log(diff(a, b));
let length = 10;
let breadth = 5;
let are = lib.area;

// Calling the functions 
// defined in the lib module
function fun (){
    are(length, breadth);
    lib.perimeter(length, breadth);
	lib2.lib2_fun();
}

fun();
// console.log(leftPad(17, 5, 0));
// console.log(cryptoJs.SHA256('message'));
