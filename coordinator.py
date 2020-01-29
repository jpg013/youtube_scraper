import subprocess

channel_id = "UCXX1iQGufHujuIvQ38MPKMA"

def do_run():
    process = subprocess.run(
        ["python3", "youtube/crawler.py", channel_id],
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )

    if process.returncode == 0:
        print("process returned ok")
    else:
        print("i guess this failed")

if __name__ == "__main__":
    do_run()