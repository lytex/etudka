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

    @staticmethod
    def gen():
        return random.choice(list(NoteLetter))


class NoteKind(Enum):
    NATURAL = 1
    SHARP = 2
    FLAT = 3

    @staticmethod
    def gen():
        result = random.choice(list(NoteKind))

        if result is NoteKind.SHARP and not AccidentalSettings.sharps:
            result = NoteKind.NATURAL
        if result is NoteKind.FLAT and not AccidentalSettings.flats:
            result = NoteKind.NATURAL

        return result

    def toLilyPondAccidental(self):
        result = ""

        if (self is NoteKind.SHARP):
            result += "s"
        elif (self is NoteKind.FLAT):
            result += "f"

        return result


class Note:
    def __init__(self, letter: NoteLetter, kind: NoteKind):
        self.letter = letter
        self.kind = kind

    @staticmethod
    def gen():
        return Note(NoteLetter.gen(), NoteKind.gen())

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

        return mapping[self.letter] + self.kind.toLilyPondAccidental()


class Chord:
    def __init__(self, derivedFrom: Note):
        self.derivedFrom = derivedFrom

    @staticmethod
    def gen():
        return Chord(Note.gen())

    def toLilyPongChord(self, lilyPondMark: str) -> str:
        return "\chordmode {{ {}{} }}".format(self.derivedFrom.toLilyPondNote(), lilyPondMark)


class Clef(Enum):
    TREBLE = 1
    BASS = 2

    def toLilyPondMarkIndividual(self):
        if self == Clef.TREBLE:
            return "'"
        else:
            return ""

    def toLilyPondMarkChord(self):
        if self == Clef.TREBLE:
            return ""
        else:
            return ","


def canGenerateIndividualNote(clef: Clef):
    return (PatternSettings.individualNotesTreble and clef == Clef.TREBLE or PatternSettings.individualNotesBass and clef == Clef.BASS)


def canGenerateChord(clef: Clef):
    return (PatternSettings.chordsTreble and clef == Clef.TREBLE or PatternSettings.chordsBass and clef == Clef.BASS)


def genBeat(clef: Clef) -> str:
    chordProbability = 20
    choice = random.randrange(0, 100)

    if canGenerateChord(clef) and (choice < chordProbability or not canGenerateIndividualNote(clef)):
        return Chord.gen().toLilyPongChord(clef.toLilyPondMarkChord())
    if canGenerateIndividualNote(clef):
        return Note.gen().toLilyPondNote() + clef.toLilyPondMarkIndividual()

    raise RuntimeError(
        "Either chords or individual notes or both must be specified")


def genMelody(clef: Clef) -> list:
    melody = []

    for i in range(CommonSettings.notesCount):
        melody.append(genBeat(clef))

    return melody


def genMusicSheet(trebleMelody: list, bassMelody: list):
    with open("sheet.ly", "w") as sheet:
        commonStaffSettings = "\\time {}\n\\key {}".format(
            CommonSettings.timeSignature, CommonSettings.keySignature)

        treble = "{{\n{}\n\\clef treble\n\n{}\n}}".format(
            commonStaffSettings, " ".join(trebleMelody))
        bass = "{{\n{}\n\\clef bass\n\n{}\n}}".format(
            commonStaffSettings, " ".join(bassMelody))

        print(
            "\\version \"2.10.33\"\n"
            "\\include \"english.ly\"\n\n"
            "upper = {}\n\n"
            "lower = {}\n\n"
            "\\score {{\n"
            "\\new PianoStaff \\with {{ instrumentName = \"Piano\" }}\n"
            "<<\n"
            "\\new Staff = \"upper\" \\upper\n"
            "\\new Staff = \"lower\" \\lower\n"
            ">>\n"
            "\\layout {{}}\n"
            "}}\n".format(treble, bass),
            file=sheet)

    os.system("lilypond --pdf sheet.ly")


def openSheetMusic():
    webbrowser.open(r"sheet.pdf")


class CommonSettings:
    notesCount = 150  # This is a private property.
    timeSignature = "3/4"
    keySignature = "c \major"


class AccidentalSettings:
    flats = sharps = naturals = True


class PatternSettings:
    individualNotesTreble = individualNotesBass = chordsTreble = chordsBass = True


def createLayout():
    layout = []

    layout.append(commonSettingsLayout())
    layout.append(accidentalSettingsLayout())
    layout.append(patternSettingsLayout())
    layout.append([
        [sg.HorizontalSeparator()],
        [sg.Button("New Sheet")]
    ])

    return layout


def commonSettingsLayout():
    keySignature = [sg.Text("Key Signature:"), sg.Input(
        default_text="c \major", key="-KEY-SIGNATURE-", size=(10, 1))]
    timeSignature = [sg.Text("Time Signature:"), sg.Input(
        default_text="3/4", key="-TIME-SIGNATURE-", size=(10, 1))]

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


def patternSettingsLayout():
    individualNotes = [sg.Checkbox(
        "Treble Individual Notes", key="-INDIVIDUAL-NOTES-TREBLE-", default=True), sg.Checkbox(
        "Bass Individual Notes", key="-INDIVIDUAL-NOTES-BASS-", default=True)]

    chords = [sg.Checkbox(
        "Treble Chords", key="-CHORDS-TREBLE-", default=True), sg.Checkbox(
        "Bass Chords", key="-CHORDS-BASS-", default=True)]

    return [[sg.Text("Patterns")], [sg.HorizontalSeparator()], individualNotes, chords]


def extractSettings(window):
    extractCommonSettings(window)
    extractAccidentalSettings(window)
    extractPatternSettings(window)


def extractCommonSettings(window):
    CommonSettings.keySignature = window["-KEY-SIGNATURE-"].Get()
    CommonSettings.timeSignature = window["-TIME-SIGNATURE-"].Get()


def extractAccidentalSettings(window):
    AccidentalSettings.flats = window["-FLATS-"].Get()
    AccidentalSettings.sharps = window["-SHARPS-"].Get()
    AccidentalSettings.naturals = window["-NATURALS-"].Get()


def extractPatternSettings(window):
    PatternSettings.individualNotesTreble = window["-INDIVIDUAL-NOTES-TREBLE-"].Get(
    )
    PatternSettings.individualNotesBass = window["-INDIVIDUAL-NOTES-BASS-"].Get()

    PatternSettings.chordsTreble = window["-CHORDS-TREBLE-"].Get()
    PatternSettings.chordsBass = window["-CHORDS-BASS-"].Get()


window = sg.Window("Etudes Generator", createLayout())

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "New Sheet":
        extractSettings(window)
        genMusicSheet(genMelody(Clef.TREBLE), genMelody(Clef.BASS))
        openSheetMusic()

window.close()
