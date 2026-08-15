import json
import urllib.request
import urllib.error
from html import escape
from datetime import datetime, timezone


# ============================================================
# CONFIGURATION
# ============================================================

USERNAME = "Ayushivam22"
OUTPUT_FILE = "leetcode-stats.svg"

API_URL = "https://leetcode.com/graphql/"


# ============================================================
# LEETCODE GRAPHQL QUERY
# ============================================================

QUERY = """
query getUserProfile($username: String!) {

  matchedUser(username: $username) {

    username

    profile {
      realName
      ranking
    }

    submitStats: submitStatsGlobal {

      acSubmissionNum {
        difficulty
        count
        submissions
      }

    }

    badges {
      id
      name
      displayName
      icon
      creationDate
    }

  }

  userContestRanking(username: $username) {

    attendedContestsCount
    rating
    globalRanking
    totalParticipants
    topPercentage

  }

}
"""


# ============================================================
# FETCH DATA
# ============================================================

def fetch_leetcode_data(username):

    payload = {
        "query": QUERY,
        "variables": {
            "username": username
        }
    }

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/142.0 Safari/537.36"
            ),
            "Referer": "https://leetcode.com/",
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as error:

        print(
            f"LeetCode HTTP error: "
            f"{error.code} {error.reason}"
        )

        raise

    except urllib.error.URLError as error:

        print(
            f"Connection error: {error.reason}"
        )

        raise

    if result.get("errors"):

        print("GraphQL errors:")

        for error in result["errors"]:
            print(error)

        raise RuntimeError(
            "LeetCode GraphQL request failed"
        )

    return result["data"]


# ============================================================
# PROCESS DATA
# ============================================================

def process_stats(data):

    user = data.get("matchedUser")

    if not user:

        raise RuntimeError(
            f"User '{USERNAME}' not found."
        )

    profile = user.get("profile") or {}

    submit_stats = (
        user.get("submitStats")
        or {}
    )

    submissions = (
        submit_stats.get(
            "acSubmissionNum"
        )
        or []
    )

    stats = {
        "all": 0,
        "easy": 0,
        "medium": 0,
        "hard": 0,
    }

    for item in submissions:

        difficulty = (
            item.get("difficulty")
            or ""
        ).lower()

        count = item.get(
            "count",
            0
        )

        if difficulty == "all":
            stats["all"] = count

        elif difficulty == "easy":
            stats["easy"] = count

        elif difficulty == "medium":
            stats["medium"] = count

        elif difficulty == "hard":
            stats["hard"] = count

    contest = (
        data.get("userContestRanking")
        or {}
    )

    # --------------------------------------------------------
    # Find Knight badge specifically
    # --------------------------------------------------------

    badges = user.get("badges") or []

    knight_badge = "Not Earned"

    for badge in badges:

        name = (
            badge.get("name")
            or ""
        ).strip().lower()

        display_name = (
            badge.get("displayName")
            or ""
        ).strip().lower()

        if (
            name == "knight"
            or display_name == "knight"
            or "knight" in name
            or "knight" in display_name
        ):
            knight_badge = (
                badge.get("displayName")
                or badge.get("name")
                or "Knight"
            )

            knight_badge = knight_badge.replace(
                " Badge",
                ""
            )

            break

    return {

        "username":
            user.get(
                "username",
                USERNAME
            ),

        "solved":
            stats["all"],

        "easy":
            stats["easy"],

        "medium":
            stats["medium"],

        "hard":
            stats["hard"],

        "rating":
            contest.get("rating"),

        "global_ranking":
            contest.get(
                "globalRanking"
            ),

        "top_percentage":
            contest.get(
                "topPercentage"
            ),

        "contests":
            contest.get(
                "attendedContestsCount"
            ),

        "knight_badge":
            knight_badge,
    }


# ============================================================
# FORMATTERS
# ============================================================

def number(value):

    if value is None:
        return "—"

    try:
        return f"{int(value):,}"

    except:
        return str(value)


def rating(value):

    if value is None:
        return "—"

    try:
        return f"{float(value):.0f}"

    except:
        return str(value)


def percentage(value):

    if value is None:
        return "—"

    try:
        return f"{float(value):.1f}%"

    except:
        return str(value)


# ============================================================
# SVG ICONS
# ============================================================

