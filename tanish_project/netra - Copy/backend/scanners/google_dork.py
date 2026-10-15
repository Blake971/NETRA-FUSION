import time
from typing import Dict, Any, List
from utils.logger import log_module_start, log_module_complete, setup_logger


def scan_google_dorks(domain: str) -> Dict[str, Any]:
    """
    Generate useful Google Dork queries for OSINT reconnaissance.

    This module ONLY generates queries - it never executes searches or scrapes Google.

    Args:
        domain: Domain to generate queries for

    Returns:
        Standardized JSON response with Google Dork queries
    """
    logger = setup_logger()
    start_time = time.time()

    log_module_start(logger, "GOOGLE_DORK", domain)

    queries: List[Dict[str, str]] = [
        {
            "query": f"site:{domain}",
            "description": "List all indexed pages for this domain",
            "purpose": "Discover what pages Google knows about",
            "category": "General"
        },
        {
            "query": f"site:{domain} filetype:pdf",
            "description": "Find PDF documents exposed by the domain",
            "purpose": "Discover publicly accessible documents",
            "category": "Files"
        },
        {
            "query": f"site:{domain} filetype:xls OR filetype:xlsx OR filetype:doc OR filetype:docx",
            "description": "Find office documents (Excel, Word)",
            "purpose": "Discover potentially sensitive business documents",
            "category": "Files"
        },
        {
            "query": f"site:{domain} inurl:login OR inurl:admin OR inurl:dashboard",
            "description": "Find login and admin pages",
            "purpose": "Identify authentication entry points",
            "category": "Sensitive Pages"
        },
        {
            "query": f'site:{domain} intitle:"index of"',
            "description": "Find open directory listings",
            "purpose": "Discover directories with file listing enabled",
            "category": "Sensitive Pages"
        },
        {
            "query": f"site:{domain} inurl:wp-content OR inurl:wp-includes",
            "description": "Detect WordPress installation paths",
            "purpose": "Identify CMS technology and plugin paths",
            "category": "Technology"
        },
        {
            "query": f'site:{domain} "password" OR "secret" OR "api_key" OR "token"',
            "description": "Search for accidentally exposed secrets",
            "purpose": "Find potentially leaked sensitive information",
            "category": "Sensitive Data"
        },
        {
            "query": f"site:{domain} ext:sql OR ext:bak OR ext:env OR ext:log",
            "description": "Find backup and log files",
            "purpose": "Discover accidentally exposed database dumps or config files",
            "category": "Sensitive Data"
        },
        {
            "query": f"site:github.com {domain}",
            "description": "Search GitHub for domain references",
            "purpose": "Find code repositories that mention this domain",
            "category": "Third Party"
        },
        {
            "query": f"site:pastebin.com {domain}",
            "description": "Search Pastebin for domain mentions",
            "purpose": "Check for pasted content referencing this domain",
            "category": "Third Party"
        },
        {
            "query": f'site:{domain} intitle:"error" OR "exception" OR "stack trace"',
            "description": "Find exposed error pages",
            "purpose": "Discover error pages that may leak internal information",
            "category": "Sensitive Data"
        },
        {
            "query": f"site:{domain} inurl:phpinfo OR inurl:test OR inurl:debug",
            "description": "Find debug and test pages",
            "purpose": "Discover development artifacts left in production",
            "category": "Sensitive Pages"
        },
    ]

    execution_time = time.time() - start_time
    log_module_complete(logger, "GOOGLE_DORK", domain, execution_time)

    return {
        "module": "GOOGLE_DORK",
        "status": "SUCCESS",
        "severity": "INFO",
        "message": f"Generated {len(queries)} Google Dork queries for {domain}",
        "execution_time": f"{execution_time:.2f}",
        "confidence": 100,
        "data": {
            "domain": domain,
            "total_queries": len(queries),
            "queries": queries,
            "disclaimer": "These queries are for educational and defensive security purposes only. Use responsibly."
        }
    }


