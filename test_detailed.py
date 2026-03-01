import cloudscraper

scraper = cloudscraper.create_scraper()

# Test REAL user
print("Testing REAL user (FlorenceArt)...")
response = scraper.get('https://www.librarything.com/profile/FlorenceArt')

# Check what's actually in the page
has_cloudflare = "cloudflare" in response.text.lower()
has_challenge = "challenge" in response.text.lower()
has_profile = "FlorenceArt" in response.text
has_error = "doesn't exist" in response.text

print(f"Status Code: {response.status_code}")
print(f"Page contains 'cloudflare': {has_cloudflare}")
print(f"Page contains 'challenge': {has_challenge}")
print(f"Page contains 'FlorenceArt': {has_profile}")
print(f"Page contains error message: {has_error}")
print(f"Page length: {len(response.text)} bytes")

# Save to file for inspection
with open('real_user_response.html', 'w') as f:
    f.write(response.text)
print("\nSaved response to real_user_response.html")

print("\n" + "="*50 + "\n")

# Test FAKE user
print("Testing FAKE user...")
response2 = scraper.get('https://www.librarything.com/profile/asdkjfhakjsdhf123456789')
has_error2 = "doesn't exist" in response2.text

print(f"Status Code: {response2.status_code}")
print(f"Has error message: {has_error2}")

with open('fake_user_response.html', 'w') as f:
    f.write(response2.text)
print("Saved response to fake_user_response.html")
