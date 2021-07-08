from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz


@dataclass(frozen=True)
class SessionInfo:
    """The session information for a paper."""

    session_name: str
    start_time: datetime
    end_time: datetime
    link: str
    hosts: str = None

    @property
    def day(self) -> str:
        start_time = self.start_time.astimezone(pytz.timezone("America/Los_Angeles"))
        return f'{start_time.strftime("%b")} {start_time.day}'

    @property
    def time_string(self) -> str:
        start = self.start_time.astimezone(pytz.utc)
        end = self.end_time.astimezone(pytz.utc)
        return "({}-{} UTC)".format(start.strftime("%H:%M"), end.strftime("%H:%M"))

    @property
    def start_time_string(self) -> str:
        start_time = self.start_time.astimezone(pytz.utc)
        return start_time.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def end_time_string(self) -> str:
        end_time = self.end_time.astimezone(pytz.utc)
        return end_time.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def session(self) -> str:
        start_time = self.start_time.astimezone(pytz.timezone("America/Los_Angeles"))

        start_date = f'{start_time.strftime("%b")} {start_time.day}'
        if self.session_name.startswith("D"):
            # demo sessions
            return f"Demo Session {self.session_name[1:]}: {start_date}"
        if self.session_name.startswith("P-"):
            # plenary sessions
            return f"{self.session_name[2:]}: {start_date}"
        if self.session_name.startswith("S-"):
            # social event sessions
            return f"{self.session_name[2:]}: {start_date}"
        if self.session_name.startswith("T-"):
            # workshop sessions
            return f"{self.session_name[2:]}: {start_date}"
        if self.session_name.startswith("W-"):
            # workshop sessions
            return f"{self.session_name[2:]}: {start_date}"
        if self.session_name.startswith("z") or self.session_name.startswith("g"):
            # paper sessions
            prefix = self.session_type.capitalize()
            return f"{prefix}-{self.session_name[1:]}: {start_date}"

        return f"Session {self.session_name}: {start_date}"

    @property
    def session_type(self):
        if self.session_name.startswith("z"):
            return "zoom"
        elif self.session_name.startswith("g"):
            return "gather"
        else:
            return "unknown"



@dataclass(frozen=True)
class PaperContent:
    """The content of a paper.

    Needs to be synced with static/js/papers.js and static/js/paper_vis.js.
    """
    # needs to be synced with
    title: str
    authors: List[str]
    track: str
    paper_type: str
    abstract: str
    tldr: str
    keywords: List[str]
    pdf_url: Optional[str]
    demo_url: Optional[str]
    sessions: List[SessionInfo]
    similar_paper_uids: List[str]
    program: str
    date1: str = None
    time1: str = None
    date2: str = None
    time2: str = None
    date3: str = None
    time3: str = None
    room: str = None
    room_letter1 : str = None
    room_letter2 : str = None
    room_letter3 : str = None
    cluster: str = None
    position: int = None
    cluster_name: str = None
    gather_town_link: str = None
    material: str = None
    best_type: int = None
    best_type_desc: str = None

    def __post_init__(self):
        pass
        # if self.program != "workshop" and self.program != "findings":
        #     assert self.track, self
        # if self.pdf_url:
        #     assert self.pdf_url.startswith("https://"), self.pdf_url
        # if self.demo_url:
        #     assert self.demo_url.startswith("https://") or self.demo_url.startswith(
        #         "http://"
        #     ), self.demo_url


