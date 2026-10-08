function sum(numbers) {
  return numbers.reduce((total, n) => total + n, 0);
}

module.exports = { sum };
