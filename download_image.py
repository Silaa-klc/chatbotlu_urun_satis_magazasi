import urllib.request
import ssl

url = "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Besiktas_JK_logo.svg/1200px-Besiktas_JK_logo.svg.png"
output_path = "static/images/besiktas_logo.png"

req = urllib.request.Request(
    url, 
    data=None, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
)

try:
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, context=context) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())
    print("Download successful")
except Exception as e:
    print(f"Download failed: {e}")
