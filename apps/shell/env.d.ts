/// <reference types="@rsbuild/core/types" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly WORKSPACE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
