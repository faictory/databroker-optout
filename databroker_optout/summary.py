def format_text(result):
    lines = []

    lines.append("databroker-optout — exposure audit")

    input_info = result["input"]
    lines.append(f"input: {input_info['path']}  ({input_info['rows']} rows, {input_info['format']})")

    broker_db = result["broker_db"]
    lines.append(f"broker DB: {broker_db['brokers']} brokers, verified {broker_db['verified']}")

    lines.append("")

    summary = result["summary"]
    exposures_count = summary["exposures"]
    deduped_rows = summary["deduped_rows"]
    lines.append(f"exposures: {exposures_count} unique  ({deduped_rows} rows deduped)")

    high_priority = summary["high_priority"]
    lines.append(f"high priority: {high_priority}")

    lines.append("")

    for exposure in result["exposures"]:
        priority_marker = "[HIGH]" if exposure["priority"] == "high" else "[   ]"
        exp_id = exposure["id"]
        name = exposure["name"]
        location = exposure["location"]
        sources_str = ", ".join(exposure["sources"])

        if exposure["priority"] == "high":
            spacing_after_bracket = " "
            spacing_base = 28
        else:
            spacing_after_bracket = "  "
            spacing_base = 29

        spacing_before_sources = max(3, spacing_base - len(name) - len(location))
        sources_spacing = " " * spacing_before_sources
        line = f"  {priority_marker}{spacing_after_bracket}{exp_id}  {name} — {location}{sources_spacing}sources: {sources_str}"

        if exposure.get("deadname_matches"):
            deadname_str = ", ".join(f'"{dn}"' for dn in exposure["deadname_matches"])
            line += f"   (deadname match: {deadname_str})"

        lines.append(line)

    lines.append("")

    requests = result["requests"]
    request_count = len(requests)
    tracker_path = result["tracker"]["path"]
    request_dir = f"{tracker_path.rsplit('/', 1)[0]}/requests/"
    lines.append(f"removal requests: {request_count} written → {request_dir}")

    request_files = [req["file"].split("/")[-1] for req in requests]
    lines.append("  " + "  ".join(request_files))

    tracker = result["tracker"]
    pending = tracker["pending"]
    submitted = tracker["submitted"]
    confirmed = tracker["confirmed"]
    lines.append(f"tracker: {tracker['path']}  ({pending} pending · {submitted} submitted · {confirmed} confirmed)")

    return "\n".join(lines)


def format_json(result):
    return {
        "input": result["input"],
        "broker_db": result["broker_db"],
        "exposures": [
            {
                "id": exp["id"],
                "name": exp["name"],
                "location": exp["location"],
                "sources": exp["sources"],
                "priority": exp["priority"],
                "deadname_matches": exp.get("deadname_matches", []),
                "urls": exp.get("urls", [])
            }
            for exp in result["exposures"]
        ],
        "summary": result["summary"],
        "requests": [
            {
                "broker": req["broker"],
                "slug": req["slug"],
                "file": req["file"]
            }
            for req in result["requests"]
        ],
        "tracker": result["tracker"]
    }
