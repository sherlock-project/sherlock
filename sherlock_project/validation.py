"""Validation tools for detecting and fixing false positives in Sherlock sites"""

import requests
from typing import Dict, List, Optional
import secrets
import time

# Handle relative imports
try:
    from .result import QueryStatus
    from .sites import SitesInformation
except ImportError:
    # Fallback for direct execution or when running from sherlock_project directory
    from result import QueryStatus
    from sites import SitesInformation

class FalsePositiveDetector:
    def __init__(self, sites_info: SitesInformation):
        self.sites = sites_info
    
    def test_site_accuracy(self, site_name: str, test_usernames: Optional[List[str]] = None) -> Dict:
        """Test a specific site for false positive detection accuracy"""
        
        if site_name not in self.sites.sites:
            return {"error": f"Site {site_name} not found"}
        
        site = self.sites.sites[site_name]
        
        # Use provided test usernames or generate test cases
        if not test_usernames:
            test_usernames = [
                site.username_claimed,  
                secrets.token_urlsafe(16),  # Random unclaimed username
                "test_user_unlikely_to_exist_12345",  # Another unlikely username
                "nonexistentuser999999",  # Common pattern for testing
            ]
        
        results = {}
        
        for username in test_usernames:
            try:
                url = site.url_username_format.format(username)
                
                # Use similar headers as main Sherlock
                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
                }
                
                # Add site-specific headers if they exist
                if hasattr(site, 'information') and "headers" in site.information:
                    headers.update(site.information["headers"])
                
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                
                # Analyze based on detection method
                detection_method = site.information.get("errorType", "status_code")
                detected_status = self._analyze_response(response, site.information, detection_method)
                
                results[username] = {
                    "url": url,
                    "status_code": response.status_code,
                    "detected_as": detected_status.name if detected_status else "UNKNOWN",
                    "response_length": len(response.text),
                    "detection_method": detection_method,
                    "response_time": response.elapsed.total_seconds() if hasattr(response, 'elapsed') else None,
                    "final_url": response.url  # In case of redirects
                }
                
            except Exception as e:
                results[username] = {"error": str(e)}
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        return {
            "site": site_name,
            "url_format": site.url_username_format,
            "home_url": site.url_home,
            "detection_info": site.information.get("errorType", "unknown"),
            "tests": results,
            "analysis": self._analyze_results(results, site_name)
        }
    
    def _analyze_response(self, response, site_info, detection_method):
        """Analyze response based on site's detection method"""
        
        if detection_method == "status_code":
            error_codes = site_info.get("errorCode", [404])
            if isinstance(error_codes, int):
                error_codes = [error_codes]
            
            if response.status_code in error_codes:
                return QueryStatus.AVAILABLE
            elif 200 <= response.status_code < 300:
                return QueryStatus.CLAIMED
            else:
                return QueryStatus.UNKNOWN
                
        elif detection_method == "message":
            error_msgs = site_info.get("errorMsg", [])
            if isinstance(error_msgs, str):
                error_msgs = [error_msgs]
            
            for error_msg in error_msgs:
                if error_msg in response.text:
                    return QueryStatus.AVAILABLE
            
            return QueryStatus.CLAIMED
            
        elif detection_method == "response_url":
            # Check if we were redirected (indicates username not found)
            if response.url != response.request.url:
                return QueryStatus.AVAILABLE
            elif 200 <= response.status_code < 300:
                return QueryStatus.CLAIMED
            else:
                return QueryStatus.AVAILABLE
        
        return QueryStatus.UNKNOWN
    
    def _analyze_results(self, results, site_name):
        """Analyze test results for potential false positives"""
        analysis = {
            "potential_false_positive": False,
            "issues": [],
            "recommendations": [],
            "confidence": "unknown"
        }
        
        # Filter out error results
        valid_results = {k: v for k, v in results.items() if "error" not in v}
        
        if len(valid_results) < 2:
            analysis["issues"].append("Insufficient valid test results")
            return analysis
        
        # Check if all usernames return the same detection status
        statuses = [r.get("detected_as") for r in valid_results.values()]
        unique_statuses = set(statuses)
        
        if len(unique_statuses) == 1:
            analysis["potential_false_positive"] = True
            analysis["issues"].append(f"All test usernames returned the same status: {statuses[0]}")
            analysis["confidence"] = "high"
        
        # Check for suspicious patterns
        status_codes = [r.get("status_code") for r in valid_results.values()]
        
        # All requests return error codes
        if all(code >= 400 for code in status_codes):
            analysis["issues"].append("All requests returned HTTP error codes (>=400)")
            analysis["recommendations"].append("Site may be blocking requests or have changed structure")
        
        # All requests return same status code
        if len(set(status_codes)) == 1:
            analysis["issues"].append(f"All requests returned the same HTTP status code: {status_codes[0]}")
        
        # Check response lengths (too similar might indicate same error page)
        response_lengths = [r.get("response_length", 0) for r in valid_results.values()]
        if len(set(response_lengths)) == 1 and response_lengths[0] > 0:
            analysis["issues"].append("All responses have identical length (possible error page)")
        
        # Set confidence level
        if not analysis["issues"]:
            analysis["confidence"] = "good"
        elif len(analysis["issues"]) == 1:
            analysis["confidence"] = "medium"
        else:
            analysis["confidence"] = "low"
        
        return analysis

    def test_specific_sites(self, site_names: List[str]) -> Dict:
        """Test specific sites from the provided list"""
        results = {}
        
        print(f"Testing {len(site_names)} sites for false positive detection...")
        
        for i, site_name in enumerate(site_names, 1):
            print(f"[{i}/{len(site_names)}] Testing {site_name}...")
            
            if site_name in self.sites.sites:
                results[site_name] = self.test_site_accuracy(site_name)
            else:
                results[site_name] = {"error": f"Site {site_name} not found in manifest"}
            
            # Small delay between sites
            time.sleep(1)
        
        return results

    def test_excluded_sites(self) -> Dict:
        """Test sites that are currently in the exclusions list"""
        try:
            from sherlock_project.sites import EXCLUSIONS_URL
        except ImportError:
            from sites import EXCLUSIONS_URL
        
        try:
            print("Fetching exclusions list...")
            response = requests.get(EXCLUSIONS_URL)
            if response.status_code != 200:
                return {"error": f"Could not fetch exclusions list (HTTP {response.status_code})"}
            
            excluded_sites = [site.strip() for site in response.text.splitlines() if site.strip()]
            print(f"Found {len(excluded_sites)} sites in exclusions list")
            
            if not excluded_sites:
                return {"error": "No sites found in exclusions list"}
            
            # Filter to only test sites that exist in our manifest
            available_excluded_sites = [site for site in excluded_sites if site in self.sites.sites]
            missing_sites = [site for site in excluded_sites if site not in self.sites.sites]
            
            print(f"Testing {len(available_excluded_sites)} excluded sites that exist in manifest")
            if missing_sites:
                print(f"Note: {len(missing_sites)} excluded sites not found in current manifest")
            
            results = {}
            for i, site_name in enumerate(available_excluded_sites, 1):
                print(f"[{i}/{len(available_excluded_sites)}] Testing excluded site: {site_name}...")
                results[site_name] = self.test_site_accuracy(site_name)
                time.sleep(0.5)  # Be respectful to servers
            
            return {
                "excluded_sites_tested": results,
                "total_excluded": len(excluded_sites),
                "tested_count": len(available_excluded_sites),
                "missing_from_manifest": missing_sites
            }
            
        except Exception as e:
            return {"error": f"Error testing excluded sites: {str(e)}"}

    def generate_report(self, results: Dict) -> str:
        """Generate a formatted report from validation results"""
        report = []
        report.append("=" * 60)
        report.append("SHERLOCK FALSE POSITIVE VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        problematic_sites = []
        working_sites = []
        error_sites = []
        
        for site_name, result in results.items():
            if "error" in result:
                error_sites.append(site_name)
            elif result.get("analysis", {}).get("potential_false_positive"):
                problematic_sites.append((site_name, result))
            else:
                working_sites.append(site_name)
        
        # Summary
        report.append(f"SUMMARY:")
        report.append(f"  Total sites tested: {len(results)}")
        report.append(f"  Working correctly: {len(working_sites)}")
        report.append(f"  Potentially problematic: {len(problematic_sites)}")
        report.append(f"  Errors during testing: {len(error_sites)}")
        report.append("")
        
        # Problematic sites details
        if problematic_sites:
            report.append("POTENTIALLY PROBLEMATIC SITES:")
            report.append("-" * 40)
            for site_name, result in problematic_sites:
                report.append(f"\n{site_name}:")
                report.append(f"  URL Format: {result.get('url_format', 'N/A')}")
                report.append(f"  Detection Method: {result.get('detection_info', 'N/A')}")
                
                analysis = result.get("analysis", {})
                report.append(f"  Confidence: {analysis.get('confidence', 'unknown')}")
                
                issues = analysis.get("issues", [])
                if issues:
                    report.append("  Issues:")
                    for issue in issues:
                        report.append(f"    - {issue}")
                
                recommendations = analysis.get("recommendations", [])
                if recommendations:
                    report.append("  Recommendations:")
                    for rec in recommendations:
                        report.append(f"    - {rec}")
        
        # Error sites
        if error_sites:
            report.append(f"\nSITES WITH ERRORS:")
            report.append("-" * 40)
            for site_name in error_sites:
                error_msg = results[site_name].get("error", "Unknown error")
                report.append(f"  {site_name}: {error_msg}")
        
        # Working sites
        if working_sites:
            report.append(f"\nWORKING SITES:")
            report.append("-" * 40)
            report.append(f"  {', '.join(working_sites)}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)