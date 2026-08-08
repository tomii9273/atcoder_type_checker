import os
import shutil
import ssl
import tempfile
import time
from collections.abc import Callable, Iterable
from http.cookiejar import Cookie, CookieJar
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

try:
    import browser_cookie3  # type: ignore[import]
except ImportError:  # pragma: no cover - 本番環境ではブラウザ Cookie を使わない
    browser_cookie3 = None


ATCODER_COOKIE_DOMAIN = "atcoder.jp"
DEFAULT_COOKIE_BROWSERS = "firefox,chrome,edge"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0"

BrowserCookieLoader = Callable[..., CookieJar]


class AtCoderSessionError(Exception):
    """AtCoder のブラウザセッションを利用できない場合の例外。"""


class WindowsSystemCertificateAdapter(HTTPAdapter):
    """Windows の証明書ストアを使って HTTPS を検証するアダプター。"""

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["ssl_context"] = ssl.create_default_context()
        super().init_poolmanager(
            connections,
            maxsize,
            block=block,
            **pool_kwargs,
        )

    def cert_verify(self, conn, url, verify, cert) -> None:
        if not url.lower().startswith("https") or not verify:
            super().cert_verify(conn, url, verify=verify, cert=cert)
            return

        conn.cert_reqs = "CERT_REQUIRED"
        if cert:
            raise ValueError("クライアント証明書には対応していません。")


def get_atcoder_cookie_browsers() -> tuple[str, ...]:
    """Cookie 読み込み対象ブラウザを優先順に返す。"""
    browser_names = tuple(
        browser_name.strip().lower()
        for browser_name in os.environ.get("ATCODER_COOKIE_BROWSER", DEFAULT_COOKIE_BROWSERS).split(",")
        if browser_name.strip() != ""
    )
    if len(browser_names) == 0:
        return ("firefox",)
    return browser_names


def get_browser_cookie_config(
    browser_name: str,
) -> tuple[Path | None, BrowserCookieLoader]:
    """ブラウザの Cookie DB ルートと読み込み関数を返す。"""
    if browser_cookie3 is None:
        raise AtCoderSessionError("browser-cookie3 が見つかりません。requirements_dev.txt の依存関係をインストールしてください。")

    local_app_data = Path(
        os.environ.get(
            "LOCALAPPDATA",
            Path.home() / "AppData" / "Local",
        )
    )
    browser_configs: dict[str, tuple[Path | None, BrowserCookieLoader]] = {
        "chrome": (
            local_app_data / "Google" / "Chrome" / "User Data",
            browser_cookie3.chrome,
        ),
        "edge": (
            local_app_data / "Microsoft" / "Edge" / "User Data",
            browser_cookie3.edge,
        ),
        "firefox": (None, browser_cookie3.firefox),
    }

    if browser_name not in browser_configs:
        raise AtCoderSessionError(f"未対応のブラウザです: {browser_name}")

    return browser_configs[browser_name]


def copy_browser_cookie_file(browser_name: str, cookie_file: Path) -> Path:
    """ロック回避のため Chromium 系の Cookie DB を一時ファイルへコピーする。"""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        shutil.copy2(cookie_file, temp_path)
    except OSError as e:
        temp_path.unlink(missing_ok=True)
        raise AtCoderSessionError(f"{browser_name} の Cookie DB を読めませんでした。" f"{browser_name} を閉じてから再実行してください。") from e

    return temp_path


def is_atcoder_cookie(cookie: Cookie) -> bool:
    """AtCoder 自身またはそのサブドメインの Cookie かを返す。"""
    cookie_domain = cookie.domain.lstrip(".").lower()
    return cookie_domain == ATCODER_COOKIE_DOMAIN or cookie_domain.endswith(f".{ATCODER_COOKIE_DOMAIN}")


def filter_atcoder_cookies(
    cookie_jar: Iterable[Cookie],
) -> requests.cookies.RequestsCookieJar:
    """AtCoder 用の Cookie だけを抽出する。"""
    filtered_cookies = requests.cookies.RequestsCookieJar()
    for cookie in cookie_jar:
        if is_atcoder_cookie(cookie):
            filtered_cookies.set_cookie(cookie)
    return filtered_cookies


