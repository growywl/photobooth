from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Optional

from flask import (
    Blueprint,
    abort,
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
from .printer import print_photo
from .qrcode_gen import generate_qr
from .uploader import upload_photo


bp = Blueprint("photobooth", __name__)


def _asset_url_or_none(path: Optional[Path]) -> Optional[str]:
    if path and path.exists():
        return url_for("photobooth.asset", filename=path.name)
    return None


def _frame_context() -> dict:
    return {
        "frame_url": _asset_url_or_none(config.FRAME_IMAGE),
        "frame_ratio": config.FRAME_ASPECT_RATIO,
        "slot_left": config.FRAME_SLOT_LEFT_PCT,
        "slot_top": config.FRAME_SLOT_TOP_PCT,
        "slot_width": config.FRAME_SLOT_WIDTH_PCT,
        "slot_height": config.FRAME_SLOT_HEIGHT_PCT,
    }


@bp.route("/", methods=["GET"])
def index():
    return render_template(
        "home.html",
        year=datetime.now().year,
        promptpay_url=_asset_url_or_none(config.PROMPTPAY_QR),
        wechat_url=_asset_url_or_none(config.WECHAT_QR),
        **_frame_context(),
    )


@bp.route("/capture_page", methods=["GET"])
def capture_page():
    if not session.get("paid"):
        return redirect(url_for("photobooth.index"))
    return render_template(
        "capture.html",
        countdown=config.COUNTDOWN_SECONDS,
        **_frame_context(),
    )


@bp.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    payload: Optional[dict] = None
    if request.data:
        try:
            payload = request.get_json(force=True)
        except Exception:  # pylint: disable=broad-except
            payload = None

    method = (payload or {}).get("method", "unknown")
    password_attempt = (payload or {}).get("password", "")

    if method == "cash":
        expected = config.CASH_PASSWORD_HASH
        actual = sha256(password_attempt.encode("utf-8")).hexdigest() if password_attempt else ""
        if actual != expected:
            return jsonify({"error": "Invalid staff password for cash payment."}), 403
    elif method not in {"promptpay", "wechat"}:
        return jsonify({"error": "Unsupported payment method."}), 400

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

    final_path = config.OUTPUT_DIR / photo_filename
    download_url = None
    qr_url = None
    print_status = "disabled"

    if config.AUTO_PRINT_ENABLED:
        print_status = "sent" if print_photo(final_path) else "failed"

    if config.AUTO_UPLOAD_ENABLED:
        try:
            shared_path = upload_photo(final_path)
            relative = shared_path.relative_to(config.SHARED_DIR)
            download_url = url_for(
                "photobooth.shared_file", filename=relative.as_posix(), _external=True
            )
            if config.AUTO_QR_ENABLED and download_url:
                qr_path = shared_path.with_name(f"{shared_path.stem}_qr.png")
                try:
                    qr_image = generate_qr(download_url, qr_path)
                    qr_relative = qr_image.relative_to(config.SHARED_DIR)
                    qr_url = url_for(
                        "photobooth.shared_file", filename=qr_relative.as_posix(), _external=True
                    )
                except Exception as qr_error:  # pylint: disable=broad-except
                    print(f"QR warning: {qr_error}")
        except Exception as upload_error:  # pylint: disable=broad-except
            print(f"Upload warning: {upload_error}")

    session["paid"] = False
    return jsonify(
        {
            "photoUrl": url_for("photobooth.serve_capture", filename=photo_filename),
            "downloadUrl": download_url,
            "qrUrl": qr_url,
            "printStatus": print_status,
        }
    )


@bp.route("/captures/<path:filename>", methods=["GET"])
def serve_capture(filename: str):
    return send_from_directory(str(config.OUTPUT_DIR), filename)


@bp.route("/shared/<path:filename>", methods=["GET"])
def shared_file(filename: str):
    return send_from_directory(str(config.SHARED_DIR), filename)


@bp.route("/assets/<path:filename>", methods=["GET"])
def asset(filename: str):
    if not config.ASSETS_DIR.exists():
        abort(404)
    file_path = config.ASSETS_DIR / filename
    if not file_path.exists():
        abort(404)
    return send_from_directory(str(config.ASSETS_DIR), filename)
