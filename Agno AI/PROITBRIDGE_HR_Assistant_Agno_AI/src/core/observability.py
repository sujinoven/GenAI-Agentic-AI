def enable_tracing(db) -> None:
    """Instrument all agent/team runs in THIS process and store traces in `db`.

    Safe to call more than once, and safe if the OpenTelemetry packages are missing
    (it just warns; runs are still saved as sessions).
    """
    try:
        from agno.tracing import setup_tracing

        setup_tracing(db=db)
    except ImportError:
        print(
            "(Tracing packages not installed — runs are still saved as sessions. "
            "Install them with: uv sync)"
        )
