import { useEffect, useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { createNote, listNotes, type Note } from '@/lib/api'

export function App() {
  const [notes, setNotes] = useState<Note[]>([])
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try { setNotes(await listNotes()) }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not load notes.') }
    finally { setLoading(false) }
  }

  useEffect(() => { void load() }, [])

  async function save(event: FormEvent) {
    event.preventDefault()
    if (!text.trim() || saving) return
    setSaving(true)
    setError('')
    try {
      const note = await createNote(text.trim())
      setNotes((current) => [...current, note])
      setText('')
    } catch (e) { setError(e instanceof Error ? e.message : 'Could not save note.') }
    finally { setSaving(false) }
  }

  return <main className="mx-auto max-w-3xl px-6 py-12 sm:py-20">
    <header className="mb-12 border-b border-border pb-8">
      <p className="mb-5 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground">A place to begin</p>
      <h1 className="font-serif text-5xl tracking-tight sm:text-6xl">Your notebook.</h1>
      <p className="mt-4 max-w-md text-muted-foreground">Capture something worth keeping. Come back to it whenever you need.</p>
    </header>
    <form onSubmit={save} className="mb-10">
      <label htmlFor="note" className="mb-3 block text-sm font-semibold">New note</label>
      <textarea id="note" value={text} onChange={(e) => setText(e.target.value)}
        maxLength={500} required rows={3} disabled={saving}
        placeholder="An idea, a reminder, a small discovery…"
        className="w-full resize-y rounded-xl border border-border bg-card p-4 focus-visible:outline-2 focus-visible:outline-ring" />
      <div className="mt-3 flex items-center justify-between gap-4">
        <span className="text-xs text-muted-foreground">{text.length} / 500</span>
        <Button type="submit" disabled={saving || loading || !text.trim()}>{saving ? 'Saving…' : 'Save note'}</Button>
      </div>
    </form>
    {error && <div role="alert" className="mb-6 flex items-center justify-between gap-4 rounded-xl border border-red-300 p-4 text-sm">
      <p>{error}</p><Button type="button" variant="outline" onClick={() => void load()}>Retry</Button>
    </div>}
    <section aria-label="Saved notes" aria-live="polite">
      <h2 className="mb-5 text-sm font-semibold">Saved notes <span className="ml-2 text-muted-foreground">{notes.length}</span></h2>
      {loading ? <p role="status" className="text-muted-foreground">Opening your notebook…</p>
        : notes.length ? <ul className="divide-y divide-border">{notes.map((note) =>
          <li key={note.id} className="whitespace-pre-wrap break-words py-5 leading-relaxed">{note.text}</li>)}</ul>
        : !error && <p className="rounded-xl border border-dashed border-border p-8 text-center text-muted-foreground">A blank page. Add your first note above.</p>}
    </section>
  </main>
}
