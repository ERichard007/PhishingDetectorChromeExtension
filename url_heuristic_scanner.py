from urllib.parse import urlsplit, unquote, parse_qs

from urlextract import URLExtract

import pandas as pd

import math
import requests
import ipaddress
import re

#Also scan PhishTank Database for urls to check if they are known or active.

#Information retrieved from https://www.spamhaus.org/reputation-statistics/cctlds/phishing/
# "<tld>" : bad repuation score
malicious_tlds = {
    "vu": 0.3,
    "cc": 0.3,
    "cn": 0.2,
    "to": 0.2,
    "ac": 0.1,
    "pw": 0.0599,
    "su": 0.0552,
    "ru": 0.0511,
    "cv": 0.041,
    "io": 0.0379,

    "us": 0.0315,
    "my": 0.0271,
    "co": 0.0234,
    "me": 0.0184,
    "id": 0.0135,
    "ng": 0.0128,
    "hk": 0.0125,
    "tv": 0.0117,
    "tr": 0.0087,
    "mx": 0.0076,

    "ua": 0.0071,
    "at": 0.0070,
    "es": 0.0069,
    "ai": 0.0063,
    "de": 0.0057,
    "in": 0.0051,
    "pl": 0.0044,
    "eu": 0.0036,
    "uk": 0.0035,
    "za": 0.0033,

    "br": 0.0027,
    "fr": 0.0027,
    "ca": 0.0025,
    "jp": 0.0018,
    "au": 0.0016,
    "nl": 0.0013,
    "it": 0.0013
}

malicious_schemes = {
    "http": 0.15,
    "mailto": .25,
    "ftp": .25,
    "intent": .5,
    "file": .75,
    "data": .75,
    "javascript": 1
}

malicious_keywords = [
        "login", "signin", "sign-in", "verify", "verification",
        "secure", "account", "update", "confirm", "password",
        "auth", "wallet"
    ]

#From https://www.statista.com/chart/22528/most-impersonated-brands-in-phishing-attacks/?srsltid=AfmBOooh6rbeEbDOMXgzfTbKnkkSdm0aChOtlKERSVcYqQhkh9BlXB4t
# And https://schneiderdowns.com/our-thoughts-on/phishings-favorite-brands-the-most-spoofed-companies-in-q4-2025/
impersonated_brands = [
    "paypal", "apple", "google", "amazon", "microsoft",
    "facebook", "netflix", "bankofamerica", "wellsfargo",
    "chase", "linkedin", "dropbox", "icloud", "ebay",
    "twitter", "instagram", "yahoo", "adobe", "meta",
    "booking", "dhl"
]

# From https://success.trendmicro.com/en-US/solution/KA-0003909
malicious_extensions = {
    ".exe": 0.5,
    ".scr": 0.5,
    ".vbs": 0.5,

    ".pdf": 0.25,
    ".doc": 0.25,
    ".xls": 0.25,
    ".rtf": 0.25,

    ".jpeg": 0.15,
    ".zip": 0.3
}

# From https://isc.sans.edu/diary/Open+Redirects+A+Forgotten+Vulnerability/32742
redirect_indicators = [
    "redirect",
    "url",
    "next",
    "return",
    "dest",
    "continue",
    "goto",
    "redir",
    "forward",
    "away",
    "jump"
]

cred_keys = [
    "user", "username", "email", "password", 
    "pass", "login", "token", "auth"
]

