import copy
import csv
import glob
import itertools
import json
import os
from collections import OrderedDict, defaultdict
from datetime import timedelta
# from scripts.dataentry.tutorials import Session
from typing import Any, DefaultDict, Dict, List, Optional, Tuple

import jsons
import pytz
import yaml

from miniconf.site_data import (
    CommitteeMember,
    Paper,
    PaperContent,
    PlenarySession,
    PlenaryVideo,
    QaSession,
    QaSubSession,
    SessionInfo,
    SocialEvent,
    SocialEventOrganizers,
    Tutorial,
    TutorialSessionInfo,
    TutorialAuthorInfo,
    Workshop,
    WorkshopPaper,
    DoctoralConsortium,
    PosterInfo,
    Award,
    Awardee,
    Demonstrations,
    AiInPractice
)


def load_site_data(
    site_data_path: str, site_data: Dict[str, Any], by_uid: Dict[str, Any],
) -> List[str]:
    """Loads all site data at once.

    Populates the `committee` and `by_uid` using files under `site_data_path`.

    NOTE: site_data[filename][field]
    """
    registered_sitedata = {
        "config",
        # index.html
        "committee",
        # schedule.html
        "overall_calendar",
        "plenary_sessions",
        "opening_remarks",
        "teams",
        # tutorials.html
        "tutorials",
        # papers.html
        "AI for Social Impact Track_papers",
        "Demos_papers",
        "Doctoral Consortium_papers",
        "doctoral_consortium",
        "EAAI_papers",
        "IAAI_papers",
        "Main Track_papers",
        "Senior Member Track_papers",
        "Sister Conference_papers",
        "Student Abstracts_papers",
        "Undergraduate Consortium_papers",
        "award_papers",
        "poster_infos",
        "paper_recs",
        "papers_projection",
        "paper_sessions",
        # socials.html
        "socials",
        # workshops.html
        "workshops",
        "workshop_papers",
        # sponsors.html
        "sponsors",
        # about.html
        "awards",
        "code_of_conduct",
        "faq",
        "demonstrations",
        "ai_in_practice"
    }
    extra_files = []
    # Load all for your sitedata one time.
    for f in glob.glob(site_data_path + "/*"):
        filename = os.path.basename(f)
        if filename == "inbox":
            continue
        name, typ = filename.split(".")
        if name not in registered_sitedata:
            continue

        extra_files.append(f)
        if typ == "json":
            site_data[name] = json.load(open(f, encoding="utf-8"))
        elif typ in {"csv", "tsv"}:
            site_data[name] = list(csv.DictReader(open(f, encoding="utf-8")))
        elif typ == "yml":
            site_data[name] = yaml.load(open(f, encoding="utf-8").read(), Loader=yaml.SafeLoader)
    assert set(site_data.keys()) == registered_sitedata, registered_sitedata - set(
        site_data.keys()
    )

    display_time_format = "%H:%M"

    # index.html
    site_data["teams"] = build_committee(site_data["teams"]["teams"])

    # overall_schedule_week = copy.deepcopy(site_data["overall_calendar"])
    # for event in overall_schedule_week:
    #     event["view"] = "day"
    # site_data["overall_calendar"].extend(overall_schedule_week)


    # schedule.html
    generate_plenary_events(site_data)   # cha-cha Plenary
    generate_tutorial_events(site_data)  # chenqian  Tutorials
    generate_workshop_events(site_data)  # haiying   Workshops
    generate_dc_events(site_data)        # haiying   Doctoral Consortium
    # TODO: generate_uc_events(site_data)  chenqian   Undergraduate Consortium
    generate_paper_events(site_data)     # en-yue, mingkai  Posters
    # TODO: generate_diversity_events(site_data) # liu-xiao  Diversity and Inclusion

    generate_social_events(site_data)


    site_data["calendar"] = build_schedule(site_data["overall_calendar"])
    # site_data["event_types"] = list(
    #     {event["type"] for event in site_data["overall_calendar"]}
    # )
    site_data["event_types"] = ["AAAI Plenary", "IAAI Plenary", "EAAI", "Posters", "Workshops", "Tutorials", "Doctoral Consortium",
                 "Undergraduate Consortium", "Diversity and Inclusion",
                "Meet with a Fellow", "Sponsors/Exhibitors", "AI Job Fair"
               ]
    # plenary_sessions.html
    plenary_sessions = build_plenary_sessions(
        raw_plenary_sessions=site_data["plenary_sessions"],
        raw_plenary_videos={"opening_remarks": site_data["opening_remarks"]},
    )
    invited_panels = build_invited_panels_sessions(
        raw_plenary_sessions=site_data["plenary_sessions"],
        raw_plenary_videos={"opening_remarks": site_data["opening_remarks"]},
    )
    invited_speakers = build_invited_speakers_sessions(
        raw_plenary_sessions=site_data["plenary_sessions"],
        raw_plenary_videos={"opening_remarks": site_data["opening_remarks"]},
    )
    ai_in_practice = build_ai_in_practice_sessions(
        raw_plenary_sessions=site_data["plenary_sessions"],
        raw_plenary_videos={"opening_remarks": site_data["opening_remarks"]},
    )

    site_data["plenary_sessions"] = plenary_sessions
    by_uid["plenary_sessions"] = {
        plenary_session.id: plenary_session
        for _, plenary_sessions_on_date in plenary_sessions.items()
        for plenary_session in plenary_sessions_on_date
    }
    site_data["plenary_session_days"] = [
        [day.replace(" ", "").lower(), day, ""] for day in plenary_sessions
    ]
    site_data["plenary_session_days"][0][-1] = "active"


    # invited panels

    site_data["invited_panels"] = invited_panels
    site_data["invited_panels_days"] = [
        #update by mankind 2021/02/01
        [day.replace(" ", "").lower(), day, ""] for day in invited_panels if day.replace(" ", "").lower() not in ["feb4","feb6"]
    ]
    site_data["invited_panels_days"][0][-1] = "active"

    # invited speaker
    site_data["invited_speakers"] = invited_speakers
    site_data["invited_speakers_days"] = [
        [day.replace(" ", "").lower(), day, ""] for day in invited_speakers
    ]
    site_data["invited_speakers_days"][0][-1] = "active"

    # Ai in practice
    # ai_in_practice=build_tutorials(site_data["ai_in_practice"])
    # site_data["ai_in_practice"] = ai_in_practice
    site_data["ai_in_practice"] = ai_in_practice
    site_data["ai_in_practice_days"] = [
        [day.replace(" ", "").lower(), day, ""] for day in ai_in_practice
    ]
    site_data["ai_in_practice_days"][0][-1] = "active"

    # Papers' progam to their data
    for p in site_data["AI for Social Impact Track_papers"]:
        p["program"] = "AISI"
    for p in site_data["Demos_papers"]:
        p["program"] = "Demo"
    for p in site_data["Doctoral Consortium_papers"]:
        p["program"] = "DC"
    for p in site_data["EAAI_papers"]:
        p["program"] = "EAAI"
    for p in site_data["IAAI_papers"]:
        p["program"] = "IAAI"
    for p in site_data["Main Track_papers"]:
        p["program"] = "Main"
    for p in site_data["Senior Member Track_papers"]:
        p["program"] = "SMT"
    for p in site_data["Sister Conference_papers"]:
        p["program"] = "SC"
    for p in site_data["Student Abstracts_papers"]:
        p["program"] = "SA"
    for p in site_data["Undergraduate Consortium_papers"]:
        p["program"] = "UC"
    for p in site_data["award_papers"]:
        p["program"] = "Award"

    site_data["programs"] = ["AISI", "Demo", "DC",
                             "EAAI", "IAAI","Main","SMT","SC",
                             "SA","UC","Award","Best"]

    # tutorials.html
    tutorial_MQ = []
    tutorial_MH = []
    tutorial_AQ = []
    tutorial_AH = []

    # IAAI poster presentation
    iaai_poster_schedule = {}
    iaai_poster_schedule['Feb 4'] = {}
    iaai_poster_schedule['Feb 5'] = {}
    iaai_poster_schedule['Feb 6'] = {}
    iaai_poster_schedule['Feb 4']['Aerospace'] = [74,132,171]
    iaai_poster_schedule['Feb 4']['Commerce'] = [23,84,87,92,93,101,140,179,190]
    iaai_poster_schedule['Feb 4']['Security'] = [98,113,142]
    iaai_poster_schedule['Feb 5']['General'] = [104]
    iaai_poster_schedule['Feb 5']['Engineering'] = [100,105,165,176]
    iaai_poster_schedule['Feb 5']['Knowledge'] = [21,37,59,65,119,151,157,174]
    iaai_poster_schedule['Feb 5']['Natural Language Processing'] = [89]
    iaai_poster_schedule['Feb 5']['Prediction'] = [43,55]
    iaai_poster_schedule['Feb 6']['Artificial Intelligence'] = [17,31,60,73,167]
    iaai_poster_schedule['Feb 6']['Bioscience'] = [76,77,124,145,146,149]
    iaai_poster_schedule['Feb 6']['COVID'] = [152,154]
    iaai_poster_schedule['Feb 6']['Driving'] = [34]
    iaai_poster_schedule['Feb 6']['Intelligent Technology'] = [99]

    site_data["iaai_poster_schedule"] = iaai_poster_schedule
    site_data["iaai_poster_schedule_days"] = [[day] for day in list(iaai_poster_schedule.keys())]
    site_data["iaai_poster_schedule_days"] = site_data['plenary_session_days'][:-1]
    # site_data["iaai_poster_schedule_days"] = [1,2,3,4]
    site_data["iaai_poster_schedule_days"][0][-1] = "active"
    # for i in range(len(site_data["iaai_poster_schedule_days"])):
    #     site_data["iaai_poster_schedule_days"][i][-1] = "active"
    # site_data["iaai_poster_schedule_days"] = site_data['plenary_session_days'][:]


        # [[day.replace(" ", "").lower(), day, ""] for day in iaai_poster_schedule.keys()]


    # undergraduate_consortium.html
    tutorial_UC = []
    tutorial_OTHER = []
    tutorial_FH = []

    part1,part2,part3,part4 = [],[],[],[]
    for item in site_data["tutorials"]:
        if "part1" in item["part"]:
            part1.append(item)
        if "part2" in item["part"]:
            part2.append(item)
        if "part3" in item["part"]:
            part3.append(item)
        if "part4" in item["part"]:
            part4.append(item)
        if item["UID"] == "UC":
            tutorial_OTHER.append(item)
        if "UC" in item["UID"]:
            tutorial_UC.append(item)
        if "FH" in item["UID"]:
            tutorial_FH.append(item)

    tutorials = build_tutorials(site_data["tutorials"])

    site_data["tutorials"] = tutorials
