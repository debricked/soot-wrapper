export const sqrt = Math.sqrt;
export function square(x) {
    return x * x;
}
export function diag(a, b) {
    return sqrt(square(a) + square(b));
}
