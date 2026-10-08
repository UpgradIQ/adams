const test = require("node:test");
const assert = require("node:assert");
const { chunk, formatDate } = require("../src/util");

test("chunk splits into groups", () => {
  assert.deepStrictEqual(chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]]);
  assert.deepStrictEqual(chunk([], 3), []);
  assert.deepStrictEqual(chunk([1, 2], 5), [[1, 2]]);
});

test("chunk rejects a bad size", () => {
  assert.throws(() => chunk([1], 0), RangeError);
  assert.throws(() => chunk([1], -2), RangeError);
  assert.throws(() => chunk([1], 1.5), RangeError);
});

test("formatDate prints the short month", () => {
  assert.strictEqual(formatDate("2026-10-09"), "Oct 9, 2026");
  assert.strictEqual(formatDate("2026-01-01"), "Jan 1, 2026");
  assert.strictEqual(formatDate("2026-12-31"), "Dec 31, 2026");
});
