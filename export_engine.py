"""Download-friendly serialization for local analysis results."""

import csv
import io
import json
from collections.abc import Mapping, Sequence
from typing import Any


def analysis_to_json(analysis: Mapping[str, Any]) -> str:
    return json.dumps(analysis, indent=2, ensure_ascii=False)


def _analysis_row(analysis: Mapping[str, Any]) -> dict[str, Any]:
    distribution = analysis["distribution"]
    return {
        "text": analysis["text"],
        "total_words": analysis["total_words"],
        "unique_words": analysis["unique_words"],
        "english_percentage": distribution["English"],
        "gujarati_percentage": distribution["Gujarati"],
        "hindi_percentage": distribution["Hindi"],
        "switching_count": analysis["switching_count"],
        "switching_density": analysis["switching_density"],
        "lexical_diversity": analysis["lexical_diversity"],
        "dominant_language": analysis["dominant_language"],
        "mixing_score": analysis["mixing_score"],
        "cmis": analysis["cmis"],
        "cmis_level": analysis["cmis_level"],
        "sentiment": analysis["sentiment"],
        "intent": analysis["intent"],
    }


def analyses_to_csv(analyses: Sequence[Mapping[str, Any]]) -> str:
    rows = [_analysis_row(analysis) for analysis in analyses]
    output = io.StringIO(newline="")
    if not rows:
        return ""
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def analysis_to_csv(analysis: Mapping[str, Any]) -> str:
    return analyses_to_csv([analysis])


def evaluation_to_csv(records: Sequence[Mapping[str, Any]]) -> str:
    """Serialize the evaluation table without recomputing analyses."""
    output = io.StringIO(newline="")
    fields = [
        "id",
        "text",
        "expected",
        "detected",
        "exact_match",
        "cmis",
        "switches",
        "english_percentage",
        "gujarati_percentage",
        "hindi_percentage",
    ]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()
