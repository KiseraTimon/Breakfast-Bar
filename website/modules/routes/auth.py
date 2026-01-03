from website.modules.routes import *

# Logout Route
@routes.route("/logout")
def logout():
    pass

# Signin Route
@routes.route("/signin")
def signin():
    return render_template("auth/auth.html")

# Signup Route
@routes.route("/signup")
def signup():
    return render_template("auth/auth.html")

# Password Reset Route
@routes.route("/reset-password")
def reset():
    return render_template("auth/auth.html")

# Verification Route
@routes.route("/verify")
def verify():
    return render_template("auth/auth.html")