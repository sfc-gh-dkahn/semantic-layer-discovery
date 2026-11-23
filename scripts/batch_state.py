#!/usr/bin/env python3
"""Atomic, SHA-256-keyed batch manifest CLI for agentic-bi-migration."""
import argparse
import datetime
import json
import os
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 11):
    print("Python 3.11+ is required.", file=sys.stderr)
    raise SystemExit(2)

STATE_VERSION = 1
VALID_STATUSES = {
    "queued",
    "running",
    "completed",
    "partial",
    "needs_input",
    "failed",
    "skipped",
    "canceled",
}
VALID_SA_ACTIONS = {"pending", "reuse", "consolidate", "create_new"}


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write_json(path: Path, payload: dict, save_prev: bool = True) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError(f"Refusing to write through symlink: {path}")
    if save_prev and path.exists():
        prev_path = path.with_suffix(".prev.json")
        if not prev_path.is_symlink():
            prev_bytes = path.read_bytes()
            fd_prev, tmp_prev = tempfile.mkstemp(dir=path.parent, prefix=".prev-", suffix=".tmp")
            try:
                with os.fdopen(fd_prev, "wb") as f:
                    f.write(prev_bytes)
                    f.flush()
                    os.fsync(f.fileno())
                os.replace(tmp_prev, prev_path)
            except Exception:
                if os.path.exists(tmp_prev):
                    os.unlink(tmp_prev)
                raise

    encoded = (json.dumps(payload, indent=2, sort_keys=False) + "\n").encode("utf-8")
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".manifest-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(encoded)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise


