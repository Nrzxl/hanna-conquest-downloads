#!/usr/bin/env python3
"""Promote ONLY a verified original-signed HANNA Android release to update.json.

Called by the reusable workflow after the source workflow's signed-validation
job passes. Fail closed on bad signatures, missing tests, nonmonotonic version
codes, stale manifest or mismatched SHA-256. Requires gh/curl/Android SDK.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

REPO = "Nrzxl/hanna-conquest-downloads"
PACKAGE = "com.example.hanna_conquest_app"
RELEASE_TAG_PATTERN = re.compile(r"v(\d+\.\d+\.\d+)-b(\d+)-preview")
CERT_PATTERN = re.compile(
    r"(?:Signer #1|V[123] Signer): certificate SHA-256 digest:\s*([a-fA-F0-9]{64})"
)
PACKAGE_PATTERN = re.compile(
    r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", re.M
)


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def gh(path):
    return json.loads(run("gh", "api", path))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def android_tool(tool):
    files = list((Path(os.environ["ANDROID_HOME"]) / "build-tools").glob("*/" + tool))
    if not files:
        raise ValueError("Android SDK build tool missing: " + tool)
    files.sort(key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.parent.name)))
    return str(files[-1])


def download(url, path):
    prefix = "https://github.com/" + REPO + "/releases/download/"
    if not url.startswith(prefix):
        raise ValueError("Release download outside official HANNA repository")
    subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error",
         "--retry", "2", "--max-time", "210", "--output", str(path), url],
        check=True,
    )
    if path.stat().st_size < 10000000:
        raise ValueError("Truncated release APK")


def main():
    tag = os.environ["HANNA_RELEASE_TAG"]
    source_run = os.environ["HANNA_SOURCE_RUN_ID"]
    notes = os.environ["HANNA_RELEASE_NOTES"].strip()
    found = RELEASE_TAG_PATTERN.fullmatch(tag)
    if not found or not source_run.isdecimal() or not (0 < len(notes) <= 650):
        raise ValueError("Invalid release tag, verified CI ID or notes")
    version, build = found.group(1), int(found.group(2))
    release = gh("repos/" + REPO + "/releases/tags/" + tag)
    if release.get("draft") or release.get("tag_name") != tag:
        raise ValueError("Release not published")
    name = "HANNA-conquest-" + version + "-ORIGINAL-HOMOLOGACAO.apk"
    assets = {a["name"]: a for a in release.get("assets", [])}
    apk, sha_sidecar = assets.get(name), assets.get(name + ".sha256")
    if apk is None or sha_sidecar is None or apk.get("size", 0) < 10000000:
        raise ValueError("Verified APK and SHA sidecar required")
    url = ("https://github.com/" + REPO + "/releases/download/" +
           tag + "/" + name)
    if apk["browser_download_url"] != url or \
            sha_sidecar["browser_download_url"] != url + ".sha256":
        raise ValueError("Unexpected official release asset path")
    apk_sha = str(apk.get("digest", ""))
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", apk_sha):
        raise ValueError("No authoritative GitHub release SHA256")

    ci = gh("repos/" + REPO + "/actions/runs/" + source_run)
    if ci.get("repository", {}).get("full_name") != REPO or \
            ci.get("head_branch") != "main" or \
            version not in str(ci.get("name", "")):
        raise ValueError("Unrelated GitHub CI run")
    if ci.get("status") not in ("in_progress", "completed") or \
            (ci.get("status") == "completed" and ci.get("conclusion") != "success"):
        raise ValueError("Failed signed release workflow")
    jobs = gh("repos/" + REPO + "/actions/runs/" + source_run + "/jobs?per_page=100")
    signed = [j for j in jobs.get("jobs", [])
              if j.get("name") == "Build and prove in-place upgrade compatibility"
              and j.get("conclusion") == "success"]
    if len(signed) != 1:
        raise ValueError("Original signed validation job did not pass")
    steps = {s["name"] for s in signed[0].get("steps", [])
             if s.get("conclusion") == "success"}
    for gate in (
        "Resolve dependencies and analyze",
        "Run all Flutter regressions",
        "Verify both certificate and Android upgrade metadata",
        "Publish signed APK as directly downloadable Android prerelease",
    ):
        if gate not in steps:
            raise ValueError("Missing required signing gate: " + gate)
    if not any(s.startswith("Build signed in-place cumulative") for s in steps):
        raise ValueError("Original-signed APK build not verified")

    manifest_path = Path("update.json")
    old = json.loads(manifest_path.read_text(encoding="utf-8"))
    previous_build = old.get("build")
    previous_sha = old.get("sha256")
    previous_url = old.get("apk_url")
    if not isinstance(previous_build, int) or not \
            re.fullmatch(r"[a-f0-9]{64}", str(previous_sha)):
        raise ValueError("Current update.json is invalid")
    if build < previous_build:
        raise ValueError("Rollback forbidden")
    if build == previous_build:
        if (old.get("version"), previous_url, previous_sha) == (
                version, url, apk_sha[7:]):
            print("Already the official in-app version; no update necessary")
            return
        raise ValueError("Existing Android versionCode has a different APK")

    old_url_pattern = (
        r"https://github\.com/Nrzxl/hanna-conquest-downloads/releases/"
        r"download/v\d+\.\d+\.\d+-b\d+-preview/"
        r"HANNA-conquest-\d+\.\d+\.\d+-ORIGINAL-HOMOLOGACAO\.apk"
    )
    if not re.fullmatch(old_url_pattern, str(previous_url)):
        raise ValueError("Previous signed APK is not an official HANNA release")

    temp = Path(os.environ["RUNNER_TEMP"])
    before, after, sidecar = (
        temp / "hanna-previous.apk",
        temp / "hanna-new.apk",
        temp / "hanna-new.sha256",
    )
    download(previous_url, before)
    download(url, after)
    subprocess.run(
        ["curl", "--fail", "--location", "--silent", "--show-error",
         "--retry", "2", "--max-time", "90", "--output", str(sidecar),
         url + ".sha256"],
        check=True,
    )
    if digest(before) != previous_sha or digest(after) != apk_sha[7:]:
        raise ValueError("APK SHA256 differs from official manifest or GitHub")
    hashes = re.findall(r"(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])",
                        sidecar.read_text())
    if len(hashes) != 1 or hashes[0].lower() != apk_sha[7:]:
        raise ValueError("APK and SHA256 sidecar mismatch")

    signer = android_tool("apksigner")
    aapt = android_tool("aapt")
    old_sig = CERT_PATTERN.search(run(signer, "verify", "--print-certs", str(before)))
    new_sig = CERT_PATTERN.search(run(signer, "verify", "--print-certs", str(after)))
    if not old_sig or not new_sig or \
            old_sig.group(1).lower() != new_sig.group(1).lower():
        raise ValueError("Original Android signing certificate changed")
    old_package = PACKAGE_PATTERN.search(run(aapt, "dump", "badging", str(before)))
    new_package = PACKAGE_PATTERN.search(run(aapt, "dump", "badging", str(after)))
    if not old_package or not new_package:
        raise ValueError("Android manifests cannot be compared")
    if old_package.group(1) != PACKAGE or new_package.group(1) != PACKAGE or \
            int(old_package.group(2)) != previous_build or \
            int(new_package.group(2)) != build or \
            build <= previous_build or \
            not new_package.group(3).startswith(version):
        raise ValueError("Android applicationId or versionCode incompatible")

    new_manifest = {
        "version": version,
        "build": build,
        "apk_url": url,
        "sha256": apk_sha[7:],
        "notes": notes,
    }
    manifest_path.write_text(
        json.dumps(new_manifest, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"HANNA {version} build {build}: all CI and Android checks passed.")
    print("Official updater manifest ready to publish.")


if __name__ == "__main__":
    main()
