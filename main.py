#!/usr/bin/python3

import random
import webbrowser
import os
from enum import Enum
import PySimpleGUI as sg
from pathlib import Path


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
        availableNotes = []

        if (NoteSettings.C):
            availableNotes.append(NoteLetter.C)
        if (NoteSettings.D):
            availableNotes.append(NoteLetter.D)
        if (NoteSettings.E):
            availableNotes.append(NoteLetter.E)
        if (NoteSettings.F):
            availableNotes.append(NoteLetter.F)
        if (NoteSettings.G):
            availableNotes.append(NoteLetter.G)
        if (NoteSettings.A):
            availableNotes.append(NoteLetter.A)
        if (NoteSettings.B):
            availableNotes.append(NoteLetter.B)

        return random.choice(availableNotes)


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

    suffixlessOutputFile = Path(window["-OUTPUT-"].Get()).with_suffix("")
    outputFileStr = os.fspath(suffixlessOutputFile)
    print(outputFileStr)

    os.system("lilypond --output " + outputFileStr + " --pdf sheet.ly")


def openSheetMusic():
    webbrowser.open(window["-OUTPUT-"].Get())


class CommonSettings:
    notesCount = 150  # This is a private property.
    timeSignature = "3/4"
    keySignature = "c \major"


class NoteSettings:
    C = D = E = F = G = A = B = True


class AccidentalSettings:
    flats = sharps = naturals = True


class PatternSettings:
    individualNotesTreble = individualNotesBass = chordsTreble = chordsBass = True


def createLayout():
    layout = []

    layout.append(commonSettingsLayout())
    layout.append(noteSettingsLayout())
    layout.append(accidentalSettingsLayout())
    layout.append(patternSettingsLayout())
    layout.append([
        [sg.HorizontalSeparator()],
        [sg.Text("Output:"), sg.Input(
            default_text="sheet.pdf", key="-OUTPUT-", size=(30, 1))],
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


def noteCheckbox(note: str):
    return sg.Checkbox(note, key="-NOTE-" + note + "-", default=True)


def noteSettingsLayout():
    return [[sg.Text("Notes")],
            [sg.HorizontalSeparator()],
            [[noteCheckbox("C"), noteCheckbox("D"), noteCheckbox(
                "E"), noteCheckbox("F"), noteCheckbox("G")], [noteCheckbox("A"), noteCheckbox("B")]]
            ]


def accidentalSettingsLayout():
    flats = sg.Checkbox("Flats", key="-FLATS-", default=True)
    sharps = sg.Checkbox("Sharps", key="-SHARPS-", default=True)
    naturals = sg.Checkbox("Naturals", key="-NATURALS-", default=True)

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
    extractNoteSettings(window)
    extractAccidentalSettings(window)
    extractPatternSettings(window)


def extractCommonSettings(window):
    CommonSettings.keySignature = window["-KEY-SIGNATURE-"].Get()
    CommonSettings.timeSignature = window["-TIME-SIGNATURE-"].Get()


def extractNoteSettings(window):
    NoteSettings.C = window["-NOTE-C-"].Get()
    NoteSettings.D = window["-NOTE-D-"].Get()
    NoteSettings.E = window["-NOTE-E-"].Get()
    NoteSettings.F = window["-NOTE-F-"].Get()
    NoteSettings.G = window["-NOTE-G-"].Get()
    NoteSettings.A = window["-NOTE-A-"].Get()
    NoteSettings.B = window["-NOTE-B-"].Get()


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


window = sg.Window("Etudka", createLayout())

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "New Sheet":
        extractSettings(window)
        genMusicSheet(genMelody(Clef.TREBLE), genMelody(Clef.BASS))
        openSheetMusic()

window.close()