class url_scanner:
    """
    A class that scans URLs for potential phishing indicators based on heuristics.
    Args:
        urls (list): A list of URLs to be scanned.
    Returns:
        dict: Dictionary containing scan results and associated scores along with a final threat score.
    """

    def __init__(self, urls : list):
        self.final_results = {}
        self.final_score = 0.0

        self.scan_results = {}
        self.score = 0.0

        for i, url in enumerate(urls):
            self._scan_url(i, url)
            self._phish_tank_scan(i, url)

        self.final_results["overall_threat_score"] = (1 / (1 + math.exp(-self.final_score)))
        self.final_results["overall_threat_level"] = "High" if self.final_score >= 2 else "Medium" if self.final_score >= 1 else "Low" if self.final_score >= 0.5 else "None"    

    def _scan_url(self, index : int, url : str) -> dict:
        """
        Private method that scans a single URL for potential phishing indicators based on heuristics.
        Args:
            index (int): The index of the URL in the input list.
            url (str): The URL to be scanned.
        """

        self.scan_results = {}
        self.score = 0.0

        split_url = urlsplit(url)
        #print(split_url)

        self.scan_results["url"] = url

        self._scheme_scan(split_url.scheme)
        self._authority_scan(split_url.netloc)
        self._path_scan(split_url.path)
        self._query_scan(split_url.query)
        self._fragment_scan(split_url.fragment)

        self.scan_results["url_score"] = self.score
        self.scan_results["url_threat_level"] = "High" if self.score >= 1.5 else "Medium" if self.score >= 0.75 else "Low" if self.score >= 0.25 else "None"

        self.final_results[f"URL_{index+1}"] = self.scan_results
        self.final_score += self.score

    def _scheme_scan(self, scheme : str) -> float:
        """
        Private method that checks the scheme of the URL and assigns a score based on its security.
        Args:
            scheme (str): The scheme of the URL (e.g., "http", "https").
        """
        
        if scheme in malicious_schemes:
            score = malicious_schemes[scheme]
            self.scan_results['scheme'] = {"scheme": scheme, "score": score, "reason": f"{scheme} deemed possibly malicious based on known phishing schemes"}
            self.score += score
        else:
            score = 0
            self.scan_results['scheme'] = {"scheme": scheme, "score": score, "reason": f"{scheme} not found in known phishing schemes, considered relatively safe"}

    def _authority_scan(self, authority : str) -> float:
        """
        Private method that checks the authority (domain), looks for suspicious: @ symbol, ports, ip, tlds, subdomains, hyphens, numerics, length, punycode
        Args:
            authority (str): The authority (domain) of the URL (e.g., "example.com").
        """

        score = 0
        reasons = []

        if '@' in authority:
            score += 1
            reasons.append("Authority contains '@' symbol, possible obfuscation of true domain")

        host = authority.split('@')[-1]

        if ':' in host:
            port = host.split(':')
            if len(port) == 2 and port[1].isdigit():
                port_num = int(port[1])
                if port_num not in [80, 443]:
                    score += 0.3
                    reasons.append(f"Authority contains non-standard port {port_num}")

                host = port[0]

        try:
            ipaddress.ip_address(host)
            score += 0.8
            reasons.append("Authority is an IP address")
        except:
            pass

        tld = host.split('.')[-1]

        if tld in malicious_tlds:
            score += malicious_tlds[tld]
            reasons.append(f"Authority has TLD '{tld}' with bad phishing reputation score of {malicious_tlds[tld]}")
        
        domain_count = host.count('.')
        if domain_count >= 3:
            score += 0.3
            reasons.append(f"Authority has {domain_count} subdomains, possible domain obfuscation attempt")

        if '-' in host:
            score += 0.2
            reasons.append("Authority contains hyphen, possible domain impersonation attempt")

        numeric_count = sum(c.isdigit() for c in host) / len(host)
        if numeric_count > 0.4:
            score += 0.2
            reasons.append(f"Authority has high numeric character ratio of {numeric_count:.2f}, possible obfuscation attempt")

        if len(host) > 75:
            score += 0.2
            reasons.append(f"Authority length of {len(host)} is unusually long, possible obfuscation attempt")

        self.scan_results["authority"] = {
            "authority": authority,
            "host": host,
            "score": score,
            "reasons": reasons if reasons else ["Authority does not exhibit common phishing indicators, considered relatively safe"]
        }

        self.score += score

    def _path_scan(self, path : str) -> float:
        """
        Private method that checks the path of the URL for potential phishing indicators such as excessive length, presence of suspicious keywords, or obfuscation techniques.
        Args:
            path (str): The path component of the URL (e.g., "/login").
        """

        score = 0.0
        reasons = []

        decoded_path = unquote(path.lower())

        for keyword in malicious_keywords:
            if keyword in decoded_path:
                score += 0.2
                reasons.append(f"Path contains suspicious keyword '{keyword}'")

        for brand in impersonated_brands:
            if brand in decoded_path:
                score += 0.2
                reasons.append(f"Path contains impersonated brand name '{brand}'")

        length = len([p for p in decoded_path.split('/') if p.strip() != ''])
        if length > 5:
            score += 0.2
            reasons.append(f"Path has excessive length of {length} segments, possible obfuscation attempt")
        
        encoded_pattern = re.findall(r'%[0-9a-fA-F]{2}', path)
        if len(encoded_pattern) > 0:
            score += .1 * len(encoded_pattern)
            reasons.append(f"Path contains {len(encoded_pattern)} URL-encoded characters -> {encoded_pattern}")

        for ext in malicious_extensions:
            if ext in decoded_path:
                score += malicious_extensions[ext]
                reasons.append(f"Path contains suspicious file extension '{ext}' with phishing reputation score of {malicious_extensions[ext]}")

        if "//" in decoded_path:
            score += 0.2
            reasons.append("Path contains '//', possible obfucation")

        tokens = re.findall(r'[a-zA-Z0-9]{8,}', decoded_path)
        for t in tokens:
            if len(tokens) > 3:
                score += 0.1 * len(tokens)
                reasons.append(f"Path contains {len(tokens)} long alphanumeric tokens, possible obfuscation attempt -> {tokens}")
        
        self.scan_results["path"] = {
            "path": path,
            "decoded_path": decoded_path,
            "score": score,
            "reasons": reasons if reasons else ["Path does not exhibit common phishing indicators, considered relatively safe"]
        }

        self.score += score

    def _query_scan(self, query : str) -> float:
        """
        Private method that checks the query component of the URL for potential phishing indicators such as presence of suspicious keywords, excessive length, or obfuscation techniques.
        Args:
            query (str): The query component of the URL (e.g., "id=123&action=login").
        """

        score = 0.0
        reasons = []

        decoded_query = unquote(query.lower())
        params = parse_qs(decoded_query)

        for key in params:
            if key in redirect_indicators:
                score += 0.4
                reasons.append(f"Query contains potential open redirect parameter '{key}'")

                for value in params[key]:
                    extractor = URLExtract()
                    for url in extractor.gen_urls(value):
                        score += 0.4
                        reasons.append(f"Query parameter '{key}' contains URL '{url}', possible open redirect attempt")

            if key in cred_keys:
                score += 0.3
                reasons.append(f"Query contains potential credential harvesting parameter '{key}'")

            if key == "password" or key == "pass":
                score += 0.6
                reasons.append(f"Query contains parameter '{key}', password transferring in query critical risk")

            for value in params[key]:
                if len(value) > 20:
                    score += 0.1
                    reasons.append(f"Query parameter '{key}' has excessively long value of length {len(value)}, possible obfuscation attempt")
                
                ratio = sum(c.isdigit() for c in value) / len(value) if len(value) > 0 else 0
                if ratio > 0.5:
                    score += 0.1
                    reasons.append(f"Query parameter '{key}' has high numeric character ratio of {ratio:.2f}, possible obfuscation attempt")

        encoded_pattern = re.findall(r'%[0-9a-fA-F]{2}', query)
        if len(encoded_pattern) > 0:
            score += .1 * len(encoded_pattern)
            reasons.append(f"Query contains {len(encoded_pattern)} URL-encoded characters -> {encoded_pattern}")
        
        if len(params) > 3:
            score += 0.2
            reasons.append(f"Query has excessive number of parameters ({len(params)}), possible obfuscation attempt")

        self.scan_results["query"] = {
            "query": query,
            "decoded_query": decoded_query,
            "score": score,
            "reasons": reasons if reasons else ["Query does not exhibit common phishing indicators, considered relatively safe"]
        }

        self.score += score

    def _fragment_scan(self, fragment : str) -> float:
        """
        Private method that checks the fragment component of the URL for potential phishing indicators such as presence of suspicious keywords or obfuscation techniques.
        Args:
            fragment (str): The fragment component of the URL (e.g., "section1").
        """

        score = 0.0
        reasons = []

        decoded_fragment = unquote(fragment.lower())

        for word in malicious_keywords:
            if word in decoded_fragment:
                score += 0.2
                reasons.append(f"Fragment contains suspicious keyword '{word}'")

        extractor = URLExtract()
        for url in extractor.gen_urls(decoded_fragment):
            score += 0.7
            reasons.append(f"Fragment contains URL '{url}', possible obfuscation attempt")
        
        encoded_pattern = re.findall(r'%[0-9a-fA-F]{2}', fragment)
        if len(encoded_pattern) > 0:
            score += .1 * len(encoded_pattern)
            reasons.append(f"Fragment contains {len(encoded_pattern)} URL-encoded characters -> {encoded_pattern}")
        
        if decoded_fragment.startswith('/') or '#/' in decoded_fragment:
            score += 0.2
            reasons.append("Fragment contains path-like structure, possible obfuscation attempt")

        if len(decoded_fragment) > 50:
            score += 0.2
            reasons.append(f"Fragment length of {len(decoded_fragment)} is unusually long, possible obfuscation attempt")

        self.scan_results["fragment"] = {
            "fragment": fragment,
            "decoded_fragment": decoded_fragment,
            "score": score,
            "reasons": reasons if reasons else ["Fragment does not exhibit common phishing indicators, considered relatively safe"]
        }

        self.score += score

    def _phish_tank_scan(self, index : int, url : str) -> None:
        """
        Private method that checks the URL against the PhishTank database for known phishing URLs.
        Args:
            index (int): The index of the URL in the input list.
            url (str): The URL to be checked against the PhishTank database.
        """

        df = pd.read_csv("assets/cleaned_data/phish_tank.csv", usecols=['url'])

        phish_set = set(df["url"])

        if url in phish_set:
            self.final_score += 3
            self.final_results["Phish-Tank-Database"] = {
                "reason" : f"{url} was found in Phish-Tank-Database! Critical Risk!"
            }


#test_url = ["http://t-info.mail.adobe.com/r/?id=hc43f43t4a,afd67070,affc7349&p1=t.mid.accor-mail.com/r/?id=159593f159593159593,hde43e13b13,ecdfafef,ee5cfa06&p1=filepmgklf.com/cookie@gmail.com","https://andreas-feicht.emlnk.com/lt.php?x=4lZy~GE7JFnK6KB6-N~FVeZw2aAiutTxkxgxkXfLKqHKDaJAyEy7wOHcEu2i-QhojuVAXHMWJYGb6U"]
#scanner = url_scanner(test_url)
#print(scanner.final_results)

