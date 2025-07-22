import subprocess

subprocess.Popen([
    "bash", "-c",
    "QT_SCALE_FACTOR=0.6 GDK_DPI_SCALE=0.6 /home/pi/FYP-HonkLab/honkenv/bin/python3 -m gnuradio.grc"
])