@dataclass(frozen=True)
class Paper:
    """The paper dataclass.

    This corresponds to an entry in the `papers.json`.
    See the `start()` method in static/js/papers.js.
    """

    id: str
    forum: str
    card_image_path: str
    presentation_id: str
    presentation_id_intro: str
    content: PaperContent
    @property
    def rocketchat_channel(self) -> str:
        return f"paper-{self.id.replace('.', '-')}"

    @property
    def date1_start_time_string(self) -> str:
        datetime_to_str = {
            '4-Feb 08:45AM-10:30AM':"2021-02-04 08:45:00",
            '4-Feb 04:45PM-06:30PM':"2021-02-04 16:45:00",
            '5-Feb 12:45AM-02:30AM':"2021-02-05 00:45:00",
            '5-Feb 08:45AM-10:30AM':"2021-02-05 08:45:00",
            '5-Feb 04:45PM-06:30PM':"2021-02-05 16:45:00",
            '6-Feb 12:45AM-02:30AM':"2021-02-06 00:45:00",
            '6-Feb 08:45AM-10:30AM':"2021-02-06 08:45:00",
            '6-Feb 04:45PM-06:30PM':"2021-02-06 16:45:00",
            '7-Feb 12:45AM-02:30AM':"2021-02-07 00:45:00",
            '7-Feb 08:45AM-10:30AM':"2021-02-07 08:45:00",
            '7-Feb 04:45PM-06:30PM':"2021-02-07 16:45:00",
            '8-Feb 12:45AM-02:30AM':"2021-02-08 00:45:00",
            "unknown unknown": "",
            " ": ""
        }
        time = self.content.date1 + " " + self.content.time1
        return datetime_to_str[time]

    @property
    def date1_end_time_string(self) -> str:
        datetime_to_str = {
            '4-Feb 08:45AM-10:30AM':"2021-02-04 10:30:00",
            '4-Feb 04:45PM-06:30PM':"2021-02-04 18:30:00",
            '5-Feb 12:45AM-02:30AM':"2021-02-05 02:30:00",
            '5-Feb 08:45AM-10:30AM':"2021-02-05 10:30:00",
            '5-Feb 04:45PM-06:30PM':"2021-02-05 18:30:00",
            '6-Feb 12:45AM-02:30AM':"2021-02-06 02:30:00",
            '6-Feb 08:45AM-10:30AM':"2021-02-06 10:30:00",
            '6-Feb 04:45PM-06:30PM':"2021-02-06 18:30:00",
            '7-Feb 12:45AM-02:30AM':"2021-02-07 02:30:00",
            '7-Feb 08:45AM-10:30AM':"2021-02-07 10:30:00",
            '7-Feb 04:45PM-06:30PM':"2021-02-07 18:30:00",
            '8-Feb 12:45AM-02:30AM':"2021-02-08 02:30:00",
            "unknown unknown": "",
            " ": ""
        }
        time = self.content.date1 + " " + self.content.time1
        return datetime_to_str[time]

    @property
    def date2_start_time_string(self) -> str:
        datetime_to_str = {
            '4-Feb 08:45AM-10:30AM':"2021-02-04 08:45:00",
            '4-Feb 04:45PM-06:30PM':"2021-02-04 16:45:00",
            '5-Feb 12:45AM-02:30AM':"2021-02-05 00:45:00",
            '5-Feb 08:45AM-10:30AM':"2021-02-05 08:45:00",
            '5-Feb 04:45PM-06:30PM':"2021-02-05 16:45:00",
            '6-Feb 12:45AM-02:30AM':"2021-02-06 00:45:00",
            '6-Feb 08:45AM-10:30AM':"2021-02-06 08:45:00",
            '6-Feb 04:45PM-06:30PM':"2021-02-06 16:45:00",
            '7-Feb 12:45AM-02:30AM':"2021-02-07 00:45:00",
            '7-Feb 08:45AM-10:30AM':"2021-02-07 08:45:00",
            '7-Feb 04:45PM-06:30PM':"2021-02-07 16:45:00",
            '8-Feb 12:45AM-02:30AM':"2021-02-08 00:45:00",
            "unknown unknown": "",
            " ": ""
        }
        time = self.content.date2 + " " + self.content.time2
        return datetime_to_str[time]

    @property
    def date2_end_time_string(self) -> str:
        datetime_to_str = {
            '4-Feb 08:45AM-10:30AM':"2021-02-04 10:30:00",
            '4-Feb 04:45PM-06:30PM':"2021-02-04 18:30:00",
            '5-Feb 12:45AM-02:30AM':"2021-02-05 02:30:00",
            '5-Feb 08:45AM-10:30AM':"2021-02-05 10:30:00",
            '5-Feb 04:45PM-06:30PM':"2021-02-05 18:30:00",
            '6-Feb 12:45AM-02:30AM':"2021-02-06 02:30:00",
            '6-Feb 08:45AM-10:30AM':"2021-02-06 10:30:00",
            '6-Feb 04:45PM-06:30PM':"2021-02-06 18:30:00",
            '7-Feb 12:45AM-02:30AM':"2021-02-07 02:30:00",
            '7-Feb 08:45AM-10:30AM':"2021-02-07 10:30:00",
            '7-Feb 04:45PM-06:30PM':"2021-02-07 18:30:00",
            '8-Feb 12:45AM-02:30AM':"2021-02-08 02:30:00",
            "unknown unknown": "",
            " ": ""
        }
        time = self.content.date2 + " " + self.content.time2
        return datetime_to_str[time]

    @property
    def date3_start_time_string(self) -> str:
        datetime_to_str = {
            '4-Feb 08:45AM-10:30AM':"2021-02-04 08:45:00",
            '4-Feb 04:45PM-06:30PM':"2021-02-04 16:45:00",
            '5-Feb 12:45AM-02:30AM':"2021-02-05 00:45:00",
            '5-Feb 08:45AM-10:30AM':"2021-02-05 08:45:00",
            '5-Feb 04:45PM-06:30PM':"2021-02-05 16:45:00",
            '6-Feb 12:45AM-02:30AM':"2021-02-06 00:45:00",
            '6-Feb 08:45AM-10:30AM':"2021-02-06 08:45:00",
            '6-Feb 04:45PM-06:30PM':"2021-02-06 16:45:00",
            '7-Feb 12:45AM-02:30AM':"2021-02-07 00:45:00",
            '7-Feb 08:45AM-10:30AM':"2021-02-07 08:45:00",
            '7-Feb 04:45PM-06:30PM':"2021-02-07 16:45:00",
            '8-Feb 12:45AM-02:30AM':"2021-02-08 00:45:00",
            "unknown unknown": "",
            " ": ""
        }
        time = self.content.date3 + " " + self.content.time3
        return datetime_to_str[time]

    @property
    def date3_end_time_string(self) -> str:
        datetime_to_str = {
            '4-Feb 08:45AM-10:30AM':"2021-02-04 10:30:00",
            '4-Feb 04:45PM-06:30PM':"2021-02-04 18:30:00",
            '5-Feb 12:45AM-02:30AM':"2021-02-05 02:30:00",
            '5-Feb 08:45AM-10:30AM':"2021-02-05 10:30:00",
            '5-Feb 04:45PM-06:30PM':"2021-02-05 18:30:00",
            '6-Feb 12:45AM-02:30AM':"2021-02-06 02:30:00",
            '6-Feb 08:45AM-10:30AM':"2021-02-06 10:30:00",
            '6-Feb 04:45PM-06:30PM':"2021-02-06 18:30:00",
            '7-Feb 12:45AM-02:30AM':"2021-02-07 02:30:00",
            '7-Feb 08:45AM-10:30AM':"2021-02-07 10:30:00",
            '7-Feb 04:45PM-06:30PM':"2021-02-07 18:30:00",
            '8-Feb 12:45AM-02:30AM':"2021-02-08 02:30:00",
            "unknown unknown": "",
            " ": ""
        }
        time = self.content.date3 + " " + self.content.time3
        return datetime_to_str[time]


