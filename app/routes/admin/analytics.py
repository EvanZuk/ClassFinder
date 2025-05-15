"""
Admin route for viewing system logs and analytics
"""
from collections import defaultdict, Counter
from datetime import datetime
from flask import render_template, request
from app import app, get_logs, get_request_logs, start_init_time
from app.utilities.users import verify_user

@app.route("/admin/logs")
@app.route("/admin/analytics")
@verify_user(allowed_roles=["admin"])
def logs():
    """
    Display the logs analytics dashboard.
    """
    user = request.user

    # Get logs data
    request_logs = get_request_logs()
    app_logs = get_logs()

    # Limit to the most recent logs (newest first)
    app_logs = sorted(app_logs, key=lambda x: x.get('time', datetime.min), reverse=True)[:100]

    # Calculate analytics
    analytics = calculate_analytics(request_logs)

    return render_template(
        "logs.html", 
        user=user,
        analytics=analytics,
        app_logs=app_logs,
        total_requests=len(request_logs),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        start_time=start_init_time.strftime("%Y-%m-%d %H:%M:%S"),
    )

def calculate_analytics(request_logs):
    """
    Calculate analytics from the request logs.
    
    Returns:
        dict: Various analytics data
    """
    analytics = {}

    # Skip if no logs
    if not request_logs:
        return {
            "status_codes": [],
            "path_time_total": [],
            "most_requested_paths": [],
            "path_time_avg": []
        }

    # Calculate status code distribution
    status_codes = Counter([log.get("returncode") for log in request_logs])
    total_count = sum(status_codes.values())

    analytics["status_codes"] = [
        {
            "code": code,
            "count": count,
            "percentage": round((count / total_count) * 100, 2)
        }
        for code, count in sorted(status_codes.items(), key=lambda x: x[1], reverse=True)
    ]

    # Calculate path analytics
    path_time = defaultdict(list)
    path_count = Counter()

    for log in request_logs:
        # Skip 308 redirects, these are done by flask
        if log.get("returncode") == 308:
            continue

        # Skip index.css and index.html
        if log.get("url") in ["/index.css", "/index.html"]:
            continue

        path = log.get("url")
        path_count[path] += 1

        # Calculate processing time in milliseconds
        if "time" in log and "returntime" in log:
            try:
                time_diff = (log["returntime"] - log["time"]).total_seconds() * 1000
                path_time[path].append(time_diff)
            except (TypeError, AttributeError):
                # Skip if time calculation fails
                pass

    # Calculate total time spent on paths
    path_total_time = {
        path: sum(times) for path, times in path_time.items()
    }

    # Calculate total time across all paths for percentage
    total_processing_time = sum(path_total_time.values()) if path_total_time else 1  # Avoid div by 0

    analytics["path_time_total"] = [
        {
            "path": path,
            "total_time_ms": round(total_time, 2),
            "count": path_count[path],
            "time_percentage": round((total_time / total_processing_time) * 100, 2)
        }
        for path, total_time in sorted(path_total_time.items(), key=lambda x: x[1], reverse=True)
    ][:20]  # Top 20

    # Most requested paths
    total_requests = sum(path_count.values())
    analytics["most_requested_paths"] = [
        {
            "path": path,
            "count": count,
            "percentage": round((count / total_requests) * 100, 2)
        }
        for path, count in path_count.most_common(20)  # Top 20
    ]

    # Average time per path
    path_avg_time = {
        path: sum(times) / len(times) if times else 0
        for path, times in path_time.items()
    }
    analytics["path_time_avg"] = [
        {"path": path, "avg_time_ms": round(avg_time, 2), "count": path_count[path]}
        for path, avg_time in sorted(path_avg_time.items(), key=lambda x: x[1], reverse=True)
    ][:20]  # Top 20

    return analytics
