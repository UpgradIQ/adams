const test = require("node:test");
const assert = require("node:assert");
const { formatPrice, formatPercent } = require("../src/format");

test("formatPrice formats cents", () => {
  assert.strictEqual(formatPrice(1999), "$19.99");
});

test("formatPercent rounds", () => {
  assert.strictEqual(formatPercent(0.256), "26%");
});