@dataclass(frozen=True)
class PlenaryVideo:
    id: str
    title: str
    speakers: str
    presentation_id: Optional[str]


@dataclass(frozen=True)
class PlenarySession:
    id: str
    title: str
    image: str
    day: str
    sessions: List[SessionInfo]
    presenter: Optional[str]
    introduction: Optional[str]
    institution: Optional[str]
    abstract: Optional[str]
    bio: Optional[str]
    # SlidesLive presentation ID
    presentation_id: Optional[str]
    rocketchat_channel: Optional[str]
    videos: List[PlenaryVideo]


@dataclass(frozen=True)
class CommitteeMember:
    role: str
    name: str
    aff: str
    image: Optional[str]
    pweb: str

@dataclass(frozen=True)
class TutorialSessionInfo:
    """The session information for a tutorial."""

    session_name: str
    start_time: datetime
    end_time: datetime
    hosts: str
    livestream_id: str
    zoom_link: str

    @property
    def time_string(self) -> str:
        start = self.start_time.astimezone(pytz.utc)
        end = self.end_time.astimezone(pytz.utc)
        return "({}-{} UTC)".format(start.strftime("%H:%M"), end.strftime("%H:%M"))

    @property
    def start_time_string(self) -> str:
        start_time = self.start_time.astimezone(pytz.utc)
        return start_time.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def end_time_string(self) -> str:
        end_time = self.end_time.astimezone(pytz.utc)
        return end_time.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def session(self) -> str:
        start = self.start_time.astimezone(pytz.utc)
        start_date = f'{start.strftime("%b")} {start.day}'
        return f"{self.session_name}: {start_date}"

    @property
    def day(self) -> str:
        start = self.start_time.astimezone(pytz.utc)
        start_date = f'{start.strftime("%b")} {start.day}'
        return start_date

