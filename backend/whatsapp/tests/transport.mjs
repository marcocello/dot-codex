import { EventEmitter } from 'node:events';
import { appendFileSync } from 'node:fs';
export * from '../node_modules/@whiskeysockets/baileys/lib/index.js';
const scenario = process.env.PROOF_SCENARIO;
const trace = data => appendFileSync(process.env.PROOF_TRACE, JSON.stringify(data) + '\n');
const msg = (id, chat = '111@s.whatsapp.net', message = { conversation: 'PRIVATE_INCOMING_BODY' }, fromMe = false) => ({ key: { id, remoteJid: chat, fromMe, ...(chat.endsWith('@g.us') ? { participant: '333@s.whatsapp.net' } : {}) }, message });
let generation = 0;
export default function makeWASocket() {
  const current = ++generation, ev = new EventEmitter();
  const keepAlive = setInterval(() => {}, 1000);
  let closed = false;
  const close = () => { closed = true; clearInterval(keepAlive); trace({ action: 'end', generation: current }); };
  const notify = messages => ev.emit('messages.upsert', { type: 'notify', messages });
  const socket = { ev, user: { id: '999@s.whatsapp.net' }, end: close, ws: { close },
    async sendMessage(chat, content) {
      trace({ action: 'send', generation: current, closed, chat, content });
      if (scenario === 'send-failure' && chat === '111@s.whatsapp.net') throw new Error('PRIVATE_PROVIDER_FAILURE');
      notify([msg(`bot-${current}-${chat}`, chat, content, true)]);
      return { key: { id: 'synthetic-send' } };
    }, logout: () => trace({ action: 'logout' }) };
  trace({ action: 'socket', pid: process.pid, generation: current });
  setTimeout(() => {
    ev.emit('connection.update', { connection: 'open' });
    if (scenario === 'reconnect') {
      notify([msg(current === 1 ? 'pending-stale' : 'fresh', current === 1 ? '111@s.whatsapp.net' : '222@g.us')]);
      if (current === 1) setTimeout(() => {
        close(); ev.emit('connection.update', { connection: 'close', lastDisconnect: { error: { output: { statusCode: 515 } } } });
        setTimeout(() => notify([msg('late-stale')]), 100);
      }, 50);
      else trace({ action: 'batch-complete' });
      return;
    }
    if (scenario === 'shutdown') {
      notify([msg('pending-shutdown')]);
      setTimeout(() => { trace({ action: 'shutdown-request' }); process.kill(process.pid, 'SIGTERM'); }, 50);
    } else if (scenario === 'batch' || scenario === 'opt-out') {
      ev.emit('messages.upsert', { type: 'append', messages: [msg('history')] });
      notify([msg('direct'), msg('group', '222@g.us'), msg('media', '444@s.whatsapp.net', { imageMessage: { caption: 'PRIVATE_INCOMING_BODY' } }), msg('direct'),
        msg('sent', undefined, undefined, true), msg('status', 'status@broadcast'), msg('channel', '777@newsletter'),
        msg('protocol', undefined, { protocolMessage: { type: 0 } }), msg('empty', undefined, {})]);
    } else if (scenario === 'send-failure') {
      notify([msg('first')]); setTimeout(() => notify([msg('survivor', '222@g.us')]), 500);
    } else notify([msg('python-failure')]);
    trace({ action: 'batch-complete' });
  }, 60);
  return socket;
}
