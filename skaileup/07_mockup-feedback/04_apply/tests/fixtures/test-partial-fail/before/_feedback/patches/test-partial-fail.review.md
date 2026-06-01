# Review patches for session test-partial-fail (2 patches)

## experience/screens/01_user_auth/login.md

- [x] **p-good** · category=change · annotation: "right-align the button"
  ```diff
  @@ ## Layout @@
  -- submit-button: centered below form
  +- submit-button: right-aligned below form
  ```

- [x] **p-bad** · category=change · annotation: "change something"
  ```diff
  @@ ## NONEXISTENT SECTION @@
  -- some line
  +- replacement
  ```
