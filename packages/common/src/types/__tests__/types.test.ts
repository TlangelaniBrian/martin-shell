import { describe, it, expectTypeOf } from 'vitest'
import type { CaseData, SearchSource, SearchResponse } from '../search.js'
import type { Briefcase, Reason, ReasonCase } from '../briefcase.js'
import type { Document, AnalysisResult } from '../document.js'

describe('SearchSource interface', () => {
  it('enforces search method returning Promise<SearchResponse>', () => {
    expectTypeOf<SearchSource['search']>().returns.toEqualTypeOf<Promise<SearchResponse>>()
  })

  it('CaseData id is a number', () => {
    expectTypeOf<CaseData['id']>().toBeNumber()
  })

  it('CaseData saflii_url is a required string', () => {
    expectTypeOf<CaseData['saflii_url']>().toBeString()
  })
})

describe('Briefcase types', () => {
  it('Briefcase has reasons array', () => {
    expectTypeOf<Briefcase['reasons']>().toEqualTypeOf<Reason[]>()
  })

  it('Reason has cases array of ReasonCase', () => {
    expectTypeOf<Reason['cases']>().toEqualTypeOf<ReasonCase[]>()
  })
})

describe('Document types', () => {
  it('Document status is a union of three values', () => {
    expectTypeOf<Document['status']>().toEqualTypeOf<'processing' | 'ready' | 'failed'>()
  })

  it('AnalysisResult mappings is an array', () => {
    expectTypeOf<AnalysisResult['mappings']>().toBeArray()
  })
})
