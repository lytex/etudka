#!/usr/bin/python3

import random
import webbrowser
import os
from enum import Enum, auto
import PySimpleGUI as sg


class NoteLetter(Enum):
    C = 1
    D = 2
    E = 3
    F = 4
    G = 5
    A = 6
    B = 7


class NoteKind(Enum):
    NATURAL = 1
    SHARP = 2
    FLAT = 3


class Note:
    def __init__(self, letter: NoteLetter, kind: NoteKind):
        self.letter = letter
        self.kind = kind

    @staticmethod
    def gen():
        return Note(random.choice(list(NoteLetter)), random.choice(list(NoteKind)))

    def toLilyPondNote(self) -> str:
        mapping = {
            NoteLetter.C: "c",
            NoteLetter.D: "d",
            NoteLetter.E: "e",
            NoteLetter.F: "f",
            NoteLetter.G: "g",
            NoteLetter.A: "a",
            NoteLetter.B: "b",
        }

        note = mapping[self.letter]

        if (self.kind is NoteKind.SHARP and AccidentalSettings.sharps):
            note += "s"
        elif (self.kind is NoteKind.FLAT and AccidentalSettings.flats):
            note += "f"

        note += "'4"

        return note


def genMelody() -> list:
    melody = []

    for i in range(CommonSettings.notesCount):
        melody.append(Note.gen())

    return melody


def genMusicSheet(melody: list):
    with open("sheet.ly", "w") as sheet:
        print("\\version \"2.10.33\"", file=sheet)
        print("\\include \"english.ly\"", file=sheet)

        notes = ""
        for note in melody:
            notes += note.toLilyPondNote()
            notes += " "

        print(
            "@\n\\clef treble\n\\time {}\n\\key {}\n{}\n&\n"
            .format(CommonSettings.timeSignature, CommonSettings.keySignature, notes)
            .replace("@", "{")
            .replace("&", "}"),
            file=sheet)

    os.system("lilypond --pdf sheet.ly")


def openSheetMusic():
    webbrowser.open(r"sheet.pdf")


def createLayout():
    layout = []

    layout.append(commonSettingsLayout())
    layout.append(accidentalSettingsLayout())
    layout.append([
        [sg.HorizontalSeparator()],
        [sg.Button("New Sheet")]
    ])

    return layout


def commonSettingsLayout():
    keySignature = [sg.Text("Key Signature:"), sg.Input(
        default_text="c \major", key="-KEY-SIGNATURE-", size=(10, 1))]
    timeSignature = [sg.Text("Time Signature:"), sg.Input(
        default_text="2/4", key="-TIME-SIGNATURE-", size=(10, 1))]

    return [[sg.Text("Common Settings")],
            [sg.HorizontalSeparator()],
            [sg.Column([keySignature, timeSignature],
                       element_justification="right")]
            ]


def accidentalSettingsLayout():
    flats = [sg.Checkbox("Flats", key="-FLATS-", default=True)]
    sharps = [sg.Checkbox("Sharps", key="-SHARPS-", default=True)]
    naturals = [sg.Checkbox("Naturals", key="-NATURALS-", default=True)]

    return [[sg.Text("Accidentals")], [sg.HorizontalSeparator()], flats, sharps, naturals]


def extractSettings(window):
    extractCommonSettings(window)
    extractAccidentalSettings(window)


def extractCommonSettings(window):
    CommonSettings.keySignature = window["-KEY-SIGNATURE-"].Get()
    CommonSettings.timeSignature = window["-TIME-SIGNATURE-"].Get()


def extractAccidentalSettings(window):
    AccidentalSettings.flats = window["-FLATS-"].Get()
    AccidentalSettings.sharps = window["-SHARPS-"].Get()
    AccidentalSettings.naturals = window["-NATURALS-"].Get()


class CommonSettings:
    notesCount = 300
    timeSignature = "2/4"
    keySignature = "c \major"


class AccidentalSettings:
    flats = sharps = naturals = True


genMusicSheet(genMelody())

window = sg.Window("Etudes Generator", createLayout())

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "New Sheet":
        extractSettings(window)
        genMusicSheet(genMelody())
        openSheetMusic()

window.close()