def rating_icon(x, y):

    return f"""
    <g transform="translate({x},{y})">

        <rect
            x="0"
            y="0"
            width="80"
            height="80"
            rx="14"
            fill="#111c2d"
            stroke="#26374d"
            stroke-width="2"/>

        <path
            d="
            M18 55
            L30 43
            L39 49
            L61 25
            "
            fill="none"
            stroke="#9b7cff"
            stroke-width="6"
            stroke-linecap="round"
            stroke-linejoin="round"/>

        <path
            d="
            M50 25
            H61
            V36
            "
            fill="none"
            stroke="#9b7cff"
            stroke-width="6"
            stroke-linecap="round"
            stroke-linejoin="round"/>

    </g>
    """


def globe_icon(x, y):

    return f"""
    <g transform="translate({x},{y})">

        <rect
            x="0"
            y="0"
            width="80"
            height="80"
            rx="14"
            fill="#111c2d"
            stroke="#26374d"
            stroke-width="2"/>

        <circle
            cx="40"
            cy="40"
            r="27"
            fill="none"
            stroke="#3296ff"
            stroke-width="5"/>

        <ellipse
            cx="40"
            cy="40"
            rx="12"
            ry="27"
            fill="none"
            stroke="#3296ff"
            stroke-width="4"/>

        <path
            d="M13 40 H67"
            fill="none"
            stroke="#3296ff"
            stroke-width="4"/>

    </g>
    """


def pie_icon(x, y):

    return f"""
    <g transform="translate({x},{y})">

        <rect
            x="0"
            y="0"
            width="80"
            height="80"
            rx="14"
            fill="#111c2d"
            stroke="#26374d"
            stroke-width="2"/>

        <path
            d="
            M40 40
            L40 13
            A27 27 0 0 1 67 40
            Z
            "
            fill="#3296ff"/>

        <path
            d="
            M40 40
            L40 67
            A27 27 0 0 1 13 40
            A27 27 0 0 1 40 13
            Z
            "
            fill="#2f81f7"
            opacity="0.75"/>

    </g>
    """


def medal_icon(x, y):

    return f"""
    <g transform="translate({x},{y})">

        <rect
            x="0"
            y="0"
            width="80"
            height="80"
            rx="14"
            fill="#111c2d"
            stroke="#26374d"
            stroke-width="2"/>

        <!-- Medal ribbons -->

        <path
            d="
            M24 15
            L35 15
            L35 38
            L24 32
            Z
            "
            fill="#ffc42d"/>

        <path
            d="
            M45 15
            L56 15
            L56 32
            L45 38
            Z
            "
            fill="#ffc42d"/>

        <!-- Medal -->

        <circle
            cx="40"
            cy="50"
            r="15"
            fill="none"
            stroke="#ffc42d"
            stroke-width="5"/>

        <path
            d="
            M40 40
            L43 47
            L51 48
            L45 53
            L47 61
            L40 57
            L33 61
            L35 53
            L29 48
            L37 47
            Z
            "
            fill="#ffc42d"/>

    </g>
    """


# ============================================================
# SVG GENERATOR
# ============================================================

