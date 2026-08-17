"""A tiny task list stored in a text file."""

import sys

TASK_FILE = "tasks.txt"


def add(text):
    with open(TASK_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    print("added:", text)


def show():
    try:
        with open(TASK_FILE, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        lines = []

    if not lines:
        print('no tasks yet — add one with: python tasks.py add "..."')
        return

    for i, line in enumerate(lines, start=1):
        print(f"{i}. {line}")

def done(number):
    try:
        with open(TASK_FILE, encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        lines = []

    if number < 1 or number > len(lines):
        print("no task number", number)
        return

    finished = lines.pop(number - 1)
    with open(TASK_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    print("done:", finished)


def main():
    args = sys.argv[1:]
    if args and args[0] == "add" and len(args) > 1:
        add(" ".join(args[1:]))
    elif args and args[0] == "list":
        show()
    elif args and args[0] == "done" and len(args) > 1:
        try:
            number = int(args[1])
        except ValueError:
            print("not a number:", args[1])
            return
        done(number)
    else:
        print("usage: python tasks.py [add <text> | list | done <number>]")



if __name__ == "__main__":
    main()