#    site_data["tutorial_calendar"] = build_tutorial_schedule(
#        site_data["overall_calendar"]
#    )
    site_data["part1"] = build_tutorials(part1)
    site_data["part2"] = build_tutorials(part2)
    site_data["part3"] = build_tutorials(part3)
    site_data["part4"] = build_tutorials(part4)
#    site_data["tutorials_UC"] = build_tutorials(tutorial_UC)
#    site_data["tutorials_FH"] = build_tutorials(tutorial_FH)
#    site_data["tutorials_OTHER"] = build_tutorials(tutorial_OTHER)
    # tutorial_<uid>.html
    by_uid["tutorials"] = {tutorial.id: tutorial for tutorial in tutorials}

    # workshops.html
    workshops = build_workshops(
        raw_workshops=site_data["workshops"],
        raw_workshop_papers=site_data["workshop_papers"],
    )
    site_data["workshops"] = workshops
    # workshop_<uid>.html
    # by_uid["workshops"] = {workshop.id: workshop for workshop in workshops}
    by_uid["workshops"] = {
        workshop.id: workshop
        for _, workshops_on_date in workshops.items()
        for workshop in workshops_on_date
    }

    site_data["workshop_days"] = [
        [day.replace(" ", "").lower(), day, ""] for day in workshops
    ]
    site_data["workshop_days"][0][-1] = "active"

    # Doctoral Consortium
    doctoral_consortium=build_doctoral_consortium(site_data["doctoral_consortium"])
    site_data["doctoral_consortium"] = doctoral_consortium

    # Demonstrations
#    demonstrations=build_tutorials(site_data["demonstrations"])
#    site_data["demonstrations"] = demonstrations

    # socials.html/diversity_programs.html
    diversity_programs = build_socials(site_data["socials"])
    site_data["diversity_programs"] = diversity_programs
    by_uid["diversity_programs"] = {
        dp.id: dp for _, dp_day in diversity_programs.items() for dp in dp_day
    }
    site_data["diversity_programs_days"] = [
        [day.replace(" ", "").lower(), day, ""] for day in diversity_programs
    ]
    site_data["diversity_programs_days"].sort()
    site_data["diversity_programs_days"][0][-1] = "active"
    # organization awards
    awards = build_awards(site_data['awards'])
    site_data['awards'] = awards

    # papers.{html,json}
    # print(site_data["Main Track_papers"])
    papers = build_papers(
        raw_papers=site_data["AI for Social Impact Track_papers"]+
            site_data["Demos_papers"]+
            site_data["Doctoral Consortium_papers"]+
            site_data["EAAI_papers"]+
            site_data["IAAI_papers"]+
            site_data["Main Track_papers"]+
            site_data["Senior Member Track_papers"]+
            site_data["Sister Conference_papers"]+
            site_data["Student Abstracts_papers"]+
            site_data["award_papers"]+
            site_data["Undergraduate Consortium_papers"],
        poster_infos=site_data["poster_infos"],
        paper_recs=site_data["paper_recs"],
        paper_images_path=site_data["config"]["paper_images_path"],
        default_image_path=site_data["config"]["logo"]["image"]
    )
    # remove workshop paper in papers.html
    # for wsh in site_data["workshops"]:
    #     papers.extend(wsh.papers)
    site_data["papers"] = papers

    site_data["tracks"] = list(
        sorted(track for track in {paper.content.track for paper in papers})
    )

    site_data["main_program_tracks"] = list(
        sorted(
            track
            for track in {
                paper.content.track
                for paper in papers
                if paper.content.program == "main"
            }
        )
    )
    # paper_<uid>.html
    papers_by_uid: Dict[str, Any] = {}
    for paper in papers:
        assert paper.id not in papers_by_uid, paper.id
        papers_by_uid[paper.id] = paper
    by_uid["papers"] = papers_by_uid
    # serve_papers_projection.json
    all_paper_ids_with_projection = {
        item["id"] for item in site_data["papers_projection"]
    }
    for paper_id in set(by_uid["papers"].keys()) - all_paper_ids_with_projection:
        paper = by_uid["papers"][paper_id]
        if paper.content.program == "main":
            print(f"WARNING: {paper_id} does not have a projection")

    # about.html
    site_data["faq"] = site_data["faq"]["FAQ"]
    site_data["code_of_conduct"] = site_data["code_of_conduct"]["CodeOfConduct"]

    # sponsors.html
    build_sponsors(site_data, by_uid, display_time_format)

    # posters.html
    site_data["poster_info_by_day"], site_data["poster_days"], site_data["room_list_by_day"] = build_poster_infos(
        site_data["poster_infos"],by_uid["papers"],site_data["papers"]
    )

    # site_data["main_aisi_smt_by_day"] = {
    #     day: list(sessions)
    #     for day, sessions in itertools.groupby(
    #         site_data["main_aisi_smt"], lambda qa: qa.day
    #     )
    # }

    print("Data Successfully Loaded")
    return extra_files


def extract_list_field(v, key):
    value = v.get(key, "")
    if isinstance(value, list):
        return value
    else:
        return value.split("|")


def build_committee(
    raw_committee: List[Dict[str, Any]]
) -> Dict[str, List[CommitteeMember]]:
    # We want to show the committee grouped by role. Grouping has to be done in python since jinja's groupby sorts
    # groups by name, i.e. the general chair would not be on top anymore because it doesn't start with A.
    # See https://github.com/pallets/jinja/issues/250

    committee = [jsons.load(item, cls=CommitteeMember) for item in raw_committee]
    committee_by_role = OrderedDict()
    for role, members in itertools.groupby(committee, lambda member: member.role):
        member_list = list(members)
        # add plural 's' to "chair" roles with multiple members
        if role.lower().endswith("chair") and len(member_list) > 1:
            role += "s"
        committee_by_role[role] = member_list

    return committee_by_role

def build_awards(raw_awards: List[Dict[str, Any]]) -> List[Award]:
    # print(raw_awards)
    return [
        Award(
            id=award["id"],
            name=award["name"],
            description=award["description"],
            awardees=[Awardee(
                name=awardee['name'],
                id=awardee['id'],
                link=awardee['link'] if 'link' in awardee.keys() else None,
                description=awardee['description'] if 'description' in awardee.keys() else None,
                paperlink=awardee['paperlink'] if 'paperlink' in awardee.keys() else None,
                image=awardee['image'] if 'image' in awardee.keys() else None,
                organization=awardee['organization'],
                talk=[SessionInfo(session_name = awardee['talk'][idx]['session_name'], 
                                start_time=awardee['talk'][idx]['start_time'],
                                end_time=awardee['talk'][idx]['end_time'],
                                link=awardee['talk'][idx]['link']) for idx in range(len(awardee['talk']))]
                                if 'talk' in awardee.keys() else None
            ) for awardee in award['awardees']]
        )
        for award in raw_awards
    ]

