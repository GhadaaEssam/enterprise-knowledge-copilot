# Source: https://engineering.hmn.md/standards/backend/error-logging/

# Error Logging

With `error_log()` often being used for quick debug output, many code quality tools now flag these calls as forgotten debug statements. This is because `error_log()` is typically used by developers to dump state information directly to the log file, bypassing PHP’s error handling system.

A better alternative in many cases is the more versatile `trigger_error()` function. Unlike `error_log()`, it integrates with PHP’s standard error handling, respects `error_reporting` and `display_errors`, and is caught by any registered `set_error_handler`. It also supports different error levels, such as `E_USER_NOTICE`, `E_USER_WARNING`, `E_USER_ERROR`, and `E_USER_DEPRECATED`, making it far more expressive than just logging a string.

Additionally, you might come across error messages wrapped in WordPress translation functions. This makes it harder to identify and resolve issues, since bug reports may contain translated messages we can’t directly match in the codebase.

End users should not see raw error messages anyway—developers should log or raise errors in a consistent, developer-focused way, and then provide a separate, user-friendly message when needed.

---

### Summary: `trigger_error()` vs `error_log()` [#](#summary-trigger_error-vs-error_log)

| Feature | `trigger_error()` | `error_log()` |
| --- | --- | --- |
| Purpose | Generate PHP user-level errors | Send message to configured log |
| Mechanism | Uses PHP’s error handling system | Direct log write, bypassing error handling |
| Respects `error_reporting` | Yes | No |
| Respects `display_errors` | Yes | No |
| Caught by `set_error_handler` | Yes | No |
| Error Levels | `E_USER_NOTICE`, `E_USER_WARNING`, `E_USER_ERROR`, `E_USER_DEPRECATED` | None (plain string) |
| Halts Script? | Yes, if `E_USER_ERROR` | No |
| Primary Use | Signaling code usage errors, warnings, deprecations, fatal issues | General logging, debugging, tracing |

**Guidance**:

* Use `trigger_error()` when you want to raise an issue that behaves like a standard PHP error.
* Use `error_log()` only when you need to record diagnostic information directly to the log file, without affecting PHP’s error handling flow.

Accessed Mon, 22 Sep 2025 13:58:13 +0000 from `https://engineering.hmn.md/standards/backend/error-logging/`

[Made by Humans](https://hmn.md)