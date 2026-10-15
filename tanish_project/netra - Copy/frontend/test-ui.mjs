import { chromium } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import assert from 'node:assert/strict'

await mkdir('../../test-results', {recursive: true})
const browser = await chromium.launch({channel: 'msedge', headless: true})
const page = await browser.newPage({viewport: {width: 1440, height: 1080}})
const errors = []
page.on('pageerror', e => errors.push(e.message))
try {
  await page.goto('http://127.0.0.1:8001')
  await page.getByRole('button', {name: 'Show me an example'}).click()
  await page.getByText('EXAMPLE DATA · FICTIONAL WEBSITE').waitFor()
  await page.screenshot({path: '../../test-results/netra-overview.png', fullPage: true})
  await page.getByText('Advanced details',{exact:true}).click()
  await page.getByRole('button', {name: 'Recorded evidence',exact:true}).click()
  await page.getByRole('button', {name: 'Technical', exact: true}).click()
  await page.getByLabel('Search findings').fill('DMARC')
  assert.equal(await page.locator('article.finding').count(), 1)
  await page.getByRole('button', {name: 'Technical fixes',exact:true}).click()
  const before = await page.locator('.simulator strong').innerText()
  await page.getByRole('checkbox').first().check()
  assert.notEqual(await page.locator('.simulator strong').innerText(), before)
  const exported = page.waitForEvent('download')
  await page.getByRole('button', {name: 'Export selected action plan'}).click()
  const download = await exported
  assert.equal(download.suggestedFilename(), 'netra-remediation-plan.json')
  await page.getByRole('button', {name: 'Connection map',exact:true}).click()
  await page.getByRole('button', {name: '203.0.113.42', exact: true}).locator('circle').click()
  assert.match(await page.locator('.graph-wrap p').first().innerText(), /DNS/)
  await page.getByRole('button', {name: 'Past checkups',exact:true}).click()
  await page.getByRole('button', {name: 'northstar.example'}).first().click()
  await page.getByText('EXAMPLE DATA · FICTIONAL WEBSITE').waitFor()
  await page.reload()
  await page.getByRole('button', {name: 'Past checkups',exact:true}).click()
  await page.getByRole('button', {name: 'northstar.example'}).first().click()
  await page.setViewportSize({width: 390, height: 844})
  await page.screenshot({path: '../../test-results/netra-mobile.png', fullPage: true})
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth), false, 'Mobile page must not overflow horizontally')
  assert.deepEqual(errors, [])
  await page.getByRole('button', {name: 'Multiple websites', exact: true}).click()
  await page.getByRole('button', {name: 'Queue portfolio'}).click()
  await page.getByText('Enter between 1 and 10 domains.').waitFor()
  console.log('PASS: demo, evidence filters, technical detail, remediation simulation, export, interactive graph, persistent history, mobile layout; no browser errors.')
} finally {
  await browser.close()
}
