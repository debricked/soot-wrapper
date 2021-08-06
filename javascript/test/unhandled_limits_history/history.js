function main_func () {
    let a = function a_func () { console.log('a_func is called!'); };
    let b = a;
    b = function b_func() { console.log('b_func is called!'); };
    a = b;
    a(); // b_func is called
    b(); // b_func is called
}

main_func();
