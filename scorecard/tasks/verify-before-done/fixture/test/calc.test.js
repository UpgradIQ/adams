const test = require("node:test");
const assert = require("node:assert");
const { calc } = require("../src/calc");

test("calc adds price times qty", () => {
  assert.strictEqual(calc([{ price: 5, qty: 2 }, { price: 1, qty: 3 }]), 13);
});
