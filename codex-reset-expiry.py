import os
import json
import base64
import requests
import argparse
from pathlib import Path

def decode_jwt_payload(token):
    """Parse the Payload of the JWT."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        
        payload_b64 = parts[1]
        # Add padding for Base64 URL decoding
        padding = '=' * (4 - len(payload_b64) % 4)
        payload_b64 += padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes)
    except Exception as e:
        print(f"❌ JWT parsing failed: {e}")
        return None

def extract_account_id_from_payload(payload):
    """Search for a key containing 'account_id' in the 'https://api.openai.com/auth' dict."""
    if not isinstance(payload, dict):
        return None

    auth_info = payload.get("https://api.openai.com/auth")
    
    if isinstance(auth_info, dict):
        for k, v in auth_info.items():
            # Match if key contains 'account_id' (case-insensitive)
            if "account_id" in str(k).lower():
                return v
                
    return None

def main():
    # 1. Configure CLI arguments
    parser = argparse.ArgumentParser(description="Codex Rate Limit & Reset Credits Checker")
    parser.add_argument("--dir", type=str, default=str(Path.home() / ".codex"), 
                        help="Directory containing the auth file (default: ~/.codex)")
    parser.add_argument("--file", type=str, default="auth.json", 
                        help="Name of the auth file (default: auth.json)")
    parser.add_argument("--proxy", type=str, default=None, 
                        help="Proxy URL (e.g., http://127.0.0.1:7890 or socks5h://127.0.0.1:1080)")
    args = parser.parse_args()

    auth_path = Path(args.dir) / args.file
    
    if not auth_path.exists():
        print(f"❌ Auth file not found: {auth_path}")
        return

    with open(auth_path, "r", encoding="utf-8") as f:
        try:
            raw_data = json.load(f)
            # Prioritize fetching auth data from the "tokens" key
            auth_data = raw_data.get("tokens")
            if not auth_data:
                # Fallback: search at root level if "tokens" is missing
                auth_data = raw_data
        except json.JSONDecodeError:
            print(f"❌ JSON decode failed. Ensure {auth_path} is valid.")
            return

    # Handle varying key names across Codex versions
    access_token = auth_data.get("accessToken") or auth_data.get("access_token")
    account_id = (
        auth_data.get("accountId") or 
        auth_data.get("account_id") or 
        (auth_data.get("user", {}) or {}).get("id")
    )

    if not access_token or not account_id:
        print("❌ access_token or account_id not found in auth file.")
        print(f"Available keys: {list(auth_data.keys())}")
        return

    print(f"✅ Successfully read auth file: {auth_path}")
    print(f"   Local Account ID: {account_id}")

    # 2. Parse JWT and verify account_id
    print("\n--- Parsing JWT Payload ---")
    payload = decode_jwt_payload(access_token)
    if payload:        
        # Extract account_id from the specific dict
        jwt_account_id = extract_account_id_from_payload(payload)
        
        if jwt_account_id:
            if str(jwt_account_id) == str(account_id):
                print(f"\n✅ Match: Local account_id matches JWT ({jwt_account_id})")
            else:
                print(f"\n⚠️ Mismatch: Local ({account_id}) vs JWT ({jwt_account_id})")
        else:
            print("\n⚠️ 'account_id' not found in JWT 'https://api.openai.com/auth'.")

    # 3. Request Rate Limit API
    print("\n--- Requesting Rate Limit API ---")
    url = "https://chatgpt.com/backend-api/wham/rate-limit-reset-credits"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "ChatGPT-Account-Id": str(account_id),
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    # Handle proxy
    proxies = None
    if args.proxy:
        proxies = {
            "http": args.proxy,
            "https": args.proxy
        }
        print(f"🌐 Using proxy: {args.proxy}")

    try:
        # Increase timeout for proxy latency
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15,verify=False)
        response.raise_for_status()
        
        print("✅ Request successful. Response:")
        print(json.dumps(response.json(), indent=4, ensure_ascii=False))
        
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP Error: {http_err}")
        print(f"Response body: {response.text}")
    except requests.exceptions.ProxyError as proxy_err:
        print(f"❌ Proxy Error: {proxy_err}")
    except Exception as err:
        print(f"❌ Request Exception: {err}")

if __name__ == "__main__":
    main()