#!/usr/bin/env python3
"""Validate the TOS 7 Docker application package before release."""
import argparse
import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = [
    "zh-cn", "zh-hk", "en-us", "fr-fr", "de-de", "it-it", "es-es",
    "hu-hu", "ja-jp", "ko-kr", "pl-pl", "ru-ru", "tr-tr", "pt-pt",
]
PACKAGE_FILES = {"config.ini", "milovault.lang", "milovault.svg", "docker-compose.yml"}
ERRORS = []


def fail(message):
    ERRORS.append(message)


def read_text(name):
    path = ROOT / name
    if not path.is_file():
        fail("missing file: %s" % name)
        return ""
    data = path.read_bytes()
    if data.startswith(b"\xef\xbb\xbf"):
        fail("%s: UTF-8 BOM is not allowed" % name)
    if b"\r\n" in data:
        fail("%s: CRLF line endings are not allowed" % name)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        fail("%s: not valid UTF-8" % name)
        return ""


def check_config():
    text = read_text("config.ini")
    if not text:
        return
    try:
        cfg = json.loads(text)
    except json.JSONDecodeError as exc:
        fail("config.ini: invalid JSON: %s" % exc)
        return
    required = [
        "id", "icon", "publisher", "path", "exec", "open_path", "help",
        "version", "low_version", "category", "depend", "platform",
        "application_type", "compose_project", "user",
    ]
    for key in required:
        if key not in cfg:
            fail("config.ini: missing required field %s" % key)
    if cfg.get("id") != "milovault":
        fail("config.ini: id must be milovault")
    if cfg.get("application_type") != "docker":
        fail("config.ini: application_type must be docker")
    if cfg.get("platform") != "x86_64":
        fail("config.ini: platform must be x86_64")
    if cfg.get("open_path") is not True:
        fail("config.ini: open_path must be true")
    if "type" in cfg:
        fail("config.ini: type and open_path are mutually exclusive")
    if not re.fullmatch(r"https://\$\{ip\}:18443", str(cfg.get("path", ""))):
        fail("config.ini: path must be https://${ip}:18443")
    if "DockerEngine" not in cfg.get("depend", []):
        fail("config.ini: depend must include DockerEngine")
    if cfg.get("compose_project") != cfg.get("id"):
        fail("config.ini: compose_project must equal id")
    user = str(cfg.get("user", ""))
    if user in ("0", "0:0", "root", "root:root"):
        fail("config.ini: user must be non-root")
    expected_icon = "/images/icons/%s.svg" % cfg.get("id")
    if cfg.get("icon") != expected_icon:
        fail("config.ini: icon must be %s" % expected_icon)
    version_file = ROOT / "VERSION"
    if version_file.is_file():
        expected_version = version_file.read_text(encoding="utf-8").strip()
        if str(cfg.get("version")) != expected_version:
            fail("config.ini: version must match VERSION (%s)" % expected_version)


def check_lang():
    text = read_text("milovault.lang")
    if not text:
        return
    sections = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"\[([a-z]{2}-[a-z]{2})\]", line)
        if match:
            current = match.group(1)
            sections[current] = {}
            continue
        if "=" in line and current is not None:
            key, value = line.split("=", 1)
            sections[current][key.strip()] = value.strip().strip('"')
    missing = [lang for lang in LANGS if lang not in sections]
    if missing:
        fail("milovault.lang: missing sections: %s" % ", ".join(missing))
    for lang in LANGS:
        section = sections.get(lang, {})
        for key in ("name", "auth", "descript", "release_note", "important"):
            if not section.get(key):
                fail("milovault.lang: %s.%s is empty" % (lang, key))


def check_svg():
    text = read_text("milovault.svg")
    if not text:
        return
    if "<svg" not in text or "viewBox=" not in text:
        fail("milovault.svg: must be an SVG with a viewBox")
    if re.search(r"<script|onload\s*=|onerror\s*=|href\s*=\s*[\"']https?:", text, re.I):
        fail("milovault.svg: scripts or external references are not allowed")
    size = (ROOT / "milovault.svg").stat().st_size
    if size > 50 * 1024:
        fail("milovault.svg: must be <= 50 KB (got %d bytes)" % size)


def check_compose():
    text = read_text("docker-compose.yml")
    if not text:
        return
    required = [
        "image: vaultwarden/server:1.37.5",
        "container_name: milovault",
        "restart: unless-stopped",
        'user: "10001:10001"',
        "18443:8443",
        "healthcheck:",
        "x-app-meta:",
        "port: 18443",
        "protocol: https",
        "./data:/data",
    ]
    for needle in required:
        if needle not in text:
            fail("docker-compose.yml: missing %r" % needle)
    if ":latest" in text:
        fail("docker-compose.yml: :latest tag is not allowed")
    if re.search(r"privileged\s*:\s*true", text):
        fail("docker-compose.yml: privileged mode is not allowed")
    if re.search(r"network_mode\s*:\s*host", text):
        fail("docker-compose.yml: host network mode is not allowed")


def check_package(path):
    try:
        with tarfile.open(path, "r:gz") as archive:
            names = archive.getnames()
            if set(names) != PACKAGE_FILES or len(names) != len(PACKAGE_FILES):
                fail("%s: archive must contain exactly %s" % (path, sorted(PACKAGE_FILES)))
                return
            for name in names:
                member = archive.extractfile(name)
                if member is None:
                    fail("%s: %s is not a regular file" % (path, name))
                    continue
                data = member.read()
                if b"\r\n" in data:
                    fail("%s: %s contains CRLF" % (path, name))
                source = ROOT / name
                if source.is_file() and source.read_bytes() != data:
                    fail("%s: %s differs from the source file" % (path, name))
    except (OSError, tarfile.TarError) as exc:
        fail("%s: cannot read archive: %s" % (path, exc))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", help="also validate a built .tar.gz")
    args = parser.parse_args()

    check_config()
    check_lang()
    check_svg()
    check_compose()
    if args.package:
        check_package(Path(args.package))

    if ERRORS:
        print("VALIDATION FAILED")
        for error in ERRORS:
            print(" - %s" % error)
        return 1
    print("VALIDATION OK")
    if args.package:
        print("PACKAGE OK: %s" % args.package)
    return 0


if __name__ == "__main__":
    sys.exit(main())
