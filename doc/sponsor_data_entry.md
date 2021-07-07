# Gathering sponsor data

You are currently tasked to collect the sponsor information. The virtual website needs a YAML with this information from 
which the final website will be generated.  YAML is a human friendly data format in plain text. You can write it in a simple
text editor or in online editors like https://onlineyamltools.com/edit-yaml.

We will collect general information first and schedule information in a second round. The information we ask for is:

1. Company name, logo and sponsorship level.
2. Visit Website Link (they need to give us a link)
3. Company Descriptions (no longer than 350 words)
4. A video (a YouTube link, or send us a mp4 video file)
5. Contact (they need to provide 1-2 contact persons)
6. Zoom Rooms (they need to schedule some times -- we can provide the host account using our Zoom contract)
7. Download (they can provide up to 5 pdf files)
8. RocketChat channel (We will create a unique one for each sponsor and invite the staff to the channel.)
9.  A pdf or a link to the papers & presentation pointers can be submitted after the conference schedule is released.

You can also ask the sponsors if they want to add additional information and we try to make that happen.

Please fill out the attached YAML file and name it after your sponsor. Make sure that you wrote valid YAML, check with
online tools e.g. https://onlineyamltools.com/edit-yaml. If everything is good, upload it to https://www.dropbox.com/request/Syy99uHWeEqlriltPGwA . Also, please ask your sponsor for the logo we should use and upload that also. You can reupload the file if 
you have made changes. If that link does not work for you, then you can send the material also to 
`emnlp2020@mrklie.com` . If you have questions, you can also ask questions under this mail address.

Example:

```yaml
- name: Your sponsor name
  logo: ask/for/a/logo/and/enter/filename/here
  logoontop: true
  website: https://website.of.sponsor.example.com
  description: |  
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
    Aenean ultricies diam non velit dapibus, a 
    convallis purus pretium. Phasellus justo felis, pulvinar 
    quis rhoncus a, placerat vitae libero. Fusce 
    mattis hendrerit luctus. Quisque et ornare lorem. Donec 
    viverra tellus in ornare sagittis. Nullam massa 
    enim, congue et metus in, posuere vulputate enim. Ut 
    maximus urna est, quis ultrices nibh dignissim in. 
    Vivamus id commodo orci. Suspendisse vel accumsan purus.

    Quisque quam massa, semper quis augue vitae, cursus 
    eleifend nisi. Nullam gravida vitae purus ac pretium. 
    Etiam at rutrum mauris, eu blandit dui. Vestibulum a 
    urna et ligula lobortis tempor. Nunc malesuada nisl 
    in elit maximus maximus. Donec vulputate lacus eu 
    justo pretium iaculis sit amet at lorem. Cras massa nulla,
     porta non euismod at, ultricies non arcu. Phasellus quis 
     sem erat. Vestibulum tristique hendrerit elit, 
     vitae consequat nisl tempus eu.
  youtube: https://www.youtube.com/watch?v=dQw4w9WgXcQ
  contacts:
  - name: Name of the contact 1
    email: mail1@example.com
  - name: Name of the contact 2
    email: mail2@example.com
  zoom_link: https://waitforsecondround.example.com
  schedule:
  - start: 2020-07-07 17:00:00
    duration: 0.5
    label: 'You can leave this empty until round two'
  resources:
  - label: Resource 1
    website: https://resource1.example.com
  - label: Resource 2
    website: https://resource2.example.com
```

The following list describes the fields that you need to fill in:

- name: `<sponsor name>`
- logo: `<sponsor logo>`
- website: `<external website of sponsor>`
- channel: `<RocketChat channel name>`
- video: `<link to a mp4 video (optional)>`
- youtube: `<link to a youtube video. Make sure that you use the link from 'Share -> Embed' (optional)>`
- description: `<description in markdown>`
- zoom_link: `<zoom link, one per sponsor not one per event!>`
- zooms: `<list of zoom sessions>`
    - start: `<start as ISO time with time zone>`
    - duration|end: `<Either set duration in hours OR end time>`
    - label: `<label of  the room>`
- resources: `<list of links to resources>`
    - label: `<label of the resource>`
    - website: `<link to website>`
- contacts: `<List of contacts to reach out for more information>`
  - name: `<Name/Label of the contact>`
    email: `<Valid mail address>`
- level: `<Name of the sponsorship level, e.g. Gold. If there is more than one level, use levels and a list>`
- levels: `<List of sponsorship levels if there is more than one e.g. Gold and diversity.`>
- logoontop: `<boolean that says whether logo should be shown also on the booth, default is false, see Apple for an example>`