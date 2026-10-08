var format = require("./format");

// TODO: handle coupons
function cartTotal(items) {
  var total = 0;
  for (var i = 0; i < items.length; i++) {
    total = total + items[i].cents * items[i].qty;
  }
  return format.formatPrice(total);
}

module.exports = { cartTotal };
