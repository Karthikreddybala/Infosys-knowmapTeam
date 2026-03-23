"""
Dataset routes — upload, list, delete (all JWT-protected)
POST   /api/datasets/upload
GET    /api/datasets/
DELETE /api/datasets/<id>
GET    /api/datasets/all    (admin only)
"""
import os
import uuid
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.extensions import db
from backend.models import User, Dataset

datasets_bp = Blueprint("datasets", __name__, url_prefix="/api/datasets")


def _get_user(user_id_str: str):
    return db.session.get(User, int(user_id_str))


# ── UPLOAD ────────────────────────────────────────────────────────────────────
@datasets_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_dataset():
    user = _get_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    fname   = file.filename
    ext     = os.path.splitext(fname)[1].lower()
    allowed = {".csv", ".xlsx", ".xls", ".json", ".txt", ".own"}
    if ext not in allowed:
        return jsonify({"error": f"File type {ext} not supported"}), 400

    # read into pandas
    try:
        file.seek(0)
        if ext == ".csv":
            df = pd.read_csv(file)
            file_type = "CSV"
        elif ext == ".json":
            df = pd.read_json(file)
            file_type = "JSON"
        elif ext in [".txt", ".own"]:
            content = file.read().decode("utf-8", errors="ignore")
            df = pd.DataFrame([content], columns=["Content"])
            file_type = ext.upper().replace(".", "")
        else:
            df = pd.read_excel(file)
            file_type = "Excel"
    except Exception as e:
        return jsonify({"error": f"Could not parse file: {e}"}), 422

    # save to disk
    stored_name = f"{user.username}_{uuid.uuid4().hex}{ext}"
    upload_dir  = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    file.seek(0)
    file.save(os.path.join(upload_dir, stored_name))

    # persist metadata
    ds = Dataset(
        user_id       = user.id,
        original_name = fname,
        stored_name   = stored_name,
        file_type     = file_type,
        file_size     = request.content_length or 0,
        row_count     = df.shape[0],
        column_count  = df.shape[1],
        columns       = ",".join(df.columns.astype(str).tolist()),
        source        = "upload",
    )
    db.session.add(ds)
    db.session.commit()

    return jsonify({"message": "Dataset uploaded", "dataset": ds.to_dict()}), 201


# ── LIST (current user) ───────────────────────────────────────────────────────
@datasets_bp.route("/", methods=["GET"])
@jwt_required()
def list_datasets():
    user = _get_user(get_jwt_identity())
    if not user:
        return jsonify({"error": "User not found"}), 404
    datasets = Dataset.query.filter_by(user_id=user.id).order_by(Dataset.upload_time.desc()).all()
    return jsonify({"datasets": [d.to_dict() for d in datasets]}), 200


# ── DELETE ────────────────────────────────────────────────────────────────────
@datasets_bp.route("/<int:dataset_id>", methods=["DELETE"])
@jwt_required()
def delete_dataset(dataset_id):
    user = _get_user(get_jwt_identity())
    ds   = db.session.get(Dataset, dataset_id)
    if not ds or ds.user_id != user.id:
        return jsonify({"error": "Dataset not found or not yours"}), 404

    # remove physical file
    if ds.stored_name:
        fpath = os.path.join(current_app.config["UPLOAD_FOLDER"], ds.stored_name)
        if os.path.exists(fpath):
            os.remove(fpath)

    db.session.delete(ds)
    db.session.commit()
    return jsonify({"message": "Dataset deleted"}), 200


# ── SAVE EXTERNAL DATA ────────────────────────────────────────────────────────
@datasets_bp.route("/save-external", methods=["POST"])
@jwt_required()
def save_external():
    user = _get_user(get_jwt_identity())
    data = request.get_json() or {}

    title   = data.get("title", "External Data")
    content = data.get("content", "")
    source  = data.get("source", "external")

    if not content:
        return jsonify({"error": "No content to save"}), 400

    # Create a simple CSV representation of the text or just store the text
    # For now, we save it as a text file but register it in the DB
    stored_name = f"{user.username}_{uuid.uuid4().hex}.txt"
    upload_dir  = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    
    with open(os.path.join(upload_dir, stored_name), "w", encoding="utf-8") as f:
        f.write(content)

    ds = Dataset(
        user_id       = user.id,
        original_name = title[:50] + ".txt",
        stored_name   = stored_name,
        file_type     = "Text",
        file_size     = len(content.encode("utf-8")),
        row_count     = 1,
        column_count  = 1,
        columns       = "Content",
        source        = source,
    )
    db.session.add(ds)
    db.session.commit()

    return jsonify({"message": "External data saved to DataVault", "dataset": ds.to_dict()}), 201


# ── SAVE TEXT ─────────────────────────────────────────────────────────────────
@datasets_bp.route("/save-text", methods=["POST"])
@jwt_required()
def save_text():
    user = _get_user(get_jwt_identity())
    data     = request.get_json() or {}
    content  = data.get("content", "")
    filename = data.get("filename", "external_data.txt")

    if not content:
        return jsonify({"error": "No content to save"}), 400

    stored_name = f"{user.username}_{uuid.uuid4().hex}.txt"
    upload_dir  = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    with open(os.path.join(upload_dir, stored_name), "w", encoding="utf-8") as f:
        f.write(content)

    lines = content.splitlines()
    ds = Dataset(
        user_id=user.id, original_name=filename, stored_name=stored_name,
        file_type="TXT", file_size=len(content.encode("utf-8")),
        row_count=len(lines), column_count=1, columns="text_content", source="fetch",
    )
    db.session.add(ds)
    db.session.commit()
    return jsonify({"message": "Saved to vault", "dataset": ds.to_dict()}), 201


# ── DOWNLOAD ───────────────────────────────────────────────────────────────────
@datasets_bp.route("/<int:dataset_id>/download", methods=["GET"])
@jwt_required()
def download_dataset(dataset_id):
    from flask import send_file
    user = _get_user(get_jwt_identity())
    ds   = db.session.get(Dataset, dataset_id)
    if not ds or ds.user_id != user.id:
        return jsonify({"error": "Not found"}), 404
    fpath = os.path.join(current_app.config["UPLOAD_FOLDER"], ds.stored_name)
    if not os.path.exists(fpath):
        return jsonify({"error": "File missing from disk"}), 404
    return send_file(fpath, as_attachment=True, download_name=ds.original_name)


# ── ALL (admin) ───────────────────────────────────────────────────────────────
@datasets_bp.route("/all", methods=["GET"])
@jwt_required()
def all_datasets():
    user = _get_user(get_jwt_identity())
    if not user or user.role != "admin":
        return jsonify({"error": "Admin access required"}), 403
    datasets = Dataset.query.order_by(Dataset.upload_time.desc()).all()
    result = []
    for d in datasets:
        row = d.to_dict()
        row["username"] = d.owner.username
        result.append(row)
    return jsonify({"datasets": result}), 200
