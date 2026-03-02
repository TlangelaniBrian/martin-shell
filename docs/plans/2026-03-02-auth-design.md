# Auth Design — 2026-03-02

## Scope
Email/password authentication with role support across the martin backend and martin-shell.

## Backend changes (`~/Projects/martin/backend`)

### User model — add role
```python
class UserRole(str, enum.Enum):
    member = "member"
    admin  = "admin"

class User(SQLAlchemyBaseUserTableUUID, Base):
    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(UserRole), default=UserRole.member, nullable=False
    )
```

### Schemas
```python
class UserRead(schemas.BaseUser[uuid.UUID]):
    role: UserRole

class UserCreate(schemas.BaseUserCreate):
    role: UserRole = UserRole.member
```

### Migration
New Alembic migration: adds `role VARCHAR(6) NOT NULL DEFAULT 'member'`.

## `@martin/common` changes

Add `UserRole` type and `role` field to `User` interface in `auth-store.ts`:
```ts
export type UserRole = 'member' | 'admin'

export interface User {
  id: string
  email: string
  is_verified: boolean
  role: UserRole
}
```

## Shell app changes (`apps/shell`)

### `src/auth/useAuth.ts` — composable
- `bootstrap()` — GET /users/me → setUser or clearUser
- `signIn(email, password)` — POST /auth/login (form-encoded) → setUser, redirect /
- `signUp(email, password)` — POST /auth/register (JSON) → return { requiresVerification: true }
- `signOut()` — POST /auth/logout → clearUser, redirect /sign-in

### `src/App.vue`
- Call `bootstrap()` on mount
- While `authStore.loading === true`, render full-screen spinner
- Listen for `session:expired` → clearUser + router.push('/sign-in')

### `src/router.ts` — navigation guard
- Protected routes: `/search`, `/workspace/*`
- Public routes: `/sign-in`, `/sign-up`
- Guard: if no user and protected → /sign-in; if user and public → /

### `src/auth/SignInPage.vue`
- Card with email + password inputs + submit button
- Uses @martin/components (Card, Input, Button)
- Inline error display

### `src/auth/SignUpPage.vue`
- Card with email + password inputs + submit button
- Post-submit: shows "check your email" confirmation state
- Uses @martin/components

## API endpoints (fastapi-users standard)
- `POST /auth/login` — form-encoded `username` + `password`, sets httponly cookies, returns UserRead
- `POST /auth/register` — JSON `{email, password}`, triggers verification email, returns UserRead
- `POST /auth/logout` — clears cookies, revokes refresh token
- `POST /auth/refresh` — rotates tokens via refresh cookie
- `GET /users/me` — returns current user from access cookie
