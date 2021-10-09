#!/usr/bin/env python3
import sqlite3, pathlib, os, re, mutagen
import pprint
from shutil import copyfile
from mutagen.easyid3 import EasyID3
#Пути до файлов указываются абсолютные, естественно могут отличаться
DBfile='/mnt/c/Users/<USER_NAME>/AppData/Local/Packages/A025C540.Yandex.Music_vfvw9svesycw6/LocalState/musicdb_74d91febdbc99491ab20f9d917b6f3e5.sqlite'
YAmusicdir='/mnt/c/Users/<USER_NAME>/AppData/Local/Packages/A025C540.Yandex.Music_vfvw9svesycw6/LocalState/Music/74d91febdbc99491ab20f9d917b6f3e5'
musicdir='/mnt/c/Users/<USER_NAME>/Music/Yandex'



conn = sqlite3.connect(DBfile)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

sqlgettracks="""
SELECT 
T_Track.Id, 
T_TrackAlbum.TrackPosition AS Position,
T_Track.Title AS Title,
group_concat(T_Artist.Name, ', ') AS TrackArtist,
T_Album.Title AS Album,
T_Album.Year AS Year,
T_Album.ArtistsString AS AlbumArtist
FROM T_Track 
INNER JOIN T_TrackAlbum ON T_TrackAlbum.TrackId = T_Track.id 
INNER JOIN T_Album ON T_Album.Id = T_TrackAlbum.AlbumId 
INNER JOIN T_TrackArtist ON T_TrackArtist.TrackId = T_Track.id 
INNER JOIN T_Artist ON T_Artist.Id = T_TrackArtist.ArtistId 
WHERE IsOffline=1 GROUP BY T_Track.Id ORDER BY Album, Position;
"""


cursor.execute(sqlgettracks)

tracks=list()

for row in cursor.fetchall():
  tracks.append(dict(row))

albums=list(set(tuple(map(d.get, ['AlbumArtist', 'Year', 'Album'])) for d  in tracks))



for track in tracks:
  srcfile=YAmusicdir+'/'+track['Id']
  destfile=musicdir+'/'+re.sub('[\\\/\:\*\?\"\<\>\|]', '_', track['AlbumArtist']).rstrip('.')+'/'+track['Year']+' - '+re.sub('[\\\/\:\*\?\"\<\>\|]', '_', track['Album']).rstrip('.')+'/'+str(track['Position']).zfill(2)+' '+re.sub('[\\\/\:\*\?\"\<\>\|]', '_', track['Title'])+'.mp3'
  copyfile(srcfile, destfile)


  try:
    meta = EasyID3(destfile)
  except mutagen.id3.ID3NoHeaderError:
    meta = mutagen.File(destfile, easy=True)
    meta.add_tags()
  meta['title'] = str(track['Title'])
  meta['artist'] = str(track['TrackArtist'])
  meta['album'] = str(track['Album'])
  meta['albumartist'] = str(track['AlbumArtist'])
  meta['tracknumber'] = str(track['Position'])
  meta['date'] = str(track['Year'])
  meta.save(destfile)

