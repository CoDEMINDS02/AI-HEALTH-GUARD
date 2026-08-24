import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RedFlagRule:
    rule_id: str
    label: str
    guidance: str
    patterns: tuple[re.Pattern, ...]

    def matches(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.patterns)


def _rule(rule_id: str, label: str, guidance: str, patterns: list[str]) -> RedFlagRule:
    return RedFlagRule(
        rule_id=rule_id,
        label=label,
        guidance=guidance,
        patterns=tuple(re.compile(p, re.IGNORECASE) for p in patterns),
    )


RED_FLAG_RULES: list[RedFlagRule] = [
    _rule(
        "severe_breathing_difficulty",
        "Severe difficulty breathing",
        "Seek urgent medical attention immediately.",
        [
            r"\bcan(?:'|no)?t\s+breathe\b",
            r"\b(?:severe|serious)\s+(?:difficulty|trouble|problems?)\s+breathing\b",
            r"\bstruggling\s+to\s+breathe\b",
            r"\bgasping\b(?:\s+for\s+(?:air|breath))?",
            r"\bchoking\b",
            r"\bbreathless\s+(?:at\s+rest|even\s+(?:while\s+)?sitting|when\s+sitting)\b",
            r"\blips\s+(?:or\s+nails\s+)?turning\s+blue\b",
        ],
    ),
    _rule(
        "severe_chest_pain",
        "Severe chest pain or pressure",
        "Chest pain with these features can be an emergency. Seek immediate medical care.",
        [
            r"\bcrushing\s+chest\s+(?:pain|pressure)\b",
            r"\bchest\s+(?:pain|pressure)\s+.{0,30}\b(?:radiat\w*|spread\w*)\b",
            r"\b(?:severe|intense|worst)\s+chest\s+(?:pain|pressure)\b",
            r"\bchest\s+(?:pain|pressure)\b.{0,40}\b(?:sweating|cold\s+sweat|nausea|shortness\s+of\s+breath)\b",
            r"\bfeels?\s+like\s+(?:an?\s+)?elephant\s+(?:is\s+)?on\s+(?:my|the)\s+chest\b",
        ],
    ),
    _rule(
        "loss_of_consciousness",
        "Loss of consciousness / fainting",
        "Fainting or unresponsiveness warrants urgent professional evaluation.",
        [
            r"\bfaint(?:ed|ing)?\b",
            r"\bpassed\s+out\b",
            r"\bloss\s+of\s+consciousness\b",
            r"\bunresponsive\b",
            r"\bblacked?\s+out\b",
        ],
    ),
    _rule(
        "severe_confusion",
        "Sudden severe confusion",
        "New confusion can signal a serious problem and needs prompt assessment.",
        [
            r"\b(?:sudden|new|severe)\s+(?:onset\s+)?(?:confusion|disorientation)\b",
            r"\bseverely\s+confused\b",
            r"\bdoes\s?n[o']t\s+know\s+(?:where|who|what)\b",
        ],
    ),
    _rule(
        "severe_bleeding",
        "Signs of severe bleeding",
        "Uncontrolled bleeding is an emergency; seek immediate care.",
        [
            r"\b(?:severe|heavy|uncontrolled)\s+bleeding\b",
            r"\bbleeding\s+(?:that\s+)?won'?t\s+stop\b",
            r"\bvomiting\s+blood\b|\bvomiting.{0,20}blood\b",
            r"\bcough(?:ing)?\s+up\s+blood\b",
            r"\bblood\s+in\s+(?:stool|vomit|urine)\b",
        ],
    ),
    _rule(
        "acute_neurological",
        "Sudden severe neurological symptoms",
        "These can be signs of a stroke or other neurological emergency. Seek help immediately.",
        [
            r"\bface\s+droop(?:ing)?\b",
            r"\b(?:slurred|garbled)\s+speech\b",
            r"\bweakness\s+on\s+one\s+side\b",
            r"\bone[- ]sided\s+(?:weakness|numbness|paralysis)\b",
            r"\bsudden\s+(?:numbness|weakness)\s+(?:of|in|on)\s+(?:my\s+|the\s+)?(?:arm|leg|face|hand)",
            r"\bsudden\s+(?:loss\s+of\s+)?(?:vision|speech)\b",
            r"\bworst\s+headache\s+of\s+(?:my|the)\s+life\b",
        ],
    ),
    _rule(
        "severe_allergic_reaction",
        "Possible severe allergic reaction",
        "Swelling of the throat/tongue with breathing trouble is an emergency.",
        [
            r"\bthroat\s+(?:closing|swelling|swelling\s+up)\b",
            r"\btongue\s+swell(?:ing|ed)\b",
            r"\banaphyla(?:xis|ctic)\b",
            r"\bhives\b.{0,60}\b(?:breath\w*|swell\w*)\b",
        ],
    ),
    _rule(
        "seizure",
        "Seizure activity",
        "Seizures require urgent medical assessment.",
        [r"\bseizure[s]?\b", r"\bconvulsion[s]?\b"],
    ),
    _rule(
        "meningitis_signal",
        "Fever with stiff neck",
        "A stiff neck with fever can indicate a serious infection; seek care urgently.",
        [
            r"\bstiff\s+neck\b.{0,80}\bfever\b",
            r"\bfever\b.{0,80}\bstiff\s+neck\b",
            r"\bneck\s+pain\b.{0,40}\bcan'?t\s+touch\s+chin\b",
        ],
    ),
    _rule(
        "rapid_worsening",
        "Rapidly worsening serious symptoms",
        "Rapid deterioration should not wait; seek prompt professional evaluation.",
        [
            r"\bsymptoms?\s+(?:are\s+|is\s+)?worsening\s+(?:rapidly|quickly|suddenly|fast)\b",
            r"\brapidly\s+worsening\b",
            r"\bgetting\s+(?:much\s+)?worse\s+(?:fast|quickly|by\s+the\s+(?:hour|minute))\b",
        ],
    ),
]


@dataclass
class SafetyAssessment:
    triggered: list[RedFlagRule] = field(default_factory=list)

    @property
    def has_red_flags(self) -> bool:
        return bool(self.triggered)

    @property
    def labels(self) -> list[str]:
        return [rule.label for rule in self.triggered]


def assess_text_safety(*texts: str | None) -> SafetyAssessment:
    combined = " ".join(t for t in texts if t).lower()
    triggered = [rule for rule in RED_FLAG_RULES if rule.matches(combined)]
    return SafetyAssessment(triggered=triggered)
