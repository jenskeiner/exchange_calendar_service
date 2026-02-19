import uvicorn


def main():
    uvicorn.run(
        "exchange_calendar_service.app:get_app",
        factory=True,
        host="127.0.0.1",
        port=8080,
        log_level="info",
    )


if __name__ == "__main__":
    main()
