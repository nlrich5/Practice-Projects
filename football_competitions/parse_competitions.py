from bs4 import BeautifulSoup
import sys
import json


LAST_FIFA_COUNTRY = "Wales"


def extract_competitions_from_siblings(start_element, stop_tags):
    """Walk siblings from start_element, collecting competition links until a stop heading is hit."""
    competitions = []

    for sibling in start_element.find_next_siblings():
        # Stop if we hit a heading at the same or higher level
        if sibling.name == "div" and "mw-heading" in " ".join(sibling.get("class", [])):
            for tag in stop_tags:
                if sibling.find(tag):
                    return competitions, sibling
            # If it's a lower heading (e.g. h5), continue past it
            if sibling.find("h5"):
                continue
            # h4 inside non-FIFA section means subcategory, continue
            if sibling.find("h4"):
                continue

        # Skip hatnote divs
        if sibling.name == "div" and "hatnote" in " ".join(sibling.get("class", [])):
            continue

        # Skip TOC tables
        if sibling.name == "table" and "toc" in " ".join(sibling.get("class", [])):
            continue

        # Skip paragraph elements
        if sibling.name == "p":
            continue

        # Find all <a> tags in this sibling
        for a in sibling.find_all("a"):
            href = a.get("href", "")

            # Skip section edit links (but not redlinks)
            if "action=edit&section=" in href:
                continue

            # Skip category links
            if "Category:" in href:
                continue

            # Skip anchor-only links (TOC navigation like #Abkhazia)
            if href.startswith("#"):
                continue

            # Skip if inside a hatnote
            if a.find_parent("div", class_="hatnote"):
                continue

            # Skip if inside a table header
            if a.find_parent("th"):
                continue

            # Skip flag images (anchors wrapping country flags)
            if a.find("img"):
                continue

            # Skip if inside <small> (organiser info)
            if a.find_parent("small"):
                continue

            name = a.get_text(strip=True)
            if not name or name in ("edit source", "edit"):
                continue
            # Skip annotation references like [Sen.Men], [L], [Cup], etc.
            if name.startswith("[") and name.endswith("]"):
                continue
            # Skip "Football in X" links
            if name.startswith("Football in "):
                continue
            competitions.append(name)

    return competitions, None


def parse_competitions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    results = {}

    # --- Parse FIFA countries (h4 = country name) ---
    h4_tags = soup.find_all("h4")
    past_wales = False

    # Subcategory headings that are not country names
    subcategory_labels = ("Leagues", "Cups", "League system", "Defunct")

    for h4 in h4_tags:
        country = h4.get_text(strip=True)

        # Skip h4 tags that are subcategories (Leagues, Cups, etc.) in non-FIFA section
        if past_wales:
            continue

        # Skip h4 tags that are clearly subcategory headings, not country names
        if any(country.startswith(label) for label in subcategory_labels):
            continue

        container = h4.find_parent("div", class_="mw-heading")
        if not container:
            continue

        # For potentially duplicated h4s, prefix with parent h3 and/or h2 context
        key = country
        if country in results:
            # Find parent h3 for disambiguation
            parent_h3 = None
            parent_h2 = None
            for prev in container.find_all_previous("h3"):
                parent_h3 = prev.get_text(strip=True)
                break
            for prev in container.find_all_previous("h2"):
                parent_h2 = prev.get_text(strip=True)
                break
            if parent_h3:
                key = f"{country} ({parent_h3})"
            if key in results and parent_h2:
                key = f"{country} ({parent_h2} - {parent_h3})"

        competitions, _ = extract_competitions_from_siblings(container, ["h4", "h2"])

        if competitions:
            if key in results:
                results[key].extend(competitions)
            else:
                results[key] = competitions

        if country == LAST_FIFA_COUNTRY:
            past_wales = True

    # --- Parse Non-FIFA countries (h3 = country/region name) ---
    non_fifa_heading = soup.find("h2", id="Non-FIFA_competitions")
    if non_fifa_heading:
        # Find all h3 tags after the Non-FIFA h2
        non_fifa_container = non_fifa_heading.find_parent("div", class_="mw-heading")
        if non_fifa_container:
            for sibling in non_fifa_container.find_next_siblings():
                # Stop if we hit another h2
                if sibling.name == "div" and "mw-heading2" in " ".join(sibling.get("class", [])):
                    break

                if sibling.name == "div" and "mw-heading3" in " ".join(sibling.get("class", [])):
                    h3 = sibling.find("h3")
                    if h3:
                        country = h3.get_text(strip=True)
                        competitions = []

                        # Walk siblings of this h3 container until next h3 or h2
                        for inner_sib in sibling.find_next_siblings():
                            if inner_sib.name == "div" and "mw-heading" in " ".join(inner_sib.get("class", [])):
                                if inner_sib.find("h3") or inner_sib.find("h2"):
                                    break
                                # h4 subcategories - skip the heading itself but continue
                                if inner_sib.find("h4"):
                                    continue

                            # Skip hatnotes
                            if inner_sib.name == "div" and "hatnote" in " ".join(inner_sib.get("class", [])):
                                continue

                            if inner_sib.name == "p":
                                continue

                            for a in inner_sib.find_all("a"):
                                href = a.get("href", "")

                                if "action=edit&section=" in href:
                                    continue
                                if "Category:" in href:
                                    continue
                                if href.startswith("#"):
                                    continue
                                if a.find_parent("div", class_="hatnote"):
                                    continue
                                if a.find_parent("th"):
                                    continue
                                if a.find("img"):
                                    continue
                                if a.find_parent("small"):
                                    continue

                                name = a.get_text(strip=True)
                                if not name or name in ("edit source", "edit"):
                                    continue
                                if name.startswith("[") and name.endswith("]"):
                                    continue
                                if name.startswith("Football in "):
                                    continue
                                competitions.append(name)

                        if competitions:
                            results[country] = competitions

    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_competitions.py <html_file> [output_file]")
        sys.exit(1)

    filepath = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "competitions.json"

    results = parse_competitions(filepath)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in results.values())
    print(f"Found {total} competitions across {len(results)} countries")
    print(f"Output written to {output_file}")
