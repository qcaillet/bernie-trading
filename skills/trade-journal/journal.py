#!/usr/bin/env python3
"""
Trade journal: création, mise à jour, calcul de stats.

Format atomique: chaque trade = 1 fichier .md.
Méta stockée via "front-matter style" en début de fichier (entre <!-- BERNIE:META --> et fin marker)
pour faciliter le parsing programmatique.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TRADES = ROOT / "trades"
STATS_FILE = ROOT / "STATS.md"
TEMPLATE = TRADES / "TEMPLATE.md"


META_START = "<!-- BERNIE:META"
META_END = "BERNIE:META -->"


class TradeJournal:
    def __init__(self):
        TRADES.mkdir(exist_ok=True)

    # ---- Trade IDs ----

    def _next_trade_id(self, date: datetime | None = None) -> str:
        d = date or datetime.now(timezone.utc)
        prefix = f"t_{d.strftime('%Y%m%d')}_"
        existing = [p.name for p in TRADES.glob(f"{prefix}*.md")]
        if not existing:
            return f"{prefix}001"
        nums = []
        for name in existing:
            m = re.match(rf"{re.escape(prefix)}(\d+)", name)
            if m:
                nums.append(int(m.group(1)))
        return f"{prefix}{(max(nums) + 1):03d}"

    # ---- CRUD ----

    def create_trade(self, symbol: str, side: str, setup: str, entry: float, sl: float, tp: float,
                     risk_eur: float, rationale: str, instrument_id: int | None = None) -> str:
        tid = self._next_trade_id()
        rr = abs(tp - entry) / abs(entry - sl) if entry != sl else 0
        meta = {
            "trade_id": tid,
            "symbol": symbol,
            "side": side.upper(),
            "setup": setup,
            "entry_planned": entry,
            "sl_planned": sl,
            "tp_planned": tp,
            "risk_eur": risk_eur,
            "rr_planned": round(rr, 2),
            "instrument_id": instrument_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "proposed",
            "events": [],
        }
        path = TRADES / f"{tid}-{symbol}.md"
        body = self._render_md(meta, rationale=rationale)
        path.write_text(body)
        return tid

    def _path_for(self, trade_id: str) -> Path:
        hits = list(TRADES.glob(f"{trade_id}-*.md"))
        if not hits:
            raise ValueError(f"Trade {trade_id} introuvable")
        return hits[0]

    def _load_meta(self, trade_id: str) -> tuple[dict, str]:
        path = self._path_for(trade_id)
        content = path.read_text()
        start = content.find(META_START)
        end = content.find(META_END)
        if start == -1 or end == -1:
            raise ValueError(f"Pas de méta dans {path.name}")
        block = content[start + len(META_START):end]
        # Extract JSON from ```json ... ``` fence
        m = re.search(r"```json\s*(.+?)\s*```", block, re.DOTALL)
        json_block = m.group(1).strip() if m else block.strip()
        meta = json.loads(json_block)
        return meta, content

    def _save_meta(self, trade_id: str, meta: dict, rationale_extra: str | None = None) -> None:
        path = self._path_for(trade_id)
        content = path.read_text()
        # Replace meta block
        json_block = json.dumps(meta, indent=2, ensure_ascii=False)
        new_block = f"{META_START}\n```json\n{json_block}\n```\n{META_END}"
        start = content.find(META_START)
        end = content.find(META_END) + len(META_END)
        if start == -1 or end == -1:
            # Re-render full
            content = self._render_md(meta)
        else:
            content = content[:start] + new_block + content[end:]
        path.write_text(content)

    def mark_executed(self, trade_id: str, position_id: int, open_rate: float, order_id: int, units: float | None = None) -> None:
        meta, _ = self._load_meta(trade_id)
        meta["status"] = "open"
        meta["position_id"] = position_id
        meta["order_id"] = order_id
        meta["open_rate"] = open_rate
        meta["units"] = units
        meta["opened_at"] = datetime.now(timezone.utc).isoformat()
        meta["events"].append({"ts": meta["opened_at"], "kind": "executed", "open_rate": open_rate})
        self._save_meta(trade_id, meta)

    def mark_skipped(self, trade_id: str, reason: str) -> None:
        meta, _ = self._load_meta(trade_id)
        meta["status"] = "skipped"
        meta["skipped_at"] = datetime.now(timezone.utc).isoformat()
        meta["skip_reason"] = reason
        meta["events"].append({"ts": meta["skipped_at"], "kind": "skipped", "reason": reason})
        self._save_meta(trade_id, meta)

    def mark_closed(self, trade_id: str, exit_type: str, exit_rate: float, pnl_eur: float, duration: str | None = None) -> None:
        meta, _ = self._load_meta(trade_id)
        meta["status"] = "closed"
        meta["closed_at"] = datetime.now(timezone.utc).isoformat()
        meta["exit_type"] = exit_type
        meta["exit_rate"] = exit_rate
        meta["pnl_eur"] = pnl_eur
        meta["duration"] = duration
        risk = meta.get("risk_eur", 0)
        meta["r_realized"] = round(pnl_eur / risk, 2) if risk else 0
        meta["outcome"] = "win" if pnl_eur > 0 else ("loss" if pnl_eur < 0 else "breakeven")
        meta["events"].append({"ts": meta["closed_at"], "kind": "closed", "exit_type": exit_type, "exit_rate": exit_rate, "pnl_eur": pnl_eur})
        self._save_meta(trade_id, meta)

    def log_event(self, trade_id: str, message: str, kind: str = "note") -> None:
        meta, _ = self._load_meta(trade_id)
        meta["events"].append({"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, "message": message})
        self._save_meta(trade_id, meta)

    # ---- Stats ----

    def _all_meta(self) -> list[dict]:
        metas = []
        for p in sorted(TRADES.glob("t_*-*.md")):
            try:
                m, _ = self._load_meta(p.name.split("-", 1)[0])
                metas.append(m)
            except Exception:
                pass
        return metas

    def compute_stats(self) -> dict:
        metas = self._all_meta()
        closed = [m for m in metas if m.get("status") == "closed"]
        wins = [m for m in closed if m.get("outcome") == "win"]
        losses = [m for m in closed if m.get("outcome") == "loss"]
        be = [m for m in closed if m.get("outcome") == "breakeven"]
        wr = len(wins) / len(closed) if closed else 0
        r_wins = [m.get("r_realized", 0) for m in wins]
        r_losses = [m.get("r_realized", 0) for m in losses]
        avg_r_win = sum(r_wins) / len(r_wins) if r_wins else 0
        avg_r_loss = sum(r_losses) / len(r_losses) if r_losses else 0
        expectancy = wr * avg_r_win + (1 - wr) * avg_r_loss
        pnl_cum = sum(m.get("pnl_eur", 0) for m in closed)
        # Drawdown calc
        running = 0
        peak = 0
        max_dd = 0
        for m in sorted(closed, key=lambda x: x.get("closed_at", "")):
            running += m.get("pnl_eur", 0)
            peak = max(peak, running)
            dd = peak - running
            max_dd = max(max_dd, dd)
        # Streaks
        streak_w = streak_l = max_w = max_l = 0
        for m in sorted(closed, key=lambda x: x.get("closed_at", "")):
            if m.get("outcome") == "win":
                streak_w += 1
                streak_l = 0
            elif m.get("outcome") == "loss":
                streak_l += 1
                streak_w = 0
            max_w = max(max_w, streak_w)
            max_l = max(max_l, streak_l)
        return {
            "total": len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "breakeven": len(be),
            "winrate": round(wr, 3),
            "avg_r_win": round(avg_r_win, 2),
            "avg_r_loss": round(avg_r_loss, 2),
            "expectancy_r": round(expectancy, 2),
            "pnl_cum_eur": round(pnl_cum, 2),
            "max_drawdown_eur": round(max_dd, 2),
            "max_streak_win": max_w,
            "max_streak_loss": max_l,
        }

    def write_stats(self, stats: dict | None = None) -> None:
        s = stats or self.compute_stats()
        lines = [
            "# Stats",
            "",
            "_(mis à jour automatiquement après chaque trade clôturé)_",
            "",
            "## Vue d'ensemble",
            "",
            "| Métrique | Valeur |",
            "|---|---|",
            f"| Trades totaux | {s['total']} |",
            f"| Trades gagnants | {s['wins']} |",
            f"| Trades perdants | {s['losses']} |",
            f"| Trades à breakeven | {s['breakeven']} |",
            f"| Win rate | {s['winrate']*100:.1f}% |",
            f"| R moyen sur winners | {s['avg_r_win']:.2f} |",
            f"| R moyen sur losers | {s['avg_r_loss']:.2f} |",
            f"| **Expectancy (R)** | {s['expectancy_r']:.2f} |",
            f"| P&L cumulé | {s['pnl_cum_eur']:.2f} € |",
            f"| Drawdown max | {s['max_drawdown_eur']:.2f} € |",
            f"| Streak max gagnante | {s['max_streak_win']} |",
            f"| Streak max perdante | {s['max_streak_loss']} |",
            "",
            f"_Dernière mise à jour : {datetime.now(timezone.utc).isoformat()}_",
        ]
        STATS_FILE.write_text("\n".join(lines))

    def last_loss_time(self) -> datetime | None:
        metas = self._all_meta()
        losses = [m for m in metas if m.get("outcome") == "loss"]
        if not losses:
            return None
        latest = max(losses, key=lambda m: m.get("closed_at", ""))
        return datetime.fromisoformat(latest["closed_at"])

    def recent_streak(self) -> tuple[str, int]:
        """Returns ('win', n) or ('loss', n) based on most recent closed trades."""
        metas = sorted([m for m in self._all_meta() if m.get("status") == "closed"], key=lambda m: m.get("closed_at", ""), reverse=True)
        if not metas:
            return ("none", 0)
        outcome = metas[0].get("outcome")
        n = 0
        for m in metas:
            if m.get("outcome") == outcome:
                n += 1
            else:
                break
        return (outcome, n)

    def list_trades(self, symbol: str | None = None, status: str | None = None) -> list[dict]:
        metas = self._all_meta()
        if symbol:
            metas = [m for m in metas if m.get("symbol") == symbol]
        if status:
            metas = [m for m in metas if m.get("status") == status]
        return metas

    # ---- Rendering ----

    @staticmethod
    def _render_md(meta: dict, rationale: str = "") -> str:
        json_block = json.dumps(meta, indent=2, ensure_ascii=False)
        return f"""# Trade {meta['trade_id']} — {meta['symbol']} {meta['side']}

