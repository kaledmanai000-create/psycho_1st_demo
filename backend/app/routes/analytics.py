"""GET /analytics endpoint - aggregated statistics from analysis logs."""

from fastapi import APIRouter
from app.database import get_connection

router = APIRouter()


@router.get("")
async def get_analytics():
    """
    Return aggregated analytics from the analysis log database.
    Includes: total analyses, threat distribution, avg risk, decision breakdown, timeline.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Total analyses
    cursor.execute("SELECT COUNT(*) as total FROM analysis_logs")
    total = cursor.fetchone()["total"]

    # Average risk score
    cursor.execute("SELECT AVG(risk_score) as avg_risk FROM analysis_logs")
    row = cursor.fetchone()
    avg_risk = round(row["avg_risk"], 1) if row["avg_risk"] is not None else 0.0

    # Threat type distribution
    cursor.execute(
        "SELECT threat_type, COUNT(*) as count FROM analysis_logs GROUP BY threat_type ORDER BY count DESC"
    )
    threat_distribution = {row["threat_type"]: row["count"] for row in cursor.fetchall()}

    # User decision breakdown
    cursor.execute(
        "SELECT user_decision, COUNT(*) as count FROM analysis_logs GROUP BY user_decision ORDER BY count DESC"
    )
    decision_breakdown = {row["user_decision"]: row["count"] for row in cursor.fetchall()}

    # Risk score distribution (buckets)
    cursor.execute("""
        SELECT
            CASE
                WHEN risk_score <= 25 THEN 'low'
                WHEN risk_score <= 50 THEN 'medium'
                WHEN risk_score <= 75 THEN 'high'
                ELSE 'critical'
            END as risk_level,
            COUNT(*) as count
        FROM analysis_logs
        GROUP BY risk_level
    """)
    risk_distribution = {row["risk_level"]: row["count"] for row in cursor.fetchall()}

    # Analyses over time (last 30 days, grouped by date)
    cursor.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM analysis_logs
        WHERE timestamp >= DATE('now', '-30 days')
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    """)
    timeline = [{"date": row["date"], "count": row["count"]} for row in cursor.fetchall()]

    # Average confidence
    cursor.execute("SELECT AVG(confidence) as avg_conf FROM analysis_logs")
    row = cursor.fetchone()
    avg_confidence = round(row["avg_conf"], 2) if row["avg_conf"] is not None else 0.0

    conn.close()

    return {
        "total_analyses": total,
        "avg_risk_score": avg_risk,
        "avg_confidence": avg_confidence,
        "threat_distribution": threat_distribution,
        "decision_breakdown": decision_breakdown,
        "risk_distribution": risk_distribution,
        "timeline": timeline,
    }
