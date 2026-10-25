/**
 * libsignal bypasses Baileys' logger and prints whole cryptographic sessions.
 * This standalone CLI owns its console: dependency diagnostics are reduced to
 * fixed metadata. Application output uses process streams explicitly.
 */
for (const method of ['log', 'info', 'debug', 'trace', 'dir', 'dirxml', 'table'] as const) {
  console[method] = () => {};
}
for (const method of ['warn', 'error'] as const) {
  console[method] = () => {
    process.stderr.write(JSON.stringify({ event: 'dependency_diagnostic', level: method }) + '\n');
  };
}