{META_START}
```json
{json_block}
```
{META_END}

## Plan

| Param | Valeur |
|---|---|
| Setup | {meta.get('setup','-')} |
| Side | {meta.get('side','-')} |
| Entrée prévue | ${meta.get('entry_planned','-'):.2f} |
| Stop-loss | ${meta.get('sl_planned','-'):.2f} |
| Take-profit | ${meta.get('tp_planned','-'):.2f} |
| Risque | {meta.get('risk_eur','-')}€ |
| R/R | 1:{meta.get('rr_planned','-')} |

## Raisonnement

{rationale}

## Évolution

_(timeline auto-remplie via events)_

## Debrief

_(rempli post-clôture par le subagent `trade-debriefer`)_
"""


if __name__ == "__main__":
    import sys
    j = TradeJournal()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if cmd == "stats":
        s = j.compute_stats()
        print(json.dumps(s, indent=2))
    elif cmd == "list":
        for m in j.list_trades():
            print(f"{m['trade_id']} {m['symbol']} {m['side']} status={m['status']}")
    elif cmd == "rewrite-stats":
        j.write_stats()
        print("STATS.md updated.")
    elif cmd == "demo":
        # demo flow
        tid = j.create_trade("SPY", "LONG", "V2A", 755.50, 750.10, 766.40, 10.0,
                              "Test demo flow", instrument_id=3000)
        print(f"Created: {tid}")
        j.mark_executed(tid, position_id=99999, open_rate=755.62, order_id=12345, units=1.8)
        j.log_event(tid, "Demo event")
        j.mark_closed(tid, "TP", 766.40, 18.45, "demo")
        print(f"Closed.")
        s = j.compute_stats()
        print(json.dumps(s, indent=2))
