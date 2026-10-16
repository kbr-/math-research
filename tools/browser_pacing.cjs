// Pacing for tools/browser_get.cjs: visits to an outside site are spaced and timed like a person's.
// On 16 October 2026 three automated visits to ResearchGate within minutes, with page actions at machine
// speed, turned a session that had passed its bot check into one that was refused (user: "Use human
// reaction times and how long it takes for human to navigate a site"). Every visit to a host is recorded
// in ~/.cache/browser-get/visits.json; a new one waits until MIN_SPACING_S after the last, refused when
// that wait is longer than MAX_WAIT_S or when the host had MAX_PER_HOUR visits in the last hour. Within a
// visit, the engines read for a few seconds, scroll, and move the pointer to a link in steps before
// clicking. Local addresses (tests) are exempt.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const MIN_SPACING_S = 90;
const MAX_PER_HOUR = 10;
const MAX_WAIT_S = 120;

function isLocal(host) {
  return host === 'localhost' || /^127\./.test(host) || host === '::1' || host === '[::1]';
}

// The site a host belongs to, for spacing: www.researchgate.net and researchgate.net count as one.
function site(host) {
  return host.split('.').slice(-2).join('.');
}

// Decide a visit to `host` at time `now` (seconds) against earlier visit times: {wait} seconds to wait
// first, or {refuse} with the reason. Pure, for tests.
function plan(times, now) {
  const recent = times.filter(t => now - t < 3600);
  if (recent.length >= MAX_PER_HOUR) {
    const at = Math.min(...recent) + 3600;
    return {refuse: `${recent.length} visits in the last hour; the next is allowed in ${Math.ceil(at - now)} s`};
  }
  const last = recent.length ? Math.max(...recent) : -Infinity;
  const wait = Math.max(0, last + MIN_SPACING_S - now);
  if (wait > MAX_WAIT_S) return {refuse: `the last visit was ${Math.round(now - last)} s ago; wait ${Math.ceil(wait)} s`};
  return {wait};
}

function store(home) {
  return path.join(home || os.homedir(), '.cache', 'browser-get', 'visits.json');
}

function readVisits(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { return {}; }
}

// Wait as a visit to `url` requires, then record it; throws with the reason when the visit is refused.
async function beforeVisit(url, log, home) {
  const host = new URL(url).hostname;
  if (isLocal(host)) return;
  const file = store(home);
  const visits = readVisits(file);
  const key = site(host);
  const decision = plan(visits[key] || [], Date.now() / 1000);
  if (decision.refuse) throw new Error(`pacing: ${key} not visited now: ${decision.refuse}`);
  if (decision.wait > 0) {
    log(`pacing: waiting ${Math.ceil(decision.wait)} s before visiting ${key}`);
    await sleep(decision.wait * 1000);
  }
  const now = Date.now() / 1000;
  visits[key] = [...(visits[key] || []).filter(t => now - t < 3600), now];
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, JSON.stringify(visits));
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

// A pause of a person's length, uniform in [lo, hi] milliseconds; none for a local page.
function pause(url, lo, hi) {
  return isLocal(new URL(url).hostname) ? Promise.resolve() : sleep(lo + Math.random() * (hi - lo));
}

module.exports = {beforeVisit, pause, plan, site, isLocal, MIN_SPACING_S, MAX_PER_HOUR, MAX_WAIT_S};
