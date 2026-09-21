"""Commissioner-desk files drawn from Winston Cup-era interviews.

NASCAR did not use the title "commissioner" in these years. The job the
player sits in is the one Bill France Sr., Bill France Jr., and later
Mike Helton actually did: write the book, sell the house, take the heat
on safety, and keep Detroit, the tracks, and the garage in the same
sport. The quotes below are paraphrased from public interviews and
contemporary reporting (1947–2003). They are not transcripts. The
letters use series-office voice so the player remains the one in the chair.
"""

from game.settings import ERA_1970S, ERA_1980S, ERA_PINNACLE, current_settings


# Public-record themes, paraphrased for the desk — not licensed copy.
CHAIR_NOTES = {
    ERA_1970S: (
        "The job is the same one that came out of the Streamline Hotel: "
        "one book, a guaranteed purse, and a field that shows up. The "
        "Winston check in 1971 bought a national series; it also asked "
        "you to drop the short dirt dates. Controlled growth. Everyone "
        "in the sport has to win something, or the product dies."
    ),
    ERA_1980S: (
        "Follow Detroit — eventually — but do not obsolete last year's "
        "cars overnight. 1981 cut the wheelbase to 110 when the street "
        "coupes downsized. The little cars got twitchy at Daytona until "
        "the office put more spoiler on them. Television is still a "
        "patchwork of track deals. That is your problem, not the "
        "broadcaster's."
    ),
    ERA_PINNACLE: (
        "The product is the race. Quality of competition first; the "
        "economics follow. A national TV package beats a Saturday cable "
        "scramble. Plates at the two big ovals are not a knee-jerk — "
        "if you slow the cars you take the heat, and you take it in "
        "public. Owners are independent contractors. You write the book; "
        "they run the shops."
    ),
}


def era_book_id(era=None):
    """Return the live era book id."""

    token = era or current_settings.get("era_book") or ERA_PINNACLE
    if token in CHAIR_NOTES:
        return token
    return ERA_PINNACLE


def chair_note(era=None):
    """Return the dashboard line for this era's chair files."""

    return CHAIR_NOTES[era_book_id(era)]


def briefing_subject(era=None):
    """Return the inbox subject for the era briefing."""

    era = era_book_id(era)
    if era == ERA_1970S:
        return "Files from the chair — 1970s modern era"
    if era == ERA_1980S:
        return "Files from the chair — 1981 downsizing"
    return "Files from the chair — national TV years"