@dataclass(frozen=True)
class TutorialAuthorInfo:
    """The session information for a tutorial."""

    author_name: str
    author_description:str

    def name(self) -> str:
        return self.author_name

    def description(self) -> str:
        return self.author_description


@dataclass(frozen=True)
class Tutorial:
    id: str
    title: str
    organizers: List[str]
    abstract: str
    details: str
#    website: Optional[str]
#    material: Optional[str]
#    slides: Optional[str]
#    prerecorded: Optional[str]
#    rocketchat_channel: str
#    sessions: List[TutorialSessionInfo]
#    authors: List[TutorialAuthorInfo]
#    blocks: List[SessionInfo]
#    virtual_format_description: str

@dataclass(frozen=True)
class DoctoralConsortium:
    id: str
    title: str
    organizers: List[str]
    abstract: str
    website: Optional[str]
    material: Optional[str]
    slides: Optional[str]
    prerecorded: Optional[str]
    rocketchat_channel: str
    sessions: List[SessionInfo]
    blocks: List[SessionInfo]
    virtual_format_description: str

@dataclass(frozen=True)
class Demonstrations:
    id: str
    title: str
    organizers: List[str]
    abstract: str
    website: Optional[str]
    material: Optional[str]
    slides: Optional[str]
    prerecorded: Optional[str]
    rocketchat_channel: str
    sessions: List[SessionInfo]
    blocks: List[SessionInfo]
    virtual_format_description: str

@dataclass(frozen=True)
class AiInPractice:
    id: str
    title: str
    organizers: List[str]
    abstract: str
    website: Optional[str]
    material: Optional[str]
    slides: Optional[str]
    prerecorded: Optional[str]
    rocketchat_channel: str
    sessions: List[SessionInfo]
    blocks: List[SessionInfo]
    virtual_format_description: str


@dataclass(frozen=True)
class WorkshopPaper:
    id: str
    title: str
    speakers: str
    presentation_id: Optional[str]
    content: PaperContent
    rocketchat_channel: str


@dataclass(frozen=True)
class Workshop:
    id: str
    title: str
    organizers: List[str]
    abstract: str
    website: str
    day: str
    livestream: Optional[str]
    papers: List[WorkshopPaper]
    schedule: List[Dict[str, Any]]
    prerecorded_talks: List[Dict[str, Any]]
    rocketchat_channel: str
    sessions: List[SessionInfo]
    blocks: List[SessionInfo]
    zoom_links: List[str]


@dataclass(frozen=True)
class SocialEventOrganizers:
    members: List[str]
    website: str


@dataclass(frozen=True)
class SocialEvent:
    id: str
    name: str
    description: str
    image: str
    location: str
    organizers: SocialEventOrganizers
    sessions: List[SessionInfo]
    rocketchat_channel: str
    website: str
    zoom_link: str

@dataclass(frozen=True)
class AwardTalk:
    session_name: str
    start_time: datetime
    end_time: datetime
    link: str


@dataclass(frozen=True)
class Awardee:
    id: str
    name: str
    link: str
    organization: str
    paperlink: str = None
    image: str = None
    description: str = None
    talk: SessionInfo = None

@dataclass(frozen=True)
class Award:
    id: str
    name: str
    awardees: List[Awardee]
    description: str = None
    


@dataclass(frozen=True)
class QaSubSession:
    name: str
    link: str
    papers: List[str]


@dataclass(frozen=True)
class QaSession:
    uid: str
    name: str
    start_time: datetime
    end_time: datetime
    subsessions: List[QaSubSession]

    @property
    def time_string(self) -> str:
        start = self.start_time.astimezone(pytz.utc)
        end = self.end_time.astimezone(pytz.utc)
        return "({}-{} UTC)".format(start.strftime("%H:%M"), end.strftime("%H:%M"))

    @property
    def day(self) -> str:
        start_time = self.start_time.astimezone(pytz.utc)
        return start_time.strftime("%b %d")

@dataclass(frozen=True)
class PosterInfo:
    uid: str
    time1: str
    time2: str
    room: str
    cluster: str
    cluster_name: str
    gather_town_link: str
    session_type : str
    papers: List[str]
    time3: str = None