def build_plenary_sessions(
    raw_plenary_sessions: List[Dict[str, Any]],
    raw_plenary_videos: Dict[str, List[Dict[str, Any]]],
) -> DefaultDict[str, List[PlenarySession]]:

    plenary_videos: DefaultDict[str, List[PlenaryVideo]] = defaultdict(list)
    for plenary_id, videos in raw_plenary_videos.items():
        for item in videos:
            plenary_videos[plenary_id].append(
                PlenaryVideo(
                    id=item["UID"],
                    title=item["title"],
                    speakers=item["speakers"],
                    presentation_id=item["presentation_id"],
                )
            )

    plenary_sessions: DefaultDict[str, List[PlenarySession]] = defaultdict(list)
    for item in raw_plenary_sessions:
        plenary_sessions[item["day"]].append(
            PlenarySession(
                id=item["UID"],
                title=item["title"],
                image=item["image"],
                day=item["day"],
                sessions=[
                    SessionInfo(
                        session_name=session.get("name"),
                        start_time=session.get("start_time"),
                        end_time=session.get("end_time"),
                        link=session.get("zoom_link"),
                    )
                    for session in item.get("sessions")
                ],
                presenter=item.get("presenter"),
                introduction = item.get("introduction"),
                institution=item.get("institution"),
                abstract=item.get("abstract"),
                bio=item.get("bio"),
                presentation_id=item.get("presentation_id"),
                rocketchat_channel=item.get("rocketchat_channel"),
                videos=plenary_videos.get(item["UID"]),
            )
        )

    return plenary_sessions


def build_invited_panels_sessions(
    raw_plenary_sessions: List[Dict[str, Any]],
    raw_plenary_videos: Dict[str, List[Dict[str, Any]]],
) -> DefaultDict[str, List[PlenarySession]]:

    plenary_videos: DefaultDict[str, List[PlenaryVideo]] = defaultdict(list)
    for plenary_id, videos in raw_plenary_videos.items():
        for item in videos:
            if 'panel' in item["UID"]:
                plenary_videos[plenary_id].append(
                    PlenaryVideo(
                        id=item["UID"],
                        title=item["title"],
                        speakers=item["speakers"],
                        presentation_id=item["presentation_id"],
                    )
                )

    plenary_sessions: DefaultDict[str, List[PlenarySession]] = defaultdict(list)
    for item in raw_plenary_sessions:
        if 'panel' in item["UID"]:
            plenary_sessions[item["day"]].append(
            PlenarySession(
                id=item["UID"],
                title=item["title"],
                image=item["image"],
                day=item["day"],
                sessions=[
                    SessionInfo(
                        session_name=session.get("name"),
                        start_time=session.get("start_time"),
                        end_time=session.get("end_time"),
                        link=session.get("zoom_link"),
                    )
                    for session in item.get("sessions")
                ],
                presenter=item.get("presenter"),
                introduction=item.get("introduction"),
                institution=item.get("institution"),
                abstract=item.get("abstract"),
                bio=item.get("bio"),
                presentation_id=item.get("presentation_id"),
                rocketchat_channel=item.get("rocketchat_channel"),
                videos=plenary_videos.get(item["UID"]),
            )
            )

    return plenary_sessions

def build_invited_speakers_sessions(
    raw_plenary_sessions: List[Dict[str, Any]],
    raw_plenary_videos: Dict[str, List[Dict[str, Any]]],
) -> DefaultDict[str, List[PlenarySession]]:

    plenary_videos: DefaultDict[str, List[PlenaryVideo]] = defaultdict(list)
    for plenary_id, videos in raw_plenary_videos.items():
        for item in videos:
            if item["UID"].startswith("speaker"):
                plenary_videos[plenary_id].append(
                    PlenaryVideo(
                        id=item["UID"],
                        title=item["title"],
                        speakers=item["speakers"],
                        presentation_id=item["presentation_id"],
                    )
                )

    plenary_sessions: DefaultDict[str, List[PlenarySession]] = defaultdict(list)
    for item in raw_plenary_sessions:
        if item["UID"].startswith("speaker"):
            plenary_sessions[item["day"]].append(
            PlenarySession(
                id=item["UID"],
                title=item["title"],
                image=item["image"],
                day=item["day"],
                sessions=[
                    SessionInfo(
                        session_name=session.get("name"),
                        start_time=session.get("start_time"),
                        end_time=session.get("end_time"),
                        link=session.get("zoom_link"),
                    )
                    for session in item.get("sessions")
                ],
                presenter=item.get("presenter"),
                introduction=item.get("introduction"),
                institution=item.get("institution"),
                abstract=item.get("abstract"),
                bio=item.get("bio"),
                presentation_id=item.get("presentation_id"),
                rocketchat_channel=item.get("rocketchat_channel"),
                videos=plenary_videos.get(item["UID"]),
            )
            )

    return plenary_sessions


def build_ai_in_practice_sessions(
    raw_plenary_sessions: List[Dict[str, Any]],
    raw_plenary_videos: Dict[str, List[Dict[str, Any]]],
) -> DefaultDict[str, List[PlenarySession]]:

    plenary_videos: DefaultDict[str, List[PlenaryVideo]] = defaultdict(list)
    for plenary_id, videos in raw_plenary_videos.items():
        for item in videos:
            if 'AI in Practice Panel' in item["title"]:
                plenary_videos[plenary_id].append(
                    PlenaryVideo(
                        id=item["UID"],
                        title=item["title"],
                        speakers=item["speakers"],
                        presentation_id=item["presentation_id"],
                    )
                )

    plenary_sessions: DefaultDict[str, List[PlenarySession]] = defaultdict(list)
    for item in raw_plenary_sessions:
        if 'AI in Practice Panel' in item["title"]:
            plenary_sessions[item["day"]].append(
            PlenarySession(
                id=item["UID"],
                title=item["title"],
                image=item["image"],
                day=item["day"],
                sessions=[
                    SessionInfo(
                        session_name=session.get("name"),
                        start_time=session.get("start_time"),
                        end_time=session.get("end_time"),
                        link=session.get("zoom_link"),
                    )
                    for session in item.get("sessions")
                ],
                presenter=item.get("presenter"),
                introduction=item.get("introduction"),
                institution=item.get("institution"),
                abstract=item.get("abstract"),
                bio=item.get("bio"),
                presentation_id=item.get("presentation_id"),
                rocketchat_channel=item.get("rocketchat_channel"),
                videos=plenary_videos.get(item["UID"]),
            )
            )

    return plenary_sessions

def generate_plenary_events(site_data: Dict[str, Any]):
    """ We add sessions from the plenary for the weekly and daily view. """
    # Add plenary sessions to calendar
    all_sessions = []
    for plenary in site_data["plenary_sessions"]:
        if plenary["UID"] =='opening_remarks_speaker_by_tuomas_sandholm':
            continue
        if plenary["UID"] == 'speaker_by_michael_wooldridge':
            continue
        uid = plenary["UID"]

        if plenary["title"] == "Opening Ceremony and Conference Awards" or "AAAI/IAAI" in plenary["title"]:
            plenary_type = "Plenary-AAAI/IAAI"
        elif plenary["title"] == "2021 Robert S. Engelmore Memorial Award Lecture":
            plenary_type = "Plenary-AAAI/IAAI"
        elif "IAAI" in plenary["title"]:
            plenary_type = "IAAI Plenary"
        else:
            plenary_type = "AAAI Plenary"

        if plenary["UID"] == 'opening_remarks' or plenary["UID"] == 'speaker_by_tuomas_sandholm':
            for session in plenary["sessions"]:
                start = session["start_time"]
                end = session["end_time"]

                event = {
                    "title": "<b>" + plenary["title"] + "</b>",
                    "start": start,
                    "end": end,
                    "location": f"plenary_session_opening_remarks_speaker_by_tuomas_sandholm.html",
                    "link": f"plenary_session_opening_remarks_speaker_by_tuomas_sandholm.html",
                    "category": "time",
                    "type": plenary_type,
                    "view": "day",
                }
        else:
            for session in plenary["sessions"]:
                start = session["start_time"]
                end = session["end_time"]
                event = {
                    "title": "<b>" + plenary["title"] + "</b>",
                    "start": start,
                    "end": end,
                    "location": f"plenary_session_{uid}.html",
                    "link": f"plenary_session_{uid}.html",
                    "category": "time",
                    "type": plenary_type,
                    "view": "day",
                }

        site_data["overall_calendar"].append(event)
        assert start < end, "Session start after session end"

        all_sessions.append(session)

    blocks = compute_schedule_blocks(all_sessions)

    # Compute start and end of tutorial blocks
    for block in blocks:
        min_start = min([t["start_time"] for t in block])
        max_end = max([t["end_time"] for t in block])

        tz = pytz.timezone("America/Santo_Domingo")
        punta_cana_date = min_start.astimezone(tz)

        tab_id = punta_cana_date.strftime("%b%d").lower()

        event = {
            "title": "Plenary Session",
            "start": min_start,
            "end": max_end,
            "location": f"plenary_sessions.html#tab-{tab_id}",
            "link": f"plenary_sessions.html#tab-{tab_id}",
            "category": "time",
            "type": "Plenary Sessions",
            "view": "week",
        }
        # site_data["overall_calendar"].append(event)


