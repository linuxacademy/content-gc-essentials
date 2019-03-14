# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import current_app
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb


builtin_list = list


def init_app(app):
    pass


# [START model]
class Album(ndb.Model):
    artist = ndb.StringProperty()
    imageUrl = ndb.StringProperty()
    title = ndb.StringProperty()
# [END model]


# [START from_datastore]
def from_datastore(entity):
    """Translates Datastore results into the format expected by the
    application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    This returns:
        {id: id, prop: val, ...}
    """
    if not entity:
        return None
    if isinstance(entity, builtin_list):
        entity = entity.pop()
    album = {}
    album['id'] = entity.key.id()
    album['artist'] = entity.artist
    album['imageUrl'] = entity.imageUrl
    album['title'] = entity.title
    return album
# [END from_datastore]



# [START list]
def list(limit=10, cursor=None):
    if cursor:
        cursor = Cursor(urlsafe=cursor)
    query = Album.query().order(Album.title)
    entities, cursor, more = query.fetch_page(limit, start_cursor=cursor)
    entities = builtin_list(map(from_datastore, entities))
    return entities, cursor.urlsafe() if len(entities) == limit else None
# [END list]


# [START read]
def read(id):
    album_key = ndb.Key('Album', int(id))
    results = album_key.get()
    return from_datastore(results)
# [END read]


# [START update]
def update(data, id=None):
    if id:
        key = ndb.Key('Album', int(id))
        album = key.get()
    else:
        album = Album()
    album.artist = data['artist']
    album.imageUrl = data['imageUrl']
    album.title = data['title']
    album.put()
    return from_datastore(album)

create = update
# [END update]


# [START delete]
def delete(id):
    key = ndb.Key('Album', int(id))
    key.delete()
# [END delete]
