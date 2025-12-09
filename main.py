from website import create_app

app = create_app()

# Entry Point
if __name__ == "__main__":
    app.run(debug=True)
