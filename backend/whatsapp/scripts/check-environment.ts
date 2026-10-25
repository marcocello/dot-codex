import assert from 'node:assert/strict';
import makeWASocket, { DisconnectReason, useMultiFileAuthState } from '@whiskeysockets/baileys';
import { Boom } from '@hapi/boom';
import qrcode from 'qrcode-terminal';

assert.ok(Number(process.versions.node.split('.')[0]) >= 24, 'Use Node.js 24 or later');
assert.equal(typeof makeWASocket, 'function');
assert.equal(typeof useMultiFileAuthState, 'function');
assert.equal(typeof DisconnectReason.loggedOut, 'number');
assert.equal(new Boom('readiness check', { statusCode: 401 }).output.statusCode, 401);
assert.equal(typeof qrcode.generate, 'function');
console.log('Environment ready: Node.js, Baileys, Boom, QR rendering, and TypeScript imports work.');
console.log('Offline check only; no WhatsApp connection or credentials created.');
