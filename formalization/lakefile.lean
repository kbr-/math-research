import Lake
open Lake DSL

package math_research where
  version := v!"0.1.0"

require mathlib from git "https://github.com/leanprover-community/mathlib4.git" @
  "67248ba34806c60bf24b5e99f0f09946ffc465c9"

@[default_target] lean_lib claims where
  globs := #[.submodules `claims]

@[default_target] lean_lib «third-party-claims» where
  globs := #[.submodules `«third-party-claims»]