def briefing_body(series=None, era=None):
    """Return the era briefing letter, in series-office voice."""

    series = series or "the series"
    era = era_book_id(era)
    if era == ERA_1970S:
        return (
            "Commissioner,\n\n"
            "This is the chair you inherited. In 1947 the men who formed "
            "this sport sat in a Daytona hotel and asked for uniform rules, "
            "insurance, and a purse that actually got paid. That is still "
            "the job.\n\n"
            "1971: a tobacco company that could no longer advertise on "
            "television put its national budget on the series. The point "
            "fund jumped. The trade was real — they wanted the short dirt "
            "dates gone so the championship looked like a national tour, "
            "not a regional carnival. The modern era starts when you "
            "protect that calendar.\n\n"
            "The other file: Talladega. The house was sold. The tires were "
            "not ready. The drivers wanted the race postponed. The chair "
            "ran a lap himself and still lost the field. You will face "
            "that choice again — safety versus a sold grandstand. There "
            "is no clean answer. There is only the book you write and the "
            "heat you take.\n\n"
            "Winston Cup years. You do not own a shop. You run %s."
            % series
        )
    if era == ERA_1980S:
        return (
            "Commissioner,\n\n"
            "Bill France Jr. told the garage in 1977 that the series would "
            "follow Detroit, but not so fast that last year's cars became "
            "scrap. In 1981 the office cut the Cup car from 115 inches to "
            "110 to match the street coupes. The little cars were fast and "
            "twitchy. Some of them got airborne. The fix was more spoiler "
            "and, when a shop showed up with a sloped rear window that "
            "kept the tail planted, a midweek template change. That is "
            "this job: rewrite the book between practices if the product "
            "is unsafe.\n\n"
            "Aero is the other war. Ford's Thunderbird got slick. Chevrolet "
            "answered with a 1980 Monte Carlo that still looked like a "
            "brick, then a downsized SS, then — when the bird kept winning "
            "the big ovals — an Aerocoupe with sloped glass and a 200-car "
            "street count. Homologation is a lever, not a slogan.\n\n"
            "Television is still a scatter of track-by-track deals. The 500 "
            "on network, cable on Saturday, a different bug every week. A "
            "national package is how this sport stops being regional. You "
            "will spend this decade arguing about who owns the air.\n\n"
            "You run %s. Forty cars. One driver per entry."
            % series
        )
    return (
        "Commissioner,\n\n"
        "The files from this chair in the late eighties and nineties say "
        "the same thing in different words: the product is the race. "
        "Mike Helton, taking the presidency in 2000, put it on the record "
        "— quality of competition first. France Jr. called it controlled "
        "growth: everyone in the sport has to win, or the deal dies.\n\n"
        "Successes already on the shelf: a title sponsor that paid for a "
        "national series; the 500 on network television; plates at the two "
        "superspeedways after the cars got too fast to race; Detroit still "
        "badge-engineering coupes the fans can name from the grandstand.\n\n"
        "The live fights: a national TV contract instead of every track "
        "selling its own race; how the money splits among tracks, owners, "
        "and the sanctioning body; restrictor-plate racing that nobody in "
        "the garage likes and that the office will not drop just to please "
        "them. Helton's line after Loudon was 'we're big boys — we'll take "
        "the heat.' That is the safety file. It is also the TV file.\n\n"
        "Owners are independent contractors. You do not set a tire-changer's "
        "pay. You write the winter book, you sell the house, and you keep "
        "the factories from turning Sunday into a spec silhouette.\n\n"
        "You run %s. Reports is the race file — STATS, BOX, LEADERS. "
        "Advance when this week's desk is done."
        % series
    )


def welcome_addendum(era=None):
    """Return a short chair paragraph for the welcome letter."""

    era = era_book_id(era)
    if era == ERA_1970S:
        return (
            "The chair files from the seventies: a national point fund, "
            "fewer dirt dates, and a sold house that still has to be raced "
            "safely. Read the briefing in this bag."
        )
    if era == ERA_1980S:
        return (
            "The chair files from the eighties: follow Detroit's 110-inch "
            "cars, keep last year's coupes from becoming scrap, and stop "
            "selling the air track by track. Read the briefing in this bag."
        )
    return (
        "The chair files from the pinnacle years: the race is the product, "
        "a national TV package is the business, and plates at the big "
        "ovals are the heat you take in public. Read the briefing in this bag."
    )


def ticker_chair_line(era=None):
    """Return a preseason ticker sting from the chair files."""

    era = era_book_id(era)
    if era == ERA_1970S:
        return "CHAIR FILES: one book, a paid purse, a national point fund."
    if era == ERA_1980S:
        return "CHAIR FILES: follow Detroit — 110 inches — and sell the air as one package."
    return "CHAIR FILES: the product is the race. Take the heat on plates. Do not spec the coupes."


def golden_era_line(era=None):
    """Return a one-line golden-era sting for Reports and the dashboard."""

    era = era_book_id(era)
    if era == ERA_1970S:
        return (
            "Go back to the modern era: one book, a paid purse, "
            "and a national point fund."
        )
    if era == ERA_1980S:
        return (
            "Go back to the downsizing years: 110-inch coupes, "
            "a patchwork of TV, Detroit still in the fight."
        )
    return (
        "Go back to the golden era: packed houses, plates at the big ovals, "
        "and coupes you can name from the grandstand."
    )


def week_desk_copy(_era=None):
    """Return Football Coach-style weekly desk copy."""

    return (
        "This week's desk: read the mail, write the winter book, "
        "inspect the race file, then Advance."
    )
