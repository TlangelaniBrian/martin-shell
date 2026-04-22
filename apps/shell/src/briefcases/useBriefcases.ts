import { apiFetch } from '@martin/common'
import type { Briefcase, Reason, ReasonCase, ContentVersion, GenerateResponse } from '@martin/common'

export function useBriefcases() {
  function listBriefcases(): Promise<{ briefcases: Briefcase[]; total: number }> {
    return apiFetch('/briefcases/')
  }

  function getBriefcase(id: string): Promise<Briefcase> {
    return apiFetch(`/briefcases/${id}`)
  }

  function createBriefcase(name: string, description?: string): Promise<Briefcase> {
    return apiFetch('/briefcases/', {
      method: 'POST',
      body: JSON.stringify({ name, description: description ?? null }),
    })
  }

  function updateBriefcase(id: string, data: { name?: string; description?: string }): Promise<Briefcase> {
    return apiFetch(`/briefcases/${id}`, { method: 'PATCH', body: JSON.stringify(data) })
  }

  function deleteBriefcase(id: string): Promise<void> {
    return apiFetch(`/briefcases/${id}`, { method: 'DELETE' })
  }

  function createReason(briefcaseId: string, title: string): Promise<Reason> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons`, {
      method: 'POST',
      body: JSON.stringify({ title, description: null }),
    })
  }

  function updateReason(briefcaseId: string, reasonId: string, data: { title?: string; content?: string }): Promise<Reason> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  function deleteReason(briefcaseId: string, reasonId: string): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}`, { method: 'DELETE' })
  }

  function reorderReasons(briefcaseId: string, reasonIds: string[]): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/reorder`, {
      method: 'PATCH',
      body: JSON.stringify({ reason_ids: reasonIds }),
    })
  }

  function addCaseToReason(briefcaseId: string, reasonId: string, caseId: number): Promise<ReasonCase> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases`, {
      method: 'POST',
      body: JSON.stringify({ case_id: caseId, content: null }),
    })
  }

  function updateReasonCase(briefcaseId: string, reasonId: string, entryId: string, data: { content?: string }): Promise<ReasonCase> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  function removeReasonCase(briefcaseId: string, reasonId: string, entryId: string): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}`, { method: 'DELETE' })
  }

  function listReasonVersions(briefcaseId: string, reasonId: string): Promise<ContentVersion[]> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/versions`)
  }

  function listReasonCaseVersions(briefcaseId: string, reasonId: string, entryId: string): Promise<ContentVersion[]> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}/versions`)
  }

  function restoreVersion(briefcaseId: string, versionId: string): Promise<void> {
    return apiFetch(`/briefcases/${briefcaseId}/versions/${versionId}/restore`, { method: 'POST' })
  }

  function generateCaseContent(briefcaseId: string, reasonId: string, entryId: string): Promise<GenerateResponse> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/cases/${entryId}/generate`, { method: 'POST' })
  }

  function generateReasonArgument(briefcaseId: string, reasonId: string): Promise<GenerateResponse> {
    return apiFetch(`/briefcases/${briefcaseId}/reasons/${reasonId}/generate`, { method: 'POST' })
  }

  return {
    listBriefcases, getBriefcase, createBriefcase, updateBriefcase, deleteBriefcase,
    createReason, updateReason, deleteReason, reorderReasons,
    addCaseToReason, updateReasonCase, removeReasonCase,
    listReasonVersions, listReasonCaseVersions, restoreVersion,
    generateCaseContent, generateReasonArgument,
  }
}