def generate_svg(stats):

    username = escape(
        stats["username"]
    )

    solved = number(
        stats["solved"]
    )

    easy = number(
        stats["easy"]
    )

    medium = number(
        stats["medium"]
    )

    hard = number(
        stats["hard"]
    )

    contest_rating = rating(
        stats["rating"]
    )

    global_ranking = number(
        stats["global_ranking"]
    )

    top_percentage = percentage(
        stats["top_percentage"]
    )

    contests = number(
        stats["contests"]
    )

    knight_badge = escape(
        stats["knight_badge"]
    )

    # --------------------------------------------------------
    # Current date
    # --------------------------------------------------------

    updated = datetime.now(
        timezone.utc
    ).strftime("%B %d, %Y")


    # ========================================================
    # DIMENSIONS
    # ========================================================

    WIDTH = 1466
    HEIGHT = 633


    # ========================================================
    # COLUMN POSITIONS
    # ========================================================

    # Four equal columns

    C1 = 209
    C2 = 576
    C3 = 943
    C4 = 1310


    # ========================================================
    # SVG
    # ========================================================

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<defs>

    <!-- Background gradient -->

    <linearGradient
        id="background"
        x1="0"
        y1="0"
        x2="1"
        y2="1">

        <stop
            offset="0%"
            stop-color="#0d1828"/>

        <stop
            offset="100%"
            stop-color="#0a1422"/>

    </linearGradient>


    <!-- Glow -->

    <filter
        id="softGlow"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%">

        <feGaussianBlur
            stdDeviation="2"
            result="blur"/>

    </filter>


    <style>

        .title {{
            fill: #f0f6fc;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 42px;
            font-weight: 700;
        }}

        .username {{
            fill: #9aa8bb;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 25px;
        }}

        .updated {{
            fill: #9aa8bb;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 23px;
        }}

        .number {{
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 53px;
            font-weight: 700;
        }}

        .problem-label {{
            fill: #f0f6fc;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 22px;
            font-weight: 600;
        }}

        .small-label {{
            fill: #9aa8bb;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 20px;
        }}

        .secondary-number {{
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 45px;
            font-weight: 700;
        }}

        .secondary-label {{
            fill: #f0f6fc;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 21px;
            font-weight: 500;
        }}

        .secondary-description {{
            fill: #8c9aad;
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
            font-size: 19px;
        }}

        .divider {{
            stroke: #29394d;
            stroke-width: 2;
        }}

        .card {{
            fill: url(#background);
            stroke: #26374d;
            stroke-width: 2;
        }}

    </style>

</defs>


<!-- ====================================================== -->
<!-- CARD -->
<!-- ====================================================== -->

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="20"
    class="card"/>


<!-- ====================================================== -->
<!-- HEADER -->
<!-- ====================================================== -->

<!-- LeetCode logo -->

<g transform="translate(52,38)">

    <path
        d="
        M45 5
        L18 32
        L45 59
        "
        fill="none"
        stroke="#ffffff"
        stroke-width="8"
        stroke-linecap="round"
        stroke-linejoin="round"/>

    <path
        d="
        M28 32
        H64
        "
        fill="none"
        stroke="#ffffff"
        stroke-width="8"
        stroke-linecap="round"/>

    <circle
        cx="65"
        cy="32"
        r="5"
        fill="#f0b90b"/>

</g>


<text
    x="115"
    y="78"
    class="title">

LeetCode

</text>


<text
    x="52"
    y="128"
    class="username">

@{username}

</text>


<!-- Updated -->

<text
    x="1115"
    y="78"
    class="updated">

Last Updated: {updated}

</text>


<!-- Header divider -->

<line
    x1="52"
    y1="161"
    x2="1414"
    y2="161"
    class="divider"/>


<!-- ====================================================== -->
<!-- FIRST ROW -->
<!-- ====================================================== -->


<!-- Vertical dividers -->

<line
    x1="392"
    y1="192"
    x2="392"
    y2="341"
    class="divider"/>

<line
    x1="759"
    y1="192"
    x2="759"
    y2="341"
    class="divider"/>

<line
    x1="1126"
    y1="192"
    x2="1126"
    y2="341"
    class="divider"/>


<!-- Problems solved -->

<text
    x="{C1}"
    y="245"
    text-anchor="middle"
    class="number"
    fill="#45d16b">

{solved}

</text>

<text
    x="{C1}"
    y="281"
    text-anchor="middle"
    class="problem-label">

Problems Solved

</text>

<!-- Green check -->

<circle
    cx="{C1 - 44}"
    cy="319"
    r="11"
    fill="none"
    stroke="#45d16b"
    stroke-width="4"/>

<path
    d="
    M{C1 - 50} 319
    L{C1 - 46} 323
    L{C1 - 39} 315
    "
    fill="none"
    stroke="#45d16b"
    stroke-width="3"
    stroke-linecap="round"
    stroke-linejoin="round"/>

<text
    x="{C1 - 24}"
    y="326"
    class="small-label">

All Time

</text>


<!-- Easy -->

<text
    x="{C2}"
    y="245"
    text-anchor="middle"
    class="number"
    fill="#45d16b">

{easy}

</text>

<text
    x="{C2}"
    y="281"
    text-anchor="middle"
    class="problem-label">

Easy

</text>

<circle
    cx="{C2 - 25}"
    cy="319"
    r="10"
    fill="#35d06f"/>

<text
    x="{C2 - 4}"
    y="326"
    class="small-label">

Solved

</text>


<!-- Medium -->

<text
    x="{C3}"
    y="245"
    text-anchor="middle"
    class="number"
    fill="#ffb01b">

{medium}

</text>

<text
    x="{C3}"
    y="281"
    text-anchor="middle"
    class="problem-label">

Medium

</text>

<circle
    cx="{C3 - 29}"
    cy="319"
    r="10"
    fill="#ffae19"/>

<text
    x="{C3 - 7}"
    y="326"
    class="small-label">

Solved

</text>


<!-- Hard -->

<text
    x="{C4}"
    y="245"
    text-anchor="middle"
    class="number"
    fill="#ff4848">

{hard}

</text>

<text
    x="{C4}"
    y="281"
    text-anchor="middle"
    class="problem-label">

Hard

</text>

<circle
    cx="{C4 - 26}"
    cy="319"
    r="10"
    fill="#ff4646"/>

<text
    x="{C4 - 4}"
    y="326"
    class="small-label">

Solved

</text>


<!-- Horizontal divider -->

<line
    x1="52"
    y1="369"
    x2="1414"
    y2="369"
    class="divider"/>


<!-- ====================================================== -->
<!-- SECOND ROW -->
<!-- ====================================================== -->


<!-- Vertical dividers -->

<line
    x1="392"
    y1="395"
    x2="392"
    y2="515"
    class="divider"/>

<line
    x1="759"
    y1="395"
    x2="759"
    y2="515"
    class="divider"/>

<line
    x1="1126"
    y1="395"
    x2="1126"
    y2="515"
    class="divider"/>


<!-- Rating icon -->

{rating_icon(68, 395)}


<text
    x="180"
    y="436"
    class="secondary-number"
    fill="#9b7cff">

{contest_rating}

</text>

<text
    x="180"
    y="470"
    class="secondary-label">

Contest Rating

</text>

<text
    x="180"
    y="505"
    class="secondary-description">

Max Rating

</text>


<!-- Global ranking -->

{globe_icon(430, 395)}

<text
    x="560"
    y="436"
    class="secondary-number"
    fill="#3296ff">

{global_ranking}

</text>

<text
    x="560"
    y="470"
    class="secondary-label">

Global Ranking

</text>

<text
    x="560"
    y="505"
    class="secondary-description">

Worldwide

</text>


<!-- Top percentage -->

{pie_icon(797, 395)}

<text
    x="927"
    y="436"
    class="secondary-number"
    fill="#3296ff">

{top_percentage}

</text>

<text
    x="927"
    y="470"
    class="secondary-label">

Top Percentage

</text>

<text
    x="927"
    y="505"
    class="secondary-description">

Better than

</text>


<!-- Knight Badge -->

{medal_icon(1164, 395)}

<text
    x="1294"
    y="436"
    class="secondary-number"
    fill="#ffc42d"
    font-size="38px">

{knight_badge}

</text>

<text
    x="1294"
    y="470"
    class="secondary-label">

Badge

</text>

<text
    x="1294"
    y="505"
    class="secondary-description">

LeetCode Knight

</text>


<!-- ====================================================== -->
<!-- FOOTER -->
<!-- ====================================================== -->

<line
    x1="52"
    y1="539"
    x2="1414"
    y2="539"
    class="divider"/>


<!-- People icon -->

<g transform="translate(55,570)">

    <circle
        cx="11"
        cy="7"
        r="5"
        fill="none"
        stroke="#9aa8bb"
        stroke-width="3"/>

    <circle
        cx="27"
        cy="9"
        r="4"
        fill="none"
        stroke="#9aa8bb"
        stroke-width="3"/>

    <path
        d="M2 25
           C2 18 7 15 12 15
           C17 15 21 18 21 25"
        fill="none"
        stroke="#9aa8bb"
        stroke-width="3"
        stroke-linecap="round"/>

    <path
        d="M21 18
           C25 16 31 19 32 24"
        fill="none"
        stroke="#9aa8bb"
        stroke-width="3"
        stroke-linecap="round"/>

</g>


<text
    x="95"
    y="599"
    class="small-label">

Contests Participated: {contests}

</text>


</svg>
'''

    return svg


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        f"Fetching LeetCode data "
        f"for @{USERNAME}..."
    )

    data = fetch_leetcode_data(
        USERNAME
    )

    stats = process_stats(
        data
    )

    print()
    print(
        f"Problems solved : "
        f"{stats['solved']}"
    )

    print(
        f"Easy            : "
        f"{stats['easy']}"
    )

    print(
        f"Medium          : "
        f"{stats['medium']}"
    )

    print(
        f"Hard            : "
        f"{stats['hard']}"
    )

    print(
        f"Contest rating  : "
        f"{stats['rating']}"
    )

    print(
        f"Global ranking  : "
        f"{stats['global_ranking']}"
    )

    print(
        f"Top percentage  : "
        f"{stats['top_percentage']}"
    )

    print(
        f"Knight badge    : "
        f"{stats['knight_badge']}"
    )

    print(
        f"Contests        : "
        f"{stats['contests']}"
    )

    svg = generate_svg(
        stats
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(svg)

    print()
    print(
        f"✓ Generated {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()