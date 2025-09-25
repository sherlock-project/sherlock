"""Comprehensive validation script for your specific sites list"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sherlock_project'))

from sites import SitesInformation
from validation import FalsePositiveDetector
import time

def main():
    print("Sherlock Sites Validation Tool - Comprehensive Test")
    print("=" * 60)
    
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
        print(f"Testing {len(target_sites)} specific sites...")
        print("-" * 60)
        
        problematic_sites = []
        working_sites = []
        missing_sites = []
        error_sites = []
        
        for i, site_name in enumerate(target_sites, 1):
            print(f"[{i:2d}/{len(target_sites)}] Testing {site_name}...", end=" ")
            
            if site_name not in sites.sites:
                print("NOT FOUND")
                missing_sites.append(site_name)
                continue
            
            try:
                result = detector.test_site_accuracy(site_name)
                
                if "error" in result:
                    print(f"ERROR - {result['error']}")
                    error_sites.append(site_name)
                else:
                    analysis = result.get('analysis', {})
                    confidence = analysis.get('confidence', 'unknown')
                    
                    if analysis.get('potential_false_positive'):
                        print(f"⚠️  POTENTIAL FALSE POSITIVE ({confidence})")
                        problematic_sites.append((site_name, analysis))
                    else:
                        print(f"✅ OK ({confidence})")
                        working_sites.append(site_name)
                        
            except Exception as e:
                print(f"ERROR - {str(e)}")
                error_sites.append(site_name)
            
            # Small delay to be respectful to servers
            time.sleep(0.5)
        
        # Summary Report
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY REPORT")
        print("=" * 60)
        print(f"Total sites tested: {len(target_sites)}")
        print(f"Working correctly: {len(working_sites)}")
        print(f"Potentially problematic: {len(problematic_sites)}")
        print(f"Missing from manifest: {len(missing_sites)}")
        print(f"Errors during testing: {len(error_sites)}")
        
        if problematic_sites:
            print(f"\n⚠️  POTENTIALLY PROBLEMATIC SITES:")
            print("-" * 40)
            for site_name, analysis in problematic_sites:
                print(f"\n{site_name}:")
                print(f"  Confidence: {analysis.get('confidence', 'unknown')}")
                issues = analysis.get('issues', [])
                for issue in issues:
                    print(f"  - {issue}")
                recommendations = analysis.get('recommendations', [])
                for rec in recommendations:
                    print(f"  → {rec}")
        
        if missing_sites:
            print(f"\n❓ MISSING FROM MANIFEST:")
            print("-" * 40)
            for site in missing_sites:
                print(f"  - {site}")
        
        if error_sites:
            print(f"\n❌ ERRORS DURING TESTING:")
            print("-" * 40)
            for site in error_sites:
                print(f"  - {site}")
        
        if working_sites:
            print(f"\n✅ WORKING CORRECTLY:")
            print("-" * 40)
            for site in working_sites:
                print(f"  - {site}")
        
        # Save report to file
        report_file = "validation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("SHERLOCK SITES VALIDATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total sites tested: {len(target_sites)}\n")
            f.write(f"Working correctly: {len(working_sites)}\n")
            f.write(f"Potentially problematic: {len(problematic_sites)}\n")
            f.write(f"Missing from manifest: {len(missing_sites)}\n")
            f.write(f"Errors during testing: {len(error_sites)}\n\n")
            
            if problematic_sites:
                f.write("POTENTIALLY PROBLEMATIC SITES:\n")
                f.write("-" * 40 + "\n")
                for site_name, analysis in problematic_sites:
                    f.write(f"\n{site_name}:\n")
                    f.write(f"  Confidence: {analysis.get('confidence', 'unknown')}\n")
                    for issue in analysis.get('issues', []):
                        f.write(f"  - {issue}\n")
                    for rec in analysis.get('recommendations', []):
                        f.write(f"  → {rec}\n")
        
        print(f"\nDetailed report saved to: {report_file}")
        
    except Exception as e:
        print(f"Error during validation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()