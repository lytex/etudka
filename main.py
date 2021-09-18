#!/usr/bin/python3

import random
import os
from enum import Enum, auto
import PySimpleGUI as sg
from gensound import Sine


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
            NoteLetter.C: "c'4",
            NoteLetter.D: "d'4",
            NoteLetter.E: "e'4",
            NoteLetter.F: "f'4",
            NoteLetter.G: "g'4",
            NoteLetter.A: "a'4",
            NoteLetter.B: "b'4",
        }

        note = mapping[self.letter]

        if (self.kind is NoteKind.SHARP):
            note += ""  # TODO: `+= "s"`
        elif (self.kind is NoteKind.FLAT):
            note += ""  # TODO: `+= "f"`

        return note

    def toGensoundNote(self) -> str:
        mapping = {
            NoteLetter.C: "C",
            NoteLetter.D: "D",
            NoteLetter.E: "E",
            NoteLetter.F: "F",
            NoteLetter.G: "G",
            NoteLetter.A: "A",
            NoteLetter.B: "B",
        }

        note = mapping[self.letter]

        if (self.kind is NoteKind.SHARP):
            note += "#"
        elif (self.kind is NoteKind.FLAT):
            note += "b"

        return note


def genMelody(notesCount: int) -> list:
    melody = []

    for i in range(notesCount):
        melody.append(Note.gen())

    return melody


def genMusicSheet(melody: list, keySignature: str):
    with open("sheet.ly", "w") as sheet:
        print("\\version \"2.10.33\"", file=sheet)
        print("\\include \"english.ly\"", file=sheet)

        notes = ""
        for note in melody:
            notes += note.toLilyPondNote()
            notes += " "

        print(
            "@\n\\clef treble\n\\time 3/4\n\\key {}\n{}\n&\n"
            .format(keySignature, notes)
            .replace("@", "{")
            .replace("&", "}"),
            file=sheet)

    os.system("lilypond --png sheet.ly")


def genSound(melody: list):
    notes = ""
    for note in melody:
        notes += note.toGensoundNote()
        notes += " "

    s = Sine(notes, duration=1e3 / 3)
    s.play()


notesCount = 300
keySignature = "c \major"

melody = genMelody(notesCount)
genMusicSheet(melody, keySignature)

layout = [
    [sg.Image(key="-IMAGE-", filename="sheet.png"),
     sg.Text("Notes Count:"), sg.Spin([i for i in range(
         20, 300)], initial_value=notesCount, key="-NOTESCOUNT-", size=(10, 1)),
     sg.Text("Key Signature:"), sg.Input(
         default_text=keySignature, key="-KEY-", size=(10, 1))
     ],
    [sg.Button("Play"), sg.Button("New Melody")]
]

window = sg.Window("Etudes Generator", layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "New Melody":
        notesCount = int(window["-NOTESCOUNT-"].Get())
        keySignature = window["-KEY-"].Get()

        melody = genMelody(notesCount)
        genMusicSheet(melody, keySignature)

        window["-IMAGE-"].update(filename="sheet.png")

    if event == "Play":
        genSound(melody)

window.close()
