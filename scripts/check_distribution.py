"""Check tracked files and built archives for recordings and personal scores."""

from pathlib import Path
import subprocess
import sys
import tarfile
import zipfile


AUDIO_TYPES = {".wav", ".wave", ".flac", ".aiff", ".aif", ".aifc", ".mp3", ".m4a",
               ".aac", ".ogg", ".opus", ".pcm", ".sf2", ".sf3", ".mid", ".midi"}


def check(name, stream):
    path = Path(name)
    head = stream.read(12)
    audio = (head.startswith((b"fLaC", b"OggS", b"MThd", b"ID3"))
             or (head[:4] in (b"RIFF", b"RF64", b"FORM") and head[8:12] in (b"WAVE", b"AIFF", b"AIFC")))
    if audio or path.suffix.lower() in AUDIO_TYPES or name.lower().endswith(".score.json"):
        raise ValueError(f"Personal score or audio in distribution: {name}")


def main():
    root = Path(__file__).resolve().parents[1]
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    for name in filter(None, tracked):
        with (root / name).open("rb") as source:
            check(name, source)
    dist = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "dist"
    for pattern in ("*.whl", "*.tar.gz", "*-portable-*.zip", "*-antigravity-*.zip"):
        archives = sorted(dist.glob(pattern))
        if not archives:
            raise ValueError(f"Missing release archive: {pattern}")
        for path in archives:
            if path.name.endswith(".tar.gz"):
                with tarfile.open(path) as archive:
                    for member in archive:
                        if member.isfile():
                            with archive.extractfile(member) as source:
                                check(member.name, source)
            else:
                with zipfile.ZipFile(path) as archive:
                    for entry in archive.infolist():
                        if not entry.is_dir():
                            with archive.open(entry) as source:
                                check(entry.filename, source)
            print(f"Verified {path.name}")


if __name__ == "__main__":
    main()
