"""Recheck the frozen art bundle without rebuilding or replacing accepted art.

This verifies disk bytes, archive bytes and the committed LFS pointers. It binds
existing playback evidence to the actual cels; it does not claim a new playback
review, independent scope audit or Unity test.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
ACTORS = {
    "hero_daotong", "hero_lingyi", "hero_leixiu",
    "orig_mob01", "orig_mob02", "orig_mob03", "orig_mob04",
    "orig_mob05", "orig_mob06", "orig_boss_minor", "orig_boss01",
}


def read(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8-sig"))


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    errors = []
    manifest = read("records/complete-art-manifest.json")
    core = read("records/final-resource-manifest.json")
    package = read("records/complete-delivery-package.json")
    walks = read("records/walk-exports.json")
    reviews = {a["actor"]: a for a in read("records/walk-playback-review.json")["actors"]}
    fonts = read("records/font-sources.json")["fontFiles"]

    def expect(condition, message):
        if not condition:
            errors.append(message)

    rows = manifest["assets"] + manifest["screens"]
    expect(len(manifest["assets"]) == 242, "Expected 242 final PNGs")
    expect(len(manifest["screens"]) == 131, "Expected 131 frozen UI designs")
    expect(len({a["id"] for a in manifest["assets"]}) == 242, "Duplicate asset ids")
    expect(len({a["file"] for a in rows}) == 373, "Duplicate final image paths")
    binary_specs = {"full-game-art-v1/" + a["file"]: a["sha256"] for a in rows}
    for row in rows + core["nativeSources"]:
        path = ROOT / row["file"]
        if not path.is_file():
            errors.append("Missing image: " + row["file"])
            continue
        expect(sha(path) == row["sha256"], "Image hash: " + row["file"])
        with Image.open(path) as im:
            im.load()
            if row.get("size"):
                expect(list(im.size) == row["size"], "Image dimensions: " + row["file"])
            if row.get("mode"):
                expect(im.mode == row["mode"], "Image mode: " + row["file"])
            if row.get("alphaRange") is not None:
                expect("A" in im.getbands(), "Missing alpha: " + row["file"])
                if "A" in im.getbands():
                    expect(list(im.getchannel("A").getextrema()) == row["alphaRange"],
                           "Alpha range: " + row["file"])
    for row in manifest["screens"]:
        source = Path(row["sourceFile"]).resolve()
        expect(source.is_relative_to(PROJECT), "UI source outside this project")
        if source.is_relative_to(PROJECT):
            expect(source.is_file() and sha(source) == row["sha256"],
                   "Original UI changed: " + row["file"])

    expect(len(walks["clips"]) == 11 and {c["actor"] for c in walks["clips"]} == ACTORS,
           "Required actor coverage")
    expect(manifest["clips"] == walks["clips"], "Unified animation catalog is stale")
    image_hashes = {a["file"]: a["sha256"] for a in manifest["assets"]}
    for clip in walks["clips"]:
        review = reviews.get(clip["actor"], {})
        frames = clip["frames"]
        expect(len(frames) == 4 and len({f["sha256"] for f in frames}) == 4,
               "Four distinct cels: " + clip["actor"])
        expect(review.get("accepted") is True and clip["playbackAccepted"],
               "Missing prior playback acceptance: " + clip["actor"])
        expect(review.get("frameSha256") == [f["sha256"] for f in frames]
               and review.get("durationsMs") == [f["durationMs"] for f in frames],
               "Playback evidence does not match current cels: " + clip["actor"])
        for frame in frames:
            expect(frame["durationMs"] > 0 and image_hashes.get(frame["file"]) == frame["sha256"],
                   "Unbound animation frame: " + frame["file"])
    for name, flag in [
        ("records/final-acceptance.json", "allGameArtComplete"),
        ("records/fx-playback-review.json", "passed"),
        ("records/ground-tile-review.json", "passed"),
        ("records/composite-playback-review.json", "passed"),
        ("branding-v1/records/acceptance.json", "passed"),
    ]:
        expect(read(name).get(flag) is True, "Prior acceptance missing: " + name)
    expect(len(fonts) == 2, "Expected two font families")
    for font in fonts:
        for field, digest in [("fontFile", "fontSha256"), ("licenseFile", "licenseSha256")]:
            expect(sha(ROOT / font[field]) == font[digest], "Font or license: " + font[field])
        binary_specs["full-game-art-v1/" + font["fontFile"]] = font["fontSha256"]

    archive_path = ROOT / package["file"]
    expect(archive_path.stat().st_size == package["bytes"], "Archive size")
    expect(sha(archive_path) == package["sha256"], "Archive SHA-256")
    checksum_text = archive_path.with_suffix(".zip.sha256").read_text(encoding="utf-8").split()[0]
    expect(checksum_text == package["sha256"], "Archive checksum sidecar")
    with zipfile.ZipFile(archive_path) as archive:
        entries = {"yifu_zhen_wanyao_art/" + e["file"]: e for e in package["entries"]}
        expect(len(entries) == package["entryCount"] == 1045, "Archive record count")
        expect(len(archive.namelist()) == len(entries) and set(archive.namelist()) == set(entries),
               "Archive entry set")
        for name, entry in entries.items():
            # Reading through ZipFile also checks the actual entry CRC.
            data = archive.read(name)
            expect(len(data) == entry["bytes"] and hashlib.sha256(data).hexdigest() == entry["sha256"],
                   "Archive entry hash/CRC: " + entry["file"])
        for row in rows:
            entry = entries.get("yifu_zhen_wanyao_art/" + row["file"], {})
            expect(entry.get("sha256") == row["sha256"], "Final image absent from archive: " + row["file"])
    binary_specs["full-game-art-v1/" + package["file"]] = package["sha256"]

    # Read committed blobs directly; do not invoke the LFS clean/smudge filter.
    paths = list(binary_specs)
    raw = subprocess.check_output(
        ["git", "cat-file", "--batch"], cwd=PROJECT,
        input="".join("HEAD:" + p + "\n" for p in paths).encode("utf-8"))
    offset = 0
    for path in paths:
        end = raw.index(b"\n", offset)
        header = raw[offset:end].split()
        if len(header) != 3 or header[1] != b"blob":
            errors.append("Not committed: " + path)
            offset = end + 1
            continue
        size = int(header[2])
        blob = raw[end + 1:end + 1 + size]
        offset = end + 1 + size + 1
        expect(blob.startswith(b"version https://git-lfs.github.com/spec/v1\n")
               and ("oid sha256:" + binary_specs[path] + "\n").encode() in blob,
               "Committed LFS pointer does not match real bytes: " + path)

    report = {
        "verifiedAtUtc": datetime.now(timezone.utc).isoformat(),
        "gameName": manifest["gameName"],
        "scope": manifest["scope"],
        "referenceCommit": manifest["referenceCommit"],
        "passed": not errors,
        "errors": errors,
        "runtimePngCount": len(manifest["assets"]),
        "uiDesignCount": len(manifest["screens"]),
        "all131OriginalUIHashesMatch": not any("Original UI" in e for e in errors),
        "actorCount": len(walks["clips"]),
        "walkFrameCount": sum(len(c["frames"]) for c in walks["clips"]),
        "existingPlaybackEvidenceMatchesCurrentFrames": not any("cels" in e or "playback" in e for e in errors),
        "fontFamilyCount": len(fonts),
        "archiveEntryCount": len(entries),
        "archiveSha256": package["sha256"],
        "archiveEntryHashesAndCrcChecked": True,
        "committedLfsPointersChecked": len(binary_specs),
        "verifiedAgainstLocalCommit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=PROJECT, text=True).strip(),
        "newPlaybackReviewPerformed": False,
        "unityImportVerified": False,
        "runtimePlaybackVerifiedInUnity": False,
        "limits": manifest["limits"],
        "frozenImagesOrArchivesModified": False,
    }
    (ROOT / "records/complete-art-verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
