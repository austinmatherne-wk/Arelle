import assert from 'node:assert/strict'
import { readFile, readdir } from 'node:fs/promises'
import { test } from 'node:test'

const output = new URL('./public/demo/ixbrl-viewer/', import.meta.url)

async function artifact(name) {
  return readFile(new URL(name, output), 'utf8')
}

test('generated Viewer demo contains the complete healthy offline artifact', async () => {
  const filingDependencies = [
    'exhibit1019-formofemployme.htm',
    'exhibit1022-herrenofferlet.htm',
    'exhibit1023-peekofferletter.htm',
    'exhibit211subsidiaries1231.htm',
    'exhibit231consentofauditor.htm',
    'exhibit311-section302xceoc.htm',
    'exhibit312-section302xcfoc.htm',
    'exhibit321-section906xceoc.htm',
    'exhibit322-section906xcfoc.htm',
    'exhibit404-descriptionofse.htm',
    'wk-20251231.htm',
    'wk-20251231.xsd',
    'wk-20251231_cal.xml',
    'wk-20251231_def.xml',
    'wk-20251231_g1.jpg',
    'wk-20251231_lab.xml',
    'wk-20251231_pre.xml',
  ]
  assert.deepEqual(
    (await readdir(output)).toSorted(),
    [...filingDependencies, 'ixbrlviewer.config.json', 'ixbrlviewer.js', 'viewer.htm'].toSorted(),
  )

  assert.deepEqual(JSON.parse(await artifact('ixbrlviewer.config.json')), {
    skin: { faviconUrl: '../../favicon.ico' },
  })
  const filing = await artifact('wk-20251231.htm')
  assert.match(filing, /name="dei:EntityCentralIndexKey"[^>]*>0001445305</)
  assert.match(filing, /name="dei:DocumentType"[^>]*>10-K</)
  assert.match(filing, /name="dei:DocumentFiscalYearFocus"[^>]*>2025</)
  assert.match(filing, /name="dei:DocumentFiscalPeriodFocus"[^>]*>FY</)
  assert.match(filing, /name="dei:EntityRegistrantName"[^>]*>WORKIVA INC</)
  assert.equal(filing.match(/format="ixt-sec:/g)?.length, 48)

  const viewerHtml = await artifact('viewer.htm')
  const viewerDataSource = viewerHtml.match(
    /<script[^>]*type=(?:"application\/x\.ixbrl-viewer\+json"|application\/x\.ixbrl-viewer\+json)[^>]*>([\s\S]*?)<\/script>/,
  )?.[1]
  assert.ok(viewerDataSource, 'expected generated Viewer data')

  const viewerData = JSON.parse(viewerDataSource)
  assert.deepEqual(viewerData.features, {
    highlight_facts_on_startup: true,
    home_link_label: 'Arelle',
    home_link_url: '/',
    review: false,
  })
  const conceptCount = viewerData.sourceReports
    .flatMap((sourceReport) => sourceReport.targetReports)
    .reduce((count, targetReport) => count + Object.keys(targetReport.concepts).length, 0)
  assert.ok(conceptCount >= 800, `expected at least 800 concepts, received ${conceptCount}`)
  assert.doesNotMatch(viewerDataSource, /INVALID_IX_VALUE|ixTransformValueError/)
})
