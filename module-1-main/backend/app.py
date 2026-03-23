from backend import create_app

app = create_app()

if __name__ == "__main__":
    # The -m backend.app approach is better, but this works direct too
    app.run(host="0.0.0.0", port=5000, debug=True)
