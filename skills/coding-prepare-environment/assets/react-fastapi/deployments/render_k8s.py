"""Render deployment manifests locally; this command never contacts a cluster."""
import argparse
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend-image", required=True)
    parser.add_argument("--web-image", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--ingress-class", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--environment", default="prod", help="Manifest environment (default: prod)")
    args = parser.parse_args()
    for field in ("namespace", "release", "ingress_class", "environment"):
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?", getattr(args, field)):
            parser.error(f"invalid {field}; use a short lowercase DNS label")
    if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", args.domain):
        parser.error("domain must be a hostname")
    for value in (args.backend_image, args.web_image):
        if value.endswith(":latest") or not (":" in value.rsplit("/", 1)[-1] or "@sha256:" in value):
            parser.error("images must have an explicit release tag or digest (not latest)")
    replacements = dict(zip(
        ["APP_BACKEND_IMAGE", "APP_WEB_IMAGE", "APP_DOMAIN", "APP_RELEASE", "APP_INGRESS_CLASS"],
        [args.backend_image, args.web_image, args.domain, args.release, args.ingress_class],
    ))

    def render(value):
        if isinstance(value, dict):
            return {key: render(item) for key, item in value.items()}
        if isinstance(value, list):
            return [render(item) for item in value]
        if isinstance(value, str):
            for key, replacement in replacements.items():
                value = value.replace(key, replacement)
        return value

    source = Path(__file__).resolve().parent / args.environment / "k8s"
    paths = sorted(source.glob("*.json"))
    if not paths:
        parser.error(f"no Kubernetes manifests found in {source}")
    args.output.mkdir(parents=True, exist_ok=False)
    for path in paths:
        manifest = render(json.loads(path.read_text()))
        manifest["metadata"]["namespace"] = args.namespace
        (args.output / path.name).write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Rendered to {args.output}; review before applying to an explicitly selected cluster.")


if __name__ == "__main__":
    main()
