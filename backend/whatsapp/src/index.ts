import './console-privacy.js';
import { homedir } from 'node:os';
import { mkdirSync, renameSync, unlinkSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { startListener } from './listener.js';

process.umask(0o077);
const statusFile = process.env.WHATSAPP_STATUS_FILE;
let connected = false;
const recordStatus = () => {
  if (!statusFile) return;
  const temporary = `${statusFile}.${process.pid}.${Date.now()}.tmp`;
  try {
    mkdirSync(dirname(statusFile), { recursive: true, mode: 0o700 });
    writeFileSync(temporary, JSON.stringify({ connected, pid: process.pid, at: Date.now() / 1000 }) + '\n', { mode: 0o600, flag: 'wx' });
    renameSync(temporary, statusFile);
  } catch {
    // Setup treats an absent/stale heartbeat as incomplete. No credentials or message data enter this file.
  } finally {
    try { unlinkSync(temporary); } catch {}
  }
};
recordStatus();
if (statusFile) setInterval(recordStatus, 30000).unref();
const emit = (event: string, fields: Record<string, unknown> = {}) => {
  if (['connected', 'reconnecting', 'stopped'].includes(event)) {
    connected = event === 'connected';
    recordStatus();
  }
  process.stdout.write(JSON.stringify({ event, ...fields }) + '\n');
};
const defaultAuthDir = resolve(process.env.XDG_STATE_HOME || resolve(homedir(), '.local/state'), 'dot-codex/whatsapp');
const authDir = process.env.WHATSAPP_AUTH_DIR ? resolve(process.env.WHATSAPP_AUTH_DIR) : defaultAuthDir;
let listener: Awaited<ReturnType<typeof startListener>> | undefined;
let interrupted = false;
for (const signal of ['SIGINT', 'SIGTERM'] as const) {
  process.on(signal, () => {
    interrupted = true;
    void listener?.stop(0, signal);
  });
}
try {
  listener = await startListener(authDir, emit);
  if (interrupted) await listener.stop();
} catch {
  emit('error', { reason: 'startup_failed: check WHATSAPP_AUTH_DIR permissions and local setup' });
  process.exitCode = 1;
}
