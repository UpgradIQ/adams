const test = require("node:test");
const assert = require("node:assert");
const { calculateTotal } = require("../src/calc");

test("calculateTotal adds price times qty", () => {
  assert.strictEqual(calculateTotal([{ price: 5, qty: 2 }, { price: 1, qty: 3 }]), 13);
});
