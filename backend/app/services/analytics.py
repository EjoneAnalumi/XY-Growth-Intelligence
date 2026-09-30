"""Deterministic management panels computed from persisted CRM records."""

from collections import defaultdict
from datetime import UTC, datetime


def management_analytics(companies, pipeline):
    now = datetime.now(UTC)
    company_map = {str(c.id): c.model_dump(mode="json") for c in companies}
    stages = {s["id"]: s for s in pipeline.list_records("pipeline_stages")}
    deals = pipeline.list_records("opportunities")
    activities = pipeline.list_records("activities")
    tasks = pipeline.list_records("tasks")
    open_deals = [
        d
        for d in deals
        if not (
            stages.get(d["stage_id"], {}).get("is_won")
            or stages.get(d["stage_id"], {}).get("is_lost")
        )
    ]

    def grouping(key):
        buckets = defaultdict(lambda: {"count": 0, "value": 0, "weighted": 0})
        for deal in open_deals:
            company = company_map.get(str(deal["company_id"]), {})
            label = deal.get(key) if key in {"owner_id", "service"} else company.get(key)
            bucket = buckets[str(label or "Unspecified")]
            bucket["count"] += 1
            bucket["value"] += float(deal.get("value_eur") or 0)
            bucket["weighted"] += float(deal.get("weighted_value_eur") or 0)
        return [
            {"label": k, **{f: round(v, 2) for f, v in b.items()}}
            for k, b in sorted(buckets.items())
        ]

    forecast = defaultdict(lambda: {"count": 0, "value": 0, "weighted": 0})
    for deal in open_deals:
        month = str(deal.get("expected_close_date") or "Unscheduled")[:7]
        if month == "Unsched":
            month = "Unscheduled"
        bucket = forecast[month]
        bucket["count"] += 1
        bucket["value"] += float(deal.get("value_eur") or 0)
        bucket["weighted"] += float(deal.get("weighted_value_eur") or 0)
    won = [d for d in deals if stages.get(d["stage_id"], {}).get("is_won")]
    lost = [d for d in deals if stages.get(d["stage_id"], {}).get("is_lost")]
    trends = defaultdict(lambda: {"won": 0, "lost": 0})
    for deal in won + lost:
        month = str(deal["current_stage_entered_at"])[:7]
        trends[month]["won" if deal in won else "lost"] += 1
    distribution = {"Unscored": 0, "0–39": 0, "40–59": 0, "60–79": 0, "80–100": 0}
    for company in companies:
        score = company.fit_score
        label = (
            "Unscored"
            if score is None
            else "0–39"
            if score < 40
            else "40–59"
            if score < 60
            else "60–79"
            if score < 80
            else "80–100"
        )
        distribution[label] += 1
    conversions = []
    histories = defaultdict(list)
    for history in pipeline.list_all_stage_history():
        histories[history["opportunity_id"]].append(history)
    for stage_id, stage in stages.items():
        reached, progressed, days = 0, 0, []
        for deal in deals:
            history = histories[deal["id"]]
            entered = deal["stage_id"] == stage_id or any(
                h["from_stage_id"] == stage_id or h["to_stage_id"] == stage_id for h in history
            )
            if entered:
                reached += 1
                progressed += int(
                    any(
                        h["from_stage_id"] == stage_id
                        and stages.get(h["to_stage_id"], {}).get("sort_order", 0)
                        > stage["sort_order"]
                        and not stages.get(h["to_stage_id"], {}).get("is_lost")
                        for h in history
                    )
                )
            if deal["stage_id"] == stage_id:
                days.append(deal["days_in_current_stage"])
        conversions.append(
            {
                "stage": stage["name"],
                "reached": reached,
                "progressed": progressed,
                "conversion_percent": round(100 * progressed / reached, 2) if reached else 0,
                "average_current_days": round(sum(days) / len(days), 2) if days else 0,
            }
        )
    open_tasks = [t for t in tasks if t.get("status") not in {"completed", "cancelled"}]
    return {
        "total_prospects": sum(c.status == "prospect" for c in companies),
        "qualified_prospects": sum(c.status == "qualified" for c in companies),
        "meetings": sum(a["activity_type"] == "meeting" for a in activities),
        "pilots": sum(stages.get(d["stage_id"], {}).get("name") == "Pilot Active" for d in deals),
        "proposals": sum(
            stages.get(d["stage_id"], {}).get("name") == "Proposal Sent" for d in deals
        ),
        "conversion_percent": round(100 * len(won) / (len(won) + len(lost)), 2)
        if won or lost
        else 0,
        "average_deal_value": round(
            sum(float(d.get("value_eur") or 0) for d in deals) / len(deals), 2
        )
        if deals
        else 0,
        "pipeline_groups": {
            key: grouping(key)
            for key in ("headquarters_country", "industry", "service", "owner_id", "lead_source")
        },
        "forecast": [
            {"label": k, **{f: round(v, 2) for f, v in b.items()}}
            for k, b in sorted(forecast.items())
        ],
        "icp_distribution": [{"label": k, "count": v} for k, v in distribution.items()],
        "win_loss_trend": [{"month": k, **v} for k, v in sorted(trends.items())],
        "stage_conversion": conversions,
        "missing_next_action": [d for d in open_deals if not d.get("next_action")],
        "proposal_awaiting_response": [
            d for d in open_deals if stages.get(d["stage_id"], {}).get("name") == "Proposal Sent"
        ],
        "due_today": [
            t
            for t in open_tasks
            if t.get("due_at") and pipeline._parse_datetime(t["due_at"]).date() == now.date()
        ],
        "upcoming_meetings": [
            a
            for a in activities
            if a["activity_type"] == "meeting" and pipeline._parse_datetime(a["occurred_at"]) > now
        ],
        "recent_activity": sorted(activities, key=lambda a: str(a["occurred_at"]), reverse=True)[
            :10
        ],
    }
