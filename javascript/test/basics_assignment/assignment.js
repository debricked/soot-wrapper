// This file tests assigning a function object to an existing local variable
function func() {
	let c = 1;
	let b = function new_func () {
		console.log('new_func is called!');
	};
	c = b;
	c();
}

func();
