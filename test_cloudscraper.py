import cloudscraper

scraper = cloudscraper.create_scraper()

# Test REAL user
print("Testing REAL user (FlorenceArt)...")
response = scraper.get('https://www.librarything.com/profile/FlorenceArt')
print(f"Status Code: {response.status_code}")

if "cloudflare" in response.text.lower() or "challenge" in response.text.lower():
    print("❌ Still blocked by Cloudflare")
elif "FlorenceArt" in response.text or response.status_code == 200:
    print("✅ SUCCESS! Got the real profile")
    print(f"Page length: {len(response.text)} bytes")
else:
    print("⚠️  Unclear result")

print("\n" + "="*50 + "\n")

# Test FAKE user
print("Testing FAKE user (asdkjfhakjsdhf123456789)...")
response2 = scraper.get('https://www.librarything.com/profile/asdkjfhakjsdhf123456789')
print(f"Status Code: {response2.status_code}")

if "doesn't exist" in response2.text or "Error" in response2.text:
    print("✅ Found error message for fake user")
    # Find the exact error message
    if "<p>Error:" in response2.text:
        import re
        error = re.search(r'<p>Error:[^<]+</p>', response2.text)
        if error:
            print(f"Error message: {error.group()}")
else:
    print("⚠️  No clear error message found")
