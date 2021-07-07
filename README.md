## EMNLP 2020 Virtual Conference

This virtual conference page is based on [MiniConf](http://www.mini-conf.org/) by Alexander Rush
and Hendrik Strobelt. It was extended by the [amazing team of ACL 2020](https://github.com/acl-org/acl-2020-virtual-conference).
The ACL version is the base for this repository.

<p align="center">
  <img width="460" src="doc/img/emnlp2020_index.jpg">
</p>

The website is based on [Flask](https://flask.palletsprojects.com/) and [Frozen-Flask](https://pythonhosted.org/Frozen-Flask/). 
It uses data files like `.csv`, `.yaml` or `.json` that contains the information about events, papers, ... to populate the
HTML templates. From this it generates a static website which can then deployed easily via an HTTP server. We strongly 
recommend deploying it via Amazon CloudFront and using Amazon Cognito as the authentication provider. See 
[here](doc/deployment_aws.md) for a guide to do this.

## Quick Start

    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    make run

When you are ready to deploy run `make freeze` to get a static version of the site in the `build` folder.

## Project Structure

The repository consists of the following main components:

1) *Datastore* [sitedata](https://github.com/acl-org/emnlp-2020-virtual-conference/tree/master/sitedata)

Collection of data files representing the papers, speakers, workshops, and other important information for the conference.

2) *Routing* [main.py](https://github.com/acl-org/emnlp-2020-virtual-conference/tree/master/main.py)

This file contains defines the Flask app and the routes

3) *Templates* [templates](https://github.com/acl-org/emnlp-2020-virtual-conference/tree/master/templates)

Contains all the pages for the site. See `base.html` for the master page and `components.html` for core components.

4) *Frontend* [static](https://github.com/acl-org/emnlp-2020-virtual-conference/tree/master/static)

Contains frontend components like the default css, images, and JavaCcript libs.

5) *Scripts* [scripts](https://github.com/acl-org/emnlp-2020-virtual-conference/tree/master/scripts)

Contains additional preprocessing to add visualizations, recommendations, schedules to the conference. 

## Pages

This section describes all pages that are in this version of MiniConf and how to customize them.

### Index

This page is mainly configured via `sitedata/config.yml`. One mainly needs to change the conference name, date,
number of workshops/tutorials and help documents here. Before the conference starts, also update the
acknowledgements. In `static/js/time-extend.js`, you also need to change start and end times of the conference to 
make sure that daylight saving is handled correctly.

### Schedule

The schedule is based on [FullCalendar](https://fullcalendar.io/). The entries are automatically generated from
the data of the paper sessions/workshops/plenary. For the weekly view, we compute blocks of events and show only a
generic name, on the day view, they are shown as is. Additional events can be added via `sitedata/overall_calendar.yml`.
If you add new event types, make sure to assign them a color in `load_site_data::build_schedule`.

### Plenary

Plenary make up the official program of the conference. For EMNLP, we had live events and prerecorded keynote talks. Keynotes
were prerecorded but livestreamed via SlidesLive. Panels were fully live and used CART real-time captioning. We did not 
add the prerecorded talks to the plenary page before the talk was done. Each plenary details page can either have one 
video or a list of videos. It can also have a RocketChat channel. The default is to just show one SlidesLive video. Refer to 
[the ACL2020 repo](https://raw.githubusercontent.com/acl-org/acl-2020-virtual-conference/master/sitedata_acl2020/business_meeting.csv)
for how multiple videos can be shown on a plenary details page. 

### Livestream

Plenary events were livestreamed via SlidesLive. Make sure that your contract with them covers this.
Panels were fully live and used CART real-time captioning.

For EMNLP, we had prerecorded presentations and keynote speakers and live panels. Recordings were streamed live. For keynotes, after the 
prerecorded talk was shown, the keynote speaker, a volunteer and a SlidesLive person were in a Zoom call, this Zoom call was 
streamed after seamlessly after the keynote recording. Then the volunteer took questions from the `#live` RocketChat channel 
and asked the keynote speaker.

Before the livestream starts, change the livestream ID and CART URL on `livestream.html`. The Livestream SlidesLive IDs 
are different from the actual ID for the recording, e.g. if a keynote is livestreamed,
then the livestream ID is different from the prerecorded ID. Make sure to update the ID before the stream start
and ask SlidesLive to show a `Livestream will start soon` message. After the livestream is done, add the ID
to the plenary event itself. You can use the livestream ID as a slideslive ID for the player, it will then show
a recording of the livestream.

### Papers

EMNLP hat 4 types of papers, main conference papers (long/short), CL, TACL, demo, workshop and findings papers.
See below for the kind of things each paper had.

| Type         | Page | Video | Chat | Visualization |
|--------------|------|-------|------|---------------|
| main/CL/TACL | x    | x     | x    | x             |
| demo         | x    |       | x    |               |
| workshop     | x    |       | x    |               |
| findings     | x    |       |      |               |

Demo papers can have arbitrary markdown under `material` to add info like code repo or screencast,
see our `demo_papers.csv` for it.

For *ACL style conferences, we recommend to ask publication chairs **early** to give out a list of accepted papers with
SoftConf ids, title, authors, paper type (long/short) and anthology IDs. Also ask them to give out the proceedings
as soon as they are done, **do not** wait for them to be published in the ACL anthology page. We do not store PDFs 
directly, but link to the ACL anthology.

#### Visualization

We use [SPECTER](https://github.com/allenai/specter) to generate document embeddings from abstracts and
[DyGIE++](https://github.com/dwadden/dygiepp) to generate keywords. For the embeddings, we then use `umap`
to project them to 2D. Recommentations are generated by using n-nearest neighbours.

We provide `scripts/dataentry/projections.py` to generate the projections, please
refer to the respective repositories to find out how to install them. Install them in their seperate `virtualenv`,
they all have conflicting dependencies.

#### Images

We extract images from the PDFs and upload them to Amazon S3. You can use our bad script under
`scripts/dataentry/extract_images.py` to extract them. In order to allow authors to change their images,
we set up [an additional Github repository](https://github.com/acl-org/emnlp-2020-virtual-conference-images) that 
contains the images. Pull requests there automatically deploy the update images to S3. Look at the Github workflow
there and set the respective secrets for the autodeploy.

#### ConnectedPapers

[Connected Papers](https://www.connectedpapers.com/) is a visual tool to help researchers and applied scientists find 
academic papers relevant to their field of work. In addition to linking to the connected papers for each main paper, 
they built a custom page for EMNLP which is shown below every main paper presentation. If you want that also, then 
conference papers need to be indexed by SemanticScholar before the conference. Contact them via their website and ask 
nicely, then they will also help you.

### Tutorials

Tutorials simply contain a schedule of the events, website, Zoom links, RocketChat and optional a prerecorded SlivesLive
video. We asked tutorial organizers to fill in the information into Google Sheets and then use a script to download that
sheet and parse it. You can refer to `scripts/dataentry/tutorials.py` and see how we loaded tutorials. We used 
[this template](https://docs.google.com/spreadsheets/d/1jvAU8yNLFqQj8-iehjYwxdRsopQq78NUk0cwl2zW6ak/edit?usp=sharing) for 
tutorial organizers to fill in. Tutorial blocks on the tutorial overview page and in the main schedule are computed 
automatically.

### Workshops

Workshops contain a schedule of the events (can use markdown in there, website, Zoom links, RocketChat, a list of prerecorded
SlivesLive videos for invited talks and a link to workshop papers. We asked workshop organizers to fill in the information 
into Google Sheets and then use a script to download that sheet and parse it. You can refer to `scripts/dataentry/workshop.py`
and see how we loaded workshops. We used 
[this template](https://docs.google.com/spreadsheets/d/1LePFp66Q5v9LLNgkyQmHlzEvwFo21YJrvpvydf28yBs/edit?usp=sharing) for 
workshop organizers to fill in. Workshop blocks on the workshop overview page and in the main schedule are computed automatically.
We gave each workshop up to 5 Zoom links, but did not schedule events for them. Instead, we linked the personal meeting ID
on our website.

### Socials

We asked social organizers to fill in the information into Google Sheets and then use a script to download that sheet and parse 
it. You can refer to `scripts/dataentry/socials.py` and see how we loaded socials. We used 
[this template](https://docs.google.com/spreadsheets/d/1IDk3K1JD1hvH_hvyMy6TeRuE2F6DQDfpgwNpTIP9KgI/edit?usp=sharing) for 
social organizers to fill in. Social blocks in the main schedule are computed automatically.
We gave each social event one Zoom link or they could get a Gather room, but did not schedule events for them. Instead, we 
linked the personal meeting ID on our website.

### Sponsors

Each sponsor has a booth that is handmade just for him. We assigned one volunteer to each sponsor to write their YAML.
We collected them via Dropbox file request. Then we merged them into one file via `scripts/dataentry/sponsors.py`.
The file format is the following:

<details><summary>Sponsor File Format</summary>
<p>

- name: `<sponsor name>`
- logo: `<sponsor logo>`
- level: `<Name of the sponsorship level, e.g. Gold. If there is more than one level, use levels and a list>`
- levels: `<List of sponsorship levels if there is more than one e.g. Gold and diversity.`>
- logoontop: `<boolean that says whether logo should be shown also on the booth, default is false, see Apple for an example>`  
- website: `<external website of sponsor>`
- channel: `<RocketChat channel name>`
- description: `<description in markdown>`
- contacts: `<List of contacts to reach out for more information>`
  - name: `<Name/Label of the contact>`
    email: `<Valid mail address>`  
- video: `<link to a mp4 video (optional)>`
- youtube: `<link to a Youtube video. Make sure that you use the link from 'Share -> Embed' (optional)>`
- youtubes: `<List of links to Youtube videos. Make sure that you use the link from 'Share -> Embed' (optional)>`
- vimeo: `<link to a youtube video. Make sure that you use the link from 'Share -> Embed' (optional)>`
- gdrive: `<link to a Video on Google Drive. Make sure that you use the link from 'Click "More Actions" and Select Embed Code' (optional)>`
- zoom_link: `<link, one per sponsor not one per event! You can also use links to other meetings if sponsors want that. e.g. Webex or Google Meet>`
- zoom_schedule: `<list of zoom sessions>`
    - start: `<start as ISO time with time zone>`
    - duration|end: `<Either set duration in hours OR end time>`
    - label: `<label of  the room>`
- gather_schedule: `<list of Gather sessions>`
    - start: `<start as ISO time with time zone>`
    - duration|end: `<Either set duration in hours OR end time>`
    - label: `<label of  the room>`
- resources: `<list of links to external web resources>`
    - label: `<label of the resource>`
    - website: `<URL to resource>`
- downloads: `<list of links to resources that are hosted in this repo, e.g. PDFs>`
    - label: `<label of the resource>`
    - website: `<path to this resource>`
- papers: `<list of paper IDs so that sponsors can show accepted papers of themselves>`

</p>
</details>

Most of these are optional. If the sponsor should not get a booth, then you can link to their page via `landingpage`:

    name: ISI
    level: Bronze
    logo: isi.png
    website: https://www.isi.edu
    channel: example_sponsor
    landingpage: https://www.isi.edu/


#### Sponsor Accounts

Sponsors a number of visitor accounts based on their sponsor tier. They also can register 3 people that only exhibit.
We recommend also creating one account per sponsor early enough so that they can see their booth live. We recommend naming
it after the sponsor and not binding it to a specific person, e.g. better call it `sponsor.deepmind`. This account will
then not be removed before the conference. Additional exhibitors need to register and can usually register for free.

#### Relevant documents

- [Invitation to Dry Run](https://docs.google.com/document/d/1f0ScAG_tUNZry4F5cVBkfwtKaftnKJfZEn7nJZvkxd0/edit?usp=sharing)
- [EMNLP Instructions to sponsors](https://docs.google.com/document/d/1p6ZsN8WmtZiHG0Oyh2zY8eQmSNxH8lzMDHGIWr36LZI/edit?usp=sharing)

### Chat

We use RocketChat throughout this page to have channels for keynotes, plenaries, live, papers, workshops, tutorials
and many more. You can host RocketChat yourself, e.g. on AWS (refer to [their guide](https://docs.rocket.chat/installation))
or pay them to host it. We normally first create a demo workspace and then upgrade it to full for one month with the 
number of anticipated users during the conference.

We integrate RocketChat via SSO into our Amazon Cognito user repository so that only one set of username and password 
is needed. For that, you can refer to [this guide](https://github.com/acl-org/acl-2020-virtual-conference/issues/53).
You do not need to change the Lambda functions if you set up the project correctly when creating the AWS app. 

You can refer to our [checklist for RocketChat](https://github.com/acl-org/emnlp-2020-virtual-conference/issues/49) to
have an idea what needs to be done. 

We have scripts for RocketChat setup in `scripts\rocketchat` and [here](https://github.com/acl-org/acl-2020-virtual-conference-tools).

In order to use the `Active Chat` feature, you need to use RocketChat and host the statistics server. Please refer to
`scripts/channels-stats` to see how. If you do not want it, remove it from `base.html`.

### Help

Update the code of conduct to your own. The FAQ is generated by `faq.yml`.

## Misc

### Gather.Town

We use [VirtualChair](https://www.virtualchair.net/) to manage Gather.Town for us. We strongly recommend to also
book them. Ask them early enough. We use SSO with Gather.Town, you need to specifically ask for it and make 
sure that it lands in the contract.

### Zoom

We buy one Master account and then create accounts for the specific events. For things like tutorials, socials and workshops
we do not schedule events but use the personal meeting link. You can use
[these scripts](https://github.com/acl-org/acl-2020-virtual-conference-tools) to help you creating Zoom things.

#### Relevant documents

- [Volunteers’ Documentation on Zoom](https://docs.google.com/document/d/1MFg1CnSd2Vu4oS30MXqJt4v3c1XozHX_1DPGxkXqXeA/edit?usp=sharing)
- [Sponsors’ Documentation on Zoom](https://docs.google.com/document/d/1CPekSelpKNjGMTH7okFmCzEGaCqFmqSu2HVfYRRSWiU/edit?usp=sharing)
- [Mentors’ Documentation on Zoom](https://docs.google.com/document/d/10aVXLFKQH95cCJ-JoauhzNztBjcu_2iYw-Pz9ETFlS8/edit?usp=sharing)

### User creation

For the first batch of accounts, we are given an Excel file and bulk create accounts. This is best to be done the 
week before the conference starts. Use [these scripts](https://github.com/acl-org/acl-2020-virtual-conference-tools). You 
might need to change `custom:name` to `name` and add support for affiliation if you choose to store it.

### Late Registration

We use Zappier for that: After the first bulk creation, the registration company forwards a copy of all registration
mails to us. Then we use Zappier to parse email, name, affiliation and host. This is sent to a AWS Lambda function
that then creates the account for us. See also [this issue](https://github.com/acl-org/acl-2020-virtual-conference/issues/55).

### Help Desk

We recommend setting up a helpdesk that is staffed by volunteers. For that, create a Google Group and add helpdesk members
and also create a helpdesk channel. It is best to set the Google Group up early enough and also use it as the reply 
mail for the conference invitation account credentials mail and also to mention it there.

### Favicons

We use [this website](https://realfavicongenerator.net/) to generate favicons from an image.

## Acknowledgements

MiniConf was built by [Hendrik Strobelt](http://twitter.com/hen_str) and [Sasha Rush](http://twitter.com/srush_nlp).

Thanks to Darren Nelson for the original design sketches. Shakir Mohamed, Martha White, Kyunghyun Cho, Lee Campbell, 
and Adam White for planning and feedback. Hao Fang, Junaid Rahim, Jake Tae, Yasser Souri, Soumya Chatterjee, and Ankshita 
Gupta for contributions. 

It was extended by the [ACL 2020 virtual infrastructure team](https://acl2020.org/committees/organization), especially
by Hao Fang and Sudha Rao [with the help of many volunteers](https://virtual.acl2020.org/static/pdf/virtual_infrastructure_volunteers.pdf).

It was extended for EMNLP 2020 by [Jan-Christoph Klie](https://github.com/jcklie) with the help of the 
[EMNLP 2020 virtual infrastructure team](https://2020.emnlp.org/organizers) and 
[with the help of many volunteers](static/pdf/volunteers.pdf).




