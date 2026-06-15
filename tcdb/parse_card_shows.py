"""Parse card show information from TCDB HTML file and export to CSV."""

import csv
import re
from html.parser import HTMLParser
from pathlib import Path


class CardShowParser(HTMLParser):
    """Parse card show listings from TCDB HTML."""

    def __init__(self):
        super().__init__()
        self.shows = []
        self.current_date = None
        self.in_strong = False
        self.in_link = False
        self.in_li = False
        self.current_show = {}
        self.current_text = ""
        self.li_parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "strong":
            self.in_strong = True
            self.current_text = ""
        elif tag == "li":
            self.in_li = True
            self.current_show = {}
            self.li_parts = []
            self.current_text = ""
        elif tag == "a" and self.in_li:
            self.in_link = True
            self.current_text = ""
            # Extract the show ID from the href
            for attr_name, attr_value in attrs:
                if attr_name == "href" and "CardShows.cfm" in attr_value:
                    id_match = re.search(r"ID=(\d+)", attr_value)
                    if id_match:
                        self.current_show["id"] = id_match.group(1)
        elif tag == "br" and self.in_li:
            # A <br> separates parts within a list item
            text = self.current_text.strip()
            if text:
                self.li_parts.append(text)
            self.current_text = ""

    def handle_endtag(self, tag):
        if tag == "strong":
            self.in_strong = False
            date_text = self.current_text.strip()
            if date_text and re.match(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", date_text):
                self.current_date = date_text
        elif tag == "a" and self.in_link:
            self.in_link = False
            text = self.current_text.strip()
            if text:
                self.li_parts.append(text)
            self.current_text = ""
        elif tag == "li" and self.in_li:
            self.in_li = False
            # Capture any remaining text
            text = self.current_text.strip()
            if text:
                self.li_parts.append(text)

            # Build the show record from parts:
            # [0] = show name, [1] = venue, [2] = city/state, [3] = time
            if len(self.li_parts) >= 4:
                self.current_show["date"] = self.current_date
                self.current_show["name"] = self.li_parts[0]
                self.current_show["venue"] = self.li_parts[1]
                self.current_show["city_state"] = self.li_parts[2]
                self.current_show["time"] = self.li_parts[3]
                self.shows.append(self.current_show)
            elif len(self.li_parts) == 3:
                # Sometimes time might be missing
                self.current_show["date"] = self.current_date
                self.current_show["name"] = self.li_parts[0]
                self.current_show["venue"] = self.li_parts[1]
                self.current_show["city_state"] = self.li_parts[2]
                self.current_show["time"] = ""
                self.shows.append(self.current_show)

    def handle_data(self, data):
        if self.in_strong or self.in_li:
            self.current_text += data


def main():
    html_path = Path("html/Card Shows in Arizona _ Trading Card Database.html")
    output_path = Path("card_shows.csv")

    html_content = html_path.read_text(encoding="utf-8")

    parser = CardShowParser()
    parser.feed(html_content)

    # Filter out entries without a valid date
    parser.shows = [s for s in parser.shows if s.get("date") and re.match(
        r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+\w+\s+\d+,\s+\d{4}",
        s.get("date", "")
    )]

    # Split city_state into city and state
    fieldnames = ["date", "name", "venue", "city", "state", "time", "id"]

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for show in parser.shows:
            city_state = show.get("city_state", "")
            if ", " in city_state:
                city, state = city_state.rsplit(", ", 1)
            else:
                city = city_state
                state = ""

            writer.writerow({
                "date": show.get("date", ""),
                "name": show.get("name", ""),
                "venue": show.get("venue", ""),
                "city": city,
                "state": state,
                "time": show.get("time", ""),
                "id": show.get("id", ""),
            })

    print(f"Parsed {len(parser.shows)} card shows.")
    print(f"CSV written to: {output_path}")


if __name__ == "__main__":
    main()
