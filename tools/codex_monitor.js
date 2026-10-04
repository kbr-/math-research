/* Evaluate this expression in a Codex functions.exec cell; see tools/CODEX.md. */
(async function monitorProtectedRun({tools, notify, yield_control, root, session, args,
                                     at = 300, sandbox_permissions = "require_escalated"}) {
  if (!root || !/^[A-Za-z0-9_.-]+$/.test(session) || !Array.isArray(args)
      || args.some(arg => typeof arg !== "string")) throw new Error("Invalid monitored run arguments");
  const quote = value => "'" + value.replace(/'/g, "'\\''") + "'";
  const execute = cmd => tools.exec_command({cmd, workdir: root, sandbox_permissions, yield_time_ms: 1000});
  const show = result => { if (result.output) notify(result.output); };
  let watcher = await execute(`python3 tools/watch_run.py ${quote(session)} --arm --at ${Number(at)}`);
  show(watcher);
  const ready = /^WATCH_READY (\{.*\})$/m.exec(watcher.output || "");
  if (!ready || !watcher.session_id) throw new Error("Watcher did not acknowledge readiness; no run released");
  const run = JSON.parse(ready[1]).run_id;
  if (!/^[0-9a-f]{32}$/.test(run)) throw new Error("Invalid watcher run ID; no run released");
  let cancelled = false;
  const cancel = async () => {
    if (cancelled) return;
    cancelled = true;
    let result = await execute(`python3 tools/watch_run.py --cancel ${run}`);
    show(result);
    while (result.session_id) {
      result = await tools.write_stdin({session_id: result.session_id, chars: "", yield_time_ms: 1000});
      show(result);
    }
    if (result.exit_code !== 0) throw new Error("Cancellation failed; inspect the protected service");
  };
  const collect = async initial => {
    let result = initial;
    try {
      while (result.session_id) {
        result = await tools.write_stdin({session_id: result.session_id, chars: "", yield_time_ms: 1000});
        show(result);
      }
      if (result.exit_code !== 0) await cancel();
      return result.exit_code;
    } catch (error) {
      await cancel();
      throw error;
    }
  };
  let job;
  try {
    job = await execute(`./compute.sh run ${quote(session)} --run-id ${run} ${args.map(quote).join(" ")}`);
    show(job);
    await yield_control();
    const results = await Promise.allSettled([collect(watcher), collect(job)]);
    for (const result of results) {
      if (result.status === "rejected") throw result.reason;
      if (result.value !== 0) throw new Error("Monitored command or watcher failed; read the complete output above");
    }
    return {run_id: run, exit_code: 0};
  } catch (error) {
    await cancel();
    throw error;
  }
})
