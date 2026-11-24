"""main.py - programul complet (Partea 7b), rulat cu: python main.py"""
from httptools import PATHS, report


def main():
    # 1. un raport pentru fiecare adresă, cu adresa păstrată în dicționar
    results = []
    for path in PATHS:
        info = report(path)
        info["path"] = path
        results.append(info)

    # 2. doar paginile cu status 200, cea mai lentă prima
    ok_pages = [p for p in results if p["status"] == 200]
    ok_pages.sort(key=lambda p: p["seconds"], reverse=True)
    for p in ok_pages:
        print(f"{p['path']} -> {p['status']}, {p['seconds']} secunde")

    # 3. totaluri (404 și timeout-ul se numără ca eșuate)
    print(f"Reușite: {len(ok_pages)} | Eșuate: {len(results) - len(ok_pages)}")


if __name__ == "__main__":
    main()
