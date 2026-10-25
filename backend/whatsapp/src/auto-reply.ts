import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { BufferJSON } from '@whiskeysockets/baileys';

export type Decision = { action: 'ignore' } | { action: 'reply'; text: string };
const script = fileURLToPath(new URL('../python/auto_reply.py', import.meta.url));

function parseDecision(value: unknown): Decision {
  if (value && typeof value === 'object' && 'action' in value) {
    if (value.action === 'ignore') return { action: 'ignore' };
    if (value.action === 'reply' && 'text' in value && typeof value.text === 'string' && value.text.trim()) {
      return { action: 'reply', text: value.text };
    }
  }
  throw new Error('invalid_policy_decision');
}

/** A local protocol adapter; the persistent Python process owns message policy. */
export function createPolicyWorker() {
  let child: ReturnType<typeof spawn> | undefined;
  let stopped = false;
  let nextId = 0;
  const pending = new Map<string, {
    resolve: (decision: Decision) => void;
    reject: (error: Error) => void;
    timer: ReturnType<typeof setTimeout>;
  }>();

  function reset() {
    const previous = child;
    child = undefined;
    previous?.stdin?.destroy();
    previous?.stdout?.destroy();
    previous?.kill('SIGKILL');
    for (const request of pending.values()) {
      clearTimeout(request.timer);
      request.reject(new Error('python_policy_failed'));
    }
    pending.clear();
  }

  function start() {
    const workerProcess = spawn(process.env.WHATSAPP_PYTHON || 'python3', [script], {
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' },
      stdio: ['pipe', 'pipe', 'ignore'],
    });
    child = workerProcess;
    let buffer = '';
    const failed = () => { if (child === workerProcess) reset(); };
    workerProcess.on('error', failed);
    workerProcess.on('exit', failed);
    workerProcess.stdin!.on('error', failed);
    workerProcess.stdout!.setEncoding('utf8');
    workerProcess.stdout!.on('data', (chunk: string) => {
      if (child !== workerProcess) return;
      buffer += chunk;
      try {
        let newline: number;
        while ((newline = buffer.indexOf('\n')) !== -1) {
          if (newline > 16384) throw new Error('oversized_policy_response');
          const response = JSON.parse(buffer.slice(0, newline));
          buffer = buffer.slice(newline + 1);
          const request = pending.get(response?.id);
          if (!request) throw new Error('unknown_policy_request');
          const decision = parseDecision(response.decision);
          clearTimeout(request.timer);
          pending.delete(response.id);
          request.resolve(decision);
        }
        if (buffer.length > 16384) throw new Error('oversized_policy_response');
      } catch { failed(); }
    });
    return workerProcess;
  }

  function decide(event: Record<string, unknown>): Promise<Decision> {
    if (stopped) return Promise.reject(new Error('python_policy_stopped'));
    return new Promise((resolve, reject) => {
      const workerProcess = child ?? start();
      const id = String(++nextId);
      pending.set(id, { resolve, reject, timer: setTimeout(reset, 5000) });
      try { workerProcess.stdin!.write(JSON.stringify({ id, event }, BufferJSON.replacer) + '\n'); }
      catch { reset(); }
    });
  }

  return { decide, stop() { stopped = true; reset(); } };
}
