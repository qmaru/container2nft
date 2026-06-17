from pathlib import Path
from typing import cast

from container2nft.config import NatService, load_config


def convert(cfg_path: Path, out_root: Path):
    data = load_config(cfg_path)

    nft_rules: list[str] = []
    mapping: list[str] = []

    used_ips: dict[str, str] = {}
    used_ports: dict[tuple[str, int, str], str] = {}

    for project, conf in data.items():
        project_dir = out_root / project
        if not project_dir.is_dir():
            print(f"Skip {project}: {project_dir} does not exist")
            continue

        env: list[str] = []

        for service in conf["services"]:
            if not service["enabled"]:
                continue

            if service["type"] != "nat":
                continue

            svc = cast(NatService, service)

            who = f"{project}/{svc['name']}"

            if svc["ip"] in used_ips:
                raise ValueError(f"Duplicate ip: {svc['ip']} ({used_ips[svc['ip']]}, {who})")

            used_ips[svc["ip"]] = who
            mapping.append(f"{who} ({svc['ip']})")

            key = svc["name"].upper().replace("-", "_")
            env.append(f"{key}_IP={svc['ip']}")

            for port in svc["ports"]:
                host = port["host"]
                listen = port["listen"]
                target = port["target"]
                proto = port["proto"]

                k = (host, listen, proto)
                if k in used_ports:
                    raise ValueError(
                        f"Duplicate port mapping: {proto} {host}:{listen} ({used_ports[k]}, {who})"
                    )
                used_ports[k] = who

                mapping.append(f"  {proto:<3} {host}:{listen} -> {svc['ip']}:{target}")

                if host in ("0.0.0.0", "::"):
                    nft_rules.append(f"{proto} dport {listen} dnat to {svc['ip']}:{target}")
                else:
                    nft_rules.append(
                        f"ip daddr {host} {proto} dport {listen} dnat to {svc['ip']}:{target}"
                    )

            mapping.append("")

        if env:
            env.sort()
            (project_dir / ".env").write_text("\n".join(env) + "\n", encoding="utf-8")

    if nft_rules:
        nft_rules.sort()
        (out_root / "podman.nft").write_text("\n".join(nft_rules) + "\n", encoding="utf-8")

    if mapping:
        print("\n".join(mapping))

    print(f"\nGenerated {len(used_ips)} services, {len(nft_rules)} nft rules.")
