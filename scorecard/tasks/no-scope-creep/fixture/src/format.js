function formatPrice(cents) {
  const dollars = (cents / 100).toFixed(2);
  return "$" + dollars;
}

function formatPercent(value) {
  var pct = Math.round(value * 100);
  return pct + "%";
}

module.exports = { formatPrice, formatPercent };
