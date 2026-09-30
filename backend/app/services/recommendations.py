def recommend_services(score, catalogue):
    signals = {item.rule_id for item in score.explanations if item.points > 0}
    if signals & {"regulatory_context", "cloud_usage"}:
        names = ["Cloud Security Assessment", "Compliance Readiness Review", "Managed SOC"]
        reason = "Recorded cloud or regulatory signals support a scoped control review."
        step = "Confirm cloud scope, compliance obligations, and evidence gaps in discovery."
    elif "industry_fit" in signals or score.score >= 80:
        names = [
            "Cyber Risk Snapshot",
            "External Attack Surface Review",
            "Executive Security Workshop",
        ]
        reason = "Industry and ICP signals support an executive risk discussion."
        step = "Confirm an approved mock target and agree the scope before generating a report."
    else:
        names = ["Security Discovery Workshop", "Cyber Risk Snapshot"]
        reason = "Qualify the missing technical and commercial signals before proposing services."
        step = "Record budget, timeline, decision-maker, and service needs in a discovery meeting."
    active = {s["name"] for s in catalogue if s["active"]}
    names = [name for name in names if name in active]
    return {
        "primary": names[0] if names else "No matching active service",
        "secondary": names[1:3],
        "reason": reason,
        "nextStep": step,
    }