def generate_tutorial_events(site_data: Dict[str, Any]):
    """ We add sessions from tutorials and compute the overall tutorial blocks for the weekly view. """

    # Add tutorial sessions to calendar
    all_sessions: List[Dict[str, Any]] = []
    uc_sessions: List[Dict[str, Any]] = []
    for tutorial in site_data["tutorials"]:
        if "UC" in tutorial["UID"]:
            uid = tutorial["UID"]
            blocks = compute_schedule_blocks(tutorial["sessions"])

            for block in blocks:
                min_start = min([t["start_time"] for t in block])
                max_end = max([t["end_time"] for t in block])
                if uid == "UC":
                    event = {
                        "title": f"{tutorial['title']}</b><br/><i>{tutorial['organizers']}</i>",
                        "start": min_start,
                        "end": max_end,
                        "location": f"undergraduate_consortium.html",
                        "link": f"undergraduate_consortium.html",
                        "category": "time",
                        "type": "Undergraduate Consortium",
                        "view": "day",
                    }
                else:
                    event = {
                        "title": f"<b>Undergraduate Consortium</b><br/><b>{uid}: {tutorial['title']}</b><br/><i>{tutorial['organizers']}</i>",
                        "start": min_start,
                        "end": max_end,
                        "location": f"paper_{uid}.html",
                        "link": f"paper_{uid}.html",
                        "category": "time",
                        "type": "Undergraduate Consortium",
                        "view": "day",
                    }
                site_data["overall_calendar"].append(event)
                assert min_start < max_end, "Session start after session end"

            uc_sessions.extend(tutorial["sessions"])
        else:
            uid = tutorial["UID"]
#            blocks = compute_schedule_blocks(tutorial["sessions"])
#
#            for block in blocks:
#                min_start = min([t["start_time"] for t in block])
#                max_end = max([t["end_time"] for t in block])
#                event = {
#                    "title": f"<b>Tutorial Forum</b><br/>{uid}: {tutorial['title']}</b><br/><i>{tutorial['organizers']}</i>",
#                    "start": min_start,
#                    "end": max_end,
#                    "location": f"tutorial_{uid}.html",
#                    "link": f"tutorial_{uid}.html",
#                    "category": "time",
#                    "type": "Tutorials",
#                    "view": "day",
#                }
#                site_data["overall_calendar"].append(event)
#                assert min_start < max_end, "Session start after session end"
#
#            all_sessions.extend(tutorial["sessions"])

    # blocks = compute_schedule_blocks(all_sessions)
    #
    # # Compute start and end of tutorial blocks
    # for block in blocks:
    #     min_start = min([t["start_time"] for t in block])
    #     max_end = max([t["end_time"] for t in block])
    #
    #     event = {
    #         "title": "Tutorials",
    #         "start": min_start,
    #         "end": max_end,
    #         "location": "tutorials.html",
    #         "link": "tutorials.html",
    #         "category": "time",
    #         "type": "Tutorials",
    #         "view": "week",
    #     }
    #     site_data["overall_calendar"].append(event)
    #
    # uc_blocks = compute_schedule_blocks(uc_sessions)
    #
    # # Compute start and end of tutorial blocks
    # for block in uc_blocks:
    #     min_start = min([t["start_time"] for t in block])
    #     max_end = max([t["end_time"] for t in block])
    #
    #     event = {
    #         "title": "Undergraduate Consortium",
    #         "start": min_start,
    #         "end": max_end,
    #         "location": "undergraduate_consortium.html",
    #         "link": "undergraduate_consortium.html",
    #         "category": "time",
    #         "type": "Undergraduate Consortium",
    #         "view": "week",
    #     }
    #     site_data["overall_calendar"].append(event)

def generate_dc_events(site_data: Dict[str, Any]):
    """ We add sessions from tutorials and compute the overall dc blocks for the weekly view. """

    # Add tutorial sessions to calendar
    all_sessions: List[Dict[str, Any]] = []
    for dc in site_data["doctoral_consortium"]:
        uid = dc["UID"]
        blocks = compute_schedule_blocks(dc["sessions"])

        for block in blocks:
            min_start = min([t["start_time"] for t in block])
            max_end = max([t["end_time"] for t in block])
            event = {
                "title": f"<b>Doctoral Consortium</b>",
                "start": min_start,
                "end": max_end,
                "location": f"doctoral_consortium.html",
                "link": f"doctoral_consortium.html",
                "category": "time",
                "type": "Doctoral Consortium",
                "view": "day",
            }
            site_data["overall_calendar"].append(event)
            assert min_start < max_end, "Session start after session end"

        all_sessions.extend(dc["sessions"])

    blocks = compute_schedule_blocks(all_sessions)

    # # Compute start and end of tutorial blocks
    # for block in blocks:
    #     min_start = min([t["start_time"] for t in block])
    #     max_end = max([t["end_time"] for t in block])
    #
    #     event = {
    #         "title": "Doctoral Consortium",
    #         "start": min_start,
    #         "end": max_end,
    #         "location": "doctoral_consortium.html",
    #         "link": "doctoral_consortium.html",
    #         "category": "time",
    #         "type": "Doctoral Consortium",
    #         "view": "week",
    #     }
    #     site_data["overall_calendar"].append(event)


def generate_workshop_events(site_data: Dict[str, Any]):
    """ We add sessions from workshops and compute the overall workshops blocks for the weekly view. """
    # Add workshop sessions to calendar
    all_sessions: List[Dict[str, Any]] = []
    duplicate_sessions: List[str] = []
    for workshop in site_data["workshops"]:
        uid = workshop["UID"]
        if uid not in duplicate_sessions:
            all_sessions.extend(workshop["sessions"])
            duplicate_sessions.append(uid)

            for block in compute_schedule_blocks(workshop["sessions"]):
                min_start = min([t["start_time"] for t in block])
                max_end = max([t["end_time"] for t in block])

                event = {
                    "title": f"<b>Workshop</b><br/> <b>{workshop['title']}</b><br/> <i>{workshop['organizers']}</i>",
                    "start": min_start,
                    "end": max_end,
                    "location": f"workshop_{uid}.html",
                    "link": f"workshop_{uid}.html",
                    "category": "time",
                    "type": "Workshops",
                    "view": "day",
                }
                site_data["overall_calendar"].append(event)

                assert min_start < max_end, "Session start after session end"

    blocks = compute_schedule_blocks(all_sessions)

    # # Compute start and end of workshop blocks
    # for block in blocks:
    #     min_start = min([t["start_time"] for t in block])
    #     max_end = max([t["end_time"] for t in block])
    #
    #     event = {
    #         "title": "Workshops",
    #         "start": min_start,
    #         "end": max_end,
    #         "location": "workshops.html",
    #         "link": "workshops.html",
    #         "category": "time",
    #         "type": "Workshops",
    #         "view": "week",
    #     }
    #     site_data["overall_calendar"].append(event)


def generate_paper_events(site_data: Dict[str, Any]):
    """ We add sessions from papers and compute the overall paper blocks for the weekly view. """
    # Add paper sessions to calendar

    all_grouped: Dict[str, List[Any]] = defaultdict(list)
    for uid, session in site_data["paper_sessions"].items():
        day = uid[0]
        if "Award" in uid:
            cluster = ""
            room = uid[2:-1]
        else:
            cluster = uid[-1]
            room = uid[2:-2]
        session["cluster"] = cluster
        session["room"] = room
        all_grouped[day].append(session)
    for day in all_grouped.keys():
        all_grouped[day].sort(key=lambda x: (x["room"],x["cluster"]))
        for session in all_grouped[day]:
            start = session["start_time"]
            end = session["end_time"]
            room = session["room"]
            cluster = session["cluster"]
            cluster_name = session['cluster_name']
            if "D1" in room:
                tab_id = "feb4"
            if "D2" in room:
                tab_id = "feb5"
            if "D3" in room:
                tab_id = "feb6"
            if "D4" in room:
                tab_id = "feb7"
            if "DEMO" in room:
                session_type = "Demo"
            else:
                session_type = "Poster"
            if cluster != "":
                title = f"<b>{session_type} Session</b><br><span>Room:{room}, Cluser:{cluster}</span><br><i>{cluster_name}<i>"
            else:
                title = f"<b>{session_type} Session</b><br><span>Room:{room}</span><br><i>{cluster_name}<i>"
            if "D1" in room:
                link = f"posters.html?#{room}-{cluster}"
            else:
                link = f"posters_{tab_id}.html?#{room}-{cluster}"
            event = {
                "title": title,
                "start": start,
                "end": end,
                "location": "",
                "link": link,
                "category": "time",
                "type": "Posters",
                "view": "day",
            }
            site_data["overall_calendar"].append(event)

            assert start < end, "Session start after session end"


