// Runs every browser test case in tests/test_*.cjs concurrently in one browser (tools/tests/test_site.py
// runs this), or the cases named as FILE:CASE arguments. One JSON line per case: name, ok, seconds, error.
const fs = require('node:fs');
const {runCases} = require('./browser_support.cjs');

const cases = {};
for (const file of fs.readdirSync(__dirname).filter(name => /^test_.*\.cjs$/.test(name)).sort()) {
  for (const [name, run] of Object.entries(require(`./${file}`))) cases[`${file.replace(/\.cjs$/, '')}:${name}`] = run;
}
runCases(cases, process.argv.slice(2)).catch(error => { console.error(error); process.exitCode = 1; });
