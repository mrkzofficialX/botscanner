import requests

COMMON_PATHS = [
    "/admin",
    "/login",
    "/dashboard",
    "/.env",
    "/.git",
    "/backup",
    "/phpinfo.php"
]

HEADERS_TO_CHECK = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "Referrer-Policy"
]

def scan(url, deep=False):
    result = {
        "status": None,
        "security": {},
        "paths": {},
        "server": None,
        "error": None
    }

    try:
        r = requests.get(url, timeout=10)
        result["status"] = r.status_code
        result["server"] = r.headers.get("Server", "Unknown")

        # Security headers
        for h in HEADERS_TO_CHECK:
            result["security"][h] = r.headers.get(h, "Missing")

        # Deep scan (premium)
        if deep:
            for path in COMMON_PATHS:
                try:
                    res = requests.get(url + path, timeout=5)
                    if res.status_code == 200:
                        result["paths"][path] = "FOUND"
                    else:
                        result["paths"][path] = "Not Found"
                except:
                    result["paths"][path] = "Error"

    except Exception as e:
        result["error"] = str(e)

    return result
