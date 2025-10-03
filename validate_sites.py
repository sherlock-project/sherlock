"""Standalone validation script for testing specific Sherlock sites"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sherlock_project'))

from sites import SitesInformation
from validation import FalsePositiveDetector

def main():
    print("Sherlock Sites Validation Tool")
    print("=" * 40)
    
    # Your specific list of sites to test
    target_sites = [
        "APClips", "CyberDefenders", "GNOME VCS", "Giphy", "HackerEarth", 
        "Heavy-R", "Itch.io", "LessWrong", "LushStories", "Mydramalist", 
        "PepperIT", "PocketStars", "Reddit", "Roblox", "RocketTube", 
        "SlideShare", "SoylentNews", "Splice", "Spotify", "Topcoder", 
        "Weblate", "YandexMusic", "kaskus", "opennet", "svidbook", "threads"
    ]
    
    try:
        print("Loading sites...")
        sites = SitesInformation(honor_exclusions=False)
        detector = FalsePositiveDetector(sites)
        print(f"Loaded {len(sites)} sites")
        
        # Test a single site first
        if len(sys.argv) > 1:
            site_name = sys.argv[1]
            print(f"\nTesting {site_name}...")
            result = detector.test_site_accuracy(site_name)
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"\nResults for {site_name}:")
                analysis = result.get('analysis', {})
                print(f"  Confidence: {analysis.get('confidence', 'unknown')}")
                
                if analysis.get('potential_false_positive'):
                    print("  ⚠️  POTENTIAL FALSE POSITIVE DETECTED")
                    for issue in analysis.get('issues', []):
                        print(f"    - {issue}")
                else:
                    print("  ✅ Site appears to be working correctly")
                
                # Show test details
                print(f"\nTest Details:")
                for username, test_result in result.get('tests', {}).items():
                    if 'error' in test_result:
                        print(f"  {username}: ERROR - {test_result['error']}")
                    else:
                        print(f"  {username}: {test_result.get('detected_as', 'UNKNOWN')} "
                              f"(HTTP {test_result.get('status_code', '?')})")
        else:
            for site_name in target_sites:
                if site_name in sites.sites:
                    print(f"\nTesting {site_name}...")
                    result = detector.test_site_accuracy(site_name)
                    
                    if "error" in result:
                        print(f"  Error: {result['error']}")
                    else:
                        analysis = result.get('analysis', {})
                        print(f"  Confidence: {analysis.get('confidence', 'unknown')}")
                        
                        if analysis.get('potential_false_positive'):
                            print("  ⚠️  POTENTIAL FALSE POSITIVE")
                        else:
                            print("  ✅ Working correctly")
                else:
                    print(f"\nSite {site_name} not found in manifest.")
                    
        
    except Exception as e:
        print(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()