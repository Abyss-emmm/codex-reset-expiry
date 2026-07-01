# codex-reset-expiry

A lightweight Python CLI that reads your local Codex CLI `auth.json`, validates the
account id embedded in the JWT, and queries the ChatGPT backend endpoint
`wham/rate-limit-reset-credits` to inspect your current rate-limit and reset-credits
state.

> Intended for personal diagnostics. This is not an official OpenAI / Codex tool, and
> it does not wrap, persist, or proxy any credentials.

## Features

- **Zero configuration** — reuses `~/.codex/auth.json` directly, no token copy-paste.
- **Multi-version compatible** — handles both the modern `tokens`-wrapped layout and
  the legacy flat layout (plus a `user.id` fallback for account id).
- **JWT self-check** — parses the `access_token` payload, extracts the account id from
  `https://api.openai.com/auth`, and verifies it matches the locally stored one
  before issuing any API call.
- **Proxy friendly** — HTTP and SOCKS proxies can be passed through a single flag.
- **No side effects** — read-only script. Writes nothing to disk, stores no credentials.

## Requirements

- Python ≥ 3.7
- One third-party dependency: [`requests`](https://requests.readthedocs.io/)

## Installation

```bash
git clone https://github.com/Abyss/codex-reset-expiry.git
cd codex-reset-expiry
pip install requests
```

If you prefer not to clone, just download `codex-reset-expiry.py` and make sure
`requests` is available in your interpreter.

## Usage

### Simplest invocation

```bash
python codex-reset-expiry.py
```

Reads `~/.codex/auth.json` and prints the JWT payload plus the API response.

### Custom auth file location

```bash
python codex-reset-expiry.py --dir /path/to/codex --file auth.json
```

### Through a proxy

```bash
# HTTP/HTTPS proxy
python codex-reset-expiry.py --proxy http://127.0.0.1:7890
```

### CLI flags

| Flag       | Description                                            | Default        |
| ---------- | ------------------------------------------------------ | -------------- |
| `--dir`    | Directory containing the auth file                    | `~/.codex`     |
| `--file`   | Auth file name                                         | `auth.json`    |
| `--proxy`  | Proxy URL (HTTP / HTTPS / SOCKS5 / SOCKS5h)            | _none_         |



## License

Apache License 2.0 — see [LICENSE](./LICENSE).