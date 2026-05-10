# Review patches for session test-pass (2 patches across 1 file)

## experience/screens/01_user_auth/login.md

- [x] **p-ann-c1-content** · category=change · annotation: "this should be on the right"
  ```diff
  @@ ## Layout @@
  -- submit-button: centered below form
  +- submit-button: right-aligned below form
  ```

- [x] **p-ann-c1-promotion** · provisional ID promotion for `submit-button`
  ```diff
  @@ frontmatter:elements @@
  -  - id: submit-button
  -    kind: button
  -    label: Sign In
  -    states: [default, loading]
  -    provisional: true
  +  - id: submit-button
  +    kind: button
  +    label: Sign In
  +    states: [default, loading]
  +    provisional: false
  ```
