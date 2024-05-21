try:
    import webbrowser
    import os
    import sys
except ImportError as e:
    print(f"Error importing module: {e}")
    sys.exit(1)

try:
    # Input the username and the number of urls to open from command line
    username = sys.argv[1]
    num_urls = int(sys.argv[2])

    # Open the file and read the links
    with open(f'{username}.txt', 'r') as file:
        urls = file.readlines()
except IndexError:
    print("Please provide both username and the number of URLs to open.")
    sys.exit(1)
except FileNotFoundError:
    print(f"No file found with the name {username}.txt")
    sys.exit(1)
except ValueError:
    print("The number of URLs to open should be an integer.")
    sys.exit(1)

# Remove the newline character from each url
urls = [url.strip() for url in urls]

# If the number of urls is more than the number of urls in the file, adjust it
num_urls = min(num_urls, len(urls))

print(f"Opening the first {num_urls} URLs:")

# Open each link in incognito mode
for i in range(num_urls):
    print(urls[i])
    try:
        if os.name == 'posix':  # macOS and Linux
            webbrowser.get("open -a /Applications/Google/ Chrome.app %s --args --incognito").open(urls[i])
        else:  # Windows
            webbrowser.get("C:/Program Files/Google/Chrome/Application/chrome.exe %s --incognito").open(urls[i])
    except webbrowser.Error:
        print(f"Failed to open URL: {urls[i]}")
        continue

print("Done")
