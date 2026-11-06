#!/usr/bin/env python3
"""
mycurl - 輕量級 HTTP 命令列工具
實作類似 curl 的核心參數與功能：
- 支援 GET, POST, PUT, DELETE, PATCH, HEAD
- 自訂 Header (-H)
- 傳送 Payload / Body (-d)
- 跟隨 3xx 重新導向 (-L)
- 輸出包含 HTTP 回應標頭 (-i)
- 詳細通訊資訊 (-v)
- 檔案儲存輸出 (-o)
- 自訂超時時間 (-m)
"""

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request


class SmartRedirectHandler(urllib.request.HTTPRedirectHandler):
    """自訂 Redirect Handler，依參數決定是否自動跟隨重新導向"""

    def __init__(self, allow_redirects=False):
        self.allow_redirects = allow_redirects

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if self.allow_redirects:
            return super().redirect_request(req, fp, code, msg, headers, newurl)
        return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="mycurl - 輕量級 curl 替代工具 (基於 Python 3 原生函式庫)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("url", help="目標網址 (例如: https://httpbin.org/get)")
    parser.add_argument(
        "-X",
        "--request",
        dest="method",
        default="GET",
        help="指定 HTTP 請求方法 (預設: GET，例如 POST, PUT, DELETE, PATCH)",
    )
    parser.add_argument(
        "-H",
        "--header",
        action="append",
        dest="headers",
        default=[],
        help='自訂請求標頭 (格式: "Key: Value"，可重複指定多次)',
    )
    parser.add_argument(
        "-d",
        "--data",
        dest="data",
        default=None,
        help="傳送的請求主體資料 (POST/PUT body)",
    )
    parser.add_argument(
        "-L",
        "--location",
        action="store_true",
        help="自動跟隨 HTTP 3xx 重新導向 (預設關閉)",
    )
    parser.add_argument(
        "-i",
        "--include",
        action="store_true",
        help="在輸出中包含 HTTP 狀態行與回應標頭",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="顯示詳細的傳輸除錯訊息 (> 請求, < 回應)",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        default=None,
        help="將回應 Body 儲存至指定的檔案路徑",
    )
    parser.add_argument(
        "-m",
        "--max-time",
        dest="timeout",
        type=float,
        default=30.0,
        help="請求超時時間 (單位: 秒，預設 30.0 秒)",
    )

    return parser.parse_args()


def normalize_url(url: str) -> str:
    """若使用者未包含通訊協議，預設加上 http://"""
    if not (url.startswith("http://") or url.startswith("https://")):
        return "http://" + url
    return url


def execute_request(args):
    url = normalize_url(args.url)
    method = args.method.upper()

    # 處理傳送資料
    data_bytes = None
    if args.data is not None:
        data_bytes = args.data.encode("utf-8")
        # 若指定了 -d 且使用者未手動指定方法，預設行為轉為 POST
        if args.method == "GET":
            method = "POST"

    # 建立 Request 物件
    req = urllib.request.Request(url, data=data_bytes, method=method)

    # 預設自訂 User-Agent，避免部分網站封鎖 Python 預設 UA
    req.add_header("User-Agent", "mycurl/1.0")

    # 解析自訂 Header
    for h in args.headers:
        if ":" in h:
            k, v = h.split(":", 1)
            req.add_header(k.strip(), v.strip())
        else:
            sys.stderr.write(f"[警告] 無效的 Header 格式: '{h}'，已跳過。\n")

    # Verbose: 顯示請求訊息
    if args.verbose:
        sys.stderr.write(f"* 連線至目標: {url} ...\n")
        sys.stderr.write(f"> {method} {req.selector} HTTP/1.1\n")
        for k, v in req.header_items():
            sys.stderr.write(f"> {k}: {v}\n")
        sys.stderr.write(">\n")

    # 建立處理器以支援 redirect 開關
    opener = urllib.request.build_opener(
        SmartRedirectHandler(allow_redirects=args.location)
    )

    # 發出連線請求
    try:
        response = opener.open(req, timeout=args.timeout)
    except urllib.error.HTTPError as e:
        # HTTP 狀態碼 >= 400 時，仍保留 response 以便印出 body
        response = e
    except urllib.error.URLError as e:
        sys.stderr.write(f"[錯誤] 連線失敗: {e.reason}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"[錯誤] 發生非預期例外: {e}\n")
        sys.exit(1)

    # 處理 Verbose 或 Include 的標頭印出
    status_code = getattr(response, "status", getattr(response, "code", 200))
    reason = getattr(response, "reason", "OK")

    if args.verbose:
        sys.stderr.write(f"< HTTP/1.1 {status_code} {reason}\n")
        for k, v in response.headers.items():
            sys.stderr.write(f"< {k}: {v}\n")
        sys.stderr.write("<\n")
    elif args.include:
        sys.stdout.write(f"HTTP/1.1 {status_code} {reason}\r\n")
        for k, v in response.headers.items():
            sys.stdout.write(f"{k}: {v}\r\n")
        sys.stdout.write("\r\n")
        sys.stdout.flush()

    # 讀取回應 Body
    body = response.read()

    # 輸出至檔案或標準輸出
    if args.output_file:
        try:
            with open(args.output_file, "wb") as f:
                f.write(body)
            if args.verbose:
                sys.stderr.write(f"* 已將回應寫入檔案: {args.output_file}\n")
        except IOError as e:
            sys.stderr.write(f"[錯誤] 無法寫入檔案 {args.output_file}: {e}\n")
            sys.exit(1)
    else:
        sys.stdout.buffer.write(body)
        sys.stdout.flush()


def main():
    args = parse_args()
    execute_request(args)


if __name__ == "__main__":
    main()