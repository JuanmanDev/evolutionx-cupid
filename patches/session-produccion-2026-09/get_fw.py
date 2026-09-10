import urllib.request, re
html = urllib.request.urlopen('https://xiaomifirmwareupdater.com/firmware/cupid/').read().decode('utf-8')
print('\n'.join(re.findall(r'href="(https://[^"]*firmware[^"]*\.zip)"', html)[:5]))
