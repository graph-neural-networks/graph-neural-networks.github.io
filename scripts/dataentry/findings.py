from pybtex import database

import pandas as pd

from pylatexenc.latex2text import LatexNodes2Text


def read_findings_bib():
    with open("downloads/2020.findings-EMNLP.0.bib") as f:
        bib = database.parse_file(f)

        uids = []
        titles = []
        abstracts = []
        authors = []
        urls = []

        for i, entry in enumerate(bib.entries.values()):
            if entry.type == "book":
                continue

            title = LatexNodes2Text().latex_to_text(entry.fields["title"])
            url = entry.fields["url"]
            abstract = LatexNodes2Text().latex_to_text(entry.fields["abstract"])
            author = "|".join(
                [
                    " ".join(reversed(str(e).split(", ")))
                    for e in entry.persons["author"]
                ]
            )

            uids.append(f"findings.{i}")
            titles.append(title)
            abstracts.append(abstract)
            authors.append(author)
            urls.append(url)

        data = {
            "UID": uids,
            "title": titles,
            "abstract": abstracts,
            "authors": authors,
            "pdf_url": urls,
        }

        df = pd.DataFrame(data)

        df.to_csv("yamls/findings_papers.csv", index=False)


if __name__ == "__main__":
    read_findings_bib()
