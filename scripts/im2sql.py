#!/usr/bin/env python
# coding: utf-8

# Import required packages
import cv2
import pytesseract
import numpy as np
from typing import Any, List, Tuple, Dict
# import sys
from decouple import config
import base64
import uuid

class TableNameException(Exception):
    def __init__(self):
        self.msg = """Your table name isn't in one word. Consider using underscores (_) instead of spaces and hyphens(-)"""
        super().__init__(self.msg)


class Im2SQL:
    def __init__(self, image_path: str, tesseract_path: str):
        self.img_path = image_path
        self.tesseract_path = tesseract_path

    def recognize(self) -> str:  # Taken from GFG

        # Mention the installed location of Tesseract-OCR in your system
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path

        # Read image from which text needs to be extracted
        img = cv2.imread(self.img_path)

        # Preprocessing the image starts

        # Convert the image to gray scale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Performing OTSU threshold
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Specify structure shape and kernel size.
        # Kernel size increases or decreases the area
        # of the rectangle to be detected.
        # A smaller value like (10, 10) will detect
        # each word instead of a sentence.
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

        # Applying dilation on the threshold image
        dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

        # Finding contours
        contours, hierarchy = cv2.findContours(
            dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )

        # Creating a copy of image
        im2 = img.copy()

        # A text file is created and flushed
        #     file = open(output_path, "w+")
        #     file.write("")
        #     file.close()

        # Looping through the identified contours
        # Then rectangular part is cropped and passed on
        # to pytesseract for extracting text from it
        # Extracted text is then written into the text file
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # Drawing a rectangle on copied image
            # rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Cropping the text block for giving input to OCR
            cropped = im2[y:(y + h), x:(x + w)]

            # Open the file in append mode
            #         file = open(output_path, "a")

            # Apply OCR on the cropped image
            text = pytesseract.image_to_string(cropped)  # cropped)

            # Appending the text into file
        #         file.write(text)
        #         file.write("\n")

        # Close the file
        #         file.close

        return text

    def typecast(self, text: str, decimals: int = 1) -> Any:
        try:
            if decimals == 0:
                return int(text)
            else:
                return np.round(float(text), decimals)
        except Exception:
            if text.lower() == "null":
                return text
            else:
                return f"'{text}'"

    def tokenize(self, text: str, decimals: int = 0) -> List:
        tx2: str = str(text.strip().replace("|", "; ").replace("[", "; "))
        lines: List = [
            [
                self.typecast(j.strip(" "), decimals) for j in i.split(";") if self.typecast(j.strip(" "), decimals) != "''"
            ] for i in tx2.split("\n")
        ]

        while([] in lines):
            lines.remove([])

        return lines

