import os 
import json 
import re 
import datetime


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
                if section == "names" and not re.match("^[A-Z]+: ", line):
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
                    m = re.match("^([A-Za-z]+): (.+)", line)

                    name = {}

                    name["Language"] = abbreviations[m.group(1)]["Abbreviation"]
                    name["Text"] = m.group(2)

                    place["Names"].append(name)

                if section == "description":
                    text = line.strip()
                    text = text.replace(" - ", " – ")
                    text = text.replace("OE", "Old English")
                    text = text.replace("AS", "Anglo-Saxon")
                    text = re.sub(r"\[(\d+)\]", r"<sup>[\1]</sup>", text)
                    place["Description"] += "<p>" + text + "</p>"

                if section == "parts":
                    m = re.match("^([A-Za-z]+)\s+([^,]+),\s+(.+)", line)

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

    def compile(self):

        abbreviations = self.getAbbreviations()
        placeFilePaths = self.getPlaceFilePaths()

        places = [self.compilePlace(filePath, abbreviations) for filePath in placeFilePaths]

        data = {"Places": places}

        print(data)

        with open("../data/Compiled.json", "w", encoding="utf-8") as fileObject:
            json.dump(data, fileObject, indent=4)

        with open("../web/places.json", "w", encoding="utf-8") as fileObject:
            json.dump(data, fileObject, indent=4)

if __name__ == "__main__":
    compiler = Compiler()

    compiler.compile()