def load_manifest(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("state_version") != STATE_VERSION:
        raise ValueError(f"Unsupported or invalid manifest schema in {path}")
    return data


def build_manifest_from_plan(plan: dict, existing: dict | None = None) -> dict:
    now = utc_now()
    prev_sa = {s["id"]: s for s in (existing or {}).get("subject_areas", [])}
    prev_rep_by_sha = {
        r["source_sha256"]: r
        for r in (existing or {}).get("reports", [])
        if r.get("source_sha256")
    }
    prev_rep_by_id = {r["id"]: r for r in (existing or {}).get("reports", [])}

    plan_data = plan.get("bi_data", plan)
    subject_areas = []
    for sa in plan_data.get("subject_areas", []):
        old = prev_sa.get(sa["id"])
        if old and old.get("sv_status") == "completed":
            subject_areas.append(old)
            continue
        rec = sa.get("consolidation_recommendation") or {}
        action = rec.get("action", "create_new")
        if action not in VALID_SA_ACTIONS:
            action = "create_new"
        subject_areas.append({
            "id": sa["id"],
            "name": sa["name"],
            "report_ids": sa.get("report_ids", []),
            "base_tables": sa.get("base_tables", []),
            "recommended_action": action,
            "approved_action": "pending",
            "existing_sv_fqn": rec.get("existing_sv_fqn"),
            "existing_agent_fqns": rec.get("existing_agent_fqns", []),
            "semantic_view_fqn": None,
            "agent_fqn": None,
            "sv_status": "queued",
            "verify_status": "queued",
            "verify_label": "pending",
            "agent_status": "queued",
            "retry_count": 0,
            "whats_missing": None,
            "what_i_need": None,
            "last_error": None,
            "observed_utc": now,
        })

    reports = []
    for rep in plan_data.get("reports", []):
        sha = rep.get("source_sha256", "")
        old = prev_rep_by_sha.get(sha) or prev_rep_by_id.get(rep["id"])
        if old and old.get("status") == "completed":
            reports.append(old)
            continue
        init_status = "needs_input" if rep.get("blocking_gaps") else "queued"
        whats_missing = ", ".join(rep.get("blocking_gaps", [])) if rep.get("blocking_gaps") else None
        what_i_need = rep.get("recommended_fix") if rep.get("blocking_gaps") else None
        reports.append({
            "id": rep["id"],
            "slug": rep["slug"],
            "filename": rep["filename"],
            "source_path": rep.get("source_path", ""),
            "stage_path": rep.get("stage_path"),
            "source_sha256": sha,
            "tool": rep.get("tool", "unknown"),
            "subject_area_id": rep.get("subject_area_id"),
            "companion_files": rep.get("companion_files", []),
            "screenshot_path": rep.get("screenshot_path"),
            "scratch_dir": f"/tmp/bulk_bi/{rep['slug']}",
            "dashboard_path": None,
            "status": init_status,
            "retry_count": 0,
            "whats_missing": whats_missing,
            "what_i_need": what_i_need,
            "unconverted_items": [],
            "last_error": None,
            "observed_utc": now,
        })

    return {
        "state_version": STATE_VERSION,
        "note": "Progress ledger only. Never treat this file as user approval.",
        "created_utc": (existing or {}).get("created_utc", now),
        "updated_utc": now,
        "target": (existing or {}).get("target", {
            "semantic_view_database": None,
            "semantic_view_schema": None,
            "base_table_remap_database": None,
            "base_table_remap_schema": None,
            "dashboard_output_dir": None,
            "output_mode": "full_migration",
            "surface": "unknown",
        }),
        "subject_areas": subject_areas,
        "reports": reports,
    }


def summarize_counts(items: list[dict], field: str) -> dict[str, int]:
    counts = {k: 0 for k in sorted(VALID_STATUSES)}
    for item in items:
        st = item.get(field, "queued")
        counts[st] = counts.get(st, 0) + 1
    return counts


def render_status_markdown(manifest: dict) -> str:
    sas = manifest.get("subject_areas", [])
    reps = manifest.get("reports", [])
    sv_c = summarize_counts(sas, "sv_status")
    ag_c = summarize_counts(sas, "agent_status")
    rp_c = summarize_counts(reps, "status")

    sa_done = sv_c["completed"] + sv_c["skipped"]
    rep_done = rp_c["completed"] + rp_c["partial"] + rp_c["skipped"]

    lines = [
        f"## Batch Migration Status ({rep_done} of {len(reps)} reports finished)",
        "",
        f"- **Semantic Views ({sa_done}/{len(sas)}):** "
        f"{sv_c['completed']} completed | {sv_c['running']} running | {sv_c['queued']} queued | "
        f"{sv_c['needs_input']} needs input | {sv_c['partial']} partial | {sv_c['failed']} failed",
        f"- **Cortex Agents:** "
        f"{ag_c['completed']} completed | {ag_c['running']} running | {ag_c['queued']} queued | "
        f"{ag_c['needs_input']} needs input | {ag_c['failed']} failed",
        f"- **Dashboards:** "
        f"{rp_c['completed']} completed | {rp_c['running']} running | {rp_c['queued']} queued | "
        f"{rp_c['needs_input']} needs input | {rp_c['partial']} partial | {rp_c['failed']} failed",
        "",
        "### Subject Areas",
        "",
        "| ID | Subject Area | Action | Semantic View | Validation | Agent |",
        "|---|---|---|---|---|---|",
    ]
    for sa in sas:
        sv_cell = f"{sa['sv_status']}" + (f" ({sa['semantic_view_fqn']})" if sa.get("semantic_view_fqn") else "")
        ag_cell = f"{sa['agent_status']}" + (f" ({sa['agent_fqn']})" if sa.get("agent_fqn") else "")
        ver_cell = f"{sa['verify_status']} ({sa.get('verify_label', 'pending')})"
        act = sa.get("approved_action") if sa.get("approved_action") != "pending" else f"rec: {sa.get('recommended_action')}"
        lines.append(f"| {sa['id']} | {sa['name']} | {act} | {sv_cell} | {ver_cell} | {ag_cell} |")

    lines.extend([
        "",
        "### Reports",
        "",
        "| ID | File | Subject Area | Status | Output / Blocker |",
        "|---|---|---|---|---|",
    ])
    for r in reps:
        detail = r.get("dashboard_path") or r.get("whats_missing") or r.get("last_error") or "-"
        lines.append(f"| {r['id']} | {r['filename']} | {r.get('subject_area_id') or '-'} | {r['status']} | {detail} |")
    return "\n".join(lines) + "\n"


def render_rollup_markdown(manifest: dict) -> str:
    lines = [render_status_markdown(manifest).rstrip(), ""]
    needs = [s for s in manifest.get("subject_areas", []) if s.get("sv_status") == "needs_input" or s.get("agent_status") == "needs_input"]
    needs_rep = [r for r in manifest.get("reports", []) if r.get("status") == "needs_input"]
    failed_sa = [s for s in manifest.get("subject_areas", []) if s.get("sv_status") == "failed" or s.get("agent_status") == "failed"]
    failed_rep = [r for r in manifest.get("reports", []) if r.get("status") == "failed"]

    lines.append("### Needs Input Queue")
    lines.append("")
    if not needs and not needs_rep:
        lines.append("No items waiting for input.")
    else:
        for item in needs:
            lines.append(f"- **{item['id']} ({item['name']})**")
            lines.append(f"  - What is missing: {item.get('whats_missing') or 'unspecified'}")
            lines.append(f"  - What I need: {item.get('what_i_need') or 'confirm source mapping or scope'}")
        for item in needs_rep:
            lines.append(f"- **{item['id']} ({item['filename']})**")
            lines.append(f"  - What is missing: {item.get('whats_missing') or 'unspecified'}")
            lines.append(f"  - What I need: {item.get('what_i_need') or 'provide companion file or table FQN'}")

    lines.append("")
    lines.append("### Failed Items")
    lines.append("")
    if not failed_sa and not failed_rep:
        lines.append("No failed items.")
    else:
        for item in failed_sa:
            lines.append(f"- **{item['id']} ({item['name']})** (retries: {item.get('retry_count', 0)}): {item.get('last_error') or 'unknown error'}")
        for item in failed_rep:
            lines.append(f"- **{item['id']} ({item['filename']})** (retries: {item.get('retry_count', 0)}): {item.get('last_error') or 'unknown error'}")

    lines.append("")
    lines.append("### Open / Unconverted Definitions")
    lines.append("")
    open_rows = []
    for r in manifest.get("reports", []):
        for u in r.get("unconverted_items", []):
            open_rows.append((r["filename"], u.get("name", "?"), u.get("reason", "?"), u.get("formula", "none")))
    if not open_rows:
        lines.append("No unconverted definitions recorded.")
    else:
        lines.append("| Report | Metric / Visual | Reason | Original Formula |")
        lines.append("|---|---|---|---|")
        for rep_name, name, reason, formula in open_rows:
            lines.append(f"| {rep_name} | {name} | {reason} | `{formula}` |")
    return "\n".join(lines) + "\n"


def cmd_init(args: argparse.Namespace) -> int:
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    manifest_path = Path(args.manifest)
    existing = load_manifest(manifest_path) if (args.merge_existing and manifest_path.exists()) else None
    manifest = build_manifest_from_plan(plan, existing=existing)
    atomic_write_json(manifest_path, manifest, save_prev=manifest_path.exists())
    out = {
        "ok": True,
        "manifest": str(manifest_path),
        "subject_areas": len(manifest["subject_areas"]),
        "reports": len(manifest["reports"]),
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    manifest = load_manifest(Path(args.manifest))
    if args.format == "markdown":
        print(render_status_markdown(manifest), end="")
    else:
        out = {
            "state_version": manifest["state_version"],
            "updated_utc": manifest["updated_utc"],
            "semantic_views": summarize_counts(manifest["subject_areas"], "sv_status"),
            "verify": summarize_counts(manifest["subject_areas"], "verify_status"),
            "agents": summarize_counts(manifest["subject_areas"], "agent_status"),
            "reports": summarize_counts(manifest["reports"], "status"),
        }
        print(json.dumps(out, indent=2))
    return 0


def cmd_next_batch(args: argparse.Namespace) -> int:
    manifest = load_manifest(Path(args.manifest))
    limit = max(1, args.limit)
    max_retries = args.max_retries
    sa_by_id = {s["id"]: s for s in manifest.get("subject_areas", [])}
    picked = []

    if args.phase == "semantic_views":
        for sa in manifest["subject_areas"]:
            if sa["sv_status"] == "queued" and sa.get("retry_count", 0) < max_retries:
                picked.append(sa)
                if len(picked) >= limit:
                    break
    elif args.phase == "agents":
        for sa in manifest["subject_areas"]:
            if sa["sv_status"] == "completed" and sa["agent_status"] == "queued" and sa.get("retry_count", 0) < max_retries:
                picked.append(sa)
                if len(picked) >= limit:
                    break
    elif args.phase == "verify":
        for sa in manifest["subject_areas"]:
            if sa["sv_status"] == "completed" and sa["verify_status"] == "queued":
                picked.append(sa)
                if len(picked) >= limit:
                    break
    elif args.phase == "dashboards":
        for rep in manifest["reports"]:
            sa = sa_by_id.get(rep.get("subject_area_id"))
            sv_ready = (sa is None) or (sa.get("sv_status") == "completed")
            if sv_ready and rep["status"] == "queued" and rep.get("retry_count", 0) < max_retries:
                picked.append(rep)
                if len(picked) >= limit:
                    break

    print(json.dumps({"phase": args.phase, "count": len(picked), "items": picked}, indent=2))
    return 0


def cmd_set_subject_area(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    target = next((s for s in manifest["subject_areas"] if s["id"] == args.id), None)
    if target is None:
        print(json.dumps({"ok": False, "error": f"Unknown subject area: {args.id}"}))
        return 1

    for field_name in ("sv_status", "verify_status", "agent_status"):
        val = getattr(args, field_name)
        if val is not None:
            if val not in VALID_STATUSES:
                print(json.dumps({"ok": False, "error": f"Invalid status: {val}"}))
                return 2
            target[field_name] = val
            if val == "failed":
                target["retry_count"] = target.get("retry_count", 0) + 1

    if args.approved_action is not None:
        if args.approved_action not in VALID_SA_ACTIONS:
            print(json.dumps({"ok": False, "error": f"Invalid action: {args.approved_action}"}))
            return 2
        target["approved_action"] = args.approved_action
    if args.semantic_view_fqn is not None:
        target["semantic_view_fqn"] = args.semantic_view_fqn
    if args.agent_fqn is not None:
        target["agent_fqn"] = args.agent_fqn
    if args.verify_label is not None:
        target["verify_label"] = args.verify_label
    if args.whats_missing is not None:
        target["whats_missing"] = args.whats_missing
    if args.what_i_need is not None:
        target["what_i_need"] = args.what_i_need
    if args.last_error is not None:
        target["last_error"] = args.last_error

    now = utc_now()
    target["observed_utc"] = now
    manifest["updated_utc"] = now
    atomic_write_json(manifest_path, manifest)
    print(json.dumps({"ok": True, "subject_area": target}, indent=2))
    return 0


def cmd_set_report(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    target = next((r for r in manifest["reports"] if r["id"] == args.id), None)
    if target is None:
        print(json.dumps({"ok": False, "error": f"Unknown report: {args.id}"}))
        return 1

    if args.status is not None:
        if args.status not in VALID_STATUSES:
            print(json.dumps({"ok": False, "error": f"Invalid status: {args.status}"}))
            return 2
        target["status"] = args.status
        if args.status == "failed":
            target["retry_count"] = target.get("retry_count", 0) + 1
        if args.status == "completed":
            target["whats_missing"] = None
            target["what_i_need"] = None
            target["last_error"] = None

    if args.stage_path is not None:
        target["stage_path"] = args.stage_path
    if args.dashboard_path is not None:
        target["dashboard_path"] = args.dashboard_path
    if args.whats_missing is not None:
        target["whats_missing"] = args.whats_missing
    if args.what_i_need is not None:
        target["what_i_need"] = args.what_i_need
    if args.last_error is not None:
        target["last_error"] = args.last_error
    if args.add_unconverted is not None:
        item = json.loads(args.add_unconverted)
        target.setdefault("unconverted_items", []).append(item)

    now = utc_now()
    target["observed_utc"] = now
    manifest["updated_utc"] = now
    atomic_write_json(manifest_path, manifest)
    print(json.dumps({"ok": True, "report": target}, indent=2))
    return 0


def cmd_resume(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = load_manifest(manifest_path)
    reset_states = {"running"}
    if args.retry_needs_input:
        reset_states.add("needs_input")
    if args.retry_failed:
        reset_states.add("failed")

    requeued = {"subject_areas": [], "reports": []}
    for sa in manifest["subject_areas"]:
        for field in ("sv_status", "verify_status", "agent_status"):
            if sa.get(field) in reset_states:
                sa[field] = "queued"
                requeued["subject_areas"].append(f"{sa['id']}:{field}")
    for rep in manifest["reports"]:
        if rep.get("status") in reset_states:
            rep["status"] = "queued"
            requeued["reports"].append(rep["id"])

    manifest["updated_utc"] = utc_now()
    atomic_write_json(manifest_path, manifest)
    print(json.dumps({"ok": True, "requeued": requeued}, indent=2))
    return 0


def cmd_rollup(args: argparse.Namespace) -> int:
    manifest = load_manifest(Path(args.manifest))
    md = render_rollup_markdown(manifest)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(json.dumps({"ok": True, "rollup_path": str(out_path)}))
    else:
        print(md, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Atomic batch state CLI for agentic-bi-migration")
    sub = p.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--plan", required=True)
    p_init.add_argument("--manifest", required=True)
    p_init.add_argument("--merge-existing", action="store_true")
    p_init.set_defaults(func=cmd_init)

    p_st = sub.add_parser("status")
    p_st.add_argument("--manifest", required=True)
    p_st.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p_st.set_defaults(func=cmd_status)

    p_nb = sub.add_parser("next-batch")
    p_nb.add_argument("--manifest", required=True)
    p_nb.add_argument("--phase", choices=["semantic_views", "verify", "agents", "dashboards"], required=True)
    p_nb.add_argument("--limit", type=int, default=4)
    p_nb.add_argument("--max-retries", type=int, default=3)
    p_nb.set_defaults(func=cmd_next_batch)

    p_sa = sub.add_parser("set-subject-area")
    p_sa.add_argument("--manifest", required=True)
    p_sa.add_argument("--id", required=True)
    p_sa.add_argument("--approved-action")
    p_sa.add_argument("--sv-status")
    p_sa.add_argument("--verify-status")
    p_sa.add_argument("--verify-label")
    p_sa.add_argument("--agent-status")
    p_sa.add_argument("--semantic-view-fqn")
    p_sa.add_argument("--agent-fqn")
    p_sa.add_argument("--whats-missing")
    p_sa.add_argument("--what-i-need")
    p_sa.add_argument("--last-error")
    p_sa.set_defaults(func=cmd_set_subject_area)

    p_rep = sub.add_parser("set-report")
    p_rep.add_argument("--manifest", required=True)
    p_rep.add_argument("--id", required=True)
    p_rep.add_argument("--status")
    p_rep.add_argument("--stage-path")
    p_rep.add_argument("--dashboard-path")
    p_rep.add_argument("--whats-missing")
    p_rep.add_argument("--what-i-need")
    p_rep.add_argument("--last-error")
    p_rep.add_argument("--add-unconverted")
    p_rep.set_defaults(func=cmd_set_report)

    p_res = sub.add_parser("resume")
    p_res.add_argument("--manifest", required=True)
    p_res.add_argument("--retry-failed", action="store_true")
    p_res.add_argument("--retry-needs-input", action="store_true")
    p_res.set_defaults(func=cmd_resume)

    p_rol = sub.add_parser("rollup")
    p_rol.add_argument("--manifest", required=True)
    p_rol.add_argument("--out")
    p_rol.set_defaults(func=cmd_rollup)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
