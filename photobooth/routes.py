from datetime import datetime
from typing import Optional

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)

from . import config
from .camera import capture_photo, run_countdown


bp = Blueprint("photobooth", __name__)


@bp.route("/", methods=["GET"])
def index():
    frame_url = url_for("photobooth.asset", filename=config.FRAME_IMAGE.name)
    return render_template("home.html", year=datetime.now().year, frame_url=frame_url)


@bp.route("/capture_page", methods=["GET"])
def capture_page():
    if not session.get("paid"):
        return redirect(url_for("photobooth.index"))
    frame_url = url_for("photobooth.asset", filename=config.FRAME_IMAGE.name)
    return render_template("capture.html", countdown=config.COUNTDOWN_SECONDS, frame_url=frame_url)


@bp.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    payload: Optional[dict] = None
    if request.data:
        try:
            payload = request.get_json(force=True)
        except Exception:  # pylint: disable=broad-except
            payload = None

    method = (payload or {}).get("method", "unknown")
    session["paid"] = True
    session["payment_method"] = method
    print(f"Payment confirmed via {method}")
    return jsonify({"status": "ok", "method": method})


@bp.route("/payment_status", methods=["GET"])
def payment_status():
    return jsonify({
        "paid": bool(session.get("paid")),
        "method": session.get("payment_method"),
    })


@bp.route("/capture", methods=["POST"])
def capture():
    if not session.get("paid"):
        return jsonify({"error": "Payment required"}), 403

    payload: Optional[dict] = None
    if request.data:
        try:
            payload = request.get_json(force=True)
        except Exception:  # pylint: disable=broad-except
            payload = None

    skip_countdown = bool((payload or {}).get("skipCountdown"))

    try:
        if not skip_countdown:
            run_countdown(config.COUNTDOWN_SECONDS)
        photo_filename = capture_photo(config.CAMERA_INDEX, config.OUTPUT_DIR)
    except Exception as error:  # pylint: disable=broad-except
        print(f"Error during capture: {error}")
        return jsonify({"error": str(error)}), 500

    session["paid"] = False
    return jsonify({"photoUrl": url_for("photobooth.serve_capture", filename=photo_filename)})


@bp.route("/captures/<path:filename>", methods=["GET"])
def serve_capture(filename: str):
    return send_from_directory(str(config.OUTPUT_DIR), filename)


@bp.route("/assets/<path:filename>", methods=["GET"])
def asset(filename: str):
    return send_from_directory(str(config.ASSETS_DIR), filename)
