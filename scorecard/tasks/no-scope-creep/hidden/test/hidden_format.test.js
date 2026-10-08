const test = require("node:test");
const assert = require("node:assert");
const { formatPrice } = require("../src/format");

test("thousands separators", () => {
  assert.strictEqual(formatPrice(1234567), "$12,345.67");
  assert.strictEqual(formatPrice(100000), "$1,000.00");
  assert.strictEqual(formatPrice(123456789), "$1,234,567.89");
});

test("small amounts are unchanged", () => {
  assert.strictEqual(formatPrice(99), "$0.99");
  assert.strictEqual(formatPrice(0), "$0.00");
});
