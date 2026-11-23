import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
PREFLIGHT = SCRIPTS_DIR / "preflight_batch.py"
BATCH_STATE = SCRIPTS_DIR / "batch_state.py"


def make_pbit(path: Path, tables: list[dict], pages: list[str] | None = None, thin: bool = False) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        if not thin:
            schema = {"model": {"tables": tables}}
            zf.writestr("DataModelSchema", json.dumps(schema).encode("utf-16-le"))
        if pages is not None:
            layout = {"sections": [{"displayName": p, "visualContainers": []} for p in pages]}
            zf.writestr("Report/Layout", json.dumps(layout).encode("utf-16-le"))


def make_m_expr(db: str, schema: str, table: str) -> str:
    return (
        'let Source = Snowflake.Databases("acct.snowflakecomputing.com", "WH"), '
        f'DB = Source{{[Name="{db}",Kind="Database"]}}[Data], '
        f'SCH = DB{{[Name="{schema}",Kind="Schema"]}}[Data], '
        f'TBL = SCH{{[Name="{table}",Kind="Table"]}}[Data] in TBL'
    )


def make_twb(path: Path, db: str, schema: str, tables: list[str], calcs: list[tuple[str, str]],
             sqlproxy_stub: str | None = None, worksheets: list[str] | None = None) -> None:
    ds_xml = []
    if sqlproxy_stub:
        ds_xml.append(
            f'<datasource name="{sqlproxy_stub}" caption="{sqlproxy_stub}">'
            f'<connection class="sqlproxy" dbname="{sqlproxy_stub}" />'
            '</datasource>'
        )
    else:
        rels = "".join(f'<relation type="table" table="[{schema}].[{t}]" />' for t in tables)
        cols = "".join(
            f'<column caption="{name}" name="[{name}]"><calculation formula="{formula}" /></column>'
            for name, formula in calcs
        )
        ds_xml.append(
            f'<datasource name="sf_ds" caption="Snowflake DS">'
            f'<connection class="snowflake" dbname="{db}" schema="{schema}" />'
            f'{rels}{cols}</datasource>'
        )
    ws_xml = "".join(f'<worksheet name="{w}" />' for w in (worksheets or ["Sheet1"]))
    xml = f'<workbook><datasources>{"".join(ds_xml)}</datasources><worksheets>{ws_xml}</worksheets></workbook>'
    path.write_text(xml, encoding="utf-8")


def make_tds(path: Path, db: str, schema: str, tables: list[str], calcs: list[tuple[str, str]]) -> None:
    rels = "".join(f'<relation type="table" table="[{schema}].[{t}]" />' for t in tables)
    cols = "".join(
        f'<column caption="{name}" name="[{name}]"><calculation formula="{formula}" /></column>'
        for name, formula in calcs
    )
    xml = (
        f'<datasource name="published" caption="Published">'
        f'<connection class="snowflake" dbname="{db}" schema="{schema}" />'
        f'{rels}{cols}</datasource>'
    )
    path.write_text(xml, encoding="utf-8")


