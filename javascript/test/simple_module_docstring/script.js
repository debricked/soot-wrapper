// Importing the module library containing
// area and perimeter functions.
// " ./ " is used if both the files are in the same folder.
const lib = require('./node_mod/library');
// const leftPad = require('left-pad');
// const cryptoJs = require('crypto-js');
// var diff = require('arr-diff');

var a = ['a', 'b', 'c', 'd'];
var b = ['b', 'c'];

// console.log(diff(a, b));
let length = 10;
let breadth = 5;

// Calling the functions 
// defined in the lib module

/**
 * This is a long docstring that might cause parsing problems.
 *
 * @return {void} - something.
 * @param {nothing} target - blablabla.
 * @param {nothing} appName - something something
 * @param {function(Error)} callback - this is fake news
 *     sdfkjsd
 */


function fun (){
    lib.area(length, breadth);
    lib.perimeter(length, breadth);
}

fun();
// console.log(leftPad(17, 5, 0));
// console.log(cryptoJs.SHA256('message'));