def generate_social_events(site_data: Dict[str, Any]):
    """ We add social sessions and compute the overall paper social for the weekly view. """
    # Add paper sessions to calendar

    all_sessions = []
    for social in site_data["socials"]:
        for session in social["sessions"]:
            start = session["start_time"]
            end = session["end_time"]

            uid = social["UID"]
            # if uid.startswith("B"):
            #     name = "<b>Birds of a Feather</b><br>" + social["name"]
            # elif uid.startswith("A"):
            #     name = "<b>Affinity group meeting</b><br>" + social["name"]
            # else:
            name = social["name"]
            # day = session.day.replace(" ", "").lower()
            # start_time = start.astimezone(pytz.utc)
            day = f'{start.strftime("%b")} {start.day}'
            day = day.lower().replace(" ", "")
            # print(day)
            event = {
                "title": "<b>Diversity Program</b>: {}".format(name),
                "start": start,
                "end": end,
                "location": "",
                "link": "diversity_programs.html#tab-{}".format(day),
                "category": "time",
                "type": "Diversity and Inclusion",
                "view": "day",
            }
            site_data["overall_calendar"].append(event)

            assert start < end, "Session start after session end"

            all_sessions.append(session)

    blocks = compute_schedule_blocks(all_sessions)

    # Compute start and end of tutorial blocks
    # for block in blocks:
    #     min_start = min([t["start_time"] for t in block])
    #     max_end = max([t["end_time"] for t in block])

    #     event = {
    #         "title": f"Diversity Programs",
    #         "start": min_start,
    #         "end": max_end,
    #         "location": "",
    #         "link": f"diversity_programs.html",
    #         "category": "time",
    #         "type": "Diversity and Inclusion",
    #         "view": "week",
    #     }
    #     site_data["overall_calendar"].append(event)


