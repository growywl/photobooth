"""Entry point for the Flask-based photo booth application."""

from photobooth import create_app

app = create_app()


if __name__ == "__main__":
    print("Starting web photo booth on http://127.0.0.1:5000")
    app.run(debug=True)
