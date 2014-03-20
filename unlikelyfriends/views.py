from django.shortcuts import render
from django.template import RequestContext
import subprocess
import json

def home(request):
  output_list = None
  display_login = True
  if request.method == 'POST':
    oauth = request.POST.get('title')
    command = "python /Users/telenardo/Documents/PyUnlikelyFriendFinder/fullScript.py " + str(oauth)
    #json = os.system(command)
    proc = subprocess.Popen([command, ""], stdout=subprocess.PIPE, shell=True)
    (output, err) = proc.communicate()
    output = json.loads(output)
    output_list = []
    for i in range(1,100):
      output_list.append(output[str(i)])
    display_login = False
  variables = RequestContext(request,{'output': output_list, 'display_login': display_login})
  return render(request, 'index.html', variables)# ,variables)
# Create your views here.
