import json
import os

import tables
from tqdm import tqdm

# Local path constants
DATA_PATH = 'D:\\Users\\Claire\\Data\\datasets\\lakh_midi_dataset\\lmd_matched'
RESULTS_PATH = 'D:\\Users\\Claire\\Data\\datasets\\lakh_midi_dataset'
# Path to the file match_scores.json distributed with the LMD
SCORE_FILE = os.path.join(RESULTS_PATH, 'match_scores.json')


# Utility functions for retrieving paths
def msd_id_to_dirs(msd_id):
  """Given an MSD ID, generate the path prefix.
  E.g. TRABCD12345678 -> A/B/C/TRABCD12345678"""
  return os.path.join(msd_id[2], msd_id[3], msd_id[4], msd_id)


def msd_id_to_mp3(msd_id):
  """Given an MSD ID, return the path to the corresponding mp3"""
  return os.path.join(DATA_PATH, 'msd', 'mp3',
                      msd_id_to_dirs(msd_id) + '.mp3')


def msd_id_to_h5(h5):
  """Given an MSD ID, return the path to the corresponding h5"""
  return os.path.join(RESULTS_PATH, 'lmd_matched_h5',
                      msd_id_to_dirs(msd_id) + '.h5')


def get_midi_path(msd_id, midi_md5, kind):
  """Given an MSD ID and MIDI MD5, return path to a MIDI file.
  kind should be one of 'matched' or 'aligned'. """
  return os.path.join(RESULTS_PATH, 'lmd_{}'.format(kind),
                      msd_id_to_dirs(msd_id), midi_md5 + '.mid')


with open(SCORE_FILE) as f:
  scores_matches = json.load(f)

# Grab a Million Song Dataset ID from the scores dictionary
# scores = random.sample(list(scores), 1000)
scores = list(scores_matches)

possible_categories = {"jazz", "blues", "funk"}
tracks = set()
for msd_id in tqdm(scores):
  with tables.open_file(msd_id_to_h5(msd_id)) as h5:
    title = h5.root.metadata.songs.cols.title[0]
    artist_name = h5.root.metadata.songs.cols.artist_name[0]
    release = h5.root.metadata.songs.cols.release[0]
    genre = h5.root.metadata.songs.cols.genre[0]
    artist_terms = list(h5.root.metadata.artist_terms)
    artist_mbtags = list(h5.root.musicbrainz.artist_mbtags)
    for artist_term in artist_terms:
      artist_term = artist_term.decode("utf-8")
      for category in possible_categories:
        if category in artist_term:
          tracks.add(msd_id)
    for artist_term in artist_mbtags:
      artist_term = artist_term.decode("utf-8")
      for category in possible_categories:
        if category in artist_term:
          tracks.add(msd_id)

print()
print("total")
print(f"tracks: {len(tracks)}")
with open("tutorial4_tracks.csv", "w") as file:
  file.write(f"msd_id,midi_path\n")
  for msd_id in tracks:
    max_score = 0
    matched_midi_md5 = None
    score_matches = scores_matches[msd_id]
    # TODO here
    for midi_md5, score in score_matches.items():
      if score > max_score:
        matched_midi_md5 = midi_md5
    if not matched_midi_md5:
      print(f"not matched {msd_id} {score_matches}")
    get_midi_path(msd_id, matched_midi_md5, "matched")
    file.write(f"{msd_id}\n")
