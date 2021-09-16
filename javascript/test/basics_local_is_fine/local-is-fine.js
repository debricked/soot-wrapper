(function () {
  let func_1 = function (x) { return x; };
  let func_2 = { 'func_1': function (x) { return x; }};
  func_2.func_1()
  func_1()  
}());
