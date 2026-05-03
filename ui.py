"""
ui.py — Simple Streamlit UI for the Organ Note Cutter
Run with: streamlit run ui.py
"""

import streamlit as st
import os
import subprocess
import sys

# ── Page config ───────────────────────────────────────────────────────────────
st.title("🎹 Organ Note Cutter")
st.caption("Upload a WAV file, set your config, and cut individual notes automatically.")

# ── Settings ──────────────────────────────────────────────────────────────────
st.header("Settings")

col1, col2 = st.columns(2)
with col1:
    stop_length   = st.text_input("Stop Length (e.g. 8, 5 1/3)", value="8")
    base_pitch    = st.number_input("Base Pitch (Hz)", value=440.0, step=0.5)
with col2:
    margin        = st.number_input("Pitch Margin of Error (%)", value=1.0, step=0.5)
    num_pipes     = st.number_input("Number of Pipes in Rank", value=54, step=1)

# ── File upload ───────────────────────────────────────────────────────────────
st.header("Input File")

uploaded = st.file_uploader("Upload a WAV file", type=["wav"])

# ── Run ───────────────────────────────────────────────────────────────────────
if st.button("▶ Run Processing", disabled=(uploaded is None)):

    # Save uploaded file to input_files/
    os.makedirs("input_files",  exist_ok=True)
    os.makedirs("output_files", exist_ok=True)

    input_path = os.path.join("input_files", uploaded.name)
    with open(input_path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Saved: {uploaded.name}")

    # Write CONFIG.txt from UI values
    config_text = (
        f"Stop length number (Ex. 8ft organ stop would be 8): {stop_length}\n"
        f"Organ base pitch (default in America is 440): {base_pitch}\n"
        f"Pitch margin of error (number specifies +/- percent off): {margin}\n"
        f"Number of pipes in rank: {int(num_pipes)}\n"
    )
    with open("CONFIG.txt", "w") as f:
        f.write(config_text)

    # Run note_cutout.py and stream output
    st.header("Processing Log")
    log_area = st.empty()
    log_lines = []

    with st.spinner("Processing... (this may take a minute for long files)"):
        proc = subprocess.Popen(
            [sys.executable, "note_cutout.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in proc.stdout:
            log_lines.append(line.rstrip())
            log_area.code("\n".join(log_lines))
        proc.wait()

    if proc.returncode == 0:
        st.success("✅ Processing complete!")
    else:
        st.error("❌ Processing finished with errors. See log above.")

    # ── Output files ──────────────────────────────────────────────────────────
    st.header("Output Files")
    output_files = [f for f in os.listdir("output_files") if f.endswith(".wav")]

    if output_files:
        st.write(f"**{len(output_files)} file(s) created:**")
        for fname in sorted(output_files):
            fpath = os.path.join("output_files", fname)
            with open(fpath, "rb") as f:
                st.download_button(
                    label=f"⬇ {fname}",
                    data=f,
                    file_name=fname,
                    mime="audio/wav",
                    key=fname  # unique key per button
                )
    else:
        st.warning("No output files found. Check the log for errors.")

elif uploaded is None:
    st.info("Upload a WAV file above to enable processing.")
