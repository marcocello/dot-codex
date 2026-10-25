import { registerHooks } from 'node:module';
const fake = new URL('./transport.mjs', import.meta.url).href;
registerHooks({ resolve(specifier, context, next) {
  if (specifier === '@whiskeysockets/baileys') return { url: fake, shortCircuit: true };
  return next(specifier, context);
} });
