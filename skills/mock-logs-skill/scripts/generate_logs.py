#!/usr/bin/env python3
"""Generate mock log entries for testing."""

import sys
import random
from datetime import datetime, timedelta

LEVELS = ["INFO", "WARN", "ERROR", "DEBUG"]

SERVICES = [
    "api-gateway",
    "auth-service",
    "user-service",
    "payment-service",
    "notification-service",
    "cache-manager",
    "db-connector",
    "queue-worker",
]

MESSAGES = {
    "INFO": [
        "Request processed successfully",
        "User session started",
        "Cache hit for key: user_{}",
        "Connection established to database",
        "Health check passed",
        "Configuration reloaded",
        "Scheduled task completed",
        "Message published to queue",
    ],
    "WARN": [
        "High memory usage detected: {}%",
        "Slow query detected: {}ms",
        "Rate limit approaching for client {}",
        "Retry attempt {} of 3",
        "Connection pool running low",
        "Deprecated API endpoint called",
        "Certificate expires in {} days",
    ],
    "ERROR": [
        "Failed to connect to database: timeout",
        "Authentication failed for user {}",
        "Payment processing error: insufficient funds",
        "Service unavailable: upstream timeout",
        "Invalid request payload",
        "Queue message processing failed",
        "Disk space critical: {}% used",
    ],
    "DEBUG": [
        "Entering function: process_request",
        "Variable state: count={}",
        "SQL query: SELECT * FROM users WHERE id={}",
        "HTTP response: status={}, body_size={}",
        "Cache miss for key: session_{}",
        "Decoding JWT token",
        "Validating input parameters",
    ],
}

def generate_log_entry(level=None, base_time=None):
    if level is None:
        level = random.choice(LEVELS)

    service = random.choice(SERVICES)
    message_template = random.choice(MESSAGES[level])

    # Fill in placeholders with random values
    message = message_template
    while "{}" in message:
        placeholder_value = random.randint(1, 9999)
        message = message.replace("{}", str(placeholder_value), 1)

    if base_time is None:
        base_time = datetime.now()

    timestamp = base_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    return f"[{timestamp}] [{level:5}] [{service}] {message}"

def main():
    count = 5
    level_filter = None

    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid count '{sys.argv[1]}'", file=sys.stderr)
            sys.exit(1)

    if len(sys.argv) > 2:
        level_arg = sys.argv[2].upper()
        if level_arg != "ALL" and level_arg in LEVELS:
            level_filter = level_arg
        elif level_arg != "ALL":
            print(f"Error: Invalid level '{sys.argv[2]}'. Use: info, warn, error, debug, or all", file=sys.stderr)
            sys.exit(1)

    base_time = datetime.now() - timedelta(seconds=count)

    for i in range(count):
        log_time = base_time + timedelta(seconds=i, milliseconds=random.randint(0, 999))
        print(generate_log_entry(level=level_filter, base_time=log_time))

if __name__ == "__main__":
    main()
