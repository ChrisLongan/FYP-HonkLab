import subprocess

subprocess.Popen([
    "bash", "-c",
    "PYTHONPATH=/usr/lib/python3/dist-packages QT_SCALE_FACTOR=0.6 GDK_DPI_SCALE=0.6 /usr/bin/python3 -m gnuradio.grc"
])
