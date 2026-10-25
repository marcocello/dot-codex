import { getContentType, normalizeMessageContent, type BaileysEventMap } from '@whiskeysockets/baileys';

export type Emit = (event: string, fields?: Record<string, unknown>) => void;

/** Dedupe is bounded and survives socket replacement, but not process restart. */
export function messageHandler(emit: Emit) {
  const seen = new Set<string>();
  return ({ type, messages }: BaileysEventMap['messages.upsert'], ownId: string | null = null) => {
    const events: Record<string, unknown>[] = [];
    if (type !== 'notify') return events;
    for (const message of messages) {
      const { id, remoteJid: chatId, participant, fromMe } = message.key ?? {};
      if (!id || !chatId || !message.message) continue;
      if (!/^[^@]+@(s\.whatsapp\.net|lid|g\.us|c\.us|hosted|hosted\.lid)$/.test(chatId)) continue;
      const content = normalizeMessageContent(message.message);
      const messageType = getContentType(content);
      if (!messageType || messageType === 'protocolMessage' || messageType === 'senderKeyDistributionMessage') continue;
      const direction = fromMe ? 'sent_message' : 'incoming_message';
      const key = JSON.stringify([direction, chatId, fromMe ? '' : participant ?? '', id]);
      if (seen.has(key)) continue;
      seen.add(key);
      if (seen.size > 5000) seen.delete(seen.values().next().value!);
      const fields = { id, chatId, senderId: fromMe ? ownId : participant || chatId, messageType, receivedAt: new Date().toISOString() };
      emit(direction, fields);
      const text = content?.conversation ?? content?.extendedTextMessage?.text
        ?? content?.imageMessage?.caption ?? content?.videoMessage?.caption ?? content?.documentMessage?.caption ?? null;
      events.push({ event: direction, ...fields, key: message.key, message: content, text });
    }
    return events;
  };
}
