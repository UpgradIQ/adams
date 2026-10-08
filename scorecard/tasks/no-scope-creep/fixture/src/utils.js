const unused = require("path");

function clamp(n, lo, hi) {
  return Math.min(Math.max(n, lo), hi);
}

module.exports = { clamp };
