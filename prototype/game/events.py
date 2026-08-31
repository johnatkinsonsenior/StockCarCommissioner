"""Reusable commissioner decision-event framework."""

import random

from game.race import clamp


def choose_weighted_outcome(outcomes):
    """Select one weighted outcome from a choice."""

    if not outcomes:
        return {
            "text": "The decision is recorded.",
            "effects": [],
        }

    weights = [max(1, outcome.get("weight", 1)) for outcome in outcomes]
    return random.choices(outcomes, weights=weights, k=1)[0]


def apply_effect(effect, context):
    """Apply one effect dictionary to the live game context."""

    effect_type = effect["type"]
    league = context["league"]
    policies = context["policies"]
    drivers = context["drivers"]
    teams = context["teams"]
    subject_driver = context.get("subject_driver")
    subject_team = context.get("subject_team")
    subject_other_driver = context.get("subject_other_driver")
    season = context.get("season", 1)

    if effect_type == "league":
        stat = effect["stat"]
        league[stat] = clamp(league.get(stat, 0) + effect["delta"])

    elif effect_type == "fines":
        league["fines_collected"] += effect["amount"]

    elif effect_type == "policy":
        policies[effect["key"]] = effect["value"]

    elif effect_type == "all_drivers":
        stat = effect["stat"]
        delta = effect["delta"]

        for driver in drivers:
            setattr(driver, stat, clamp(getattr(driver, stat) + delta))

    elif effect_type == "subject_driver" and subject_driver is not None:
        stat = effect["stat"]
        setattr(
            subject_driver,
            stat,
            clamp(getattr(subject_driver, stat) + effect["delta"]),
        )

    elif effect_type == "team_drivers" and subject_team is not None:
        stat = effect["stat"]
        delta = effect["delta"]

        for driver in drivers:
            if driver.team_name == subject_team.name:
                setattr(driver, stat, clamp(getattr(driver, stat) + delta))

    elif effect_type == "subject_team_budget" and subject_team is not None:
        amount = effect["delta"]

        if amount < 0:
            subject_team.pay_fine(-amount)
        else:
            subject_team.budget += amount

    elif effect_type == "all_teams_budget":
        amount = effect["delta"]

        for team in teams:
            if amount < 0:
                team.pay_fine(-amount)
            else:
                team.budget += amount

    elif effect_type == "subject_owner" and subject_team is not None:
        owner = subject_team.owner

        if owner is not None:
            stat = effect["stat"]
            setattr(
                owner,
                stat,
                clamp(getattr(owner, stat) + effect["delta"]),
            )

    elif effect_type == "subject_team" and subject_team is not None:
        stat = effect["stat"]
        setattr(
            subject_team,
            stat,
            clamp(getattr(subject_team, stat) + effect["delta"]),
        )

    elif (
        effect_type == "subject_other_driver"
        and subject_other_driver is not None
    ):
        stat = effect["stat"]
        setattr(
            subject_other_driver,
            stat,
            clamp(
                getattr(subject_other_driver, stat) + effect["delta"]
            ),
        )

    elif effect_type == "rivalry" and subject_driver is not None:
        amount = effect["delta"]
        subject_driver.adjust_rivalry(amount)

        if (
            subject_other_driver is not None
            and subject_other_driver.rival == subject_driver.name
        ):
            subject_other_driver.adjust_rivalry(amount)

    elif effect_type == "feud" and subject_driver is not None:
        other_name = effect.get("opponent")
        if not other_name and subject_other_driver is not None:
            other_name = subject_other_driver.name

        if other_name:
            incident = effect.get("incident", "")
            delta = effect.get("delta", 8)
            subject_driver.record_feud(
                other_name,
                season,
                delta,
                incident,
            )

            if subject_other_driver is not None:
                subject_other_driver.record_feud(
                    subject_driver.name,
                    season,
                    delta,
                    incident,
                )

    elif effect_type == "friendship" and subject_driver is not None:
        other_name = effect.get("friend")
        if not other_name and subject_other_driver is not None:
            other_name = subject_other_driver.name

        if other_name:
            delta = effect["delta"]
            subject_driver.adjust_friendship(other_name, delta)

            if subject_other_driver is not None:
                subject_other_driver.adjust_friendship(
                    subject_driver.name,
                    delta,
                )


def apply_effects(effects, context):
    """Apply a list of effects."""

    for effect in effects or []:
        apply_effect(effect, context)


def find_choice(event, choice_id):
    """Return the matching choice from an event."""

    for choice in event["choices"]:
        if choice["id"] == str(choice_id):
            return choice

    raise ValueError(f"Unknown choice for {event['id']}: {choice_id}")


def resolve_event_choice(event, choice_id, context):
    """Apply a choice, roll a weighted outcome, and return a result record."""

    choice = find_choice(event, choice_id)
    apply_effects(choice.get("effects", []), context)
    outcome = choose_weighted_outcome(choice.get("outcomes", []))
    apply_effects(outcome.get("effects", []), context)

    return {
        "event_id": event["id"],
        "event_title": event["title"],
        "category": event["category"],
        "phase": event["phase"],
        "choice_id": choice["id"],
        "choice_label": choice["label"],
        "outcome": outcome.get("text", ""),
        "subject_driver": (
            context["subject_driver"].name
            if context.get("subject_driver")
            else None
        ),
        "subject_team": (
            context["subject_team"].name
            if context.get("subject_team")
            else None
        ),
        "subject_other_driver": (
            context["subject_other_driver"].name
            if context.get("subject_other_driver")
            else None
        ),
    }
