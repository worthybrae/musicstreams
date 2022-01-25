# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import datetime
from numerize import numerize
from GoogleNews import GoogleNews
import json
from colorthief import ColorThief
import urllib.request
import numpy as np


class Albums(models.Model):
    spotifyid = models.CharField(db_column='spotifyId', primary_key=True, max_length=255)  # Field name made lowercase.
    name = models.CharField(max_length=255, blank=True, null=True)
    artist = models.CharField(max_length=255, blank=True, null=True)
    releasedate = models.DateField(db_column='releaseDate', blank=True, null=True)  # Field name made lowercase.
    cover = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    totalstreams = models.BigIntegerField(blank=True, null=True)
    day0streams = models.BigIntegerField(blank=True, null=True)
    day1streams = models.BigIntegerField(blank=True, null=True)
    totalgrowth = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'albums'

    def get_album_detail_view(self):
        album_dict = {}
        album_dict['streams_dict'] = {'totalalbumstreams': {}}
        album_dict['new_streams_dict'] = {'totalnewalbumstreams': {}}
        album_dict['revenue_dict'] = {'totalalbumrevenue': {}}
        album_dict['growth_dict'] = {}
        album_dict['songsorder'] = []
        album_dict['growthorder'] = []
        album_dict['name'] = self.name
        album_dict['artist'] = self.artist
        album_dict['cover'] = self.cover
        album_dict['releasedate'] = self.releasedate.strftime('%m-%d-%Y')
        album_dict['totalsongs'] = 0
        album_dict['runtime'] = 0
        valence_list = []
        energy_list = []
        danceability_list = []
        for song in self.songs_set.all():
            album_dict['totalsongs'] += 1
            album_dict['runtime'] += song.duration / 1000
            valence_list.append(song.valence)
            energy_list.append(song.energy)
            danceability_list.append(song.danceability)
            song_stream_counter = 0
            for songstream in song.songstreams_set.all().order_by('daterecorded'):
                if song_stream_counter == 0:
                    song_day_0_streams = songstream.totalstreams
                    most_recent_streams = songstream.totalstreams
                else:
                    #Growth
                    if song_stream_counter == 1:
                        old_growth_value = songstream.totalstreams - song_day_0_streams
                        song_day_1_streams = songstream.totalstreams - song_day_0_streams
                    else:
                        new_growth_value = songstream.totalstreams - song_day_0_streams
                        if old_growth_value == 0:
                            pass
                        else:
                            if song.name not in album_dict['growth_dict']:
                                album_dict['growth_dict'][song.name] = {(songstream.daterecorded - self.releasedate).days: (new_growth_value / song_day_1_streams - 1) * 100}
                            else:
                                album_dict['growth_dict'][song.name][(songstream.daterecorded - self.releasedate).days] = (new_growth_value / song_day_1_streams - 1) * 100
                            old_growth_value = new_growth_value
                    #Streams
                    if song.name not in album_dict['streams_dict']:
                        album_dict['streams_dict'][song.name] = {(songstream.daterecorded - self.releasedate).days: songstream.totalstreams - song_day_0_streams}
                    else:
                        album_dict['streams_dict'][song.name][(songstream.daterecorded - self.releasedate).days] = songstream.totalstreams - song_day_0_streams
                    if (songstream.daterecorded - self.releasedate).days not in album_dict['streams_dict']['totalalbumstreams']:
                        album_dict['streams_dict']['totalalbumstreams'][(songstream.daterecorded - self.releasedate).days] = songstream.totalstreams - song_day_0_streams
                    else:
                        album_dict['streams_dict']['totalalbumstreams'][(songstream.daterecorded - self.releasedate).days] += songstream.totalstreams - song_day_0_streams
                    #New Streams
                    if song.name not in album_dict['new_streams_dict']:
                        album_dict['new_streams_dict'][song.name] = {(songstream.daterecorded - self.releasedate).days: songstream.totalstreams - most_recent_streams}
                    else:
                        album_dict['new_streams_dict'][song.name][(songstream.daterecorded - self.releasedate).days] = songstream.totalstreams - most_recent_streams
                    if (songstream.daterecorded - self.releasedate).days not in album_dict['new_streams_dict']['totalnewalbumstreams']:
                        album_dict['new_streams_dict']['totalnewalbumstreams'][(songstream.daterecorded - self.releasedate).days] = songstream.totalstreams - most_recent_streams
                    else:
                        album_dict['new_streams_dict']['totalnewalbumstreams'][(songstream.daterecorded - self.releasedate).days] += songstream.totalstreams - most_recent_streams
                    #Revenue
                    if song.name not in album_dict['revenue_dict']:
                        album_dict['revenue_dict'][song.name] = {(songstream.daterecorded - self.releasedate).days: (songstream.totalstreams - song_day_0_streams) * .00348}
                    else:
                        album_dict['revenue_dict'][song.name][(songstream.daterecorded - self.releasedate).days] = (songstream.totalstreams - song_day_0_streams) * .00348
                    if (songstream.daterecorded - self.releasedate).days not in album_dict['revenue_dict']['totalalbumrevenue']:
                        album_dict['revenue_dict']['totalalbumrevenue'][(songstream.daterecorded - self.releasedate).days] = (songstream.totalstreams - song_day_0_streams) * .00348
                    else:
                        album_dict['revenue_dict']['totalalbumrevenue'][(songstream.daterecorded - self.releasedate).days] += (songstream.totalstreams - song_day_0_streams) * .00348
                    most_recent_streams = songstream.totalstreams - song_day_0_streams
                song_stream_counter += 1
            streams_list = []
            dsr_list = []
            for key, value in album_dict['streams_dict'][song.name].items():
                dsr_list.append(key)
                streams_list.append(value)
            streams_list = sorted(streams_list)
            total_streams = max(streams_list)
            total_streams_str = numerize.numerize(total_streams, 1)

            growth_list = []
            for key, value in album_dict['growth_dict'][song.name].items():
                growth_list.append(value)
            total_growth = max(growth_list)
            album_dict['songsorder'].append([song.name, total_streams, total_streams_str, streams_list, dsr_list])
            album_dict['growthorder'].append([song.name, round(total_growth, 1)])
        album_dict['songsorder'].sort(key = lambda x: x[1], reverse = True)
        album_dict['growthorder'].sort(key = lambda x: x[1], reverse = True)
        growth_graph_label = []
        for x in album_dict['growthorder']:
            if len(x[0]) > 20:
                growth_graph_label.append(x[0][:20] + '...')
            else:
                growth_graph_label.append(x[0][:20])
        album_dict['growthgraphlabels'] = json.dumps(growth_graph_label)
        album_dict['growthgraphdata'] = [x[1] for x in album_dict['growthorder']]
        mean = sum([x[1] for x in album_dict['growthorder']]) / len([x[1] for x in album_dict['growthorder']])
        variance = sum([((x - mean) ** 2) for x in [x[1] for x in album_dict['growthorder']]]) / len([x[1] for x in album_dict['growthorder']])
        res = ((variance ** 0.5) / mean) * 100
        album_dict['avgsonggrowthcov'] = f"{res:,.1f}%"
        streams_graph_label = []
        for x in album_dict['songsorder']:
            if len(x[0]) > 20:
                streams_graph_label.append(x[0][:20] + '...')
            else:
                streams_graph_label.append(x[0][:20])
        album_dict['streamsgraphlabels'] = json.dumps(streams_graph_label)
        album_dict['streamsgraphdata'] = [x[1] for x in album_dict['songsorder']]
        album_dict['revenuegraphdata'] = [round((x[1] * .00348), 2) for x in album_dict['songsorder']]
        print(album_dict['songsorder'])
        album_dict['avgsonglength'] = str(datetime.timedelta(seconds=(album_dict['runtime']) / album_dict['totalsongs'])).split(':')
        avg_minutes = int(album_dict['avgsonglength'][1])
        avg_seconds = float(album_dict['avgsonglength'][2])
        album_dict['avgsonglength'] = f'{avg_minutes:.0f}:{avg_seconds:02.0f}'
        album_dict['totalduration'] = self.totalstreams * album_dict['runtime'] / 86400
        album_dict['totalduration'] = numerize.numerize(album_dict['totalduration'], 1)
        album_dict['runtime'] = str(datetime.timedelta(seconds=album_dict['runtime'])).split(':')
        if int(album_dict['runtime'][0]) != 0:
            total_hours = int(album_dict['runtime'][0])
            total_minutes = int(album_dict['runtime'][1])
            total_seconds = float(album_dict['runtime'][2])
            album_dict['runtime'] = f'{total_hours:.0f}:{total_minutes:.0f}:{total_seconds:02.0f}'
        else:
            total_minutes = int(album_dict['runtime'][1])
            total_seconds = float(album_dict['runtime'][2])
            album_dict['runtime'] = f'{total_minutes:.0f}:{total_seconds:02.0f}'
        mean_energy = sum(energy_list) / len(energy_list)
        album_dict['energy'] = round(mean_energy*100)
        variance_energy = sum([((x - mean_energy) ** 2) for x in energy_list]) / len(energy_list)
        res_energy = (variance_energy ** 0.5) * 100
        album_dict['energysd'] = f'{res_energy:.2f}%'
        mean_happiness = sum(valence_list) / len(valence_list)
        album_dict['happiness'] = round(mean_happiness*100, 0)
        variance_happiness = sum([((x - mean_happiness) ** 2) for x in valence_list]) / len(valence_list)
        res_happiness = (variance_happiness ** 0.5) * 100
        album_dict['happinesssd'] = f'{res_happiness:.2f}%'
        mean_danceability = sum(danceability_list) / len(danceability_list)
        album_dict['danceability'] = round(mean_danceability*100, 0)
        variance_danceability = sum([((x - mean_danceability) ** 2) for x in danceability_list]) / len(danceability_list)
        res_danceability = (variance_danceability ** 0.5) * 100
        album_dict['danceabilitysd'] = f'{res_danceability:.2f}%'
        album_dict['totalstreams'] = numerize.numerize(self.totalstreams, 1)
        album_dict['avgsongstreams'] = numerize.numerize((self.totalstreams / album_dict['totalsongs']), 1)
        album_dict['totalgrowth'] = f"{self.totalgrowth:,.1f}%"
        album_dict['avgsonggrowth'] = f"{(self.totalgrowth / album_dict['totalsongs']):,.1f}%"
        album_dict['totalrevenue'] = '$' + numerize.numerize((self.totalstreams * .00348), 1)
        album_dict['avgsongrevenue'] = '$' + numerize.numerize(((self.totalstreams * .00348) / album_dict['totalsongs']), 1)
        streams_list = []
        dsr_list = []
        for key, value in album_dict['streams_dict']['totalalbumstreams'].items():
            streams_list.append(value)
            dsr_list.append(key)
        streams_list = sorted(streams_list)
        mean = sum(streams_list) / len(streams_list)
        variance = sum([((x - mean) ** 2) for x in streams_list]) / len(streams_list)
        res = ((variance ** 0.5) / mean) * 100
        album_dict['avgsongstreamscov'] = f"{res:,.1f}%"
        dsr_list = sorted(dsr_list)
        album_dict['totalstreamslist'] = streams_list
        album_dict['totaldsrlist'] = dsr_list
        album_dict['dsr'] = len(dsr_list)
        news_list = []
        googlenews = GoogleNews()
        googlenews = GoogleNews(lang='en')
        googlenews.get_news(self.artist + ' ' + self.name)
        for item in googlenews.results():
            if self.artist.lower() in item['title'].lower() or self.name.lower() in item['title'].lower():
                if len(item['title'].replace(' bookmark_border', '').strip()) > 50:
                    title = item['title'].replace(' bookmark_border', '').strip()[:50] + '...'
                else:
                    title = item['title'].replace(' bookmark_border', '').strip()
                if title != '' and item['date'] != None and isinstance(item['datetime'], datetime.datetime) == True and item['link'] != None:
                    news_list.append([title, item['date'], item['link'], item['datetime']])
            if len(news_list) > 9:
                break
        news_list.sort(key = lambda x: x[3], reverse = True)
        album_dict['newslist'] = news_list
        urllib.request.urlretrieve(self.cover, "cover.png")
        color_thief = ColorThief('cover.png')
        palette = color_thief.get_palette(color_count=20)
        best_color_match = {'distance': 0}
        for c in palette:
            for c2 in [x for x in palette if x != c]:
                color1 = np.asarray(tuple(c))
                color2 = np.asarray(tuple(c2))
                rm = 0.5*(color1[0]+color2[0])
                d = sum((2+rm,4,3-rm)*(color1-color2)**2)**0.5
                if d > best_color_match['distance']:
                    best_color_match['color1'] = color1
                    best_color_match['color2'] = color2
                    best_color_match['distance'] = d
                    best_color_match['color1gray'] = 0.2126*tuple(c)[0] + 0.7152*tuple(c)[1] + 0.0722*tuple(c)[2]
                    best_color_match['color2gray'] = 0.2126*tuple(c2)[0] + 0.7152*tuple(c2)[1] + 0.0722*tuple(c2)[2]

        if best_color_match['color1gray'] >= best_color_match['color2gray']:
            best_color_match['colormain'] = c2
            best_color_match['coloralt'] = c
        else:
            best_color_match['colormain'] = c
            best_color_match['coloralt'] = c2
        album_dict['colormainr'] = best_color_match['coloralt'][0] - (255 - best_color_match['coloralt'][0]) * .5
        album_dict['colormaing'] = best_color_match['coloralt'][1] - (255 - best_color_match['coloralt'][1]) * .5
        album_dict['colormainb'] = best_color_match['coloralt'][2] - (255 - best_color_match['coloralt'][2]) * .5
        album_dict['coloraltr'] = best_color_match['colormain'][0] + (255 - best_color_match['colormain'][0]) * .75
        album_dict['coloraltg'] = best_color_match['colormain'][1] + (255 - best_color_match['colormain'][1]) * .75
        album_dict['coloraltb'] = best_color_match['colormain'][2] + (255 - best_color_match['colormain'][2]) * .75
        album_dict['colormain'] = json.dumps(f"rgb({best_color_match['colormain'][0]}, {best_color_match['colormain'][1]}, {best_color_match['colormain'][2]})")
        album_dict['coloralt'] = json.dumps(f"rgb({best_color_match['coloralt'][0]}, {best_color_match['coloralt'][1]}, {best_color_match['coloralt'][2]})")
        return album_dict


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Songstreams(models.Model):
    daterecorded = models.DateField(db_column='dateRecorded', blank=True, null=True)  # Field name made lowercase.
    songspotifyid = models.ForeignKey('Songs', models.DO_NOTHING, db_column='songSpotifyId', blank=True, null=True)  # Field name made lowercase.
    totalstreams = models.BigIntegerField(db_column='totalStreams', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'songStreams'


class Songs(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    songorder = models.SmallIntegerField(db_column='songOrder', blank=True, null=True)  # Field name made lowercase.
    songspotifyid = models.CharField(db_column='songSpotifyId', primary_key=True, max_length=255)  # Field name made lowercase.
    albumspotifyid = models.ForeignKey(Albums, models.DO_NOTHING, db_column='albumSpotifyId', blank=True, null=True)  # Field name made lowercase.
    acousticness = models.FloatField(blank=True, null=True)
    danceability = models.FloatField(blank=True, null=True)
    energy = models.FloatField(blank=True, null=True)
    instrumentalness = models.FloatField(blank=True, null=True)
    pitch = models.IntegerField(blank=True, null=True)
    liveness = models.FloatField(blank=True, null=True)
    loudness = models.FloatField(blank=True, null=True)
    mode = models.IntegerField(blank=True, null=True)
    speechiness = models.FloatField(blank=True, null=True)
    tempo = models.FloatField(blank=True, null=True)
    timesignature = models.IntegerField(db_column='timeSignature', blank=True, null=True)  # Field name made lowercase.
    valence = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'songs'
