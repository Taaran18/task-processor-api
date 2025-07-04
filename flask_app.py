"""from flask import Flask, request, jsonify
from transcribe_audio import transcribe_audio
from transcribe_text import transcribe_text
from gemini_extractor import extract_tasks
from parse_output import parse_structured_output
from write_output import write_to_sheet

app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process():
    data = request.get_json()
    choice = data.get("choice", "").strip().lower()
    gdrive_url = data.get("gdrive_url", "").strip()

    if choice not in ["audio", "text"]:
        return jsonify({"error": "Invalid choice. Use 'audio' or 'text'."}), 400

    try:
        if choice == "audio":
            if not gdrive_url:
                return (
                    jsonify({"error": "Missing Google Drive URL for audio choice."}),
                    400,
                )
            transcription, source_link = transcribe_audio(gdrive_url)
        else:
            transcription = transcribe_text()
            source_link = ""

        structured_output = extract_tasks(transcription)
        rows = parse_structured_output(structured_output, choice, source_link)
        write_to_sheet(rows)
        return jsonify({"message": f"{len(rows)} structured tasks added."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
"""