class TestBatchScripts(unittest.TestCase):
    def run_cli(self, script: Path, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_preflight_clusters_detects_drift_pairs_tds_and_matches_existing_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exports = root / "exports"
            exports.mkdir()
            out_dir = root / "run"

            make_pbit(
                exports / "finance_exec.pbit",
                tables=[{
                    "name": "FactRevenue",
                    "partitions": [{"source": {"expression": make_m_expr("ANALYTICS", "FINANCE", "FACT_REVENUE")}}],
                    "measures": [
                        {"name": "Net Revenue", "expression": "SUM(FactRevenue[NET_AMT])"},
                        {"name": "Gross Margin", "expression": "DIVIDE(SUM(FactRevenue[PROFIT]), SUM(FactRevenue[NET_AMT]))"},
                    ],
                }, {
                    "name": "DimCustomer",
                    "partitions": [{"source": {"expression": make_m_expr("ANALYTICS", "FINANCE", "DIM_CUSTOMER")}}],
                    "measures": [],
                }],
                pages=["Executive Summary", "Margin"],
            )
            (exports / "finance_exec.png").write_bytes(b"fakepng")

            make_twb(
                exports / "finance_regional.twb",
                db="ANALYTICS",
                schema="FINANCE",
                tables=[],
                calcs=[],
                sqlproxy_stub="Finance_Published",
                worksheets=["Regional Revenue"],
            )
            make_tds(
                exports / "Finance_Published.tds",
                db="ANALYTICS",
                schema="FINANCE",
                tables=["FACT_REVENUE", "DIM_REGION"],
                calcs=[("Net Revenue", "SUM([GROSS_AMT]) - SUM([DISCOUNT])")],
            )

            make_pbit(
                exports / "inventory_ops.pbit",
                tables=[{
                    "name": "FactInventory",
                    "partitions": [{"source": {"expression": make_m_expr("ANALYTICS", "SUPPLY", "FACT_INVENTORY")}}],
                    "measures": [{"name": "On Hand Units", "expression": "SUM(FactInventory[QTY])"}],
                }],
                pages=["Inventory"],
            )

            make_twb(
                exports / "orphan_sales.twb",
                db="ANALYTICS",
                schema="SALES",
                tables=[],
                calcs=[],
                sqlproxy_stub="Missing_PDS",
                worksheets=["Sales"],
            )

            make_pbit(exports / "thin_view.pbit", tables=[], pages=["Thin"], thin=True)
            (exports / "legacy_model.qvf").write_bytes(b"binary")

            existing_path = root / "existing.json"
            existing_path.write_text(json.dumps({
                "semantic_views": [
                    {
                        "fqn": "ANALYTICS.FINANCE.FINANCE_CORE_SV",
                        "base_tables": ["ANALYTICS.FINANCE.FACT_REVENUE", "ANALYTICS.FINANCE.DIM_CUSTOMER"],
                    },
                    {
                        "fqn": "ANALYTICS.SUPPLY.INVENTORY_SV",
                        "base_tables": ["ANALYTICS.SUPPLY.FACT_INVENTORY"],
                    },
                ],
                "agents": [
                    {
                        "fqn": "ANALYTICS.FINANCE.FINANCE_AGENT",
                        "semantic_views": ["ANALYTICS.FINANCE.FINANCE_CORE_SV"],
                    }
                ],
            }), encoding="utf-8")

            res = self.run_cli(PREFLIGHT, [
                "--input-dir", str(exports),
                "--out-dir", str(out_dir),
                "--existing-assets", str(existing_path),
            ])
            self.assertEqual(res.returncode, 0, res.stderr)
            summary = json.loads(res.stdout)
            self.assertTrue(summary["ok"])
            self.assertEqual(summary["summary"]["report_count"], 5)
            self.assertEqual(summary["summary"]["unsupported_count"], 1)
            self.assertEqual(summary["summary"]["metric_drift_count"], 1)

            plan = json.loads((out_dir / "batch_plan.json").read_text(encoding="utf-8"))
            self.assertEqual(plan["_meta"]["content_trust"], "untrusted_bi_export_data")
            self.assertTrue((out_dir / "batch_plan.yaml").exists())

            sas = {sa["name"]: sa for sa in plan["bi_data"]["subject_areas"]}
            self.assertIn("Finance", sas)
            self.assertEqual(len(sas["Finance"]["report_ids"]), 2)
            self.assertEqual(sas["Finance"]["consolidation_recommendation"]["action"], "consolidate")
            self.assertEqual(sas["Finance"]["consolidation_recommendation"]["existing_sv_fqn"], "ANALYTICS.FINANCE.FINANCE_CORE_SV")
            self.assertEqual(sas["Finance"]["consolidation_recommendation"]["existing_agent_fqns"], ["ANALYTICS.FINANCE.FINANCE_AGENT"])

            self.assertIn("Supply", sas)
            self.assertEqual(sas["Supply"]["consolidation_recommendation"]["action"], "reuse")

            reps = {r["filename"]: r for r in plan["bi_data"]["reports"]}
            self.assertEqual(reps["finance_regional.twb"]["companion_files"], ["Finance_Published.tds"])
            self.assertTrue(reps["finance_exec.pbit"]["screenshot_path"].endswith("finance_exec.png"))
            self.assertTrue(reps["orphan_sales.twb"]["blocking_gaps"])
            self.assertTrue(reps["thin_view.pbit"]["blocking_gaps"])

            manifest = json.loads((out_dir / "batch_manifest.json").read_text(encoding="utf-8"))
            m_reps = {r["filename"]: r for r in manifest["reports"]}
            self.assertEqual(m_reps["finance_exec.pbit"]["status"], "queued")
            self.assertEqual(m_reps["orphan_sales.twb"]["status"], "needs_input")
            self.assertEqual(m_reps["thin_view.pbit"]["status"], "needs_input")
            self.assertEqual(m_reps["finance_exec.pbit"]["scratch_dir"], "/tmp/bulk_bi/finance_exec")

    def test_xxe_dtd_rejected_and_bracket_filename_and_slug_collision_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exports = root / "exports"
            (exports / "sub1").mkdir(parents=True)
            (exports / "sub2").mkdir(parents=True)
            out_dir = root / "run"

            (exports / "hostile[1].twb").write_text(
                '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><workbook/>',
                encoding="utf-8",
            )
            make_pbit(exports / "sub1" / "sales.pbit", tables=[], pages=["P1"])
            make_pbit(exports / "sub2" / "sales.pbit", tables=[], pages=["P2"])

            res = self.run_cli(PREFLIGHT, ["--input-dir", str(exports), "--out-dir", str(out_dir)])
            self.assertEqual(res.returncode, 0, res.stderr)
            codes = {f["code"] for f in json.loads(res.stdout)["findings"]}
            self.assertIn("B001", codes)
            self.assertIn("B003", codes)
            self.assertIn("B007", codes)

    def test_batch_state_lifecycle_gating_atomic_snapshot_and_resume(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exports = root / "exports"
            exports.mkdir()
            out_dir = root / "run"
            make_pbit(
                exports / "rev.pbit",
                tables=[{
                    "name": "Orders",
                    "partitions": [{"source": {"expression": make_m_expr("DB1", "SALES", "ORDERS")}}],
                    "measures": [{"name": "Revenue", "expression": "SUM(Orders[AMT])"}],
                }],
                pages=["Overview"],
            )
            res = self.run_cli(PREFLIGHT, ["--input-dir", str(exports), "--out-dir", str(out_dir)])
            self.assertEqual(res.returncode, 0, res.stderr)
            manifest_path = out_dir / "batch_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            sa_id = manifest["subject_areas"][0]["id"]
            rep_id = manifest["reports"][0]["id"]

            nb_dash_early = json.loads(self.run_cli(BATCH_STATE, [
                "next-batch", "--manifest", str(manifest_path), "--phase", "dashboards", "--limit", "4"
            ]).stdout)
            self.assertEqual(nb_dash_early["count"], 0)

            up_sa = self.run_cli(BATCH_STATE, [
                "set-subject-area", "--manifest", str(manifest_path),
                "--id", sa_id,
                "--approved-action", "create_new",
                "--sv-status", "completed",
                "--semantic-view-fqn", "DB1.SALES.SALES_SV",
                "--verify-status", "completed",
                "--verify-label", "dashboard_parity",
            ])
            self.assertEqual(up_sa.returncode, 0, up_sa.stderr)
            self.assertTrue((out_dir / "batch_manifest.prev.json").exists())

            nb_dash = json.loads(self.run_cli(BATCH_STATE, [
                "next-batch", "--manifest", str(manifest_path), "--phase", "dashboards", "--limit", "4"
            ]).stdout)
            self.assertEqual(nb_dash["count"], 1)

            self.run_cli(BATCH_STATE, [
                "set-report", "--manifest", str(manifest_path),
                "--id", rep_id,
                "--status", "needs_input",
                "--whats-missing", "Missing filter state",
                "--what-i-need", "Confirm default fiscal year",
                "--add-unconverted", json.dumps({"name": "YTD Ratio", "reason": "Complex DAX formula", "formula": "CALCULATE(...)"}),
            ])

            rollup_md = self.run_cli(BATCH_STATE, ["rollup", "--manifest", str(manifest_path)]).stdout
            self.assertIn("Missing filter state", rollup_md)
            self.assertIn("YTD Ratio", rollup_md)

            res_resume = json.loads(self.run_cli(BATCH_STATE, [
                "resume", "--manifest", str(manifest_path), "--retry-needs-input"
            ]).stdout)
            self.assertIn(rep_id, res_resume["requeued"]["reports"])
            reloaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded["subject_areas"][0]["sv_status"], "completed")
            self.assertEqual(reloaded["reports"][0]["status"], "queued")


if __name__ == "__main__":
    unittest.main()
