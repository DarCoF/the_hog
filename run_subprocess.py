import subprocess

the_other_process = subprocess.Popen(['python', 'hog.py', '-r'], shell= True)


result = the_other_process.poll()
if result is not None:
    print('the other process has finished and retuned %s' % result)