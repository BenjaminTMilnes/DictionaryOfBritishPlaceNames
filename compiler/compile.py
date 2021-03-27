import os 
import json 
import re 


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

            place = {}

            if lines[0].startswith("ME: "):
                name = lines[0][4:]
                place["URLReference"] = name.lower()
                place["PrimaryName"] = name

            place["Names"] = []
            place["Description"] = ""
            place["Timeline"] = []

            section = "names"

            for line in lines:
                if section == "names" and not re.match("^[A-Z]+: ", line):
                    section = "description"
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
                    m = re.match("^([A-Z]+): (.+)", line)

                    name = {}

                    name["Language"] = abbreviations[m.group(1)]
                    name["Text"] = m.group(2)

                    place["Names"].append(name)

                if section == "description":
                    place["Description"] += "<p>" + line.strip() + "</p>"

                if section == "timeline":
                    m = re.match("^(~?\d+s?) ([^\,]+)(,\s*(.+))?", line)

                    where = m.group(4) if m.group(4) != None else ""

                    place["Timeline"].append({"Year": m.group(1), "Text": m.group(2), "Where": where})



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