def scan_person_dorks(
    name: str,
    username: str = "",
    location: str = "",
    employer: str = ""
) -> Dict[str, Any]:
    """
    Generate Google Dork queries to discover a person's public social profiles
    and online footprint from their name (plus optional username/location/employer).

    Like scan_google_dorks, this ONLY generates query strings - it never executes
    searches, scrapes any site, or collects personal data itself. The user copies
    the queries and runs them manually in a search engine.

    Args:
        name: Person's full name (required)
        username: Optional online handle/username to pivot on
        location: Optional city/region to narrow results
        employer: Optional company/organisation to narrow results

    Returns:
        Standardized JSON response with person-focused Google Dork queries
    """
    logger = setup_logger()
    start_time = time.time()

    name = (name or "").strip()
    username = (username or "").strip()
    location = (location or "").strip()
    employer = (employer or "").strip()

    log_module_start(logger, "PERSON_DORK", name or "(empty)")

    if not name:
        execution_time = time.time() - start_time
        return {
            "module": "PERSON_DORK",
            "status": "FAILED",
            "severity": "ERROR",
            "message": "A person name is required",
            "execution_time": f"{execution_time:.2f}",
            "confidence": 0,
            "data": {"queries": [], "reason": "empty_name"}
        }

    q = f'"{name}"'  # quoted phrase for exact-name matching
    queries: List[Dict[str, str]] = []

    # ── Professional & developer networks ──
    queries.append({
        "query": f'{q} site:linkedin.com/in',
        "description": "Find LinkedIn profile pages for this name",
        "purpose": "Locate professional profile and work history",
        "category": "Professional"
    })
    queries.append({
        "query": f'{q} site:github.com',
        "description": "Find GitHub accounts or contributions mentioning this name",
        "purpose": "Discover developer identity and repositories",
        "category": "Professional"
    })
    queries.append({
        "query": f'{q} site:gitlab.com OR site:bitbucket.org',
        "description": "Find GitLab and Bitbucket developer profiles",
        "purpose": "Discover additional source-code hosting identities",
        "category": "Professional"
    })
    queries.append({
        "query": f'{q} site:stackoverflow.com OR site:stackexchange.com',
        "description": "Find Stack Overflow / Stack Exchange contributions",
        "purpose": "Locate Q&A activity and technical reputation",
        "category": "Professional"
    })
    queries.append({
        "query": f'{q} site:dev.to OR site:hashnode.dev',
        "description": "Find developer blog profiles and articles",
        "purpose": "Discover technical writing under the person's name",
        "category": "Professional"
    })
    queries.append({
        "query": f'{q} site:kaggle.com',
        "description": "Find Kaggle data-science profiles",
        "purpose": "Locate data-science / ML competition identity",
        "category": "Professional"
    })
    queries.append({
        "query": f'{q} site:behance.net OR site:dribbble.com',
        "description": "Find Behance / Dribbble design portfolios",
        "purpose": "Discover creative and design portfolios",
        "category": "Professional"
    })

    # ── Social platforms ──
    queries.append({
        "query": f'{q} site:twitter.com OR site:x.com',
        "description": "Find X (Twitter) profiles and posts",
        "purpose": "Locate microblog presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:facebook.com',
        "description": "Find Facebook profiles or public pages",
        "purpose": "Locate social network presence (often login-gated)",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:instagram.com',
        "description": "Find Instagram profiles",
        "purpose": "Locate photo/social presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:reddit.com',
        "description": "Find Reddit usernames, posts, or comments",
        "purpose": "Discover forum activity tied to the name",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:youtube.com OR site:tiktok.com',
        "description": "Find video-platform channels and content",
        "purpose": "Locate video/social presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:pinterest.com',
        "description": "Find Pinterest profiles and boards",
        "purpose": "Discover interest-based social presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:tumblr.com',
        "description": "Find Tumblr blogs and posts",
        "purpose": "Locate blog-style social presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:twitch.tv',
        "description": "Find Twitch streaming channels",
        "purpose": "Discover live-streaming presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:vimeo.com OR site:flickr.com',
        "description": "Find Vimeo videos and Flickr photo accounts",
        "purpose": "Locate video and photo-sharing presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:threads.net OR site:bsky.app',
        "description": "Find Threads and Bluesky profiles",
        "purpose": "Discover newer microblog platform presence",
        "category": "Social Profiles"
    })
    queries.append({
        "query": f'{q} site:t.me OR site:telegram.me',
        "description": "Find public Telegram channels or profiles",
        "purpose": "Locate messaging-platform public presence",
        "category": "Social Profiles"
    })

    # ── Academic & research ──
    queries.append({
        "query": f'{q} site:scholar.google.com',
        "description": "Find Google Scholar author profiles and papers",
        "purpose": "Discover academic publications and citations",
        "category": "Academic & Research"
    })
    queries.append({
        "query": f'{q} site:researchgate.net OR site:academia.edu',
        "description": "Find ResearchGate / Academia.edu profiles",
        "purpose": "Locate researcher profiles and publications",
        "category": "Academic & Research"
    })
    queries.append({
        "query": f'{q} site:orcid.org',
        "description": "Find ORCID researcher identifiers",
        "purpose": "Confirm academic identity via ORCID iD",
        "category": "Academic & Research"
    })
    queries.append({
        "query": f'{q} site:.edu',
        "description": "Find university / institutional pages (.edu)",
        "purpose": "Discover faculty, staff, or student directory listings",
        "category": "Academic & Research"
    })

    # ── Business & directories ──
    queries.append({
        "query": f'{q} site:crunchbase.com',
        "description": "Find Crunchbase founder / executive profiles",
        "purpose": "Discover business and funding relationships",
        "category": "Business"
    })
    queries.append({
        "query": f'{q} site:wellfound.com OR site:angel.co',
        "description": "Find Wellfound (AngelList) startup profiles",
        "purpose": "Locate entrepreneur / startup-team identity",
        "category": "Business"
    })
    queries.append({
        "query": f'{q} (intext:"CEO" OR intext:"founder" OR intext:"co-founder" OR intext:"director")',
        "description": "Find pages describing a leadership role",
        "purpose": "Surface executive bios and role mentions",
        "category": "Business"
    })

    # ── Forums, Q&A & wikis ──
    queries.append({
        "query": f'{q} site:quora.com',
        "description": "Find Quora profiles, answers, and questions",
        "purpose": "Discover Q&A activity and stated expertise",
        "category": "Forums & Q&A"
    })
    queries.append({
        "query": f'{q} site:news.ycombinator.com',
        "description": "Find Hacker News profiles and comments",
        "purpose": "Locate tech-community activity",
        "category": "Forums & Q&A"
    })
    queries.append({
        "query": f'{q} site:wikipedia.org OR site:wikidata.org',
        "description": "Find Wikipedia / Wikidata entries",
        "purpose": "Discover notable-person encyclopedia records",
        "category": "Forums & Q&A"
    })

    # ── Personal sites & profile aggregators ──
    queries.append({
        "query": f'intitle:{q}',
        "description": "Find pages with the exact name in the title",
        "purpose": "Surface personal websites and profile pages",
        "category": "Personal Sites"
    })
    queries.append({
        "query": f'{q} inurl:profile OR inurl:about OR inurl:bio OR inurl:author',
        "description": "Find profile/about/bio pages referencing the name",
        "purpose": "Locate personal or author bios",
        "category": "Personal Sites"
    })
    queries.append({
        "query": f'{q} site:about.me OR site:gravatar.com OR site:keybase.io OR site:medium.com',
        "description": "Search common profile aggregators and blogging platforms",
        "purpose": "Discover consolidated online identity pages",
        "category": "Personal Sites"
    })

    # ── News & media mentions ──
    queries.append({
        "query": f'{q} (inurl:news OR inurl:press OR inurl:media OR inurl:article OR inurl:blog)',
        "description": "Find news, press, and article mentions",
        "purpose": "Surface media coverage referencing the person",
        "category": "News & Mentions"
    })
    queries.append({
        "query": f'{q} (intext:"interview" OR intext:"speaks at" OR intext:"conference" OR intext:"podcast")',
        "description": "Find talks, interviews, and appearances",
        "purpose": "Discover public speaking and media appearances",
        "category": "News & Mentions"
    })

    # ── Documents ──
    queries.append({
        "query": f'{q} filetype:pdf resume OR cv OR "curriculum vitae"',
        "description": "Find publicly exposed resumes or CVs",
        "purpose": "Discover career documents left publicly indexed",
        "category": "Documents"
    })
    queries.append({
        "query": f'{q} filetype:doc OR filetype:docx resume OR cv',
        "description": "Find resume/CV files in Word format",
        "purpose": "Discover editable career documents indexed publicly",
        "category": "Documents"
    })
    queries.append({
        "query": f'{q} filetype:ppt OR filetype:pptx OR site:slideshare.net OR site:speakerdeck.com',
        "description": "Find presentations and slide decks",
        "purpose": "Discover conference talks and authored decks",
        "category": "Documents"
    })

    # ── Contact exposure (defensive) ──
    queries.append({
        "query": f'{q} intext:"@" (intext:"email" OR intext:"contact" OR intext:"phone")',
        "description": "Find pages that may expose contact details",
        "purpose": "Identify accidental exposure of personal contact info",
        "category": "Contact Exposure"
    })
    queries.append({
        "query": f'{q} (intext:"phone" OR intext:"mobile" OR intext:"address" OR intext:"email me")',
        "description": "Find pages listing phone numbers or addresses",
        "purpose": "Detect personal contact data leaked in public pages",
        "category": "Contact Exposure"
    })

    # ── Leaked / paste sites (defensive) ──
    queries.append({
        "query": f'{q} site:pastebin.com OR site:justpaste.it OR site:controlc.com',
        "description": "Find paste-site content mentioning the name",
        "purpose": "Check for leaked lists or dumped data referencing the person",
        "category": "Leaked Data"
    })
    queries.append({
        "query": f'{q} site:gist.github.com',
        "description": "Find GitHub Gists mentioning the name",
        "purpose": "Discover code/text snippets tied to the person",
        "category": "Leaked Data"
    })

    # ── Username pivots (only when provided) ──
    if username:
        u = f'"{username}"'
        queries.append({
            "query": f'{u} site:linkedin.com OR site:twitter.com OR site:x.com OR site:instagram.com OR site:github.com',
            "description": "Search the username/handle across major platforms",
            "purpose": "Pivot from a known handle to linked profiles",
            "category": "Username"
        })
        queries.append({
            "query": f'{u} site:reddit.com OR site:twitch.tv OR site:tumblr.com OR site:pinterest.com OR site:youtube.com',
            "description": "Search the handle across social and community platforms",
            "purpose": "Extend the handle pivot to more networks",
            "category": "Username"
        })
        queries.append({
            "query": f'{q} {u}',
            "description": "Find pages containing both the name and the username",
            "purpose": "Correlate the real name with the online handle",
            "category": "Username"
        })
        queries.append({
            "query": f'intext:{u} inurl:profile OR inurl:user OR inurl:author OR inurl:members',
            "description": "Find profile/user pages built around the handle",
            "purpose": "Discover accounts tied to the username",
            "category": "Username"
        })

    # ── Location narrowing (only when provided) ──
    if location:
        loc = f'"{location}"'
        queries.append({
            "query": f'{q} {loc} site:linkedin.com/in',
            "description": "Find LinkedIn profiles matching the name and location",
            "purpose": "Disambiguate common names by geography",
            "category": "Location"
        })
        queries.append({
            "query": f'{q} {loc} (site:facebook.com OR site:instagram.com OR site:twitter.com)',
            "description": "Find social profiles matching name and location",
            "purpose": "Narrow social results by geography",
            "category": "Location"
        })
        queries.append({
            "query": f'{q} {loc}',
            "description": "General search combining the name and location",
            "purpose": "Narrow results to a specific city or region",
            "category": "Location"
        })

    # ── Employer narrowing (only when provided) ──
    if employer:
        emp = f'"{employer}"'
        queries.append({
            "query": f'{q} {emp} site:linkedin.com/in',
            "description": "Find LinkedIn profiles matching the name and employer",
            "purpose": "Confirm identity via workplace",
            "category": "Employer"
        })
        queries.append({
            "query": f'{q} ({emp}) ("works at" OR "employee" OR "staff" OR "team")',
            "description": "Find pages linking the person to the organisation",
            "purpose": "Surface team pages, bios, and announcements",
            "category": "Employer"
        })
        queries.append({
            "query": f'{q} {emp} (filetype:pdf OR site:.edu OR site:.gov)',
            "description": "Find documents or institutional pages tying name to employer",
            "purpose": "Discover papers, reports, or directory listings",
            "category": "Employer"
        })

    execution_time = time.time() - start_time
    log_module_complete(logger, "PERSON_DORK", name, execution_time)

    return {
        "module": "PERSON_DORK",
        "status": "SUCCESS",
        "severity": "INFO",
        "message": f"Generated {len(queries)} person-focused Google Dork queries for {name}",
        "execution_time": f"{execution_time:.2f}",
        "confidence": 100,
        "data": {
            "name": name,
            "username": username,
            "location": location,
            "employer": employer,
            "total_queries": len(queries),
            "queries": queries,
            "disclaimer": (
                "These queries target publicly indexed information about a person. "
                "Use responsibly, respect privacy, and comply with applicable laws and "
                "platform terms of service. NETRA generates queries only - it does not "
                "execute searches, scrape sites, or collect personal data."
            )
        }
    }
