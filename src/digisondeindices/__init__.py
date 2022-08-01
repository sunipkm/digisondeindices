from .base import get_indices

def cli():
    """
    simple demo of retrieving DIDBase indices by date
    """
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument("date", help="time of observation yyyy-mm-ddTHH:MM:ss")
    p.add_argument("-s", "--station", help='Observation station code e.g. AH223', type=str)
    a = p.parse_args()

    inds = get_indices(a.date, p.station)

    print(inds)


if __name__ == "__main__":
    cli()