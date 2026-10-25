import { mkdir, chmod } from 'node:fs/promises';
import makeWASocket, { DisconnectReason, useMultiFileAuthState, type UserFacingSocketConfig } from '@whiskeysockets/baileys';
import qrcode from 'qrcode-terminal';
import { messageHandler, type Emit } from './messages.js';
import { createPolicyWorker, type Decision } from './auto-reply.js';

// Baileys debug output can contain message bodies and session material.
const silentLogger: NonNullable<UserFacingSocketConfig['logger']> = {
  level: 'silent', child: () => silentLogger,
  trace() {}, debug() {}, info() {}, warn() {}, error() {},
};
const terminalReasons = new Map<number, string>([
  [DisconnectReason.loggedOut, 'logged_out: link again using a new private WHATSAPP_AUTH_DIR'],
  [DisconnectReason.badSession, 'bad_session: link again using a new private WHATSAPP_AUTH_DIR'],
  [DisconnectReason.connectionReplaced, 'connection_replaced: stop the other connection before restarting'],
  [DisconnectReason.forbidden, 'forbidden: check account access before restarting'],
  [DisconnectReason.multideviceMismatch, 'multidevice_mismatch: check linked devices and link again'],
]);

export async function startListener(authDir: string, emit: Emit) {
  await mkdir(authDir, { recursive: true, mode: 0o700 });
  await chmod(authDir, 0o700);
  const { state, saveCreds } = await useMultiFileAuthState(authDir);
  const handleMessages = messageHandler(emit);
  let current: ReturnType<typeof makeWASocket> | undefined;
  let policy: ReturnType<typeof createPolicyWorker> | undefined;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let writes: Promise<void> = Promise.resolve();
  let stopped = false;
  let failures = 0;
  let stopping: Promise<void> | undefined;

  function stop(code = 0, reason = 'requested') {
    if (code) process.exitCode = code;
    if (stopping) return stopping;
    stopped = true;
    policy?.stop();
    clearTimeout(timer);
    const socket = current;
    current = undefined;
    stopping = (async () => {
      try { await socket?.end(undefined); }
      catch { process.exitCode = 1; emit('error', { reason: 'socket_close_failed' }); }
      await writes;
      emit('stopped', { reason });
    })();
    return stopping;
  }

  function retry(code?: number) {
    if (stopped || timer) return;
    const delayMs = code === DisconnectReason.restartRequired ? 0 : Math.min(1000 * 2 ** Math.min(failures++, 5), 30000);
    emit('reconnecting', { reason: code ?? 'connection_failed', delayMs });
    timer = setTimeout(() => {
      timer = undefined;
      void writes.then(() => { if (!stopped) connect(); });
    }, delayMs);
  }

  function connect() {
    if (stopped || current) return;
    try {
      const socket = makeWASocket({ auth: state, logger: silentLogger,
        markOnlineOnConnect: false, syncFullHistory: false, shouldSyncHistoryMessage: () => false });
      current = socket;
      const worker = createPolicyWorker();
      policy = worker;
      socket.ev.on('creds.update', () => {
        if (stopped || current !== socket) return;
        writes = writes.then(saveCreds).catch(() => {
          emit('error', { reason: 'credential_save_failed: check session directory permissions and disk space' });
          void stop(1, 'credential_save_failed');
        });
      });
      socket.ev.on('messages.upsert', async event => {
        if (stopped || current !== socket) return;
        const messages = handleMessages(event, socket.user?.id ?? state.creds.me?.id ?? null);
        if (process.env.WHATSAPP_AUTO_REPLY !== '1') return;
        for (const message of messages) {
          if (stopped || current !== socket) return;
          let decision: Decision;
          try { decision = await worker.decide(message); }
          catch {
            if (!stopped && current === socket) emit('error', { reason: 'python_reply_failed: check Python 3 or WHATSAPP_PYTHON' });
            continue;
          }
          if (stopped || current !== socket) return;
          if (decision.action === 'ignore') continue;
          try {
            await socket.sendMessage(String(message.chatId), { text: decision.text });
            if (!stopped && current === socket) emit('auto_reply_sent', { id: message.id, chatId: message.chatId });
          } catch {
            if (!stopped && current === socket) emit('error', { reason: 'auto_reply_send_failed' });
          }
        }
      });
      socket.ev.on('connection.update', update => {
        if (stopped || current !== socket) return;
        if (update.qr) {
          process.stderr.write('Scan this QR in WhatsApp → Settings → Linked devices → Link a device.\n');
          qrcode.generate(update.qr, { small: true }, qr => process.stderr.write(qr + '\n'));
        }
        if (update.connection === 'open') {
          failures = 0;
          emit('connected');
        }
        if (update.connection === 'close') {
          policy?.stop();
          const error = update.lastDisconnect?.error as { output?: { statusCode?: number } } | undefined;
          const code = error?.output?.statusCode;
          current = undefined;
          const reason = code === undefined ? undefined : terminalReasons.get(code);
          if (reason) void stop(1, reason);
          else retry(code);
        }
      });
    } catch {
      emit('error', { reason: 'connection_start_failed' });
      retry();
    }
  }
  connect();
  return { stop };
}
