import assert from 'node:assert/strict';
import { spawn, spawnSync } from 'node:child_process';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const scratch = await mkdtemp(join(tmpdir(), 'python-reply-proof-'));
const children = new Set();
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const parse = text => text.split('\n').flatMap(line => { try { return [JSON.parse(line)]; } catch { return []; } });
const expected = '🤖 hey I am the AI assistant of Marco';
async function run(scenario) {
  const tracePath = join(scratch, `${scenario}.jsonl`);
  const env = { ...process.env, WHATSAPP_AUTH_DIR: join(scratch, scenario, 'auth'), PROOF_SCENARIO: scenario, PROOF_TRACE: tracePath,
    WHATSAPP_STATUS_FILE: join(scratch, scenario, 'status.json'),
    NODE_OPTIONS: `--import=${fileURLToPath(new URL('./register.mjs', import.meta.url))}`, NO_COLOR: '1' };
  env.WHATSAPP_AUTO_REPLY = '1';
  delete env.WHATSAPP_PYTHON;
  if (scenario === 'opt-out') delete env.WHATSAPP_AUTO_REPLY;
  if (scenario === 'missing-python') env.WHATSAPP_PYTHON = join(scratch, 'does-not-exist');
  if (['reconnect', 'shutdown', 'timeout'].includes(scenario)) {
    const wrapper = join(scratch, `${scenario}-python`);
    await writeFile(wrapper, `#!/bin/sh\nsleep ${scenario === 'timeout' ? '7' : '0.5'}\nexec python3 "$@"\n`, { mode: 0o700 });
    env.WHATSAPP_PYTHON = wrapper;
  }
  const child = spawn('npm', ['start'], { cwd: fileURLToPath(new URL('../', import.meta.url)), detached: true, env, stdio: ['ignore', 'pipe', 'pipe'] });
  children.add(child);
  let stdout = '', stderr = '', done = false, code;
  child.stdout.on('data', data => stdout += data);
  child.stderr.on('data', data => stderr += data);
  child.on('exit', value => { code = value; done = true; });
  const trace = async () => parse(await readFile(tracePath, 'utf8').catch(() => ''));
  const deadline = Date.now() + 12000;
  while (!(await trace()).some(e => e.action === 'batch-complete')) {
    assert(!done, `${scenario}: CLI exited before input\n${stdout}\n${stderr}`);
    assert(Date.now() < deadline, `${scenario}: no transport input\n${stdout}\n${stderr}`);
    await sleep(25);
  }
  const sendsExpected = { batch: 3, 'send-failure': 2, reconnect: 1 }[scenario];
  if (sendsExpected !== undefined) {
    while ((await trace()).filter(e => e.action === 'send').length < sendsExpected && !done && Date.now() < deadline) await sleep(25);
    assert.equal((await trace()).filter(e => e.action === 'send').length, sendsExpected, `${scenario}: expected automatic sends via normal startup\n${stdout}\n${stderr}`);
    await sleep(700); // also expose recursive replies to bot-origin sends
  } else if (['missing-python', 'timeout'].includes(scenario)) {
    while (!parse(stdout).some(e => e.event === 'error') && !done && Date.now() < deadline) await sleep(25);
    const errors = parse(stdout).filter(e => e.event === 'error');
    assert.equal(errors.length, 1, `${scenario}: actionable error required\n${stdout}\n${stderr}`);
    assert.match(errors[0].reason, /python/i);
    assert.match(errors[0].reason, /Python 3|WHATSAPP_PYTHON/);
    await sleep(250);
  } else await sleep(1000);
  if (scenario !== 'shutdown') {
    assert(!done, `${scenario}: listener must survive`);
    const status = JSON.parse(await readFile(env.WHATSAPP_STATUS_FILE, 'utf8'));
    assert.equal(status.connected, true, `${scenario}: persisted live connection`);
    assert.equal(status.pid, (await trace()).find(e => e.action === 'socket').pid);
    const setupReadback = spawnSync('python3', ['-c',
      'import sys; sys.path.insert(0, sys.argv[2]); from pathlib import Path; from setup_host import wait_baileys; wait_baileys(Path(sys.argv[1]))',
      env.WHATSAPP_STATUS_FILE, fileURLToPath(new URL('../../../scripts/', import.meta.url))], { encoding: 'utf8' });
    assert.equal(setupReadback.status, 0, `${scenario}: setup must verify the live bot consumer\n${setupReadback.stderr}`);
    process.kill((await trace()).find(e => e.action === 'socket').pid, 'SIGTERM');
  }
  const stopDeadline = Date.now() + 9000;
  while (!done && Date.now() < stopDeadline) await sleep(25);
  assert(done && code === 0, `${scenario}: clean shutdown required\n${stdout}\n${stderr}`);
  const stopped = JSON.parse(await readFile(env.WHATSAPP_STATUS_FILE, 'utf8'));
  assert.equal(stopped.connected, false, `${scenario}: stopped connection is not reported healthy`);
  assert.deepEqual(Object.keys(stopped).sort(), ['at', 'connected', 'pid']);
  const records = await trace(), sends = records.filter(e => e.action === 'send');
  assert(records.some(e => e.action === 'end'), `${scenario}: socket closes`);
  assert(!records.some(e => e.action === 'logout'));
  assert(!/PRIVATE_INCOMING_BODY|PRIVATE_PROVIDER_FAILURE|noiseKey|signedIdentityKey|advSecretKey/.test(stdout + stderr), 'no content, raw provider errors or auth secrets in logs');
  for (const send of sends) { assert.deepEqual(send.content, { text: expected }); assert.equal(send.closed, false); }
  if (scenario === 'batch') assert.deepEqual(sends.map(e => e.chat).sort(), ['111@s.whatsapp.net', '222@g.us', '444@s.whatsapp.net']);
  if (scenario === 'send-failure') {
    assert.deepEqual(sends.map(e => e.chat), ['111@s.whatsapp.net', '222@g.us']);
    const errors = parse(stdout).filter(e => e.event === 'error');
    assert.equal(errors.length, 1); assert.match(errors[0].reason, /send/);
  }
  if (scenario === 'reconnect') { assert.equal(sends.length, 1); assert.equal(sends[0].generation, 2); assert.equal(sends[0].chat, '222@g.us'); }
  if (['opt-out', 'missing-python', 'timeout', 'shutdown'].includes(scenario)) assert.equal(sends.length, 0, `${scenario}: no sends`);
  if (scenario === 'opt-out') assert.equal(parse(stdout).filter(e => e.event === 'incoming_message').length, 3);
  // Kill any surviving test wrapper descendants before dropping the isolated process group.
  try { process.kill(-child.pid, 'SIGKILL'); } catch {}
  children.delete(child);
  console.log(`PASS ${scenario}: real CLI, real Python boundary and clean shutdown`);
}
try {
  for (const scenario of ['batch', 'opt-out', 'missing-python', 'send-failure', 'reconnect', 'shutdown', 'timeout']) await run(scenario);
} finally {
  for (const child of children) { try { process.kill(-child.pid, 'SIGKILL'); } catch {} }
  await rm(scratch, { recursive: true, force: true });
}
