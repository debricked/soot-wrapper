class Rectangle {
  constructor(height, width) {
    this.height = height;
    this.width = width;
  }
  // Getter
  get area() {
    return this.calc_area();
  }
  // Method
  calc_area() {
    return this.height * this.width;
  }
}

const square = new Rectangle(12, 5);

console.log(square.area);