# for i in lines:
#     print(i, end=",\n")

    def to_insertion(self, table_name: str, lines: List) -> List:
        print("\nConverting to INSERT commands...")
        commands: List = list()

        # print("\nTo parse:\n")
        # for i in lines:
        #     print(i)
        print("\n\n")
        for i in lines:
            cmd: str = f"INSERT INTO {table_name} VALUES("
            for j in range(len(i)):
                cmd += f"{i[j]}"
                if j < len(i) - 1:
                    cmd += ", "
            cmd += ");"
            commands.append(cmd)

        return commands

    def typeEnforce(self, cols: int, cmd: List) -> List:
        count: int = cols
        checks: List = list()
        cmd2: List = list(cmd)
        # correct_col_len = list()

        print("\nChecking row contents...\n")
        for i in range(len(cmd2) - 1):
            if len(cmd2[i]) != len(cmd2[i + 1]):
                checks.append(f" -> Entry {i+1} is different in length compared to entry {i+2}")
                print(
                    f" -> Entry {i+1} (Length: {len(cmd2[i])}) has different number of columns compared to entry {i+2} (Length: {len(cmd2[i+1])})"
                )

        for i in range(len(cmd2)):
            if len(cmd2[i]) != count:
                checks.append(f" -> Entry {i+1} (Length: {len(cmd2[i])}) has different number of columns compared to intended length ({count})")
                print(
                    f" -> Entry {i+1} (Length: {len(cmd2[i])}) has different number of columns compared to intended length ({count})"
                )
            # else:
            #     correct_col_len.append(cmd2[i])

        lengths: List = [len(x) for x in cmd]
        unique_lengths: List = list(set(lengths))
        frequencies: Dict = dict()

        for i in unique_lengths:
            frequencies[i] = 0

        for i in lengths:
            frequencies[i] += 1

        most_common_column_no: Tuple = (sorted(list(frequencies.items()),
                                        key=lambda x: x[0]))[-1]
        print("Number of entries:", len(cmd))
        print("Most common number of columns: ", most_common_column_no[0])

        correct_length_columns: List = [
            (cmd[i], i + 1)
            for i in range(len(cmd))
            if len(cmd[i]) == count
        ]

        # if len(checks) >= 1:
        #     return checks

        # for i in checks:
        #     print(i)

        # print(f"Columns with {most_common_column_no[0]} columns:\n")
        # for i in correct_length_columns:
        #     print(i[0])

        if len(correct_length_columns) > 0:
            print("\nType checking column contents...\n")

        for i in range(len(correct_length_columns) - 1):
            for j in range(most_common_column_no[0]):
                if type(correct_length_columns[i][0][j]) != \
                type(correct_length_columns[i + 1][0][j]):
                    print(f" -> Column {j+1} in entry", end=" ")
                    print(f"{correct_length_columns[i][1]} is different", end=" ")
                    print(
                        f"type compared to that in entry {correct_length_columns[i+1][1]}"
                    )
                    checks.append(f" -> Column {j+1} in entry {correct_length_columns[i][1]} is different type compared to that in entry {correct_length_columns[i+1][1]}")
                    # return False

        print(f"\nChecks completed, {len(checks)} errors found.\n")
        
        return checks

    def write(self, table_name: str, lines: List, path: str) -> None:
        try:
            f = open(path, "w")

            for i in lines:
                f.write(i)
                f.write("\n")

            f.close()
        except Exception as e:
            print(f"Error occured while writing to file. Details: {e}")


def driver(tesseract_path: str, floc: str, columns: int = 0, tablename: str="Test", typecheck: bool=False, includes_schema: bool=False) -> None:
    fname = uuid.uuid4().hex
    # floc = f"media/{fname}.png"
    # write_image = open(floc, 'wb')

    START_POS:int = 0
    if includes_schema:
        START_POS += 1

    # write_image.write(base64.decodebytes(data))

    im2sql = Im2SQL(floc, tesseract_path)
    text: str = im2sql.recognize()

    lines: List = im2sql.tokenize(text)
    # print("\nIdentified Text:\n")
    # print(text.strip().replace("|", ", ").replace("[", ", "))

    table_name: str = tablename

    if len(table_name.strip().split(" ")) != 1 or table_name == "":
        raise TableNameException

    commands: List = im2sql.to_insertion(table_name, lines[START_POS:])

    for i in range(len(commands)):
        print(f"{i+1}.\t{commands[i]}")

    # chk: List = typeEnforce(lines[START_POS:])

    # for i in chk:
    #     print(i)
    if typecheck is True:
        print("\nChecks:")
        chk: List = im2sql.typeEnforce(columns, lines[START_POS:])
    else:
        chk: List = []

        if len(chk) == 0:
            print("No errors found! You can copy-paste in peace :D\n")

    # if "-o" in sys.argv and "-o" != sys.argv[-1]:
    #     index: int = sys.argv.index("-o")

    #     path: str = sys.argv[index + 1]

    #     im2sql.write(table_name, commands, path)

    return [commands, chk]

# def test():
#     # pass
#     if "--test" in sys.argv:
#         pass

#     INPUT_DIR: List = list(os.walk("tests/tesseract/input"))[0][-1]

    # for i in


if __name__ == "__main__":
    INPUT_PATH = input("Enter image path: ")
    if INPUT_PATH == "":
        INPUT_PATH: str = "/home/anuran/Desktop/sample sql table 8.png"  # "tests/tesseract/input/works on.png"

    TESSERACT_PATH: str = config("TESSERACT_PATH")

    try:
        print(driver(INPUT_PATH, TESSERACT_PATH))
    except Exception as e:
        print(f"Exception encountered. Details: {e}")
