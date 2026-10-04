export type Note = { id: number; text: string }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init)
  if (!response.ok) throw new Error('Could not reach your notebook. Please try again.')
  return response.json() as Promise<T>
}

export const listNotes = () => request<Note[]>('/notes')
export const createNote = (text: string) => request<Note>('/notes', {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text }),
})