def build_schedule(overall_calendar: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    event_type = list(
        {event["type"] for event in overall_calendar}
    )
    events = copy.deepcopy(overall_calendar)

    # events = [
    #     copy.deepcopy(event)
    #     for event in overall_calendar
    #     if event["type"]
    #     in {
    #         "Plenary Sessions",
    #         "Tutorials",
    #         "Workshops",
    #         "QA Sessions",
    #         "Socials",
    #         "Sponsors",
    #         "Undergraduate Consortium",
    #         "Doctoral Consortium",
    #     }
    # ]
    
    classnames = []

    for event in events:
        event_type = event["type"]
        if "Plenary" in event_type:
            event["classNames"] = ["calendar-event-plenary"]
        else:
            event["classNames"] = ["calendar-event-" + event_type.lower().replace(" ", "").replace("/", "")]
        classnames.append(event["classNames"][0])

        event["url"] = event["link"]
        # if event_type == "Plenary Sessions":
        #     event["classNames"] = ["calendar-event-plenary"]
        #     event["url"] = event["link"]
        # elif event_type == "Tutorials":
        #     event["classNames"] = ["calendar-event-tutorial"]
        #     event["url"] = event["link"]
        # elif event_type == "Workshops":
        #     event["classNames"] = ["calendar-event-workshops"]
        #     event["url"] = event["link"]
        # elif event_type == "QA Sessions":
        #     event["classNames"] = ["calendar-event-qa"]
        #     event["url"] = event["link"]
        # elif event_type == "Socials":
        #     event["classNames"] = ["calendar-event-socials"]
        #     event["url"] = event["link"]
        # elif event_type == "Sponsors":
        #     event["classNames"] = ["calendar-event-sponsors"]
        #     event["url"] = event["link"]
        # elif event_type == "Undergraduate Consortium":
        #     event["classNames"] = ["calendar-event-uc"]
        #     event["url"] = event["link"]
        # elif event_type == "Doctoral Consortium":
        #     event["classNames"] = ["calendar-event-dc"]
        #     event["url"] = event["link"]
        # else:
        #     event["classNames"] = ["calendar-event-other"]
        #     event["url"] = event["link"]
        #

        # event["classNames"].append("calendar-event")
    return events


def build_tutorial_schedule(
    overall_calendar: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    events = [
        copy.deepcopy(event)
        for event in overall_calendar
        if event["type"] in {"Tutorials"}
    ]

    for event in events:
        event["classNames"] = ["calendar-event-tutorial"]
        event["url"] = event["link"]
        event["classNames"].append("calendar-event")
    return events


def normalize_track_name(track_name: str) -> str:
    if track_name == "SRW":
        return "Student Research Workshop"
    elif track_name == "Demo":
        return "System Demonstrations"
    return track_name


def get_card_image_path_for_paper(paper_id: str, paper_images_path: str, default_image_path: str) -> str:
    file_name = f"{paper_images_path}/{paper_id}.png"
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # get root path
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    abs_file_name = os.path.join(root_path,file_name)
    if os.path.exists(abs_file_name):
        return f"{paper_images_path}/{paper_id}.png"
    else:
        return default_image_path


def build_papers(
    raw_papers: List[Dict[str, str]],
    poster_infos: Dict[str, Any],
    paper_recs: Dict[str, List[str]],
    paper_images_path: str,
    default_image_path: str
) -> List[Paper]:
    """Builds the site_data["papers"].

    Each entry in the papers has the following fields:
    - UID: str
    - title: str
    - authors: str (separated by '|')
    - keywords: str (separated by '|')
    - track: str
    - paper_type: str (i.e., "Long", "Short", "SRW", "Demo")
    - pdf_url: str
    - demo_url: str

    """
    # build the lookup from (paper, slot) to zoom_link
    paper_id_to_link: Dict[str, str] = {}
    paper_id_to_cluster_name : Dict[str, str] = {}
    for uid, rs in poster_infos.items():
        if "Award" in uid:
            cluster = ""
            room = uid[:-1]
        else:
            cluster = uid.split("-")[-1]
            room = uid[:-2]
        papers = rs["papers"]
        for paper_id in rs["papers"]:
            paper_id_to_link[paper_id] = "www.baidu.com" #TODO gather town link
            paper_id_to_cluster_name[paper_id] = rs["cluster_name"]

    # # build the lookup from paper to slots
    # sessions_for_paper: DefaultDict[str, List[SessionInfo]] = defaultdict(list)
    # for session_name, session_info in paper_sessions.items():
    #     start_time = session_info["start_time"]
    #     end_time = session_info["end_time"]
    #
    #     for paper_id in session_info["papers"]:
    #         #TODO  continue deal with it when we get session data
    #         # pass
    #         link = paper_id_to_link[paper_id]
    #         sessions_for_paper[paper_id].append(
    #             SessionInfo(
    #                 session_name=session_name,
    #                 start_time=start_time,
    #                 end_time=end_time,
    #                 link=link,
    #             )
    #         )
    whole_day_map = {
        "4-Feb": [('4-Feb', '08:45AM-10:30AM'), ('4-Feb', '04:45PM-06:30PM'), ('5-Feb', '12:45AM-02:30AM')],
        "5-Feb": [('5-Feb', '08:45AM-10:30AM'), ('5-Feb', '04:45PM-06:30PM'), ('6-Feb', '12:45AM-02:30AM')],
        "6-Feb": [('6-Feb', '08:45AM-10:30AM'), ('6-Feb', '04:45PM-06:30PM'), ('7-Feb', '12:45AM-02:30AM')],
        "7-Feb": [('7-Feb', '08:45AM-10:30AM'), ('7-Feb', '04:45PM-06:30PM'), ('8-Feb', '12:45AM-02:30AM')],
    }

    '''
    best_type
    1.(Best Papers Award)AAAI-7346,AAAI-2294,AISI-8076
    2(Best Paper Runners Up Award)AAAI-9868,AAAI-10151,AISI-4906
    3(Distinguished Papers Award)AAAI-8265,AAAI-3534,AAAI-2549,AAAI-10339,AAAI-4640,AAAI-7047
    '''
    best_papers_award = ['AAAI-7346','AAAI-2294','AISI-8076']
    best_paper_runners_up_award = ['AAAI-9868','AAAI-10151','AISI-4906']
    distinguished_papers_award = ['AAAI-8265','AAAI-3534','AAAI-2549','AAAI-10339','AAAI-4640','AAAI-7047']
    for item in raw_papers:
        if item['UID'] in paper_id_to_cluster_name :
            item['cluster_name'] = paper_id_to_cluster_name[item['UID']]
        if item['UID'] in best_papers_award:
            item['best_type']=1
            item['best_type_desc'] = "Best Papers Award"
        if item['UID'] in best_paper_runners_up_award:
            item['best_type']=2
            item['best_type_desc'] = "Best Paper Runners Up Award"
        if item['UID'] in distinguished_papers_award:
            item['best_type']=3
            item['best_type_desc'] = "Distinguished Papers Award"
        if "CLASSIC" in item["UID"] or "DISS" in item["UID"]:
            item['room'] = item['room'][:-1]
        if item.get("position","")=="" or item["position"] is None:
            item['position'] = 0
        if item.get('time1') == "" and item.get('date1')!= "":
            date1 = item.get('date1')
            for i, (date, time) in enumerate(whole_day_map[date1]):
                if i == 0:
                    item['date1'] = date
                    item['time1'] = time
                elif i == 1:
                    item['date2'] = date
                    item['time2'] = time
                    item['room_letter2'] = item['room_letter1']
                else:
                    item['date3'] = date
                    item['time3'] = time
                    item['room_letter3'] = item['room_letter1']

    papers = [
        Paper(
            id=item["UID"],
            forum=item["UID"],
            card_image_path=get_card_image_path_for_paper(
                item["UID"], paper_images_path, default_image_path
            ),
            presentation_id=item.get("presentation_id", None),
            presentation_id_intro=item.get("presentation_id_intro", None),
            content=PaperContent(
                title=item["title"],
                authors=extract_list_field(item, "authors"),
                keywords=extract_list_field(item, "keywords"),
                abstract=item["abstract"],
                tldr=item["abstract"][:250] + "...",
                pdf_url=item.get("pdf_url", "https://scholar.google.com/"),
                demo_url=item.get("demo_url", ""),
                material=item.get("material"),
                track=normalize_track_name(item.get("track", "")),
                paper_type=item.get("paper_type", ""),
                sessions=[],
                similar_paper_uids=paper_recs.get(item["UID"], [item["UID"]]),
                program=item["program"],
                date1=item.get("date1", "unknown"),
                time1=item.get("time1", "unknown"),
                date2=item.get("date2", "unknown"),
                time2=item.get("time2", "unknown"),
                date3=item.get("date3", "unknown"),
                time3=item.get("time3", "unknown"),
                room_letter1=item.get("room_letter1", "unknown"),
                room_letter2=item.get("room_letter2", "unknown"),
                room_letter3=item.get("room_letter3", "unknown"),
                room=item.get("room", "unknown"),
                cluster=item.get("cluster", "unknown"),
                position=int(float(item.get("position", 0))),
                cluster_name=item.get("cluster_name", "unknown"),
                gather_town_link= item.get("gather_town_link", "unknown"),
                best_type=item.get("best_type",0),
                best_type_desc=item.get("best_type_desc","")
                # gather_town_link=paper_id_to_link[item["UID"]] if item['UID'] in paper_id_to_link else "",
            ),
        )
        for item in raw_papers
    ]


    # throw warnings for missing information
    # for paper in papers:
    #     if not paper.presentation_id and paper.content.program not in [
    #         "demo",
    #         "findings",
    #     ]:
    #         print(f"WARNING: presentation_id not set for {paper.id}")
    #     if not paper.content.track:
    #         print(f"WARNING: track not set for {paper.id}")
    #     if paper.presentation_id and len(paper.content.sessions) != 1:
    #         print(
    #             f"WARNING: found {len(paper.content.sessions)} sessions for {paper.id}"
    #         )
    #     if not paper.content.similar_paper_uids:
    #         print(f"WARNING: empty similar_paper_uids for {paper.id}")

    return papers


def build_poster_infos(
    raw_paper_sessions: Dict[str, Any],by_uid,papers
) -> Tuple[List[QaSession], List[Tuple[str, str, str]]]:

    # poster_infos_by_day: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    poster_infos_by_day = defaultdict()
    room_list_by_day = defaultdict(list)
    # day_map = {"A":"Feb 4","B":"Feb 4","C":"Feb 4","D":"Feb 5","E":"Feb 5","F":"Feb 5",
    #            "G":"Feb 6","H":"Feb 6","I":"Feb 6","J":"Feb 7","K":"Feb 7","L":"Feb 7"}
    day_map = {"D1":"Feb 4","D2":"Feb 5","D3":"Feb 6","D4":"Feb 7"}
    day_map_2 = {"4-Feb":"Feb 4","5-Feb":"Feb 5","6-Feb":"Feb 6","7-Feb":"Feb 7"}
    types = ["Poster","Demo","SA","DC","UC","IAAI","Award"]

    for day in day_map.values():
        poster_infos_by_day[day] = defaultdict(list)
    for uid, rs in raw_paper_sessions.items():
        if "Award" in uid:
            cluster = ""
            room = uid[:-1]
        else:
            cluster = uid.split("-")[-1]
            room = uid[:-2]
        if "IAAI" in room:
            session_type = "IAAI"
        elif "UC" in room:
            session_type = "UC"
        elif "SA" in room:
            session_type = "SA"
        elif "DC" in room:
            session_type = "DC"
        elif "DEMO" in room:
            session_type = "Demo"
        elif "Award" in room:
            session_type = "Award"
        else:
            session_type = "Poster"
        if session_type == "Poster":
            pass
        else:
            day_id = rs['time1'].split(' ')[0]
            whole_day_map = {
                "4-Feb": ['4-Feb 08:45AM-10:30AM', '4-Feb 04:45PM-06:30PM' ,'5-Feb 12:45AM-02:30AM'],
                "5-Feb": ['5-Feb 08:45AM-10:30AM', '5-Feb 04:45PM-06:30PM', '6-Feb 12:45AM-02:30AM'],
                "6-Feb": ['6-Feb 08:45AM-10:30AM', '6-Feb 04:45PM-06:30PM', '7-Feb 12:45AM-02:30AM'],
                "7-Feb": ['7-Feb 08:45AM-10:30AM', '7-Feb 04:45PM-06:30PM', '8-Feb 12:45AM-02:30AM'],
            }
            rs['time1'] = whole_day_map[day_id][0]
            rs['time2'] = whole_day_map[day_id][1]
            rs['time3'] = whole_day_map[day_id][2]

        day = day_map[uid.split("-")[1]]
        papers = rs["papers"]
        papers.sort(key=lambda x:by_uid[x].content.position)
        poster_info = PosterInfo(
            uid = uid,
            room = room,
            time1 = rs["time1"],
            time2 = rs["time2"],
            time3 = rs.get('time3',None),
            session_type = session_type,
            cluster = cluster,
            cluster_name = rs["cluster_name"],
            gather_town_link=rs.get("gather_town_link", "http://zoom.us"),
            papers=rs["papers"],
            # papers=[],
        )
        poster_infos_by_day[day][room].append(poster_info)
        # 添加best paper逻辑


    # best_papers_award = ['AAAI-7346','AAAI-2294','AISI-8076']
    # best_paper_runners_up_award = ['AAAI-9868','AAAI-10151','AISI-4906']
    # distinguished_papers_award = ['AAAI-8265','AAAI-3534','AAAI-2549','AAAI-10339','AAAI-4640','AAAI-7047']


    sort_rule = {
        "Poster":1,"Demo":2,"SA":3,"DC":4,"UC":5,"IAAI":6,"Award":7
    }
    sort_rule_2 = {
        "AB-R1":1,"AB-R2":2,"BC-R1":3,"BC-R2":4,"AC-R1":5,"AC-R2":6,"DEMO":7,"SA":9,"DC":9,"UC":10,"IAAI":11,"Award":12
    }
    def room_name_expect_day(room):
        if len(room.split("-")) == 3:
            room_name_expect_day = room.split("-")[0] + "-" + room.split("-")[-1]
        else:
            room_name_expect_day = room.split("-")[0]
        # print(room,room_name_expect_day)
        return room_name_expect_day

    sorted_poster_infos_by_day = defaultdict()
    for day in poster_infos_by_day.keys():
        sorted_poster_infos_by_day[day] = defaultdict()
        rooms = sorted(poster_infos_by_day[day].keys(),key=lambda x: sort_rule_2[room_name_expect_day(x)])
        for room in rooms:
            sorted_poster_infos_by_day[day][room] = poster_infos_by_day[day][room]
    for day in sorted_poster_infos_by_day.keys():
        for room in sorted_poster_infos_by_day[day].keys():
            sorted_poster_infos_by_day[day][room].sort(key=lambda x:(sort_rule[x.session_type],x.room,x.cluster))
            for x in sorted_poster_infos_by_day[day][room]:
                if x.room not in room_list_by_day[day]:
                    room_list_by_day[day].append(x.room)
    poster_days = []
    # add best paper tab
    days = ["Feb 4","Feb 5","Feb 6","Feb 7"]
    for i, day in enumerate(days):
        poster_days.append(
            (day.replace(" ", "").lower(), day, "active" if i == 0 else "")
        )

    sorted_poster_infos_by_day["Award-Winning Papers"] = defaultdict(list)
    sorted_poster_infos_by_day["Award-Winning Papers"]["Best Papers"] = ['AAAI-7346','AAAI-2294','AISI-8076']
    sorted_poster_infos_by_day["Award-Winning Papers"]["Best Paper Runners Up"] = ['AAAI-9868','AAAI-10151','AISI-4906']
    sorted_poster_infos_by_day["Award-Winning Papers"]["Distinguished Papers"] = ['AAAI-8265','AAAI-3534','AAAI-2549','AAAI-10339','AAAI-4640','AAAI-7047']



    return sorted_poster_infos_by_day, poster_days,room_list_by_day


def build_qa_sessions(
    raw_paper_sessions: Dict[str, Any]
) -> Tuple[List[QaSession], List[Tuple[str, str, str]]]:
    raw_subsessions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for uid, subsession in raw_paper_sessions.items():
        overall_id = uid[:-1]
        raw_subsessions[overall_id].append(subsession)

    days = set()

    paper_sessions = []
    for uid, rs in raw_subsessions.items():
        number = uid[1:]
        if uid.startswith("z"):
            name = f"Zoom Q&A Session {number}"
        elif uid.startswith("g"):
            name = f"Gather Session {number}"
        else:
            raise Exception("Invalid session type")

        start_time = rs[0]["start_time"]
        end_time = rs[0]["end_time"]
        assert all(s["start_time"] == start_time for s in rs)
        assert all(s["end_time"] == end_time for s in rs)

        subsessions = []
        for s in rs:
            qa_subsession = QaSubSession(
                name=s["long_name"].split(":")[-1].strip(),
                link=s.get("zoom_link", "http://zoom.us"),
                # TODO  make qa_session.html pass
                papers=s["papers"],
                # papers=[],
            )
            subsessions.append(qa_subsession)

        qa_session = QaSession(
            uid=uid,
            name=name,
            start_time=start_time,
            end_time=end_time,
            subsessions=subsessions,
        )
        paper_sessions.append(qa_session)

        days.add(qa_session.day)

    qa_session_days = []
    for i, day in enumerate(sorted(days)):
        qa_session_days.append(
            (day.replace(" ", "").lower(), day, "active" if i == 0 else "")
        )

    return paper_sessions, qa_session_days


def build_tutorials(raw_tutorials: List[Dict[str, Any]]) -> List[Tutorial]:
    def build_tutorial_blocks(t: Dict[str, Any]) -> List[SessionInfo]:
        blocks = compute_schedule_blocks(t["sessions"])
        result = []
        for i, block in enumerate(blocks):
            min_start = min([t["start_time"] for t in block])
            max_end = max([t["end_time"] for t in block])

            assert all(s["zoom_link"] == block[0]["zoom_link"] for s in block)

            result.append(
                SessionInfo(
                    session_name=f"T-Live Session {i+1}",
                    start_time=min_start,
                    end_time=max_end,
                    link=block[0]["zoom_link"],
                )
            )
        return result
    return [
        Tutorial(
            id=item["UID"],
            title=item["title"],
            organizers=item["organizers"],
            abstract=item["abstract"],
            details=item["details"]
#            website=item.get("website", None)
#            sessions=[
#                TutorialSessionInfo(
#                    session_name=session.get("name"),
#                    start_time=session.get("start_time"),
#                    end_time=session.get("end_time"),
#                    hosts=session.get("hosts", ""),
#                    livestream_id=session.get("livestream_id"),
#                    zoom_link=session.get("zoom_link"),
#                )
#                for session in item.get("sessions")
#            ],
#            authors=[
#                TutorialAuthorInfo(
#                    author_name=author.get("name"),
#                    author_description=author.get("description"),
#                )
#                for author in item.get("authors")
#            ],
#            blocks=build_tutorial_blocks(item),
#            virtual_format_description=item["info"],
        )
        for item in raw_tutorials
    ]


def build_workshops(
    raw_workshops: List[Dict[str, Any]], raw_workshop_papers: List[Dict[str, Any]],
) -> List[Workshop]:
    def workshop_title(workshop_id):
        for wsh in raw_workshops:
            if wsh["UID"] == workshop_id:
                return wsh["title"]
        return ""

    def build_workshop_blocks(t: Dict[str, Any]) -> List[SessionInfo]:
        blocks = compute_schedule_blocks(t["sessions"], leeway=timedelta(hours=1))
        if len(blocks) == 0:
            return []

        result = []
        for i, block in enumerate(blocks):
            min_start = min([t["start_time"] for t in block])
            max_end = max([t["end_time"] for t in block])

            result.append(
                SessionInfo(
                    session_name=f"W-Live Session {i+1}",
                    start_time=min_start,
                    end_time=max_end,
                    link="",
                )
            )
        return result

    grouped_papers: DefaultDict[str, Any] = defaultdict(list)
    for paper in raw_workshop_papers:
        grouped_papers[paper["workshop"]].append(paper)

    ws_id_to_alias: Dict[str, str] = {w["UID"]: w["alias"] for w in raw_workshops}

    workshop_papers: DefaultDict[str, List[WorkshopPaper]] = defaultdict(list)
    for workshop_id, papers in grouped_papers.items():
        for item in papers:
            workshop_papers[workshop_id].append(
                WorkshopPaper(
                    id=item["UID"],
                    title=item["title"],
                    speakers=item["authors"],
                    presentation_id=item.get("presentation_id", None),
                    rocketchat_channel=f"paper-{ws_id_to_alias[workshop_id]}-{item['UID'].split('.')[-1]}",
                    content=PaperContent(
                        title=item["title"],
                        authors=extract_list_field(item, "authors"),
                        track=workshop_title(workshop_id),
                        paper_type="Workshop",
                        abstract=item.get("abstract"),
                        tldr=item["abstract"][:250] + "..."
                        if item["abstract"]
                        else None,
                        keywords=[],
                        pdf_url=item.get("pdf_url"),
                        demo_url=None,
                        sessions=[],
                        similar_paper_uids=[],
                        program="workshop",
                    ),
                )
            )

    workshops: DefaultDict[str, List[Workshop]] = defaultdict(list)
    for item in raw_workshops:
        workshops[item["day"]].append(
        Workshop(
            id=item["UID"],
            title=item["title"],
            organizers=item["organizers"],
            abstract=item["abstract"],
            website=item["website"],
            livestream=item.get("livestream"),
            papers=workshop_papers[item["UID"]],
            schedule=item.get("schedule"),
            prerecorded_talks=item.get("prerecorded_talks"),
            rocketchat_channel=item["rocketchat_channel"],
            zoom_links=item.get("zoom_links", []),
            day=item["day"],
            sessions=[
                SessionInfo(
                    session_name=session.get("name", ""),
                    start_time=session.get("start_time"),
                    end_time=session.get("end_time"),
                    link=session.get("zoom_link", ""),
                    hosts=session.get("hosts"),
                )
                for session in item.get("sessions")
            ],
            blocks=build_workshop_blocks(item),
        )
    )

    return workshops

def build_doctoral_consortium(raw_doctoral_consortiums: List[Dict[str, Any]]) -> List[DoctoralConsortium]:
    def build_doctoral_consortium_blocks(t: Dict[str, Any]) -> List[SessionInfo]:
        blocks = compute_schedule_blocks(t["sessions"])
        result = []
        for i, block in enumerate(blocks):
            min_start = min([t["start_time"] for t in block])
            max_end = max([t["end_time"] for t in block])

            assert all(s["zoom_link"] == block[0]["zoom_link"] for s in block)

            result.append(
                SessionInfo(
                    session_name=f"T-Live Session {i+1}",
                    start_time=min_start,
                    end_time=max_end,
                    link=block[0]["zoom_link"],
                )
            )
        return result

    return [
        DoctoralConsortium(
            id=item["UID"],
            title=item["title"],
            organizers=item["organizers"],
            abstract=item["abstract"],
            website=item.get("website", None),
            material=item.get("material", None),
            slides=item.get("slides", None),
            prerecorded=item.get("prerecorded", ""),
            rocketchat_channel=item.get("rocketchat_channel", ""),
            sessions=[
                SessionInfo(
                    session_name=session.get("name"),
                    start_time=session.get("start_time"),
                    end_time=session.get("end_time"),
                    hosts=session.get("hosts", ""),
                    link=session.get("zoom_link", ""),
                )
                for session in item.get("sessions")
            ],
            blocks=build_doctoral_consortium_blocks(item),
            virtual_format_description=item["info"],
        )
        for item in raw_doctoral_consortiums
    ]

def build_demonstrations(raw_demonstrations: List[Dict[str, Any]]) -> List[Demonstrations]:
    def build_demonstrations_blocks(t: Dict[str, Any]) -> List[SessionInfo]:
        blocks = compute_schedule_blocks(t["sessions"])
        result = []
        for i, block in enumerate(blocks):
            min_start = min([t["start_time"] for t in block])
            max_end = max([t["end_time"] for t in block])

            assert all(s["zoom_link"] == block[0]["zoom_link"] for s in block)

            result.append(
                SessionInfo(
                    session_name=f"T-Live Session {i+1}",
                    start_time=min_start,
                    end_time=max_end,
                    link=block[0]["zoom_link"],
                )
            )
        return result

    return [
        Demonstrations(
            id=item["UID"],
            title=item["title"],
            organizers=item["organizers"],
            abstract=item["abstract"],
            website=item.get("website", None),
            material=item.get("material", None),
            slides=item.get("slides", None),
            prerecorded=item.get("prerecorded", ""),
            rocketchat_channel=item.get("rocketchat_channel", ""),
            sessions=[
                SessionInfo(
                    session_name=session.get("name"),
                    start_time=session.get("start_time"),
                    end_time=session.get("end_time"),
                    hosts=session.get("hosts", ""),
                    livestream_id=session.get("livestream_id"),
                    zoom_link=session.get("zoom_link"),
                )
                for session in item.get("sessions")
            ],
            blocks=build_demonstrations_blocks(item),
            virtual_format_description=item["info"],
        )
        for item in raw_demonstrations
    ]

# def build_ai_in_practice(raw_ai_in_practice: List[Dict[str, Any]]) -> List[AiInPractice]:
#     def build_ai_in_practice_blocks(t: Dict[str, Any]) -> List[SessionInfo]:
#         blocks = compute_schedule_blocks(t["sessions"])
#         result = []
#         for i, block in enumerate(blocks):
#             min_start = min([t["start_time"] for t in block])
#             max_end = max([t["end_time"] for t in block])
#
#             assert all(s["zoom_link"] == block[0]["zoom_link"] for s in block)
#
#             result.append(
#                 SessionInfo(
#                     session_name=f"T-Live Session {i+1}",
#                     start_time=min_start,
#                     end_time=max_end,
#                     link=block[0]["zoom_link"],
#                 )
#             )
#         return result
#
#     return [
#         AiInPractice(
#             id=item["UID"],
#             title=item["title"],
#             organizers=item["organizers"],
#             abstract=item["abstract"],
#             website=item.get("website", None),
#             material=item.get("material", None),
#             slides=item.get("slides", None),
#             prerecorded=item.get("prerecorded", ""),
#             rocketchat_channel=item.get("rocketchat_channel", ""),
#             sessions=[
#                 SessionInfo(
#                     session_name=session.get("name"),
#                     start_time=session.get("start_time"),
#                     end_time=session.get("end_time"),
#                     hosts=session.get("hosts", ""),
#                     livestream_id=session.get("livestream_id"),
#                     zoom_link=session.get("zoom_link"),
#                 )
#                 for session in item.get("sessions")
#             ],
#             blocks=build_ai_in_practice_blocks(item),
#             virtual_format_description=item["info"],
#         )
#         for item in raw_ai_in_practice
#     ]

def build_socials(raw_socials: List[Dict[str, Any]]) -> DefaultDict[str, List[SocialEvent]]:
    socials: DefaultDict[str, List[SocialEvent]] = defaultdict(list)
    for item in raw_socials:
        event = SocialEvent(
                    id=item["UID"],
                    name=item["name"],
                    description=item["description"],
                    image=item.get("image"),
                    location=item.get("location"),
                    organizers=SocialEventOrganizers(
                        members=item["organizers"]["members"],
                        website=item["organizers"].get("website", ""),
                    ),
                    sessions=[
                        SessionInfo(
                            session_name=session.get("name"),
                            start_time=session.get("start_time"),
                            end_time=session.get("end_time"),
                            link=session.get("link"),
                        )
                        for session in item["sessions"]
                    ],
                    rocketchat_channel=item.get("rocketchat_channel", ""),
                    website=item.get("website", ""),
                    zoom_link=item.get("zoom_link"),
                )
        days = set()
        for session in event.sessions:
            # print(session.start_time.month, session.start_time.day)
            # return
            day = f'{session.start_time.strftime("%b")} {session.start_time.day}'
            days.add(day)
        days = list(days)
        # print(days)
        # print('---------------')
        
        for d in days:
            socials[d].append(event)
        # print(len(socials['Feb 3']))
    return socials
    # return [
    #     SocialEvent(
    #         id=item["UID"],
    #         name=item["name"],
    #         description=item["description"],
    #         image=item.get("image"),
    #         location=item.get("location"),
    #         organizers=SocialEventOrganizers(
    #             members=item["organizers"]["members"],
    #             website=item["organizers"].get("website", ""),
    #         ),
    #         sessions=[
    #             SessionInfo(
    #                 session_name=session.get("name"),
    #                 start_time=session.get("start_time"),
    #                 end_time=session.get("end_time"),
    #                 link=session.get("link"),
    #             )
    #             for session in item["sessions"]
    #         ],
    #         rocketchat_channel=item.get("rocketchat_channel", ""),
    #         website=item.get("website", ""),
    #         zoom_link=item.get("zoom_link"),
    #     )
    #     for item in raw_socials
    # ]


def build_sponsors(site_data, by_uid, display_time_format) -> None:
    def generate_schedule(schedule: List[Dict[str, Any]]) -> Dict[str, Any]:
        times: Dict[str, List[Any]] = defaultdict(list)

        for session in schedule:
            if session["start"] is None:
                continue

            start = session["start"].astimezone(pytz.timezone("GMT"))
            if session.get("end") is None:
                end = start + timedelta(hours=session["duration"])
            else:
                end = session["end"].astimezone(pytz.timezone("GMT"))
            day = start.strftime("%A, %b %d")
            start_time = start.strftime(display_time_format)
            end_time = end.strftime(display_time_format)
            time_string = "{} ({}-{} GMT)".format(day, start_time, end_time)

            times[day].append((time_string, session["label"]))
        return times

    by_uid["sponsors"] = {}

    for sponsor in site_data["sponsors"]:
        uid = "_".join(sponsor["name"].lower().split())
        sponsor["UID"] = uid
        by_uid["sponsors"][uid] = sponsor

    # Format the session start and end times
    for sponsor in by_uid["sponsors"].values():
        sponsor["zoom_times"] = generate_schedule(sponsor.get("schedule", []))
        sponsor["gather_times"] = generate_schedule(sponsor.get("gather_schedule", []))

        publications = sponsor.get("publications")
        if not publications:
            continue

        grouped_publications: Dict[str, List[Any]] = defaultdict(list)
        for paper_id in publications:
            if paper_id not in by_uid["papers"]: continue
            paper = by_uid["papers"][paper_id]
            grouped_publications[paper.content.paper_type].append(paper)

        sponsor["grouped_publications"] = grouped_publications

    # In the YAML, we just have a list of sponsors. We group them here by level
    sponsors_by_level: DefaultDict[str, List[Any]] = defaultdict(list)
    for sponsor in site_data["sponsors"]:
        if "level" in sponsor:
            sponsors_by_level[sponsor["level"]].append(sponsor)
        elif "levels" in sponsor:
            for level in sponsor["levels"]:
                sponsors_by_level[level].append(sponsor)

    site_data["sponsors_by_level"] = sponsors_by_level
    site_data["sponsor_levels"] = [
        "Diamond",
        "Platinum",
        "Gold",
        "Silver",
        "Bronze",
        "Supporter",
        "Exhibitor",
        "Publisher",
        "Diversity & Inclusion: Champion",
        "Diversity & Inclusion: In-Kind",
    ]

    assert all(lvl in site_data["sponsor_levels"] for lvl in sponsors_by_level)


def compute_schedule_blocks(
    events, leeway: Optional[timedelta] = None
) -> List[List[Dict[str, Any]]]:
    if leeway is None:
        leeway = timedelta()

    # Based on
    # https://stackoverflow.com/questions/54713564/how-to-find-gaps-given-a-number-of-start-and-end-datetime-objects
    if len(events) <= 1:
        return [events]

    # sort by start times
    events = sorted(events, key=lambda x: x["start_time"])

    # Start at the end of the first range
    now = events[0]["end_time"]

    blocks = []
    block: List[Dict[str, Any]] = []

    for pair in events:
        # if next start time is before current end time, keep going until we find a gap
        # if next start time is after current end time, found the first gap
        if pair["start_time"] - (now + leeway) > timedelta():
            blocks.append(block)
            block = [pair]
        else:
            block.append(pair)

        # need to advance "now" only if the next end time is past the current end time
        now = max(pair["end_time"], now)

    if len(block):
        blocks.append(block)

    return blocks
