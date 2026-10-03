// Runs every browser test case in tests/test_*.cjs concurrently in one browser, or the cases named as
// FILE:CASE arguments, or with --group K/N every Nth case from the Kth, one at a time
// (tools/tests/test_site.py runs N groups on the suite's workers). One JSON line per case: name, ok, seconds, error.
const fs = require('node:fs');
const {runCases} = require('./browser_support.cjs');

const cases = {};
for (const file of fs.readdirSync(__dirname).filter(name => /^test_.*\.cjs$/.test(name)).sort()) {
  for (const [name, run] of Object.entries(require(`./${file}`))) cases[`${file.replace(/\.cjs$/, '')}:${name}`] = run;
}
let names = process.argv.slice(2);
const grouped = names[0] === '--group';
if (grouped) {
  const [k, n] = names[1].split('/').map(Number);
  names = Object.keys(cases).filter((_, i) => i % n === k);
}
runCases(cases, names, {sequential: grouped}).catch(error => { console.error(error); process.exitCode = 1; });