def validate_loaded_cookies(
    browser_name: str,
    cookie_jar: CookieJar,
) -> requests.cookies.RequestsCookieJar:
    """読み込んだ Cookie に AtCoder のセッション情報があるかを確認する。"""
    filtered_cookies = filter_atcoder_cookies(cookie_jar)
    if len(filtered_cookies) == 0:
        raise AtCoderSessionError(
            f"{browser_name} に AtCoder の Cookie が見つかりませんでした。" "ブラウザで AtCoder にログインしてから再実行してください。"
        )
    return filtered_cookies


def load_atcoder_cookies_from_browser(
    browser_name: str,
) -> requests.cookies.RequestsCookieJar:
    """指定ブラウザの通常プロファイルから AtCoder の Cookie を読む。"""
    browser_root, loader = get_browser_cookie_config(browser_name)

    if browser_name == "firefox":
        try:
            all_cookies = loader()
        except Exception as e:
            raise AtCoderSessionError(f"{browser_name} の Cookie を読めませんでした: {e}") from e
        return validate_loaded_cookies(browser_name, all_cookies)

    if browser_root is None:
        raise AtCoderSessionError(f"Cookie DB の場所を特定できません: {browser_name}")

    profile_name = os.environ.get("ATCODER_COOKIE_PROFILE", "Default")
    cookie_file = browser_root / profile_name / "Network" / "Cookies"
    key_file = browser_root / "Local State"
    if not cookie_file.exists():
        raise AtCoderSessionError(f"{browser_name} の Cookie DB が見つかりませんでした: {cookie_file}")
    if not key_file.exists():
        raise AtCoderSessionError(f"{browser_name} の Local State が見つかりませんでした: {key_file}")

    temp_cookie_file = copy_browser_cookie_file(browser_name, cookie_file)
    try:
        try:
            all_cookies = loader(
                cookie_file=str(temp_cookie_file),
                key_file=str(key_file),
            )
        except Exception as e:
            raise AtCoderSessionError(
                f"{browser_name} の Cookie 復号に失敗しました。" "Firefox を使うか、対象ブラウザを閉じてから再実行してください。"
            ) from e
    finally:
        temp_cookie_file.unlink(missing_ok=True)

    return validate_loaded_cookies(browser_name, all_cookies)


def load_atcoder_cookies() -> requests.cookies.RequestsCookieJar:
    """設定されたブラウザから AtCoder の Cookie を優先順に読み込む。"""
    errors = []
    for browser_name in get_atcoder_cookie_browsers():
        try:
            return load_atcoder_cookies_from_browser(browser_name)
        except AtCoderSessionError as e:
            errors.append(f"{browser_name}: {e}")

    raise AtCoderSessionError("AtCoder のログイン済み Cookie を取得できませんでした。\n" + "\n".join(errors))


class AtCoderClient:
    """通常ブラウザの Cookie を利用できる AtCoder 取得クライアント。"""

    def __init__(self, use_browser_cookie: bool = False, sleep_sec: float = 1.0):
        self.sleep_sec = sleep_sec
        self.session = requests.Session()
        if os.name == "nt":
            self.session.mount("https://", WindowsSystemCertificateAdapter())
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})
        if use_browser_cookie:
            self.session.cookies.update(load_atcoder_cookies())

    def __enter__(self) -> "AtCoderClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def get_response(self, url: str, require_login: bool = False) -> requests.Response:
        """レスポンスを取得し、HTTP エラーとログイン切れを検出する。"""
        response = self.session.get(url, timeout=60)
        time.sleep(self.sleep_sec)
        response.raise_for_status()

        if require_login and response.url.startswith("https://atcoder.jp/login"):
            raise AtCoderSessionError("AtCoder のログイン済みセッションを利用できませんでした。" "ブラウザで AtCoder にログインしてから再実行してください。")

        return response

    def validate_login(self) -> None:
        """AtCoder のアカウント設定ページを使ってログイン状態を確認する。"""
        self.get_response("https://atcoder.jp/settings", require_login=True)

    def get_bs(self, url: str, require_login: bool = False) -> BeautifulSoup:
        """HTML を BeautifulSoup で返す。"""
        response = self.get_response(url, require_login=require_login)
        return BeautifulSoup(response.text, "html.parser")

    def get_json(self, url: str, require_login: bool = False) -> Any:
        """JSON を読み込んで返す。"""
        response = self.get_response(url, require_login=require_login)
        try:
            return response.json()
        except ValueError as e:
            raise AtCoderSessionError("AtCoder の JSON 取得に失敗しました。ブラウザのログイン状態を確認してください。") from e

    def close(self) -> None:
        self.session.close()
