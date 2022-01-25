from django.shortcuts import render
from streams.models import Albums, Songs, Songstreams
import datetime
from numerize import numerize
from GoogleNews import GoogleNews
import json

# Create your views here.

def Homepage(request):
    all_albums = Albums.objects.all().order_by('-totalgrowth')
    top_streams = []
    albums = Albums.objects.filter(status='ACTIVE').order_by('-totalstreams')[:5]
    rank = 1
    for album in albums:
        album_spotify_id = album.spotifyid
        artist_name = album.artist
        cover_art = album.cover
        day_0_streams = album.day0streams
        streams_dict = {}
        for song in album.songs_set.all():
            for songstream in song.songstreams_set.all():
                if songstream.daterecorded not in streams_dict:
                    streams_dict[songstream.daterecorded] = songstream.totalstreams
                else:
                    streams_dict[songstream.daterecorded] += songstream.totalstreams
        streams_list = []
        dates_list = []
        for k, v in streams_dict.items():
            dates_list.append(k)
            streams_list.append(v - day_0_streams)
        streams_list = sorted(streams_list)[1:]
        dsr_list = list(range(1, len(dates_list[1:])+1))
        total_streams = numerize.numerize(album.totalstreams, 1)
        total_revenue = "$" + str(numerize.numerize((album.totalstreams * .00348), 1))
        total_growth = f"{album.totalgrowth:,.1f}%"
        top_streams.append([rank, album_spotify_id, artist_name, cover_art, streams_list, dsr_list, total_streams, total_revenue, total_growth])
        rank += 1

    top_growth = []
    albums = Albums.objects.filter(status='ACTIVE').order_by('-totalgrowth')[:5]
    rank = 1
    for album in albums:
        album_spotify_id = album.spotifyid
        artist_name = album.artist
        cover_art = album.cover
        day_0_streams = album.day0streams
        streams_dict = {}
        for song in album.songs_set.all():
            for songstream in song.songstreams_set.all():
                if songstream.daterecorded not in streams_dict:
                    streams_dict[songstream.daterecorded] = songstream.totalstreams
                else:
                    streams_dict[songstream.daterecorded] += songstream.totalstreams
        streams_list = []
        dates_list = []
        for k, v in streams_dict.items():
            dates_list.append(k)
            streams_list.append(v - day_0_streams)
        streams_list = sorted(streams_list)[1:]
        dsr_list = list(range(1, len(dates_list[1:])+1))
        total_streams = numerize.numerize(album.totalstreams, 1)
        total_revenue = "$" + str(numerize.numerize((album.totalstreams * .00348), 1))
        total_growth = f"{album.totalgrowth:,.1f}%"
        top_growth.append([rank, album_spotify_id, artist_name, cover_art, streams_list, dsr_list, total_streams, total_revenue, total_growth])
        rank += 1

    return render(request, 'streams/home.html', {'top_streams': top_streams, 'top_growth': top_growth, 'all_albums': all_albums})

def Detailpage(request, album_spotify_id):
    album = Albums.objects.get(pk=album_spotify_id)
    album_dict = album.get_album_detail_view()
    return render(request, 'streams/detail.html', {'album_dict': album_dict})


def Aboutpage(request):
    return render(request, 'streams/about.html', {})
