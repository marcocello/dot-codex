import { test, expect } from '@playwright/test'

test('a note is saved and remains after reopening', async ({ page }) => {
  const note = `Remember this ${crypto.randomUUID()}`
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Your notebook.' })).toBeVisible()
  await expect(page.getByRole('status')).not.toBeVisible()
  await page.getByLabel('New note').fill(note)
  await page.getByRole('button', { name: 'Save note' }).click()
  await expect(page.getByText(note, { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByText(note, { exact: true })).toBeVisible()
})

test('failed saves preserve the draft and report the problem', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('status')).not.toBeVisible()
  await page.route('**/api/notes', (route) => route.request().method() === 'POST'
    ? route.fulfill({ status: 503, body: '{}' }) : route.continue())
  await page.getByLabel('New note').fill('Keep my draft')
  await page.getByRole('button', { name: 'Save note' }).click()
  await expect(page.getByRole('alert')).toBeVisible()
  await expect(page.getByLabel('New note')).toHaveValue('Keep my draft')
})
