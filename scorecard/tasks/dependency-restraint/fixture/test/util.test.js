const test = require("node:test");
const assert = require("node:assert");
const { sum } = require("../src/util");

test("sum adds numbers", () => {
  assert.strictEqual(sum([1, 2, 3]), 6);
});
