import os 
import json 
import re 
import datetime
import xml.etree.cElementTree as ElementTree


class Compiler(object):

    def getAbbreviations(self):

        abbreviations = {}

        with open("../abbreviations.md", "r") as fileObject:
            lines = fileObject.readlines()
            lines = [l.strip() for l in lines if l.strip() != ""]

            for line in lines:
                parts = line.split("-")
                parts = [p.strip() for p in parts]
                abbreviations[parts[0]] = {"Name": parts[1], "Abbreviation": parts[0]}

            return abbreviations 

    def getPlaceFilePaths(self):
        filePaths = []

        for a in os.listdir("../data"):
            if a.endswith(".place"):
                filePaths.append(os.path.join("../data", a))

        return filePaths

    def getPlaceXMLFilePaths(self):
        filePaths = []

        for a in os.listdir("../data"):
            if a.endswith(".place.xml"):
                filePaths.append(os.path.join("../data", a))

        return filePaths 

    def compilePlace(self, filePath, abbreviations):

        with open(filePath, "r", encoding="utf-8") as fileObject:
            lines = fileObject.readlines()
            lines = [l.strip() for l in lines if l.strip() != ""]
            lines = [l for l in lines if not l.startswith("//")]

            place = {}

            if lines[0].startswith("ME: "):
                name = lines[0][4:]
                place["URLReference"] = name.lower()
                place["PrimaryName"] = name

            place["Names"] = []
            place["Description"] = ""
            place["Parts"] = []
            place["Timeline"] = []
            place["References"] = []

            section = "names"

            for line in lines:
                if section == "names" and not re.match(r"^[A-Za-z]+: ", line):
                    section = "description"
                if line.startswith("parts:"):
                    section = "parts"
                    continue 
                if line.startswith("timeline:"):
                    section = "timeline"
                    continue 
                if line.startswith("demonym:"):
                    place["Demonym"] = line[8:].strip()
                    continue
                if line.startswith("references:"):
                    section = "references"
                    continue

                if section == "names":
                    m = re.match(r"^([A-Za-z]+): (.+)", line)

                    name = {}

                    name["Language"] = abbreviations[m.group(1)]["Abbreviation"]
                    name["Text"] = m.group(2)

                    place["Names"].append(name)

                if section == "description":
                    text = line.strip()
                    text = text.replace(" - ", " [--] ")
                    text = text.replace("OE", "Old English")
                    text = text.replace("AS", "Anglo-Saxon")
                    text = re.sub(r"\[(\d+)\]", r"<sup>[\1]</sup>", text)
                    place["Description"] += "<p>" + text + "</p>"

                if section == "parts":
                    m = re.match(r"^([A-Za-z]+)\s+([^,]+),\s+(.+)", line)

                    part = {}

                    part["Language"] = m.group(1)
                    part["Text"] = m.group(2)
                    part["Type"] = m.group(3)

                    place["Parts"].append(part)

                if section == "timeline":
                    m = re.match(r"^(~?[\d\-]+s?( BCE)?) ([^\,\[\]]+)(,\s*([^\[\]]+))?(\s*\[(\d+)\])?", line)

                    year = m.group(1)
                    year = year + " A.D." if not year.endswith("BCE") else year[:-3] + "B.C."
                    where = m.group(5) if m.group(5) != None else ""
                    reference = m.group(7)

                    place["Timeline"].append({"Year": year, "Text": m.group(3).strip(), "Where": where.strip(), "Reference": reference})

                if section == "references":

                    m1 = re.match(r"(\d+)\.\s+(http[^\s]+)\s+\(accessed: (\d{4}\.\d{2}\.\d{2})\)\s*", line)

                    if m1:
                        reference = {}

                        reference["Type"] = "website"
                        reference["URL"] = m1.group(2)
                        reference["AccessedOn"] = m1.group(3)

                        place["References"].append(reference)

            return place 

    def exportPlacesAsXML(self, places):        
        for place in places:
            print(place["PrimaryName"])

            filePath = os.path.join("../data", place["PrimaryName"].lower() + ".place.xml")

            e1 = ElementTree.Element("place")

            e2a = ElementTree.SubElement(e1, "names")
            e2b = ElementTree.SubElement(e1, "parts")
            e2c = ElementTree.SubElement(e1, "demonyms")
            e2d = ElementTree.SubElement(e1, "description")
            e2e = ElementTree.SubElement(e1, "timeline")
            e2f = ElementTree.SubElement(e1, "references")

            for name in place["Names"]:
                e3 = ElementTree.SubElement(e2a, "name")

                language = ""

                if name["Language"] == "ME":
                    language = "modern-english"
                if name["Language"] == "OE":
                    language = "old-english"
                if name["Language"] == "L":
                    language = "latin"
                if name["Language"] == "MW":
                    language = "modern-welsh"
                if name["Language"] == "MidW":
                    language = "middle-welsh"
                if name["Language"] == "MS":
                    language = "modern-scots"
                if name["Language"] == "MSG":
                    language = "modern-scottish-gaelic"

                e3.set("language", language)
                e3.text = name["Text"]

            for part in place["Parts"]:
                e3 = ElementTree.SubElement(e2b, "part")

                language = ""

                if part["Language"] == "ME":
                    language = "modern-english"
                if part["Language"] == "OE":
                    language = "old-english"
                if part["Language"] == "L":
                    language = "latin"
                if name["Language"] == "MW":
                    language = "modern-welsh"
                if name["Language"] == "MidW":
                    language = "middle-welsh"
                if name["Language"] == "MS":
                    language = "modern-scots"
                if name["Language"] == "MSG":
                    language = "modern-scottish-gaelic"

                e3.set("language", language)
                e3.set("type", part["Type"].replace(" ", "-"))
                e3.text = part["Text"]

            if "Demonym" in place:
                e3 = ElementTree.SubElement(e2c, "demonym")
                e3.text = place["Demonym"]
                
            if "Description" in place and place["Description"] != "":
                print(place["Description"])
                e2ds = ElementTree.fromstring("<d>" + place["Description"] + "</d>")
                e2d.append(e2ds)

            for item in place["Timeline"]:
                e4 = ElementTree.SubElement(e2e, "item")

                e4.text = item["Text"]
                e4.set("year", item["Year"])

                if item["Where"] != "":
                    e4.set("where", item["Where"])

                if "Reference" in item and item["Reference"] != None:
                    e4.set("references", item["Reference"])

            n = 1

            for reference in place["References"]:
                e4 = ElementTree.SubElement(e2f, "reference")

                e4.set("type", reference["Type"])
                e4.set("key", str(n))
                n += 1

                e5 = ElementTree.SubElement(e4, "url")
                e5.text = reference["URL"]

                e6 = ElementTree.SubElement(e4, "accessed-on")
                e6.text = reference["AccessedOn"]

            tree = ElementTree.ElementTree(e1)
            ElementTree.indent(tree, space="    ", level=0)
            tree.write(filePath, encoding="utf-8", xml_declaration=True)

    def compilePlaceFromXML(self, filePath, abbreviations):
        tree = ElementTree.parse(filePath)

        latitude = tree._root.get("latitude", "")
        longitude = tree._root.get("longitude", "") 

        place = {
            "Coordinates": { "Latitude": latitude, "Longitude": longitude },
            "URLReference": tree.find("names").find("name").text.lower(),
            "PrimaryName": tree.find("names").find("name").text,
            "Names": [],
            "Parts": [],
            "Demonyms": [],
            "Description": "",
            "Timeline": [],
            "References": []
        }

        if tree.find("description") != None:
            description = str(ElementTree.tostring(tree.find("description"), encoding="unicode"))

            description = description.replace("b\"", "")
            description = description.replace("\"", "")
            description = description.replace("\n", "")
            description = description.replace("<d>", "")
            description = description.replace("</d>", "")
            description = description.replace("<description>", "")
            description = description.replace("</description>", "")
            description = description.replace("<description />", "")
            
            description = description.replace("[--]", "–")
            description = description.replace("[lqm]", "‘")
            description = description.replace("[rqm]", "’")
            description = description.replace("[ae]", "æ")
            description = description.replace("[AE]", "Æ")

            description = re.sub(r"^\s+", "", description)
            description = re.sub(r"\s+$", "", description)
            description = re.sub(r"\s+</p>", "</p>", description)

            place["Description"] = description

        for e1 in tree.find("names").findall("name"):
            name = {
                "Language": e1.get("language"),
                "Text": e1.text
            }

            place["Names"].append(name)

        for e1 in tree.find("parts").findall("part"):
            part = {
                "Language": e1.get("language"),
                "Text": e1.text,
                "Type": e1.get("type")
            }

            place["Parts"].append(part)

        for e1 in tree.find("demonyms").findall("demonym"):
            demonym = {
                "Text": e1.text
            }

            place["Demonyms"].append(demonym)

        for e1 in tree.find("timeline").findall("item"):
            item = {
                "Year": e1.get("year"),
                "Text": e1.text,
                "Where": e1.get("where", ""),
                "Reference": e1.get("references")
            }

            place["Timeline"].append(item)

        for e1 in tree.find("references").findall("reference"):
            reference = {
                "Type": e1.get("type"),
                "URL": e1.find("url").text,
                "AccessedOn": e1.find("accessed-on").text
            }

            place["References"].append(reference)

        return place

    def compile(self):

        abbreviations = self.getAbbreviations()
        placeFilePaths = self.getPlaceFilePaths()
        placeXMLFilePaths = self.getPlaceXMLFilePaths()

        places = [self.compilePlaceFromXML(filePath, abbreviations) for filePath in placeXMLFilePaths]

        data = {
            "Abbreviations": abbreviations,
            "Places": places
        }

        print(data)

        with open("../data/Compiled.json", "w", encoding="utf-8") as fileObject:
            json.dump(data, fileObject, indent=4)

        with open("../web/places.json", "w", encoding="utf-8") as fileObject:
            json.dump(data, fileObject, indent=4)

if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()